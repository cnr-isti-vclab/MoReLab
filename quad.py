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
                        self.occurence_groups.append(occ)
                        
                        self.compute_new_points(np.array([data_val[0][0], data_val[0][1], data_val[0][2]]),
                                                np.array([data_val[2][0], data_val[2][1], data_val[2][2]]),
                                                np.array([data_val[3][0], data_val[3][1], data_val[3][2]]),
                                                np.array([data_val[1][0], data_val[1][1], data_val[1][2]]))
                        
                        
                        
    def compute_new_points(self, F1, F2, F3, F4): # F1, F2, F3, F4 are the input points in clockwise order as on doc file
        
        center = 0.25*(F1 + F2 + F3 + F4)
        
        n1 = np.cross((F1 - F2), (F3 - F2))
        n2 = np.cross((F3 - F4), (F1 - F4))
        n1 = n1/np.linalg.norm(n1)
        n2 = n1/np.linalg.norm(n2)

        normal_sum = n1 + n2
        assert np.linalg.norm(normal_sum) > 0
        n_avg = normal_sum/np.linalg.norm(normal_sum)
        
        T = (F1-F2)/np.linalg.norm(F1-F2)
        B = np.cross(T, n_avg)

        
        CF1 = F1 - center
        CF2 = F2 - center
        CF3 = F3 - center
        CF4 = F4 - center
        
        projection1_T = np.dot(CF1, T)
        projection2_T = np.dot(CF2, T)
        projection3_T = np.dot(CF3, T)
        projection4_T = np.dot(CF4, T)

        projection1_B = np.dot(CF1, B)
        projection2_B = np.dot(CF2, B)
        projection3_B = np.dot(CF3, B)
        projection4_B = np.dot(CF4, B)
        
        # print(projection1_B)
        
        min_T = min(projection1_T, projection2_T, projection3_T, projection4_T)
        max_T = max(projection1_T, projection2_T, projection3_T, projection4_T)
        min_B = min(projection1_B, projection2_B, projection3_B, projection4_B)
        max_B = max(projection1_B, projection2_B, projection3_B, projection4_B)
                
        P1 = max_T*T + max_B*B + center
        P2 = min_T*T + max_B*B + center
        P3 = min_T*T + min_B*B + center
        P4 = max_T*T + min_B*B + center
        
        x = [P1, P2, P3, P4]
        # print(x)
        
        self.new_points.append(x)
        
