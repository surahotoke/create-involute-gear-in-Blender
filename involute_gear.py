import math
import bpy

def clear():
    for item in bpy.data.meshes:
        bpy.data.meshes.remove(item)

def create(name="involute_gear", m=1, b=10, alpha_deg=20, z=40, x=0, t_len = 10, x_csw=False, rho_sw=False):
    def r_i(t):
        return r_b * math.sqrt(t**2 + 1)
    
    def inv(t):
        return math.tan(t) - t
    
    def theta_i(t):
        return t - math.atan(t) - phi_i

    def theta_a(t):
        return t + phi_a
    
    def r_t0(t):
        return math.sqrt((r * t)**2 + (r - h_r)**2)
    
    def theta_t0(t):
        return t - math.atan(r * t / (r - h_r))
    
    def beta(t):
        return t + math.atan(r * t / h_r)
    
    def r_t(t):
        return math.sqrt(r_t0(t)**2 - 2 * rho * math.cos(beta(t) - theta_t0(t)) * r_t0(t) + rho**2)
    
    def theta_t(t):
        return -math.atan((r_t0(t) * math.sin(theta_t0(t)) - rho * math.sin(beta(t))) / (r_t0(t) * math.cos(theta_t0(t)) - rho * math.cos(beta(t)))) - phi_t
    
    def theta_f(t):
        return t + phi_f

    def r_iinverse(t):
        return math.sqrt((t / r_b)**2 - 1)
    
    def f(t):
        return theta_i(r_iinverse(r_t(t))) - theta_t(t)
    
    def find_an_approximate_f_inverse(t):
        # 初期値
        t_approx = 2
        
        # ニュートン法による反復
        for _ in range(64):
            # f(t_approx)とその導関数の計算
            f_t_approx = f(t_approx)
            f_prime_t_approx = (f(t_approx + 1e-6) - f_t_approx) / 1e-6
            
            # ニュートン法の反復式
            t_approx -= f_t_approx / f_prime_t_approx
        
        return t_approx
    
    def r_gear0(t):
        if t < 1:
            return r_t(t_tmax * t)
        elif t < 2:
            return r_i(t_imin + t_iw * (t - 1))
        elif t < 3:
            return r_a
        elif t < 4:
            return r_i(t_imax - t_iw * (t - 3))
        elif t < 5:
            return r_t(t_tmax * (5 - t))
        else:
            return r_f
    
    def theta_gear0(t):
        if t < 1:
            return theta_t(t_tmax * t)
        elif t < 2:
            return theta_i(t_imin + t_iw * (t - 1))
        elif t < 3:
            return theta_a(t_amax * (t - 2))
        elif t < 4:
            return math.pi/z - theta_i(t_imax - t_iw * (t - 3))
        elif t < 5:
            return math.pi/z - theta_t(t_tmax * (5 - t))
        else:
            return theta_f(t_fmax * (t - 5))
    
    def g(t):
        return t - 6 * math.floor(t / 6)
    
    def r_gear(t):
        return r_gear0(g(t))

    def phi_gear(t):
        return 2 * math.pi * math.floor(t / 6) / z
    
    def theta_gear(t):
        return theta_gear0(g(t)) + phi_gear(t)
    
    def C_gear(t, b):
        x = r_gear(t) * math.cos(theta_gear(t))
        y = r_gear(t) * math.sin(theta_gear(t))
        z = b
        return [x, y, z]
    
    def linspace(start, stop, num=50):
        if num <= 1:
            return [start]
        step = (stop - start) / (num - 1)
        return [start + step * i for i in range(num)]
    
    # degreeをradに変換
    alpha = math.radians(alpha_deg)
    # x
    x_c = 1 - z * math.sin(alpha)**2 / 2
    if x_csw:
        x = x_c
    
    # rho
    rho = 0
    if rho_sw:
        rho = 0.38 * m
    if m <= 0.4:
        rho = 0
    elif 1 < m:
        rho = 0.38 * m
    
    # normal
    d = z * m
    r = d/2
    d_b = d * math.cos(alpha)
    r_b = d_b/2
    h_a = (1 + x) * m
    d_a = d + 2 * h_a
    r_a = d_a/2
    h_f = (1.25 - x) * m
    d_f = d - 2 * h_f
    r_f = d_f/2
    h_r = h_f - rho
    
    # C_i
    phi_i = inv(alpha)
    t_imax = math.sqrt((d_a/d_b)**2 - 1)

    # C_a
    phi_a = theta_i(t_imax)
    t_amax = math.pi/z - 2 * phi_a
    
    # C_t
    phi_t = (h_r * math.tan(alpha) + rho/math.cos(alpha))/r

    # C_f
    phi_f = math.pi/z + phi_t
    t_fmax = math.pi/z - 2 * phi_t
    
    # t_tmax, t_imin
    t_tmax = find_an_approximate_f_inverse(0)
    t_imin = r_iinverse(r_t(t_tmax))
    
    # simply
    t_iw = t_imax - t_imin
    
    # 分割数
    t_len *= 6 * z
    # tの範囲
    t_max = 6 * z
    lattice_t = linspace(0, t_max, t_len+1)[:-1]
    
    if b == 0:
        # 点を追加
        verts = [C_gear(t, 0) for t in lattice_t]
        
        # 面
        faces = [[t for t in range(len(lattice_t))]]
    else:
        # 点を追加
        verts = [C_gear(t, b) for b in [0, b] for t in lattice_t]
        
        # 上下面
        faces = [[t+b for t in range(len(lattice_t))] for b in [0, t_len]]
        
        # 側面を追加
        side_faces = []
        for i in range(t_len):
            side_faces.extend([[i, (i + 1)%t_len, (i + 1)%t_len + t_len, i + t_len]])
        faces += side_faces
    
    # 作成
    msh = bpy.data.meshes.new(name + "_mesh") #Meshデータの宣言
    msh.from_pydata(verts, [], faces) # 頂点座標と各面の頂点の情報でメッシュを作成
    obj = bpy.data.objects.new(name, msh) # メッシュデータでオブジェクトを作成
    bpy.context.scene.collection.objects.link(obj) # シーンにオブジェクトを配置
    
# ここから下で作成(初期値name="involute_gear", m=1, b=10, alpha_deg=20, z=40, x=0, t_len = 10, x_csw=False, rho_sw=False)

