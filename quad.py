from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.spatial import distance
import numpy as np


class Quad_Tool(QObject):
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        self.dist_thresh_select = 10.0
        self.num_selected = 0
        self.occurence_groups = []
        self.centers_x = []
        self.centers_y = []
        self.new_points = []
        
        
    def select_feature(self, x, y):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = self.ctrl_wdg.selected_thumbnail_index

        if len(v.features_regular) > 0 or len(v.features_network) > 0:
            if self.ctrl_wdg.kf_method == "Regular":
                for i, fc in enumerate(v.features_regular[t]):
                    if not v.hide_regular[t][i]:
                        d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                        if d < self.dist_thresh_select and v.quad_groups_regular[t][i] == -1:
                            v.quad_groups_regular[t][i] = 1 + int(self.num_selected/4)                            
                            self.num_selected += 1

                if self.num_selected % 4 == 0 and self.num_selected > 0:
                    data = self.ctrl_wdg.gl_viewer.obj.ply_pts[0]    # 3D data from bundle adjustment
                    
                    num_groups = int(self.num_selected/4)
                    for j in range(num_groups):
                        occ = []
                        data_val = []
                        # print(v.quad_groups_regular[t])
                        for k,val in enumerate(v.quad_groups_regular[t]):
                            if j+1 == val:
                                occ.append(k)
                                data_val.append(data[k,:])
                        assert len(data_val) == 4
                        # print(data_val)
                        # print("Occ : "+str(occ))
                        # occ.sort()
                        self.occurence_groups.append(occ)
                        # center_x = 0.25*(v.features_regular[t][occ[0]].x_loc + v.features_regular[t][occ[1]].x_loc
                        #                  + v.features_regular[t][occ[2]].x_loc + v.features_regular[t][occ[3]].x_loc)
                        # center_y = 0.25*(v.features_regular[t][occ[0]].y_loc + v.features_regular[t][occ[1]].y_loc
                        #                  + v.features_regular[t][occ[2]].y_loc + v.features_regular[t][occ[3]].y_loc)
                        
                        center_x = 0.25*(data_val[0][0] + data_val[1][0] + data_val[2][0] + data_val[3][0])
                        center_y = 0.25*(data_val[0][1] + data_val[1][1] + data_val[2][1] + data_val[3][1])
                        center_z = 0.25*(data_val[0][2] + data_val[1][2] + data_val[2][2] + data_val[3][2])
                        
                        self.centers_x.append(center_x)
                        self.centers_y.append(center_y)
                          
                        # self.compute_new_points(np.array([v.features_regular[t][occ[0]].x_loc, v.features_regular[t][occ[0]].y_loc, 200]), 
                        #                         np.array([v.features_regular[t][occ[2]].x_loc, v.features_regular[t][occ[2]].y_loc, 250]),
                        #                         np.array([v.features_regular[t][occ[3]].x_loc, v.features_regular[t][occ[3]].y_loc, 300]),
                        #                         np.array([v.features_regular[t][occ[1]].x_loc, v.features_regular[t][occ[1]].y_loc, 350]),
                        #                         np.array([center_x, center_y, 275]))
                        
                        # self.compute_new_points(np.array([-1.01946608,  0.18388299,  6.04981712]), 
                        #                         np.array([-0.86667419, -0.08496316,  5.76754991]),
                        #                         np.array([-0.46790764,  0.21249327,  5.71121127]),
                        #                         np.array([-0.62409596,  0.47610997,  6.00283816]),
                        #                         np.array([-0.69455289, 0.1968807675, 5.882854115]))
                        
                        self.compute_new_points(np.array([data_val[0][0], data_val[0][1], data_val[0][2]]),
                                                np.array([data_val[2][0], data_val[2][1], data_val[2][2]]),
                                                np.array([data_val[3][0], data_val[3][1], data_val[3][2]]),
                                                np.array([data_val[1][0], data_val[1][1], data_val[1][2]]),
                                                np.array([center_x, center_y, center_z]))
                        
                        
                        
    def compute_new_points(self, F1, F2, F3, F4, center): # F1, F2, F3, F4 are the input points in clockwise order as on doc file
        n1 = np.cross((F1 - F2), (F3 - F2))
        n2 = np.cross((F3 - F4), (F1 - F4))
        # print("Normals:")
        # print(n1)
        # print(n2)
        normal_sum = n1 + n2
        assert np.linalg.norm(normal_sum) > 0
        n_avg = normal_sum/np.linalg.norm(normal_sum)
        T1 = F1/np.linalg.norm(F1)
        T2 = F2/np.linalg.norm(F2)
        T3 = F3/np.linalg.norm(F3)
        T4 = F4/np.linalg.norm(F4)
        
        B1 = np.cross(T1, n_avg)
        B2 = np.cross(T2, n_avg)
        B3 = np.cross(T3, n_avg)
        B4 = np.cross(T4, n_avg)
        
        CF1 = F1 - center
        CF2 = F2 - center
        CF3 = F3 - center
        CF4 = F4 - center
        
        projection1_T = np.dot(CF1, T1)
        projection2_T = np.dot(CF2, T2)
        projection3_T = np.dot(CF3, T3)
        projection4_T = np.dot(CF4, T4)

        projection1_B = np.dot(CF1, B1)
        projection2_B = np.dot(CF2, B2)
        projection3_B = np.dot(CF3, B3)
        projection4_B = np.dot(CF4, B4)
        
        # print(projection1_B)
        
        min_T = min(projection1_T, projection2_T, projection3_T, projection4_T)
        max_T = max(projection1_T, projection2_T, projection3_T, projection4_T)
        min_B = min(projection1_B, projection2_B, projection3_B, projection4_B)
        max_B = max(projection1_B, projection2_B, projection3_B, projection4_B)
        
        P1 = max_T + max_B + center
        P2 = max_T + min_B + center
        P3 = min_T + max_B + center
        P4 = min_T + min_B + center
        
        # x = [P1, P2, P3, P4]
        x = self.convert_3d_2d(P1, P2, P3, P4)
        
        self.new_points.append(x)
        
        
    def convert_3d_2d(self, P1, P2, P3, P4):
        X1 = np.concatenate((P1.reshape((3,1)), P2.reshape((3,1)), P3.reshape((3,1)), P4.reshape((3,1))), axis=1)
        Pw = np.concatenate((X1, np.ones(shape=(1,X1.shape[1]))), axis=0)
        
        # Pr is projection matrix i.e Pr = K*[Rt] of 1st image
        Pr = np.array([[ 1.34815101e+03, -2.23753918e+03,  6.52148837e+01,  5.73894430e+03],
                     [ 1.87606361e+03,  9.13289904e+02,  5.01494110e+02,  1.04862840e+03],
                     [ 1.79682769e-01, -2.93414822e-01,  9.38947200e-01,  1.17974684e+00]])
        
        x = np.matmul(Pr, Pw)
        x = x.T
        yy = []
        for i in range(x.shape[0]):
            x[i,:] = x[i,:]/x[i,2]
            yy.append([self.ctrl_wdg.gl_viewer.obj.wdg_tree.inv_trans_x(x[i,0]), self.ctrl_wdg.gl_viewer.obj.wdg_tree.inv_trans_y(x[i,1])])

        return yy
                    
