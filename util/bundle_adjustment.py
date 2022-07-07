import numpy as np
import cv2, time
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix
import matplotlib.pyplot as plt





def prepare_data(points_3d, all_pts, R_set, C_set):
    assert len(all_pts) == len(R_set)
    camera_params = []
    points_2d = []
    point_indices = []
    camera_indices = []
    for i,R in enumerate(R_set):
        C = C_set[i]
        RC = [R[0,0], R[0,1], R[0,2], R[1,0], R[1,1], R[1,2], R[2,0], R[2,1], R[2,2], C[0], C[1], C[2]]
        camera_params.append(RC)
            
    for i in range(points_3d.shape[0]):
        for j in range(len(all_pts)):
            points_2d.append(all_pts[j][i])
            point_indices.append(i)
            camera_indices.append(j)
    
    camera_params = np.asarray(camera_params)
    camera_indices = np.asarray(camera_indices)
    points_2d = np.asarray(points_2d)
    point_indices = np.asarray(point_indices) 
    
    return camera_params, camera_indices, point_indices, points_2d


def local_to_global(R_local, t_local, last_R_global, last_t_global, Pw):
    R_global = np.dot(last_R_global, R_local)
    t_global = np.add(last_t_global, t_local.reshape((3,1)))

    X_3d = []
    for i in range(Pw.shape[0]):
        pt3d = Pw[i,:].reshape((1,3))
        new_pt = np.add(np.dot(pt3d, R_global), t_global.transpose())
        X_3d.append(new_pt)
    
    X_3d = np.vstack(X_3d)
    # print(X_3d.shape)
    # print(X_3d)
    return X_3d, R_global, t_global
    



def bundle_adjustment_sparsity(n_cameras, n_points, camera_indices, point_indices):
    m = camera_indices.size * 2
    n = n_cameras * 12 + n_points * 3
    A = lil_matrix((m, n), dtype=int)

    i = np.arange(camera_indices.size)
    for s in range(12):
        A[2 * i, camera_indices * 12 + s] = 1
        A[2 * i + 1, camera_indices * 12 + s] = 1

    for s in range(3):
        A[2 * i, n_cameras * 12 + point_indices * 3 + s] = 1
        A[2 * i + 1, n_cameras * 12 + point_indices * 3 + s] = 1

    return A

def project(points, camera_params, K):
    points_proj = []
    Pw = np.concatenate((points, np.ones((points.shape[0], 1))), axis=1)
    for idx in range(len(camera_params)): # idx applies to both points and cam_params, they are = length vectors
        R = camera_params[idx][:9].reshape(3,3)
        t = camera_params[idx][9:].reshape(3,1)
        P2 = np.dot(K, np.concatenate((R, t), axis=1))
        pt4d = Pw[idx, :].reshape(4,1)
        pt2d = np.matmul(P2, pt4d)
        pt2d = pt2d/pt2d[2,0]
        points_proj.append(pt2d[:-1, 0])

    points_proj = np.asarray(points_proj)
    return points_proj

def fun(params, n_cameras, n_points, camera_indices, point_indices, points_2d, K):
    camera_params = params[:n_cameras * 12].reshape((n_cameras, 12))
    points_3d = params[n_cameras * 12:].reshape((n_points, 3))
    points_proj = project(points_3d[point_indices], camera_params[camera_indices], K)
    return (points_proj - points_2d).ravel()
    # reprojection_err = 0
    # for i in range(points_proj.shape[0]):
    #     reprojection_err = reprojection_err  + np.linalg.norm( points_2d[i,:] - points_proj[i,:] )**2
    # return reprojection_err




def bundle_adjustment(camera_params, points_3d, camera_indices, point_indices, points_2d, K):
    n_cameras = camera_params.shape[0]
    n_points = points_3d.shape[0]

    n = 12 * n_cameras + 3 * n_points
    m = 2 * points_2d.shape[0]

    print("n_cameras: {}".format(n_cameras))
    print("n_points: {}".format(n_points))
    print("Total number of parameters: {}".format(n))
    print("Total number of residuals: {}".format(m))
    x0 = np.hstack((camera_params.ravel(), points_3d.ravel()))
    f0 = fun(x0, n_cameras, n_points, camera_indices, point_indices, points_2d, K)
    # print("+++++++++++++++++++++++++++++++++++++++++++")
    # print(f0.shape)

    A = bundle_adjustment_sparsity(n_cameras, n_points, camera_indices, point_indices)
    t0 = time.time()
    res = least_squares(fun, x0, jac_sparsity=A, verbose=2, x_scale='jac', method='trf', args=(n_cameras, n_points, camera_indices, point_indices, points_2d, K))
    t1 = time.time()
    print("Optimization took {0:.0f} seconds".format(t1 - t0))
    print("Final cost after BA : "+str(res['cost']))
    
    sol = res.x
    new_camera_params = sol[0:n_cameras*12].reshape((n_cameras, 12))
    new_points_3d = sol[n_cameras*12:].reshape((n_points, 3))
    return new_camera_params, new_points_3d


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
    
    ax.set_xlim([0, 2])
    ax.set_ylim([0, 2])
    ax.set_zlim([0, 2])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_aspect('auto','box')

    plt.title('Projected 3d Points')
    plt.show()