import numpy as np
import quaternion
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection\

class Pose():
    def __init__(self, q, t, ptype='normal'):
        self.type = ptype
        if ptype == 'colmap':
            colmap_quat = np.quaternion(float(q[0]), float(q[1]), float(q[2]), float(q[3]))
            colmap_pos = np.array([float(t[0]), float(t[1]), float(t[2])])
            quat = colmap_quat.inverse()
            quat_arr = quaternion.as_float_array(quat)
            pos_arr = np.matmul(-quaternion.as_rotation_matrix(quat), colmap_pos)
            self.qw = quat_arr[0]
            self.qx = quat_arr[1]
            self.qy = quat_arr[2]
            self.qz = quat_arr[3]
            self.x = pos_arr[0]
            self.y = pos_arr[1]
            self.z = pos_arr[2]
        elif ptype == 'arcore':
            ar_quat = np.quaternion(float(q[0]), float(q[1]), float(q[2]), float(q[3]))
            quat = ar_quat * np.quaternion(0, -1, 0, 0)
            quat_arr = quaternion.as_float_array(quat)
            self.qw = quat_arr[0]
            self.qx = quat_arr[1]
            self.qy = quat_arr[2]
            self.qz = quat_arr[3]
            self.x = float(t[0])
            self.y = float(t[1])
            self.z = float(t[2])
        else:
            self.qw = float(q[0])
            self.qx = float(q[1])
            self.qy = float(q[2])
            self.qz = float(q[3])
            self.x = float(t[0])
            self.y = float(t[1])
            self.z = float(t[2])

    def pos(self):
        return np.array([self.x, self.y, self.z])

    def quat(self):
        return np.quaternion(self.qw, self.qx, self.qy, self.qz)

    def rot_mtx(self):
        return quaternion.as_rotation_matrix(self.quat())

    def __str__(self):
        return f'{self.quat()} {self.pos()}'
    
    def to_arcore_pose_str(self):
        return f'{{{self.x}f, {self.y}f, {self.z}f}} {{{self.qx}f, {self.qy}f, {self.qz}f, {self.qw}f}}'
    

def parse_arpose(arpose_str):
    trashes = ['q:', '[', 'x:', 'y:', 'z:', 'w:', ']', 't:', ',', '\n']
    for trash in trashes:
        arpose_str = arpose_str.replace(trash, "")
    tok = arpose_str.split(' ')
    # x y z qx qy qz qw -> id qw qx qy qz x y z
    q = np.array([tok[6], tok[3], tok[4], tok[5]])
    t = np.array([tok[0], tok[1], tok[2]])
    return q, t

def load_point_cloud(points_fname):
    f = open(points_fname, 'r')
    lines = f.readlines()
    pc = []
    for i, line in enumerate(lines):
        if line[0] == '#':
            continue
        p = Point(line)
        pc.append(p.pos())
    return np.array(pc)

class Point():
    def __init__(self, point3d_txt):
        #   point3D_txt: POINT3D_ID, X, Y, Z, R, G, B, ERROR, TRACK[] as (IMAGE_ID, POINT2D_IDX)
        _tmp = point3d_txt.split(' ')
        self.id = int(_tmp[0])
        self.x = float(_tmp[1])
        self.y = float(_tmp[2])
        self.z = float(_tmp[3])
        self.r = int(_tmp[4])
        self.g = int(_tmp[5])
        self.b = int(_tmp[6])

    def pos(self):
        return np.array([self.x, self.y, self.z])

    def color(self):
        return np.array([self.r, self.g, self.b])

def display_pose(fig, ax, cam_poses, pc=None, only_pos=False, axis_on=False):
    ax.cla()

    ax.axis('on' if axis_on else 'off')
    ax.set_xlim([-10, 10])
    ax.set_ylim([-10, 10])
    ax.set_zlim([-10, 10])

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    # Display point cloud
    if pc is not None:
        ax.plot(pc[:, 0], pc[:, 1], pc[:, 2], marker='.', c='gray', markersize=0.3, lw=0)
        plt.draw()

    # Display traj
    for i, values in enumerate(cam_poses):

        if len(values) == 2:
            p, c = values
            markersize = 2
        else:
            p, c, markersize = values
        
        # current pose
        if i== len(cam_poses)-1:
            c = 'red'

        if only_pos:
            t = p.pos()
            ax.plot([t[0]], [t[1]], [t[2]], marker='o', c=c, markersize=markersize, lw=0)
        else:
            p_scale = 0.1
            rot_mtx = p.rot_mtx()
            t = p.pos()

            p1 = np.dot(rot_mtx, [2, 1, 1.5]) * p_scale + t
            p2 = np.dot(rot_mtx, [-2, 1, 1.5]) * p_scale + t
            p3 = np.dot(rot_mtx, [-2, -1, 1.5]) * p_scale + t
            p4 = np.dot(rot_mtx, [2, -1, 1.5]) * p_scale + t

            x = [p1[0], p2[0], p3[0], p4[0]]
            y = [p1[1], p2[1], p3[1], p4[1]]
            z = [p1[2], p2[2], p3[2], p4[2]]
            vertices = [list(zip(x, y, z))]
            poly = Poly3DCollection(vertices, alpha=0.3, color=c)
            ax.add_collection3d(poly)

            ax.plot([t[0], p1[0]], [t[1], p1[1]], [t[2], p1[2]], marker='.', c=c, markersize=0.5, lw=0.5)
            ax.plot([t[0], p2[0]], [t[1], p2[1]], [t[2], p2[2]], marker='.', c=c, markersize=0.5, lw=0.5)
            ax.plot([t[0], p3[0]], [t[1], p3[1]], [t[2], p3[2]], marker='o', c=c, markersize=1, lw=0.5)
            ax.plot([t[0], p4[0]], [t[1], p4[1]], [t[2], p4[2]], marker='.', c=c, markersize=0.5, lw=0.5)


def get_align_matrix(down_vec):
    """
    給定一個真實世界的「向下」重力向量，計算一個旋轉矩陣，
    將該向量對齊到 [0, -1, 0] (也就是讓 Y 軸變成高度軸，XZ 變成水平地板)。
    """
    down_vec = np.array(down_vec)
    norm = np.linalg.norm(down_vec)
    if norm < 1e-6:
        return np.eye(3)
    down_vec = down_vec / norm
    target = np.array([0, -1, 0])
    
    if np.allclose(down_vec, target):
        return np.eye(3)
        
    v = np.cross(down_vec, target)
    c = np.dot(down_vec, target)
    s = np.linalg.norm(v)
    
    if s < 1e-6: # 若剛好完全反向 (朝上)
        return np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
        
    # Rodrigues' rotation formula
    vX = np.array([
        [0, -v[2], v[1]],
        [v[2], 0, -v[0]],
        [-v[1], v[0], 0]
    ])
    R = np.eye(3) + vX + np.dot(vX, vX) * ((1 - c) / (s ** 2))
    return R

def display_pose_2d(fig, ax, cam_poses, pc=None, only_pos=False, axis_on=False, align_mtx=None):
    ax.cla()
    ax.axis('on' if axis_on else 'off')
    ax.set_xlim([-10, 5])
    ax.set_ylim([-3, 3]) # 這裡的 ylim 對應到原本的 Z 軸
    ax.set_xlabel('x')
    ax.set_ylabel('z') # 將 Y 標籤改為 Z
    
    # 1. 轉換點雲 (捨棄 Y 軸，留下 X=0, Z=2)
    if pc is not None:
        pc_plot = pc if align_mtx is None else pc @ align_mtx.T
        ax.plot(pc_plot[:, 0], pc_plot[:, 2], marker='.', c='gray', markersize=0.3, lw=0)
        plt.draw()
        
    # 2. 轉換軌跡與相機視角
    for i, values in enumerate(cam_poses):
        if len(values) == 2:
            p, c = values
            markersize = 2
        else:
            p, c, markersize = values
        
        is_latest = (i == len(cam_poses) - 1)
        if is_latest:
            c = 'red'
            
        t = p.pos()
        rot_mtx = p.rot_mtx()  
        
        # 套用校正矩陣
        if align_mtx is not None:
            t = align_mtx @ t
            
        if only_pos:
            ax.plot([t[0]], [t[2]], marker='o', c=c, markersize=markersize, lw=0)
        else:
            p_scale = 0.1
            p1 = np.dot(rot_mtx, [2, 1, 1.5]) * p_scale + p.pos()
            p2 = np.dot(rot_mtx, [-2, 1, 1.5]) * p_scale + p.pos()
            
            # 套用校正矩陣
            if align_mtx is not None:
                p1 = align_mtx @ p1
                p2 = align_mtx @ p2
                
            x_points = [t[0], p1[0], p2[0], t[0]]
            z_points = [t[2], p1[2], p2[2], t[2]]
            
            ax.fill(x_points, z_points, alpha=0.3, color=c)
            ax.plot(x_points, z_points, c=c, markersize=1, lw=0.5)
            ax.plot([t[0]], [t[2]], marker='o', c=c, markersize=markersize, lw=0)