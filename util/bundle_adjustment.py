import numpy as np
import cv2, time, os, math
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
from scipy.optimize import least_squares, minimize
from scipy.sparse import lil_matrix
from scipy.spatial import distance
import scipy
from PyQt5.QtGui import *
from util.sfm import *

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt





class BA_class():
    def __init__(self):
        # Widget.__init__(self, parent)
        # super().__init__(parent)
        self.n_cameras = 0
        self.points_2d = np.array([])
        self.cam_indices = np.array([])
        self.point_indices = np.array([])
        

    
    # Function to find distance
    def shortest_distance(self, x1, y1, z1, a, b, c, d):
        d = abs((a * x1 + b * y1 + c * z1 + d))
        e = (math.sqrt(a * a + b * b + c * c))
        dist = d/e
        return dist
            
        
    def bundle_adjustment_sparsity(self, n_cameras, n_points, camera_indices, point_indices, n_dist=0):
        if n_dist > 0:
            m = camera_indices.size * 2 + int((len(point_indices)*2) /n_dist) * n_dist
        else:
            m = camera_indices.size * 2
        n = n_cameras * 6 + n_points * 3 
        A = lil_matrix((m, n), dtype=int)
        # i = 0
        i = np.arange(camera_indices.size)
        for s in range(6):
            A[2 * i, camera_indices * 6 + s] = 1
            A[2 * i + 1, camera_indices * 6 + s] = 1
    
        for s in range(3):
            A[2 * i, n_cameras * 6 + point_indices * 3 + s] = 1
            A[2 * i + 1, n_cameras * 6 + point_indices * 3 + s] = 1
            
        return A
    
    def project(self, points, cam_trans, K):
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
    
    
    
    def calc_BA_error(self, params, points_2d, n_cameras, n_points, camera_indices, point_indices, K):                
        camera_params = params[:n_cameras * 6].reshape((n_cameras, 6))
        points_3d = params[n_cameras*6 : ].reshape((n_points, 3))
        points_proj = self.project(points_3d[point_indices], camera_params[camera_indices], K)
        diff_2d = points_2d - points_proj
        result = diff_2d.ravel()

        return result

    
    def bundle_adjustment(self, xs, visible_labels, img_indices, K):
        assert len(xs) == len(visible_labels) 

        self.n_cameras = len(xs)
        self.points_2d = np.vstack(xs)
        self.point_indices = np.array([])
        self.cam_indices = np.array([])
    
        for i,x in enumerate(visible_labels):
            print("Number of features in image # "+str(img_indices[i]+1)+" : "+str(len(x)))
            self.cam_indices = np.hstack((self.cam_indices, np.full_like(np.arange(len(x), dtype=int), i)))
            self.point_indices = np.hstack((self.point_indices, x-1))    
            
        self.cam_indices = self.cam_indices.astype(int)
        self.point_indices = self.point_indices.astype(int)

    
        # Initialize cameras and 3D points
        cameras = np.zeros((self.n_cameras, 6)) # rotation and translation
        cameras[:,2] = 1 # watching forward 
        
        n_3d_points = max(self.point_indices) + 1
        Xs = np.full((n_3d_points, 3), np.array([[1, 2, 3]])) # 3d points initial num & pose. 1,2, 3 are dummy initial values 
        x0 = np.hstack((cameras.ravel(), Xs.ravel())) # camera pose and 3d points
        
        J = self.bundle_adjustment_sparsity(n_cameras=self.n_cameras, n_points=n_3d_points, camera_indices=self.cam_indices, point_indices=self.point_indices)

        res = least_squares(self.calc_BA_error, x0, verbose=1, xtol=1e-9, ftol=1e-15, method='trf', jac_sparsity=J, max_nfev=500, args=(self.points_2d, self.n_cameras, n_3d_points, self.cam_indices, self.point_indices, K))
        
        opt_cameras = res.x[:self.n_cameras * 6].reshape((self.n_cameras, 6)) # rotation and translation
        all_points = res.x[self.n_cameras * 6 : self.n_cameras * 6 + n_3d_points*3].reshape((n_3d_points, 3))  # 3d points

        # print(final_points.shape)
        return opt_cameras,  all_points
    