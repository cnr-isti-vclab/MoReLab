from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.spatial import distance
import numpy as np


class PointsConnecting(QObject):
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
        self.selected_connect_idx = -1
        self.all_pts = []
        
        
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
                            v.connect_groups_regular[t][i] = self.group_num
                            feature_selected = True

                            if len(self.data_val) == 4:
                                
                                self.occurence_groups.append(self.order)
                                self.all_pts.append(self.data_val)
                                # print("Primitive count : "+str(self.primitive_count))
                                self.group_counts.append(self.ctrl_wdg.quad_obj.primitive_count)
                                c = self.ctrl_wdg.quad_obj.getRGBfromI(self.ctrl_wdg.quad_obj.primitive_count)
                                self.colors.append(c)
                                # print(self.data_val)

                                self.deleted.append(False)
                                self.order = []
                                self.data_val = []
                                self.group_num += 1
                                self.ctrl_wdg.quad_obj.primitive_count += 1
                                
            elif self.ctrl_wdg.kf_method == "Network":
                for i, fc in enumerate(v.features_network[t]):
                    if not v.hide_network[t][i]:
                        d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                        if d < self.dist_thresh_select:
                            self.order.append(i)
                            self.data_val.append(data[i,:])
                            v.connect_groups_network[t][i] = self.group_num
                            feature_selected = True

                            if len(self.data_val) == 4:
                                self.occurence_groups.append(self.order)
                                self.all_pts.append(self.data_val)
                                # print("Primitive count : "+str(self.primitive_count))
                                self.group_counts.append(self.ctrl_wdg.quad_obj.primitive_count)
                                c = self.ctrl_wdg.quad_obj.getRGBfromI(self.ctrl_wdg.quad_obj.primitive_count)
                                self.colors.append(c)
                                self.deleted.append(False)
                                self.order = []
                                self.data_val = []
                                self.group_num += 1
                                self.ctrl_wdg.quad_obj.primitive_count += 1

             
        return feature_selected
    
    
    def delete_connect_group(self, idx):
        if idx != -1:
            self.deleted[idx] = True
            occ = self.occurence_groups[idx]
            v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
            t = self.ctrl_wdg.selected_thumbnail_index
            if self.ctrl_wdg.kf_method == "Regular":
                for i, c in enumerate(occ):
                    v.connect_groups_regular[t][c] = -1
            elif self.ctrl_wdg.kf_method == "Network":
                for i, c in enumerate(occ):
                    v.connect_groups_network[t][c] = -1
                    
            self.selected_connect_idx = -1
