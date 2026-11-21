"""Mini engine 3D low-poly bergaya PS2 (moderngl + EGL/llvmpipe)."""
import math
import sys

import moderngl
import numpy as np
from PIL import Image
from scipy.spatial import ConvexHull

# pattern codes
P_PLAIN, P_FABRIC, P_BATIK, P_WALL, P_TEX, P_UNLIT, P_UNLIT_TEX, P_SKIN, P_HAIR, P_SHADOW, P_WOOD, P_GRASS = range(12)


def C(rgb):
    return np.array(rgb, np.float32) / 255.0


# ---------------------------------------------------------------- mesh
class Mesh:
    def __init__(self):
        self.parts = []  # list of (P (M,3,3), N (M,3,3), col (M,3,3), pat (M,3), uv (M,3,2))

    def tris(self, P, color, pat=P_PLAIN, uv=None, smooth_n=None, colors=None):
        P = np.asarray(P, np.float32).reshape(-1, 3, 3)
        e1 = P[:, 1] - P[:, 0]
        e2 = P[:, 2] - P[:, 0]
        n = np.cross(e1, e2)
        ln = np.linalg.norm(n, axis=1, keepdims=True)
        ln[ln == 0] = 1
        n = n / ln
        N = np.repeat(n[:, None, :], 3, axis=1) if smooth_n is None else smooth_n
        if colors is None:
            col = np.broadcast_to(C(color), P.shape).copy()
        else:
            col = np.asarray(colors, np.float32).reshape(P.shape)
        pt = np.full(P.shape[:2], float(pat), np.float32)
        if uv is None:
            uv = np.zeros(P.shape[:2] + (2,), np.float32)
        self.parts.append((P, N.astype(np.float32), col, pt, np.asarray(uv, np.float32).reshape(-1, 3, 2)))
        return self

    def add(self, other):
        self.parts.extend(other.parts)
        return self

    def transformed(self, M):
        out = Mesh()
        R = M[:3, :3]
        for P, N, col, pt, uv in self.parts:
            P2 = P @ R.T + M[:3, 3]
            N2 = N @ R.T
            N2 /= np.linalg.norm(N2, axis=2, keepdims=True) + 1e-9
            out.parts.append((P2.astype(np.float32), N2.astype(np.float32), col, pt, uv))
        return out

    def array(self):
        if not self.parts:
            return None
        P = np.concatenate([p[0] for p in self.parts]).reshape(-1, 3)
        N = np.concatenate([p[1] for p in self.parts]).reshape(-1, 3)
        Cc = np.concatenate([p[2] for p in self.parts]).reshape(-1, 3)
        T = np.concatenate([p[3] for p in self.parts]).reshape(-1, 1)
        U = np.concatenate([p[4] for p in self.parts]).reshape(-1, 2)
        return np.hstack([P, N, Cc, T, U]).astype(np.float32)


def hull(points, color, pat=P_PLAIN):
    pts = np.asarray(points, np.float64)
    h = ConvexHull(pts)
    c = pts.mean(0)
    T = pts[h.simplices]
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    flip = np.einsum("ij,ij->i", n, T.mean(1) - c) < 0
    T[flip] = T[flip][:, [0, 2, 1]]
    return Mesh().tris(T, color, pat)


def box(center, size, color, pat=P_PLAIN):
    cx, cy, cz = center
    sx, sy, sz = [s / 2 for s in size]
    pts = [(cx + a * sx, cy + b * sy, cz + c * sz) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
    return hull(pts, color, pat)


def tbox(y0, y1, w0, d0, w1, d1, color, pat=P_PLAIN, x=0.0, z0=0.0, z1=None):
    """Tapered box along Y (bottom w0xd0 at y0, top w1xd1 at y1)."""
    z1 = z0 if z1 is None else z1
    pts = []
    for (y, w, d, z) in ((y0, w0, d0, z0), (y1, w1, d1, z1)):
        for a in (-1, 1):
            for c in (-1, 1):
                pts.append((x + a * w / 2, y, z + c * d / 2))
    return hull(pts, color, pat)


def cyl(c, r, h, color, pat=P_PLAIN, segs=8, r2=None, axis="y"):
    r2 = r if r2 is None else r2
    pts = []
    for k in range(segs):
        a = 2 * math.pi * k / segs
        for yy, rr in ((0, r), (h, r2)):
            if axis == "y":
                pts.append((c[0] + rr * math.cos(a), c[1] + yy, c[2] + rr * math.sin(a)))
            elif axis == "z":
                pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a), c[2] + yy))
            else:
                pts.append((c[0] + yy, c[1] + rr * math.cos(a), c[2] + rr * math.sin(a)))
    return hull(pts, color, pat)


def ellipsoid_pts(c, r, lats=(-60, -25, 10, 45, 75), lons=8, keep=None):
    pts = [(c[0], c[1] + r[1], c[2])]
    for la in lats:
        for k in range(lons):
            lo = 2 * math.pi * (k + 0.5 * (la % 2)) / lons
            x = c[0] + r[0] * math.cos(math.radians(la)) * math.sin(lo)
            y = c[1] + r[1] * math.sin(math.radians(la))
            z = c[2] + r[2] * math.cos(math.radians(la)) * math.cos(lo)
            if keep is None or keep(x, y, z):
                pts.append((x, y, z))
    return pts


def quad(p0, p1, p2, p3, color, pat=P_PLAIN, uv=((0, 0), (1, 0), (1, 1), (0, 1))):
    P = [[p0, p1, p2], [p0, p2, p3]]
    U = [[uv[0], uv[1], uv[2]], [uv[0], uv[2], uv[3]]]
    return Mesh().tris(P, color, pat, uv=U)


def poly(pts2d, z, color, pat=P_PLAIN):
    """Flat polygon in XY plane at depth z, facing +Z (fan)."""
    c = np.mean(pts2d, 0)
    P = []
    n = len(pts2d)
    for i in range(n):
        a = pts2d[i]
        b = pts2d[(i + 1) % n]
        P.append([(c[0], c[1], z), (a[0], a[1], z), (b[0], b[1], z)])
    return Mesh().tris(P, color, pat)


def circle2d(cx, cy, rx, ry=None, n=10):
    ry = rx if ry is None else ry
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


# ---------------------------------------------------------------- math
def rx(a):
    a = math.radians(a)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def ry(a):
    a = math.radians(a)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rz(a):
    a = math.radians(a)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def M4(t=(0, 0, 0), r=(0, 0, 0), s=(1, 1, 1)):
    M = np.eye(4)
    R = ry(r[1]) @ rx(r[0]) @ rz(r[2])
    M[:3, :3] = R @ np.diag(s)
    M[:3, 3] = t
    return M


def perspective(fovy, aspect, near, far):
    f = 1 / math.tan(math.radians(fovy) / 2)
    M = np.zeros((4, 4))
    M[0, 0] = f / aspect
    M[1, 1] = f
    M[2, 2] = (far + near) / (near - far)
    M[2, 3] = 2 * far * near / (near - far)
    M[3, 2] = -1
    return M


def look_at(eye, target, up=(0, 1, 0)):
    eye, target, up = map(lambda v: np.array(v, float), (eye, target, up))
    f = target - eye
    f /= np.linalg.norm(f)
    s = np.cross(f, up)
    s /= np.linalg.norm(s)
    u = np.cross(s, f)
    M = np.eye(4)
    M[0, :3], M[1, :3], M[2, :3] = s, u, -f
    M[:3, 3] = -M[:3, :3] @ eye
    return M


# ---------------------------------------------------------------- GL
VS = """
#version 330
uniform mat4 u_vp; uniform mat4 u_model;
in vec3 in_pos; in vec3 in_nrm; in vec3 in_col; in float in_pat; in vec2 in_uv;
out vec3 v_nrm; out vec3 v_lnrm; out vec3 v_col; flat out float v_pat; out vec2 v_uv; out vec3 v_lpos; out vec3 v_wpos;
void main(){
  vec4 w = u_model*vec4(in_pos,1.0);
  v_wpos = w.xyz; v_lpos = in_pos; v_lnrm = in_nrm;
  v_nrm = normalize(mat3(u_model)*in_nrm);
  v_col = in_col; v_pat = in_pat; v_uv = in_uv;
  gl_Position = u_vp*w;
}
"""

FS = """
#version 330
uniform sampler2D u_tex; uniform vec3 u_eye; uniform float u_ambient; uniform vec3 u_tint;
in vec3 v_nrm; in vec3 v_lnrm; in vec3 v_col; flat in float v_pat; in vec2 v_uv; in vec3 v_lpos; in vec3 v_wpos;
out vec4 frag;
float hash(vec3 p){ p = fract(p*0.3183099+vec3(.1,.2,.3)); p *= 17.0; return fract(p.x*p.y*p.z*(p.x+p.y+p.z)); }
float vnoise(vec3 x){ vec3 i=floor(x); vec3 f=fract(x); f=f*f*(3.0-2.0*f);
  return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x), mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),
             mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x), mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y), f.z); }
vec2 plane(vec3 p, vec3 n){ vec3 a=abs(n); if(a.x>a.y && a.x>a.z) return p.zy; if(a.y>a.z) return p.xz; return p.xy; }
void main(){
  int pat = int(v_pat+0.5);
  vec3 n = normalize(v_nrm); if(!gl_FrontFacing) n = -n;
  vec3 base = v_col;
  if(pat==4 || pat==6){ vec4 t = texture(u_tex, v_uv); if(t.a<0.5) discard; base = t.rgb; }
  if(pat==9){ float d = length(v_uv*2.0-1.0); float a = clamp(1.0-d,0.0,1.0); frag = vec4(0.02,0.01,0.05, a*a*0.55); return; }
  if(pat==1){ float k = vnoise(v_lpos*170.0)*0.55 + vnoise(v_lpos*48.0)*0.45; base *= 0.86 + 0.22*k; }
  if(pat==2){
    vec2 q = plane(v_lpos, v_lnrm)*26.0;
    vec2 f = fract(q)-0.5; vec2 g = fract(q+0.5)-0.5;
    float petal = smoothstep(0.30,0.26,length(vec2(f.x*1.9,f.y)))+smoothstep(0.30,0.26,length(vec2(f.x,f.y*1.9)));
    float dotc = smoothstep(0.09,0.06,length(g));
    vec3 c1 = v_col; vec3 c2 = vec3(0.86,0.66,0.32); vec3 c3 = vec3(0.95,0.88,0.72);
    base = mix(c1, c2, clamp(petal,0.0,1.0)*0.85); base = mix(base, c3, dotc);
    float k = vnoise(v_lpos*160.0); base *= 0.88+0.2*k;
  }
  if(pat==3){ float k = vnoise(v_lpos*7.0)*0.5 + vnoise(v_lpos*60.0)*0.5; base *= 0.88 + 0.2*k; }
  if(pat==7){ float k = vnoise(v_lpos*140.0)*0.6+vnoise(v_lpos*30.0)*0.4; base *= 0.93 + 0.12*k; }
  if(pat==8){ float k = vnoise(vec3(v_lpos.x*260.0, v_lpos.y*35.0, v_lpos.z*260.0)); base *= 0.72 + 0.45*k; }
  if(pat==10){ float k = vnoise(vec3(v_lpos.x*3.0, v_lpos.y*60.0, v_lpos.z*60.0)); base *= 0.8+0.3*k; }
  if(pat==11){ float k = vnoise(v_wpos*3.0)*0.5+vnoise(v_wpos*40.0)*0.5; base *= 0.78+0.38*k; }
  if(pat==5 || pat==6){ frag = vec4(base*u_tint,1.0); return; }
  vec3 L1 = normalize(vec3(-0.45,0.85,0.6));
  vec3 L2 = normalize(vec3(0.7,0.25,0.35));
  float wrap = dot(n,L1)*0.5+0.5;
  float fill = max(dot(n,L2),0.0);
  float hemi = n.y*0.5+0.5;
  vec3 V = normalize(u_eye - v_wpos);
  float rim = pow(1.0-max(dot(n,V),0.0), 3.0);
  vec3 light = vec3(0.36,0.37,0.42)*(0.75+0.25*hemi)*u_ambient + vec3(1.0,0.96,0.9)*0.78*pow(wrap,1.7)
             + vec3(0.65,0.75,0.9)*0.16*fill + vec3(0.12)*rim;
  vec3 col = base*light;
  frag = vec4(col*u_tint, 1.0);
}
"""


class GL:
    def __init__(self, w, h, samples=4):
        if sys.platform.startswith("linux"):
            self.ctx = moderngl.create_standalone_context(backend="egl")
        else:
            self.ctx = moderngl.create_standalone_context(require=330)
        self.w, self.h = w, h
        ctx = self.ctx
        self.prog = ctx.program(vertex_shader=VS, fragment_shader=FS)
        self.ms = ctx.framebuffer(color_attachments=[ctx.renderbuffer((w, h), 4, samples=samples)],
                                  depth_attachment=ctx.depth_renderbuffer((w, h), samples=samples))
        self.rs = ctx.framebuffer(color_attachments=[ctx.renderbuffer((w, h), 4)])
        self.white = ctx.texture((1, 1), 4, bytes([255, 255, 255, 255]))
        self.prog["u_tex"] = 0
        self.prog["u_ambient"] = 1.0
        self.prog["u_tint"] = (1.0, 1.0, 1.0)

    def texture(self, img):
        img = img.convert("RGBA").transpose(Image.FLIP_TOP_BOTTOM)
        t = self.ctx.texture(img.size, 4, img.tobytes())
        t.build_mipmaps()
        t.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        t.anisotropy = 8.0
        return t

    def upload(self, mesh):
        arr = mesh.array()
        if arr is None:
            return None
        vbo = self.ctx.buffer(arr.tobytes())
        return self.ctx.vertex_array(self.prog, [(vbo, "3f 3f 3f 1f 2f", "in_pos", "in_nrm", "in_col", "in_pat", "in_uv")])

    def begin(self, view, proj, eye, clear=(0.1, 0.1, 0.12)):
        self.ms.use()
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        self.ctx.clear(*clear, 1.0)
        vp = proj @ view
        self.prog["u_vp"].write(vp.T.astype("f4").tobytes())
        self.prog["u_eye"] = tuple(float(v) for v in eye)

    def draw(self, vao, model, tex=None):
        if vao is None:
            return
        self.prog["u_model"].write(model.T.astype("f4").tobytes())
        (tex or self.white).use(0)
        vao.render(moderngl.TRIANGLES)

    def read(self):
        self.ctx.copy_framebuffer(self.rs, self.ms)
        data = self.rs.read(components=3)
        a = np.frombuffer(data, np.uint8).reshape(self.h, self.w, 3)
        return a[::-1].copy()


class Obj:
    """Group of meshes (by texture) sharing one model matrix."""

    def __init__(self):
        self.meshes = {}
        self.vaos = []

    def add(self, mesh, tex=None):
        self.meshes.setdefault(tex, Mesh()).add(mesh)
        return self

    def upload(self, gl):
        self.vaos = [(gl.upload(m), t) for t, m in self.meshes.items()]
        return self

    def draw(self, gl, model):
        for vao, t in self.vaos:
            gl.draw(vao, model, t)
