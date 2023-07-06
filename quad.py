from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.spatial import distance
import numpy as np
from scipy.spatial.transform import Rotation as R


class Quad_Tool(QObject):
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        self.dist_thresh_select = 10.0
        self.group_num = 0
        self.colors = [(0,0,0)]
        self.order = []
        self.data_val = []
        self.group_counts = []
        self.deleted = []
        self.selected_quad_idx = -1
        self.all_pts = []
        self.vector1s = []
        self.occurence_groups = []


    def reset(self, ctrl_wdg):
        self.__init__(ctrl_wdg)
        
        
    def select_feature(self, x, y):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = self.ctrl_wdg.selected_thumbnail_index
        
        feature_selected = False

        if (len(v.features_regular) > 0 or len(v.features_network) > 0) and len(self.ctrl_wdg.gl_viewer.obj.all_ply_pts) > 0:
            data = self.ctrl_wdg.gl_viewer.obj.all_ply_pts[-1]    # 3D data from bundle adjustment
            cnt = 0
            if self.ctrl_wdg.kf_method == "Regular":
                for i, fc in enumerate(v.features_regular[t]):
                    if not v.hide_regular[t][i]:
                        d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                        if d < self.dist_thresh_select:
                            self.data_val.append(data[v.mapping_2d_3d_regular[t][cnt] , :])
                            self.order.append(i)
                            # self.data_val.append(data[i,:])

                            v.quad_groups_regular[t][i] = self.group_num                         
                            feature_selected = True
                            if len(self.data_val) == 4:
                                if self.ctrl_wdg.kf_method == "Regular":        
                                    for order in self.order:
                                        v.quad_groups_regular[t][order] = -1
                                elif self.ctrl_wdg.kf_method == "Network":        
                                    for order in self.order:
                                        v.quad_groups_network[t][order] = -1
                                self.add_quad()
                        cnt += 1
                        
            elif self.ctrl_wdg.kf_method == "Network":
                for i, fc in enumerate(v.features_network[t]):
                    if not v.hide_network[t][i]:
                        d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                        if d < self.dist_thresh_select:
                            self.data_val.append(data[v.mapping_2d_3d_regular[t][cnt] , :])
                            self.order.append(i)
                            # self.data_val.append(data[i,:])
                            v.quad_groups_network[t][i] = self.group_num

                            feature_selected = True
                            if len(self.data_val) == 4:
                                if self.ctrl_wdg.kf_method == "Regular":        
                                    for order in self.order:
                                        v.quad_groups_regular[t][order] = -1
                                elif self.ctrl_wdg.kf_method == "Network":        
                                    for order in self.order:
                                        v.quad_groups_network[t][order] = -1
                                self.add_quad()
                                
                        cnt += 1

        return feature_selected
    
    
    def add_quad(self):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = self.ctrl_wdg.selected_thumbnail_index
        
        self.occurence_groups.append(self.order)
        c1, c2, c3, c4 = 0.5*(self.data_val[0]+self.data_val[1]), 0.5*(self.data_val[1]+self.data_val[2]), 0.5*(self.data_val[2]+self.data_val[3]), 0.5*(self.data_val[3]+self.data_val[0])
        self.vector1s.append([self.data_val[0] - c4, self.data_val[1] - c2, self.data_val[3] - c4, self.data_val[2] - c2, self.data_val[0] - c1, self.data_val[1] - c1, self.data_val[3] - c3, self.data_val[2] - c3])
        self.all_pts.append(self.data_val)
        # print("Primitive count : "+str(self.primitive_count))
        self.group_counts.append(self.ctrl_wdg.rect_obj.primitive_count)
        c = self.ctrl_wdg.rect_obj.getRGBfromI(self.ctrl_wdg.rect_obj.primitive_count)
        self.colors.append(c)
        # print(self.data_val)
        # print("Going to append delete")
        self.deleted.append(False)
        self.order = []
        self.data_val = []
        self.group_num += 1
        self.ctrl_wdg.rect_obj.primitive_count += 1
    
    
    def delete_quad(self, idx):
        if idx != -1:
            self.deleted[idx] = True
            self.selected_quad_idx = -1

    def rotate(self, angle_degrees, rotation_axis):
        if self.selected_quad_idx != -1:
            angle_radians = np.radians(angle_degrees)
            rotation_vector = angle_radians * rotation_axis
            rotation = R.from_rotvec(rotation_vector)
            pts_list = self.all_pts[self.selected_quad_idx]
            center = 0.25*(pts_list[0] + pts_list[1] + pts_list[2] + pts_list[3])
            # print("--------------------------------")
            for i, pt in enumerate(pts_list):
                self.all_pts[self.selected_quad_idx][i] = rotation.apply(pt - center) + center


    def translate(self, axis, idx):
        if idx != -1:
            pts_list = self.all_pts[idx]
            for i, pt in enumerate(pts_list):
                self.all_pts[idx][i] = axis + pt


    def scale(self, scale, bPressed):
        i = self.selected_quad_idx
        if i != -1:
            pts_list = self.all_pts[i]

            vec1, vec2, vec3, vec4 = self.vector1s[i][0], self.vector1s[i][1], self.vector1s[i][2], self.vector1s[i][3]
            vec5, vec6, vec7, vec8 = self.vector1s[i][4], self.vector1s[i][5], self.vector1s[i][6], self.vector1s[i][7]
            
            if scale < 1:
                if bPressed:
                    scale = 10

                self.all_pts[i][3] = pts_list[3] - (1/scale)*vec3
                self.all_pts[i][2] = pts_list[2] - (1/scale)*vec4
                self.all_pts[i][0] = pts_list[0] - (1/scale)*vec1
                self.all_pts[i][1] = pts_list[1] - (1/scale)*vec2

                self.all_pts[i][3] = self.all_pts[i][3] - (1/scale)*vec7
                self.all_pts[i][2] = self.all_pts[i][2] - (1/scale)*vec8
                self.all_pts[i][0] = self.all_pts[i][0] - (1/scale)*vec5
                self.all_pts[i][1] = self.all_pts[i][1] - (1/scale)*vec6

                
            else:
                if bPressed:
                    scale = 0.1
                self.all_pts[i][3] = pts_list[3] + scale*vec3
                self.all_pts[i][2] = pts_list[2] + scale*vec4
                self.all_pts[i][0] = pts_list[0] + scale*vec1
                self.all_pts[i][1] = pts_list[1] + scale*vec2

                self.all_pts[i][3] = self.all_pts[i][3] + scale*vec7
                self.all_pts[i][2] = self.all_pts[i][2] + scale*vec8
                self.all_pts[i][0] = self.all_pts[i][0] + scale*vec5
                self.all_pts[i][1] = self.all_pts[i][1] + scale*vec6


            