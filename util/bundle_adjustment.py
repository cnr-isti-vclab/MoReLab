import numpy as np
import cv2, time, os
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix
# import matplotlib.pyplot as plt






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
    
    return points_proj[:, :2]

def calc_error(params, points_2d, n_cameras, n_points, camera_indices, point_indices, K):
    camera_params = params[:n_cameras * 6].reshape((n_cameras, 6))
    points_3d = params[n_cameras * 6:].reshape((n_points, 3))        
    points_proj = project(points_3d[point_indices], camera_params[camera_indices], K)
    # np.save(os.path.join(folder, ))
    result = (points_2d - points_proj).ravel()
    return result




def bundle_adjustment(xs, visible_labels, K, img_indices):
    assert len(xs) == len(visible_labels) 
    # print(xs)
    # print(visible_labels)
    n_cameras = len(xs)
    points_2d = np.vstack(xs)
    cam_indices = np.array([])
    point_indices = np.array([])
    for i,x in enumerate(visible_labels):
        print("Number of features in image # "+str(img_indices[i]+1)+" : "+str(len(x)))
        cam_indices = np.hstack((cam_indices, np.full_like(np.arange(len(x), dtype=int), i)))
        # print(cam_indices)
        point_indices = np.hstack((point_indices, x-1))
        # print("==========================================")
        # print(point_indices)
        
    cam_indices = cam_indices.astype(int)
    point_indices = point_indices.astype(int)
    
    # print(cam_indices)
    # print(point_indices)

    # Initialize cameras and 3D points
    cameras = np.zeros((n_cameras, 6)) # rotation and translation
    cameras[:,2] = 1 # watching forward 
    
    n_3d_points = max(point_indices) + 1
    Xs = np.full((n_3d_points, 3), np.array([[1, 2, 3]])) # 3d points initial num & pose. 1,2, 3 are dummy initial values 
    x0 = np.hstack((cameras.ravel(), Xs.ravel())) # camera pose and 3d points

    J = bundle_adjustment_sparsity(n_cameras=n_cameras, n_points=n_3d_points, camera_indices=cam_indices, point_indices=point_indices)
    res = least_squares(calc_error, x0, verbose=1, xtol=1e-8, ftol=1e-15, method='trf', jac_sparsity=J, args=(points_2d, n_cameras, n_3d_points, cam_indices, point_indices, K))

    opt_cameras = res.x[:n_cameras * 6].reshape((n_cameras, 6)) # rotation and translation
    all_points = res.x[n_cameras * 6: ].reshape((n_3d_points, 3))  # 3d points
    
    # Remove deleted feature points
    final_points = []
    for i in range(all_points.shape[0]):
        if not (all_points[i,0] == 1 and all_points[i,1] == 2 and all_points[i,2] == 3):
            final_points.append(all_points[i,:])
    
    final_points = np.asarray(final_points)

    
    return opt_cameras,  all_points, final_points