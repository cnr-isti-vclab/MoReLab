from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.spatial import distance
from quad_panel import QuadPanel
import numpy as np


class Quad_Tool(QObject):
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        self.quad_tree = QuadPanel(self)
        self.dist_thresh_select = 10.0
        self.group_num = 0
        self.occurence_groups = []
        self.colors = [(0,0,0)]
        self.centers_x = []
        self.centers_y = []
        self.new_points = []
        self.order = []
        self.data_val = []
        
        
    def select_feature(self, x, y):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = self.ctrl_wdg.selected_thumbnail_index
        
        feature_selected = False

        if (len(v.features_regular) > 0 or len(v.features_network) > 0) and len(self.ctrl_wdg.gl_viewer.obj.ply_pts) > 0:
            data = self.ctrl_wdg.gl_viewer.obj.ply_pts[-1]    # 3D data from bundle adjustment
            if self.ctrl_wdg.kf_method == "Regular":
                for i, fc in enumerate(v.features_regular[t]):
                    if not v.hide_regular[t][i]:
                        d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                        if d < self.dist_thresh_select and v.quad_groups_regular[t][i] == -1:
                            self.order.append(i)
                            self.data_val.append(data[i,:])
                            v.quad_groups_regular[t][i] = self.group_num
                            feature_selected = True

                            if len(self.data_val) == 4:
                                self.occurence_groups.append(self.order)
                                c = self.getRGBfromI(self.group_num+1)
                                self.colors.append(c)
                                xp = self.compute_new_points(self.data_val[0], self.data_val[1], self.data_val[2], self.data_val[3])
                                self.new_points.append(xp)
                                self.quad_tree.add_quad(self.order, self.group_num + 1)
                                self.order = []
                                self.data_val = []
                                self.group_num += 1

             
            elif self.ctrl_wdg.kf_method == "Network":
                for i, fc in enumerate(v.features_network[t]):
                    if not v.hide_network[t][i]:
                        d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                        if d < self.dist_thresh_select and v.quad_groups_network[t][i] == -1:
                            self.order.append(i)
                            self.data_val.append(data[i,:])
                            v.quad_groups_network[t][i] = self.group_num
                            feature_selected = True

                            if len(self.data_val) == 4:
                                self.occurence_groups.append(self.order)
                                self.all_data_val.append(self.data_val)
                                c = self.getRGBfromI(self.group_num+1)
                                self.colors.append(c)
                                xp = self.compute_new_points(self.data_val[0], self.data_val[1], self.data_val[2], self.data_val[3])
                                self.new_points.append(xp)
                                self.quad_tree.add_quad(self.order, self.group_num + 1)
                                self.order = []
                                self.data_val = []
                                self.group_num += 1
        return feature_selected


                        
                        
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
        
        x = (P1, P2, P3, P4)
        return x
    
    
    def getRGBfromI(self, RGBint):
        blue =  RGBint & 255
        green = (RGBint >> 8) & 255
        red =   (RGBint >> 16) & 255
        c = (red, green, blue)
        # print(c)
        return c
        
    def getIfromRGB(self, r, g, b):
        RGBint = int(r * 256*256 + g * 256 + b)
        # print("ID : "+str(RGBint))
        return RGBint