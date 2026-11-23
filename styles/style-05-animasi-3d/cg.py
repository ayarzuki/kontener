"""Mesin 3D "film animasi" kecil (moderngl): permukaan halus, kulit ber-subsurface, mata mengilap,
bayangan lembut, cahaya kunci/isi/rim + cahaya layar, tone-map filmic, quad bertekstur (layar laptop/HP/jendela).

Satuan: sentimeter. Lantai di y = 0. Kamera: look_at + perspective.
"""
import math
import sys

import moderngl
import numpy as np

# ---------------------------------------------------------------- matematika
def look_at(eye, target, up=(0, 1, 0)):
    eye, target, up = map(lambda v: np.asarray(v, np.float32), (eye, target, up))
    f = target - eye
    f /= np.linalg.norm(f)
    s = np.cross(f, up)
    s /= np.linalg.norm(s)
    u = np.cross(s, f)
    M = np.eye(4, dtype=np.float32)
    M[0, :3], M[1, :3], M[2, :3] = s, u, -f
    M[:3, 3] = -M[:3, :3] @ eye
    return M


def perspective(fov, aspect, near=1.0, far=600.0):
    f = 1 / math.tan(math.radians(fov) / 2)
    M = np.zeros((4, 4), np.float32)
    M[0, 0], M[1, 1] = f / aspect, f
    M[2, 2], M[2, 3] = (far + near) / (near - far), 2 * far * near / (near - far)
    M[3, 2] = -1
    return M


def ortho(l, r, b, t, n, f):
    M = np.eye(4, dtype=np.float32)
    M[0, 0], M[1, 1], M[2, 2] = 2 / (r - l), 2 / (t - b), -2 / (f - n)
    M[0, 3], M[1, 3], M[2, 3] = -(r + l) / (r - l), -(t + b) / (t - b), -(f + n) / (f - n)
    return M


def T(x=0, y=0, z=0):
    M = np.eye(4, dtype=np.float32)
    M[:3, 3] = (x, y, z)
    return M


def Sc(x, y=None, z=None):
    y = x if y is None else y
    z = x if z is None else z
    return np.diag([x, y, z, 1]).astype(np.float32)


def R(ax, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    M = np.eye(4, dtype=np.float32)
    i, j = {"x": (1, 2), "y": (2, 0), "z": (0, 1)}[ax]
    M[i, i], M[i, j], M[j, i], M[j, j] = c, -s, s, c
    return M


def chain(*ms):
    out = np.eye(4, dtype=np.float32)
    for m in ms:
        out = out @ m
    return out


# ---------------------------------------------------------------- mesh
def _normals(V, F):
    N = np.zeros_like(V)
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    for k in range(3):
        np.add.at(N, F[:, k], fn)
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9
    return N


def _lumpy(V, N, amp, seed, freq=0.35):
    if amp <= 0:
        return V
    rng = np.random.default_rng(seed)
    h = np.zeros(len(V), np.float32)
    for k in range(7):
        d = rng.normal(size=3)
        d /= np.linalg.norm(d)
        f = freq * (1.6 ** k) * rng.uniform(0.8, 1.2)
        h += np.sin(V @ d * f + rng.uniform(0, 6.28)) / (1.5 ** k)
    return V + N * (h[:, None] * amp)


class Mesh:
    def __init__(self, V, F, N=None, UV=None):
        self.V = np.asarray(V, np.float32)
        self.F = np.asarray(F, np.int32)
        self.N = _normals(self.V, self.F) if N is None else N
        self.UV = np.zeros((len(self.V), 2), np.float32) if UV is None else np.asarray(UV, np.float32)

    def lumpy(self, amp=0.08, seed=0, freq=0.35):
        V = _lumpy(self.V, self.N, amp, seed, freq)
        return Mesh(V, self.F)


def quad(w, h):
    """Quad w x h menghadap +z, UV (0,0) kiri-bawah."""
    V = np.array([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], np.float32)
    F = np.array([(0, 1, 2), (0, 2, 3)], np.int32)
    N = np.array([(0, 0, 1)] * 4, np.float32)
    UV = np.array([(0, 1), (1, 1), (1, 0), (0, 0)], np.float32)
    return Mesh(V, F, N, UV)


def sdf_mesh(sdf, center, radius, nu=120, nv=80, iters=24):
    """Mesh organik dari SDF: bola awal diproyeksikan ke permukaan nol (bentuk harus 'star-shaped' dari center)."""
    m = superellipsoid(radius, radius, radius, 1, 1, nu, nv)
    V = m.V.astype(np.float64) + np.asarray(center, np.float64)
    e = 0.05
    for _ in range(iters):
        d = sdf(V)
        g = np.stack([(sdf(V + np.array([e, 0, 0])) - sdf(V - np.array([e, 0, 0]))) / (2 * e),
                      (sdf(V + np.array([0, e, 0])) - sdf(V - np.array([0, e, 0]))) / (2 * e),
                      (sdf(V + np.array([0, 0, e])) - sdf(V - np.array([0, 0, e]))) / (2 * e)], 1)
        V = V - d[:, None] * g / np.maximum((g * g).sum(1), 1e-6)[:, None]
    return Mesh(V.astype(np.float32), m.F)


def sd_ellipsoid(P, c, r):
    q = (P - np.asarray(c)) / np.asarray(r)
    k0 = np.linalg.norm(q, axis=1)
    k1 = np.linalg.norm(q / np.asarray(r), axis=1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


def _grid_faces(nu, nv, wrap_u=True):
    F = []
    for j in range(nv - 1):
        for i in range(nu):
            i2 = (i + 1) % nu if wrap_u else i + 1
            if not wrap_u and i == nu - 1:
                continue
            a, b, c, d = j * nu + i, j * nu + i2, (j + 1) * nu + i, (j + 1) * nu + i2
            F += [(a, c, b), (b, c, d)]
    return np.array(F, np.int32)


def _spow(x, e):
    return np.sign(x) * np.abs(x) ** e


def superellipsoid(rx, ry, rz, e1=1.0, e2=1.0, nu=48, nv=32):
    u = np.linspace(-math.pi, math.pi, nu, endpoint=False)
    v = np.linspace(-math.pi / 2, math.pi / 2, nv)
    U, Vv = np.meshgrid(u, v)
    x = rx * _spow(np.cos(Vv), e1) * _spow(np.cos(U), e2)
    y = ry * _spow(np.sin(Vv), e1)
    z = rz * _spow(np.cos(Vv), e1) * _spow(np.sin(U), e2)
    V = np.stack([x, y, z], -1).reshape(-1, 3)
    F = _grid_faces(nu, nv)
    F = F[:, [0, 2, 1]]
    return Mesh(V, F)


def sphere(r, n=28):
    return superellipsoid(r, r, r, 1, 1, n, max(12, n * 2 // 3))


def rbox(w, h, d, round_=0.25, n=28):
    return superellipsoid(w / 2, h / 2, d / 2, round_, round_, n * 2, n)


def _catmull(pts, k=6):
    P = np.asarray(pts, np.float32)
    if len(P) < 3:
        return P
    out = []
    Q = np.vstack([P[0] * 2 - P[1], P, P[-1] * 2 - P[-2]])
    for i in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
        for s in range(k):
            t = s / k
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1])
    return np.array(out, np.float32)


def tube(pts, r, n=12, smooth=True, taper=0.0):
    P = _catmull(pts) if smooth else np.asarray(pts, np.float32)
    m = len(P)
    T_ = np.gradient(P, axis=0)
    T_ /= np.linalg.norm(T_, axis=1, keepdims=True) + 1e-9
    ref = np.array([0, 0, 1], np.float32) if abs(T_[0][2]) < 0.9 else np.array([0, 1, 0], np.float32)
    Vs = []
    nrm = np.cross(T_[0], ref)
    nrm /= np.linalg.norm(nrm)
    for i in range(m):
        nrm = nrm - T_[i] * float(nrm @ T_[i])
        nrm /= np.linalg.norm(nrm) + 1e-9
        b = np.cross(T_[i], nrm)
        tt = i / max(1, m - 1)
        rr = r * (1 - taper * abs(2 * tt - 1) ** 2)
        for k in range(n):
            a = 2 * math.pi * k / n
            Vs.append(P[i] + rr * (math.cos(a) * nrm + math.sin(a) * b))
    V = np.array(Vs, np.float32)
    F = _grid_faces(n, m)
    # tutup ujung dengan titik pusat
    c0, c1 = len(V), len(V) + 1
    V = np.vstack([V, P[0] - T_[0] * r * 0.6, P[-1] + T_[-1] * r * 0.6])
    cap = [(c0, k, (k + 1) % n) for k in range(n)] + [(c1, (m - 1) * n + (k + 1) % n, (m - 1) * n + k) for k in range(n)]
    F = np.vstack([F, np.array(cap, np.int32)])
    return Mesh(V, F)


# ---------------------------------------------------------------- shader
VS = """
#version 330
uniform mat4 u_mvp; uniform mat4 u_model; uniform mat4 u_light;
in vec3 in_pos; in vec3 in_nrm; in vec2 in_uv;
out vec3 v_world; out vec3 v_nrm; out vec3 v_loc; out vec4 v_ls; out vec2 v_uv;
void main(){
  vec4 w = u_model * vec4(in_pos,1.0);
  v_world = w.xyz; v_loc = in_pos; v_uv = in_uv;
  v_nrm = mat3(u_model) * in_nrm;
  v_ls = u_light * w;
  gl_Position = u_mvp * vec4(in_pos,1.0);
}
"""

FS = """
#version 330
uniform vec3 u_color; uniform float u_seed; uniform float u_bump; uniform float u_emit; uniform float u_gloss; uniform float u_sss;
uniform vec3 u_key; uniform vec3 u_keycol; uniform vec3 u_fill; uniform vec3 u_fillcol; uniform vec3 u_rim; uniform vec3 u_rimcol;
uniform vec3 u_scr; uniform vec3 u_scrcol; uniform vec3 u_eye;
uniform vec3 u_amb_top; uniform vec3 u_amb_bot; uniform float u_expo;
uniform sampler2D u_shadow; uniform float u_texel;
uniform sampler2D u_tex; uniform float u_use_tex;
in vec3 v_world; in vec3 v_nrm; in vec3 v_loc; in vec4 v_ls; in vec2 v_uv;
out vec4 frag;
float hash(vec3 p){ p = fract(p*0.3183099 + vec3(0.1,0.2,0.3)+u_seed*0.013); p*=17.0; return fract(p.x*p.y*p.z*(p.x+p.y+p.z)); }
float vnoise(vec3 x){ vec3 i=floor(x); vec3 f=fract(x); f=f*f*(3.0-2.0*f);
  return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),
             mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z); }
vec3 aces(vec3 x){ return clamp((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14),0.0,1.0); }
void main(){
  vec3 n = normalize(v_nrm);
  if(u_bump > 0.0){
    float h = (vnoise(v_loc*0.9)-0.5) + (vnoise(v_loc*2.7)-0.5)*0.5 + sin(v_loc.y*2.2+vnoise(v_loc*0.5)*3.0)*0.15;
    vec3 dpdx = dFdx(v_world), dpdy = dFdy(v_world);
    float dhdx = dFdx(h), dhdy = dFdy(h);
    vec3 r1 = cross(dpdy, n), r2 = cross(n, dpdx);
    float det = dot(dpdx, r1);
    vec3 grad = sign(det) * (dhdx*r1 + dhdy*r2);
    n = normalize(abs(det)*n - grad*u_bump);
  }
  vec3 V = normalize(u_eye - v_world);
  if(dot(n,V) < 0.0) n = -n;
  vec3 sc = v_ls.xyz / v_ls.w * 0.5 + 0.5;
  float sh = 0.0;
  for(int x=-2;x<=2;x++) for(int y=-2;y<=2;y++){
    float d = texture(u_shadow, sc.xy + vec2(x,y)*u_texel*2.0).r;
    sh += (sc.z - 0.0015 > d) ? 0.0 : 1.0;
  }
  sh /= 25.0;
  if(sc.x<0.0||sc.x>1.0||sc.y<0.0||sc.y>1.0) sh = 1.0;
  vec3 base = pow(u_color, vec3(2.2));
  if(u_use_tex > 0.5){ base = pow(texture(u_tex, v_uv).rgb, vec3(2.2)); }
  base *= (0.97 + 0.06*vnoise(v_loc*0.35 + u_seed));
  float wrapk = 0.25 + 0.45*u_sss;
  float ndl = dot(n,-u_key);
  float kd = max((ndl+wrapk)/(1.0+wrapk), 0.0) * mix(sh, 1.0, 0.12*u_sss);
  float fd = max((dot(n,-u_fill)+0.4)/1.4, 0.0);
  float sd = max((dot(n,-u_scr)+0.3)/1.3, 0.0);
  float rd = pow(max(dot(n,-u_rim),0.0), 1.5) * pow(1.0-max(dot(n,V),0.0), 1.2);
  vec3 amb = mix(u_amb_bot, u_amb_top, n.y*0.5+0.5);
  vec3 Hk = normalize(-u_key + V);
  float sp = mix(18.0, 140.0, u_gloss);
  float spec = pow(max(dot(n,Hk),0.0), sp) * (0.04 + 0.9*u_gloss) * sh;
  vec3 Hs = normalize(-u_scr + V);
  float spec2 = pow(max(dot(n,Hs),0.0), sp) * (0.9*u_gloss);
  float fres = pow(1.0 - max(dot(n,V),0.0), 5.0);
  vec3 col = base*(kd*u_keycol + fd*u_fillcol + sd*u_scrcol + amb) + rd*u_rimcol*(0.6+0.4*base);
  col += spec*u_keycol + spec2*u_scrcol + fres*amb*0.5*(0.3+u_gloss);
  // subsurface: rona hangat di batas terang-gelap
  float term = exp(-pow((ndl+0.05)/0.28, 2.0));
  col += u_sss * term * vec3(0.55,0.16,0.08) * u_keycol * base * 1.4;
  col += base*u_emit;
  col *= u_expo;
  col = aces(col*1.1);
  frag = vec4(pow(col, vec3(1.0/2.2)), 1.0);
}
"""

VS_SH = """
#version 330
uniform mat4 u_mvp; in vec3 in_pos; in vec3 in_nrm;
void main(){ gl_Position = u_mvp * vec4(in_pos,1.0); }
"""
FS_SH = """
#version 330
void main(){}
"""


class Part:
    """Satu bentuk lilin: mesh lokal + warna + matriks dunia."""
    __slots__ = ("mesh", "color", "M", "seed", "bump", "emit", "gloss", "cast", "sss", "tex")

    def __init__(self, mesh, color, M=None, seed=0, bump=0.0, emit=0.0, gloss=0.0, cast=True, sss=0.0, tex=None):
        self.mesh, self.color = mesh, np.asarray(color, np.float32) / 255.0
        self.M = np.eye(4, dtype=np.float32) if M is None else M
        self.seed, self.bump, self.emit, self.gloss, self.cast, self.sss = seed, bump, emit, gloss, cast, sss
        self.tex = tex  # (kunci_cache, PIL.Image) untuk quad bertekstur


class GL:
    def __init__(self, w, h, samples=4, shadow_res=2048):
        if sys.platform.startswith("linux"):
            self.ctx = moderngl.create_standalone_context(backend="egl")
        else:
            self.ctx = moderngl.create_standalone_context(require=330)
        ctx = self.ctx
        self.w, self.h = w, h
        self.prog = ctx.program(vertex_shader=VS, fragment_shader=FS)
        self.sprog = ctx.program(vertex_shader=VS_SH, fragment_shader=FS_SH)
        self.ms = ctx.framebuffer(color_attachments=[ctx.renderbuffer((w, h), 4, samples=samples)],
                                  depth_attachment=ctx.depth_renderbuffer((w, h), samples=samples))
        self.rs = ctx.framebuffer(color_attachments=[ctx.renderbuffer((w, h), 4)])
        self.sdepth = ctx.depth_texture((shadow_res, shadow_res))
        self.sdepth.compare_func = ""
        self.sdepth.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.sfbo = ctx.framebuffer(depth_attachment=self.sdepth)
        self.sres = shadow_res
        self._vao = {}
        self._tex = {}

    def texture(self, key, img):
        if key not in self._tex:
            if len(self._tex) > 60:
                for t_ in self._tex.values():
                    t_.release()
                self._tex.clear()
            im = img.convert("RGB")
            tx = self.ctx.texture(im.size, 3, im.tobytes())
            tx.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
            tx.build_mipmaps()
            self._tex[key] = tx
        return self._tex[key]

    def vao(self, mesh):
        k = id(mesh)
        if k not in self._vao:
            data = np.hstack([mesh.V, mesh.N, mesh.UV]).astype(np.float32)
            vbo = self.ctx.buffer(data.tobytes())
            ibo = self.ctx.buffer(mesh.F.astype(np.int32).tobytes())
            v1 = self.ctx.vertex_array(self.prog, [(vbo, "3f 3f 2f", "in_pos", "in_nrm", "in_uv")], ibo)
            v2 = self.ctx.vertex_array(self.sprog, [(vbo, "3f 20x", "in_pos")], ibo)
            self._vao[k] = (v1, v2, mesh)
        return self._vao[k]

    def render(self, parts, eye, target, fov, light, bg=(0, 0, 0, 0), expo=1.0, shadow_parts=None):
        ctx = self.ctx
        V = look_at(eye, target)
        P = perspective(fov, self.w / self.h)
        VP = P @ V
        key = np.asarray(light["key"], np.float32)
        key /= np.linalg.norm(key)
        c = np.asarray(light.get("center", (0, 5, 0)), np.float32)
        LV = look_at(c - key * light.get("dist", 300), c, up=(0, 0, -1) if abs(key[1]) > 0.95 else (0, 1, 0))
        ext = light.get("extent", 45)
        LP = ortho(-ext, ext, -ext, ext, 10, light.get("far", 600))
        LVP = LP @ LV
        # pass bayangan
        self.sfbo.use()
        self.sfbo.clear(depth=1.0)
        ctx.enable(moderngl.DEPTH_TEST)
        ctx.disable(moderngl.CULL_FACE)
        for p in (parts if shadow_parts is None else shadow_parts):
            if not p.cast:
                continue
            v1, v2, _ = self.vao(p.mesh)
            self.sprog["u_mvp"].write((LVP @ p.M).T.astype(np.float32).tobytes())
            v2.render()
        # pass utama
        self.ms.use()
        self.ms.clear(*bg, depth=1.0)
        pr = self.prog
        self.sdepth.use(location=0)
        pr["u_shadow"] = 0
        pr["u_texel"] = 1.0 / self.sres
        pr["u_light"].write(LVP.T.astype(np.float32).tobytes())
        pr["u_key"] = tuple(key)
        pr["u_keycol"] = tuple(light.get("keycol", (1.55, 1.18, 0.82)))
        def nz(v):
            v = np.asarray(v, np.float32)
            return tuple(v / (np.linalg.norm(v) + 1e-9))
        pr["u_fill"] = nz(light.get("fill", (0.6, -0.3, -0.7)))
        pr["u_fillcol"] = tuple(light.get("fillcol", (0.2, 0.26, 0.5)))
        pr["u_rim"] = nz(light.get("rim", (0.0, -0.3, 1.0)))
        pr["u_rimcol"] = tuple(light.get("rimcol", (0.6, 0.6, 0.8)))
        pr["u_scr"] = nz(light.get("scr", (0.0, -0.2, 1.0)))
        pr["u_scrcol"] = tuple(light.get("scrcol", (0.0, 0.0, 0.0)))
        pr["u_amb_top"] = tuple(light.get("amb_top", (0.13, 0.14, 0.24)))
        pr["u_amb_bot"] = tuple(light.get("amb_bot", (0.09, 0.06, 0.05)))
        pr["u_tex"] = 1
        pr["u_eye"] = tuple(np.asarray(eye, np.float32))
        pr["u_expo"] = float(expo)
        for p in parts:
            v1, _, _ = self.vao(p.mesh)
            pr["u_mvp"].write((VP @ p.M).T.astype(np.float32).tobytes())
            pr["u_model"].write(p.M.T.astype(np.float32).tobytes())
            pr["u_color"] = tuple(p.color)
            pr["u_seed"] = float(p.seed)
            pr["u_bump"] = float(p.bump)
            pr["u_emit"] = float(p.emit)
            pr["u_gloss"] = float(p.gloss)
            pr["u_sss"] = float(p.sss)
            if p.tex is not None:
                self.texture(p.tex[0], p.tex[1]).use(location=1)
                pr["u_use_tex"] = 1.0
            else:
                pr["u_use_tex"] = 0.0
            v1.render()
        ctx.copy_framebuffer(self.rs, self.ms)
        raw = self.rs.read(components=4, alignment=1)
        img = np.frombuffer(raw, np.uint8).reshape(self.h, self.w, 4)[::-1]
        return img
