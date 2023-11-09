import numpy as np
import cv2, time, os, math
# from tkinter import *
from scipy.optimize import least_squares, minimize
from scipy.sparse import lil_matrix
from scipy.spatial import distance
import scipy
from PyQt5.QtGui import *
from util.sfm import *

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

# from sklearn.linear_model import RANSACRegressor
# import pybobyqa
# from pdfo import pdfo





class BA_class():
    def __init__(self):
        # Widget.__init__(self, parent)
        # super().__init__(parent)
        self.n_cameras = 0
        self.points_2d = np.array([])
        self.cam_indices = np.array([])
        self.point_indices = np.array([])
        self.results = []
        

    
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

        # reproj_err = 0
        # for i in range(points_2d.shape[0]):
        #     reproj_err += distance.euclidean(points_2d[i, :], points_proj[i, :])

        # print(reproj_err)
        return result
    
    
    def calc_nelder_mead_error(self, params, points_2d, n_cameras, n_points, camera_indices, point_indices, K, constrained_list, weight, weight_2):
        camera_params = params[:n_cameras * 6].reshape((n_cameras, 6))
        points_3d = params[n_cameras*6 : ].reshape((n_points, 3))
        
        # planar1 = points_3d[23:32, :]
        # planar2 = points_3d[32:34, :]
        # planar_pts2 = np.concatenate((planar1, planar2), axis=0)  
        
        points_proj = self.project(points_3d[point_indices], camera_params[camera_indices], K)
        
        global reproj_err
        global all_reproj_errors
        all_reproj_errors = []
        reproj_err = 0
        
        for i in range(points_2d.shape[0]):
            d = distance.euclidean(points_2d[i, :], points_proj[i, :])
            if d > 10:
                all_reproj_errors.append(0) ### Dummy value
                reproj_err = 1e20
                break
            else:
                reproj_err += d
                all_reproj_errors.append(d)
        
        global constraint_err
        constraint_err = 0
        global all_distances
        all_distances = []

        if len(constrained_list) > 0 and reproj_err < 1e20:
            num_params = points_2d.shape[0]*2
            # num_copies = int(num_params/len(constrained_list))
            num_copies = 1
            for j in range(num_copies):            
                for i in range(0, len(constrained_list), 2):
                    tup1 = constrained_list[i]
                    tup2 = constrained_list[i+1]
            
                    d1 = distance.euclidean(points_3d[tup1[0]], points_3d[tup1[1]])
                    d2 = distance.euclidean(points_3d[tup2[0]], points_3d[tup2[1]])
                    
                    constraint_err += abs(d1 - d2)
                    
                    all_distances.append(abs(d1 - d2))

        # global planar_err
        # planar_err = 0
        # global all_planar_distances
        # all_planar_distances = []
        # for i in range(planar_pts2.shape[0]):
        #     dist = self.shortest_distance(planar_pts2[i, 0], planar_pts2[i, 1], planar_pts2[i, 2], a, b, c, d)
        #     all_planar_distances.append(dist)
        #     planar_err += dist
            

                    
        total_err = reproj_err + constraint_err*weight
        # print(total_err)
        return total_err
    
    
    
    
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
        self.results.append(res.x)
        
        opt_cameras = res.x[:self.n_cameras * 6].reshape((self.n_cameras, 6)) # rotation and translation
        all_points = res.x[self.n_cameras * 6 : self.n_cameras * 6 + n_3d_points*3].reshape((n_3d_points, 3))  # 3d points
        
        # Remove deleted feature points
        final_points = []
        for i in range(all_points.shape[0]):
            if not (all_points[i,0] == 1 and all_points[i,1] == 2 and all_points[i,2] == 3):
                final_points.append(all_points[i,:])
        
        final_points = np.asarray(final_points)

        return opt_cameras,  all_points, final_points
    
    
    
    def apply_linear_constraint(self, K, constrained_list, method_lc, planar_pts=[]):
                
        if method_lc == "Auto":
            weight_list = [10, 50, 100, 500]
        elif method_lc == "Very low":
            weight_list = [100]
        elif method_lc == "Low":
            weight_list = [500]
        elif method_lc == "Medium":
            weight_list = [700]
        elif method_lc == "High":
            weight_list = [1000]
        else:
            weight_list = [2000]
    
        # weight_list = [4000]
        
        ### print(weight_list)
        n_3d_points = max(self.point_indices) + 1
        # n_3d_points = 35
        temp_res = []
        diff_errors = []
        weight_2 = 1
        # a, b, c, d = self.find_plane(planar_pts)
        
        for weight in weight_list:
            # res = pybobyqa.solve(self.calc_nelder_mead_error, self.results[-1], print_progress = True, args=(self.points_2d, self.n_cameras, n_3d_points, self.cam_indices, self.point_indices, K, constrained_list, weight, weight_2))
            res = minimize(self.calc_nelder_mead_error, self.results[-1], method='nelder-mead', options={'disp':True},  args=(self.points_2d, self.n_cameras, n_3d_points, self.cam_indices, self.point_indices, K, constrained_list, weight, weight_2))
            temp_res.append(res.x)
            # print(res)
            print("Weights: ")
            print(weight)
            print("Errors: ")
            print(reproj_err, constraint_err)
            x1 = np.linspace(1, len(all_reproj_errors), num=len(all_reproj_errors))
            x2 = np.linspace(1, len(all_distances), num=len(all_distances))
            # x3 = np.linspace(1, len(all_planar_distances), num=len(all_planar_distances))
            fig, axs = plt.subplots(2)
            axs[0].plot(x1, all_reproj_errors, '.-')
            axs[0].set_ylabel("Reprojection errors")
            axs[0].grid()
            axs[1].plot(x2, all_distances, '.-')
            axs[1].set_ylabel("Constraint errors")
            axs[1].grid()
            # axs[2].plot(x3, all_planar_distances, '.-')
            # axs[2].set_ylabel("Planar errors")
            # axs[2].grid()
            plt.savefig('error.jpg', bbox_inches='tight')

            

            diff_errors.append(abs(reproj_err - constraint_err))   
            
            # # summarize the result
            # print(res.flag)
            # print('Status : '+ str(res.msg))
            # print('Total Evaluations: '+str(res.nf))
            print(res.success)
            print('Status : '+ str(res.message))
            print('Total Evaluations: '+str(res.nfev))
            
        
        idx = diff_errors.index(min(diff_errors))
        # print("Index : "+str(idx)) 
        final_res = temp_res[idx]
        
        self.results.append(final_res)
        opt_cameras = final_res[:self.n_cameras * 6].reshape((self.n_cameras, 6)) # rotation and translation
        all_points = final_res[self.n_cameras * 6 : ].reshape((n_3d_points, 3))  # 3d points
        
        # Remove deleted feature points
        final_points = []
        for i in range(all_points.shape[0]):
            if not (all_points[i,0] == 10 and all_points[i,1] == 20 and all_points[i,2] == 30):
                final_points.append(all_points[i,:])
        
        final_points = np.asarray(final_points)
        
        return opt_cameras,  all_points, final_points
    



    def find_plane(self, xyz):
        X = xyz[:, :2]
        Z = xyz[:, 2]

        # Fitting a plane using RANSAC
        ransac = RANSACRegressor()
        ransac.fit(X, Z)
        
        # Accessing the fitted plane parameters
        a = ransac.estimator_.coef_[0]
        b = ransac.estimator_.coef_[1]
        c = -1
        d = ransac.estimator_.intercept_
        
        return a, b, c, d



