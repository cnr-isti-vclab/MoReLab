import numpy as np
import cv2, time
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix
import matplotlib.pyplot as plt






def bundle_adjustment_sparsity(n_cameras, n_points, camera_indices, point_indices):
    m = camera_indices.size * 2
    n = n_cameras * 6 + n_points * 3
    A = lil_matrix((m, n), dtype=int)

    i = np.arange(camera_indices.size)
    for s in range(6):
        A[2 * i, camera_indices * 6 + s] = 1
        A[2 * i + 1, camera_indices * 6 + s] = 1

    for s in range(3):
        A[2 * i, n_cameras * 6 + point_indices * 3 + s] = 1
        A[2 * i + 1, n_cameras * 6 + point_indices * 3 + s] = 1

    return A

def project(points, cam_trans, K):
    """Get R and t then project points"""
    rot_vecs = cam_trans[:, :3] # 
    t_vecs = cam_trans[:, 3:]
    theta = np.linalg.norm(rot_vecs, axis=1)[:, np.newaxis]
    with np.errstate(invalid='ignore'):
        v = rot_vecs / theta
        v = np.nan_to_num(v)
    dot = np.sum(points * v, axis=1)[:, np.newaxis]
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    points_proj = cos_theta * points + sin_theta * np.cross(v, points) + dot * (1 - cos_theta) * v
    points_proj += t_vecs # points num 
    points_proj = points_proj @ K.T 
    points_proj /= points_proj[:, 2, np.newaxis] # 
    
    return points_proj[:, :2].ravel()

def func2(params, points_2d, n_cameras, n_points, camera_indices, point_indices, K):
    camera_params = params[:n_cameras * 6].reshape((n_cameras, 6))
    points_3d = params[n_cameras * 6:].reshape((n_points, 3))        
    points_proj = project(points_3d[point_indices], camera_params[camera_indices], K) # 둘의 개수를 맞춰줬다! 적절한 index로 2d points의 개수를 파악하자.
    result = (points_2d - points_proj).ravel()
    return result




def bundle_adjustment(xs, K):
    xs = np.array(xs)

    n_cameras = xs.shape[0]
    n_points = xs.shape[1]


    
    # Matching index for cam & 3d points
    cam_indices = np.array([])
    length_c_ind = np.arange(n_points, dtype=int)
    for i in range(n_cameras):
        cam_indices = np.hstack((cam_indices, np.full_like(length_c_ind, i))) # 0x28, 1x28, ...

    point_indices = np.array([])
    # length_p_ind = np.arange(n_cameras, dtype=int)
    for i in range(n_cameras):
        point_indices = np.hstack((point_indices, np.linspace(0, n_points-1, n_points, dtype=int))) # (0 ~ 28) * 5
        # point_indices = np.hstack((point_indices, np.full_like(length_p_ind, i))) # 0x5, 1x5, 2x5, ..., 28x5
    
    cam_indices = cam_indices.astype(int)
    point_indices = point_indices.astype(int)

    # Initialize cameras and 3D points
    cameras = np.zeros((xs.shape[0], 6)) # rotation and translation
    cameras[:,2] = 1 # watching forward 
    Xs = np.full((xs.shape[1], xs.shape[2]+1), np.array([[0, 0, 5.5]])) # 3d points initial num & pose 
    x0 = np.hstack((cameras.ravel(), Xs.ravel())) # camera pose and 3d points
    xs = xs.ravel()

    J = bundle_adjustment_sparsity(n_cameras=n_cameras, n_points=n_points, camera_indices=cam_indices, point_indices=point_indices)
    res = least_squares(func2, x0, verbose=2, ftol=1e-15, method='trf', jac_sparsity=J, args=(xs, n_cameras, n_points, cam_indices, point_indices, K))

    opt_cameras = res.x[:n_cameras * 6].reshape((n_cameras, 6)) # rotation and translation
    opt_points = res.x[n_cameras * 6: ].reshape((n_points, 3))  # 3d points
    
    return opt_cameras, opt_points


def plot_camera(camera_poses):
    # print(camera_poses)
    fig2 = plt.figure()
    ax = fig2.add_subplot(111, projection='3d')
    for i in range(camera_poses.shape[0]):
        x = camera_poses[i,0]
        y = camera_poses[i,1]
        z = camera_poses[i,2]
        ax.scatter(x,y,z, color='black', depthshade=False, s=6)
        ax.text(x, y, z, str(i+1),fontsize=10, color='darkblue')
    
    ax.set_xlim([-1, 2])
    ax.set_ylim([-1, 2])
    ax.set_zlim([-1, 2])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_aspect('auto','box')

    plt.title('Projected 3d Points')
    plt.show()