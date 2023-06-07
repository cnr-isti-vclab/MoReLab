from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.spatial import distance
import numpy as np
from scipy.spatial.transform import Rotation as R


class Rectangle_Tool(QObject):
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        self.dist_thresh_select = 10.0
        self.group_num = 0
        self.colors = [(0,0,0)]
        self.centers_x = []
        self.centers_y = []
        self.new_points = []
        self.order = []
        self.data_val = []
        self.primitive_count = 1
        self.rect_counts = []
        self.deleted = []
        self.tangents = []
        self.binormals = []
        self.normals = []
        self.centers = []
        self.scaling_factor = 1.1
        self.min_Ts = []
        self.max_Ts = []
        self.min_Bs = []
        self.max_Bs = []
        self.selected_rect_idx = -1
        self.bFirstAnchor = True
        self.bSecondAnchor = False
        self.first_anchor = np.array([0.0, 0.0, 0.0])
        self.second_anchor = np.array([0.0, 0.0, 0.0])

    def reset(self, ctrl_wdg):
        self.__init__(ctrl_wdg)

        
    def select_feature(self, x, y):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = self.ctrl_wdg.selected_thumbnail_index
        
        feature_selected = False

        if (len(v.features_regular) > 0 or len(v.features_network) > 0) and len(self.ctrl_wdg.gl_viewer.obj.ply_pts) > 0:
            data = self.ctrl_wdg.gl_viewer.obj.all_ply_pts[-1]    # 3D data from bundle adjustment
            if self.ctrl_wdg.kf_method == "Regular":
                for i, fc in enumerate(v.features_regular[t]):
                    if not v.hide_regular[t][i]:
                        d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                        if d < self.dist_thresh_select:
                            self.order.append(i)
                            self.data_val.append(data[i,:])
                            # print("selected rectangle")
                            for img_ind in self.ctrl_wdg.gl_viewer.obj.img_indices:
                                # print(v.rect_groups_regular)
                                v.rect_groups_regular[img_ind][i] = self.group_num
                            feature_selected = True

                            if len(self.data_val) == 4:
                                for img_ind in self.ctrl_wdg.gl_viewer.obj.img_indices:
                                    # print(v.rect_groups_regular)
                                    v.rect_groups_regular[img_ind][i] = -1
                                    v.rect_groups_regular[img_ind][self.order[0]] = -1
                                    v.rect_groups_regular[img_ind][self.order[1]] = -1
                                    v.rect_groups_regular[img_ind][self.order[2]] = -1
                                self.add_rectangle()

                                
            elif self.ctrl_wdg.kf_method == "Network":
                for i, fc in enumerate(v.features_network[t]):
                    if not v.hide_network[t][i]:
                        d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                        if d < self.dist_thresh_select:
                            self.order.append(i)
                            self.data_val.append(data[i,:])
                            for img_ind in self.ctrl_wdg.gl_viewer.obj.img_indices:
                                v.rect_groups_network[img_ind][i] = self.group_num
                            feature_selected = True

                            if len(self.data_val) == 4:
                                for img_ind in self.ctrl_wdg.gl_viewer.obj.img_indices:
                                    # print(v.rect_groups_regular)
                                    v.rect_groups_network[img_ind][i] = -1
                                    v.rect_groups_network[img_ind][self.order[0]] = -1
                                    v.rect_groups_network[img_ind][self.order[1]] = -1
                                    v.rect_groups_network[img_ind][self.order[2]] = -1
                                self.add_rectangle()

             
        return feature_selected
    
    
    
    
    def add_rectangle(self):
        self.rect_counts.append(self.primitive_count)
        c = self.getRGBfromI(self.primitive_count)
        self.colors.append(c)
        xp = self.compute_new_points(self.data_val[0], self.data_val[1], self.data_val[2], self.data_val[3])
        self.new_points.append(xp)
        self.deleted.append(False)
        self.order = []
        self.data_val = []
        self.group_num += 1
        self.primitive_count += 1
        


                        
                        
    def compute_new_points(self, F1, F2, F3, F4): # F1, F2, F3, F4 are the input points in clockwise order as on doc file
        center = 0.25*(F1 + F2 + F3 + F4)

        n1 = np.cross((F1 - F2), (F3 - F2))
        n2 = np.cross((F3 - F4), (F1 - F4))
        n1 = n1/np.linalg.norm(n1)
        n2 = n1/np.linalg.norm(n2)

        normal_sum = 0.5*(n1 + n2)

        assert np.linalg.norm(normal_sum) > 0
        n_avg = normal_sum/np.linalg.norm(normal_sum)
        
        T = (F1-F2)/np.linalg.norm(F1-F2)
        B = np.cross(T, n_avg)
        
        
        self.tangents.append(T)
        self.binormals.append(B)
        self.normals.append(n_avg)
        self.centers.append(center)

        
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
        
        self.min_Ts.append(min_T)
        self.max_Ts.append(max_T)
        self.min_Bs.append(min_B)
        self.max_Bs.append(max_B)
                
        return self.get_rect_points(len(self.new_points))
        

    
    
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
    
    def get_rect_points(self, i):
        P1 = self.max_Ts[i]*self.tangents[i] + self.max_Bs[i]*self.binormals[i] + self.centers[i]
        P2 = self.min_Ts[i]*self.tangents[i] + self.max_Bs[i]*self.binormals[i] + self.centers[i]
        P3 = self.min_Ts[i]*self.tangents[i] + self.min_Bs[i]*self.binormals[i] + self.centers[i]
        P4 = self.max_Ts[i]*self.tangents[i] + self.min_Bs[i]*self.binormals[i] + self.centers[i] 
        x = [P1, P2, P3, P4]
        return x
    
    def delete_rect(self, idx):
        if idx != -1:
            self.deleted[idx] = True
            self.selected_rect_idx = -1
                    
    def scale_up(self):
        i = self.selected_rect_idx
        if i != -1:
            # print("Scaling up "+str(i)+"st/th rect")
            self.max_Ts[i] *= self.scaling_factor
            self.min_Ts[i] *= self.scaling_factor
            self.max_Bs[i] *= self.scaling_factor
            self.min_Bs[i] *= self.scaling_factor
            self.new_points[i] = self.get_rect_points(i)


    def scale_down(self):
        i = self.selected_rect_idx
        if i != -1:
            # print("Scaling down "+str(i)+"st/th rect")
            self.max_Ts[i] /= self.scaling_factor
            self.min_Ts[i] /= self.scaling_factor
            self.max_Bs[i] /= self.scaling_factor
            self.min_Bs[i] /= self.scaling_factor
            self.new_points[i] = self.get_rect_points(i)
        
    def rotate(self, angle_degrees, rotation_axis):
        if self.selected_rect_idx != -1:
            angle_radians = np.radians(angle_degrees)
            rotation_vector = angle_radians * rotation_axis
            rotation = R.from_rotvec(rotation_vector)
            pts_list = self.new_points[self.selected_rect_idx]
            self.tangents[self.selected_rect_idx] = rotation.apply(self.tangents[self.selected_rect_idx])
            self.binormals[self.selected_rect_idx] = rotation.apply(self.binormals[self.selected_rect_idx])
            # self.centers[self.selected_rect_idx] = rotation.apply(self.centers[self.selected_rect_idx])
            center = 0.25*(pts_list[0] + pts_list[1] + pts_list[2] + pts_list[3])
            for i, pt in enumerate(pts_list):
                self.new_points[self.selected_rect_idx][i] = rotation.apply(pt - center) + center


    def translate(self, axis, idx):
        if idx != -1:
            pts_list = self.new_points[idx]
            self.centers[idx] = axis + self.centers[idx]
            for i, pt in enumerate(pts_list):
                self.new_points[idx][i] = axis + pt

        
