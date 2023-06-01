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
        self.occurence_groups = []
        self.colors = [(0,0,0)]
        self.order = []
        self.data_val = []
        self.group_counts = []
        self.deleted = []
        self.selected_quad_idx = -1
        self.all_pts = []
        self.scaling_factor = 1.1


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
                            for img_ind in self.ctrl_wdg.gl_viewer.obj.img_indices:
                                v.quad_groups_regular[img_ind][i] = self.group_num

                            feature_selected = True
                            # print("selected quad")

                            if len(self.data_val) == 4:
                                self.add_quad()

                                
            elif self.ctrl_wdg.kf_method == "Network":
                for i, fc in enumerate(v.features_network[t]):
                    if not v.hide_network[t][i]:
                        d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                        if d < self.dist_thresh_select:
                            self.order.append(i)
                            self.data_val.append(data[i,:])
                            for img_ind in self.ctrl_wdg.gl_viewer.obj.img_indices:
                                v.quad_groups_network[img_ind][i] = self.group_num

                            feature_selected = True

                            if len(self.data_val) == 4:
                                self.add_quad()

             
        return feature_selected
    
    
    def add_quad(self):
        self.occurence_groups.append(self.order)
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
            occ = self.occurence_groups[idx]
            v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]

            if self.ctrl_wdg.kf_method == "Regular":
                for i, c in enumerate(occ):
                    for t in self.ctrl_wdg.gl_viewer.obj.img_indices:
                        v.quad_groups_regular[t][c] = -1

            elif self.ctrl_wdg.kf_method == "Network":
                for i, c in enumerate(occ):
                    for t in self.ctrl_wdg.gl_viewer.obj.img_indices:
                        v.quad_groups_network[t][c] = -1
                
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


    def translate(self, axis):
        if self.selected_quad_idx != -1:
            pts_list = self.all_pts[self.selected_quad_idx]
            for i, pt in enumerate(pts_list):
                self.all_pts[self.selected_quad_idx][i] = axis + pt

    def scale_up(self):
        i = self.selected_quad_idx
        if i != -1:
            self.all_pts[i][0] = self.all_pts[i][0] * self.scaling_factor
            self.all_pts[i][1] = self.all_pts[i][1] * self.scaling_factor
            self.all_pts[i][2] = self.all_pts[i][2] / self.scaling_factor
            self.all_pts[i][3] = self.all_pts[i][3] / self.scaling_factor
            

    def scale_down(self):
        i = self.selected_quad_idx
        if i != -1:
            self.all_pts[i][0] = self.all_pts[i][0] / self.scaling_factor
            self.all_pts[i][1] = self.all_pts[i][1] / self.scaling_factor
            self.all_pts[i][2] = self.all_pts[i][2] * self.scaling_factor
            self.all_pts[i][3] = self.all_pts[i][3] * self.scaling_factor
            