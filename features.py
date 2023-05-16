from PyQt5.QtWidgets import *
from feature_panel import FeaturePanel
from util.util import *
from util.sfm import *
from util.bundle_adjustment import bundle_adjustment
from cylinder import Cylinder_Tool
from curve import Curve_Tool
import numpy as np

class Features(QWidget):
    def __init__(self, parent=None):
        # Widget.__init__(self, parent)
        super().__init__(parent)
        self.ctrl_wdg = parent
        self.feature_panel = FeaturePanel(self.ctrl_wdg)
        
        self.btn_sfm = QPushButton("Compute SfM")
        self.btn_sfm.setStyleSheet("""
                                  QPushButton:hover   { background-color: rgb(145,224,255)}
                                  QPushButton {background-color: rgb(230,230,230); border-radius: 20px; padding: 15px; border: 1px solid black; color:black; font-size: 15px;}
                                  """)
        self.btn_sfm.clicked.connect(self.compute_sfm)
        self.initialize_mats()
        self.K = np.eye(3)
        self.cylinder_obj = Cylinder_Tool(self.ctrl_wdg)
        self.curve_obj = Curve_Tool(self.ctrl_wdg)
        
        
    def initialize_mats(self):
        self.img_indices = []
        self.ply_pts = []
        self.all_ply_pts = []
        self.camera_poses = []
        self.camera_projection_mat = []
        
    def get_correspondent_pts(self, v):
        img_indices = []
        all_locs = []
        visible_labels = []
        all_pts = []
        if self.ctrl_wdg.kf_method == "Regular":
            for i,hr in enumerate(v.hide_regular):
                tmp1, tmp2, tmp3 = [], [], []
                count = 0
                for j,hide in enumerate(hr):
                    fc = v.features_regular[i][j]
                    tmp1.append([self.feature_panel.transform_x(fc.x_loc), self.feature_panel.transform_y(fc.y_loc)])
                    if not hide:
                        tmp3.append([self.feature_panel.transform_x(fc.x_loc), self.feature_panel.transform_y(fc.y_loc)])
                        tmp2.append(j)
                        count = count + 1
                if count > 7:
                    img_indices.append(i)
                    all_locs.append(tmp1)
                    a = np.asarray(tmp2)
                    # print(a.shape)
                    visible_labels.append(a)
                    tmp_arr = np.zeros((len(tmp3), 2), dtype=float)
                    for cnt in range(len(tmp3)):
                        tmp_arr[cnt, :] = tmp3[cnt]
                    # print(tmp_arr.shape)
                    all_pts.append(tmp_arr)
                    
        elif self.ctrl_wdg.kf_method == "Network":
            for i,hr in enumerate(v.hide_network):
                tmp1, tmp2 = [], []
                count = 0
                for j,hide in enumerate(hr):
                    fc = v.features_regular[i][j]
                    tmp1.append([fc.x_loc, fc.y_loc])
                    if not hide:
                        tmp3.append([fc.x_loc, fc.y_loc])
                        tmp2.append(j)
                        count = count + 1
                if count > 7:
                    img_indices.append(i)
                    all_locs.append(tmp1)
                    a = np.asarray(tmp2)
                    visible_labels.append(a)
                    tmp_arr = np.zeros((len(tmp3), 2), dtype=float)
                    for cnt in range(len(tmp3)):
                        tmp_arr[cnt, :] = tmp3[cnt]
                    # print(tmp_arr.shape)
                    all_pts.append(tmp_arr)
        # for i in range
        if len(img_indices) < 2:
            numFeature_dialogue()
            return np.zeros((1,1)), [], []         # Dummy return 
        else:
            return all_pts, img_indices, visible_labels


        
    def compute_sfm(self):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        all_pts, img_indices, visible_labels = self.get_correspondent_pts(v)

        self.K = estimateKMatrix(v.width, v.height, 30, 23.7, 15.6)

    
        if len(img_indices) > 0:
            print("Performing Bundle adjustment")
            w = Dialog()
            w.show()

            opt_cameras, opt_points, all_points = bundle_adjustment(all_pts, visible_labels, self.K)
            self.initialize_mats()

            self.all_ply_pts.append(all_points)

            opt_points_ext = np.concatenate((opt_points, np.ones((opt_points.shape[0], 1))), axis=1)

            w.done(0)

            print("Bundle adjustment has been computed.")
            
            self.img_indices = img_indices
            self.ctrl_wdg.populate_scrollbar(self.ctrl_wdg.selected_thumbnail_index)

            cam_pos_list = []
            for i in range(opt_cameras.shape[0]):
                R = getRotation(opt_cameras[i,:3], 'e')
                t = opt_cameras[i,3:].reshape((3,1))

                cam_ext = np.concatenate((np.concatenate((R, t), axis=1), np.array([0,0,0,1]).reshape((1,4))), axis=0)
                # ppm =np.concatenate((np.matmul(self.K, (np.concatenate((R, t), axis=1))), np.array([0,0,0,1]).reshape((1,4))), axis=0)

                
                self.camera_projection_mat.append((img_indices[i], cam_ext))
                
                # print(cam_ext)
                
                cm = calc_camera_pos(R, t)
                cam_pos_list.append([cm[0,0], cm[0,1], cm[0,2]])
            
            array_camera_poses = np.asarray(cam_pos_list)
            # print(array_camera_poses)
            # print(self.camera_projection_mat)
            self.camera_poses.append(array_camera_poses)
            ply_pts = np.concatenate((opt_points, array_camera_poses), axis=0)
            # print(ply_pts)
            self.ply_pts.append(opt_points)
        
        
    def add_feature(self,x,y):
        if self.ctrl_wdg.ui.cross_hair:
            t = self.ctrl_wdg.selected_thumbnail_index
            m_idx = self.ctrl_wdg.mv_panel.selected_movie_idx
            v = self.ctrl_wdg.mv_panel.movie_caps[m_idx]
            # print("===========================================")

            if self.ctrl_wdg.kf_method == "Regular":
                v.n_objects_kf_regular[t] += 1
                label = v.n_objects_kf_regular[t]
            elif self.ctrl_wdg.kf_method == "Network":
                v.n_objects_kf_network[t] += 1
                label = v.n_objects_kf_network[t]
            
            # print(label)
            fc = FeatureCrosshair(x, y, label)                

            if self.ctrl_wdg.kf_method == "Regular":
                v.features_regular[t].append(fc)
                v.hide_regular[t].append(False)
                v.rect_groups_regular[t].append(-1)
                v.quad_groups_regular[t].append(-1)
                v.cylinder_groups_regular[t].append(-1)
                
                
            elif self.ctrl_wdg.kf_method == "Network":
                v.features_network[t].append(fc)
                v.hide_network[t].append(False)
                v.rect_groups_network[t].append(-1)
                v.quad_groups_network[t].append(-1)
                v.cylinder_groups_network[t].append(-1)

                
            self.feature_panel.selected_feature_idx = -1
            self.feature_panel.display_data()
            
            
    def delete_feature(self):
        t = self.ctrl_wdg.selected_thumbnail_index            
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        i = self.feature_panel.selected_feature_idx
        # print("To be deleted : "+str(i+1))
        
        if self.ctrl_wdg.ui.cross_hair and i != -1:
            found = False
            if self.ctrl_wdg.kf_method == "Regular" and len(v.hide_regular[t]) > i:
                if not v.hide_regular[t][i] and i == (int(v.features_regular[t][i].label) - 1):
                    found = True
                
            elif self.ctrl_wdg.kf_method == "Network" and len(v.hide_network[t]) > i:
                if not v.hide_network[t][i] and i == (int(v.features_network[t][i].label) - 1):
                    found = True
                    
            if found:
                if self.ctrl_wdg.kf_method == "Regular":
                    v.hide_regular[t][i] = True
                    
                elif self.ctrl_wdg.kf_method == "Network":
                    v.hide_network[t][i] = True
                    
                    
                self.feature_panel.selected_feature_idx = -1
                self.feature_panel.display_data()
            else:
                feature_absent_dialogue()



    def move_feature(self, updated_cursor_x, updated_cursor_y, fc):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        f = self.feature_panel.selected_feature_idx
        t = self.ctrl_wdg.selected_thumbnail_index

        if self.ctrl_wdg.ui.cross_hair and f != -1:
            move = False
    
            if self.ctrl_wdg.kf_method == "Regular":
                if not v.hide_regular[t][f] and f == (int(fc.label) - 1):
                    move = True
                
            elif self.ctrl_wdg.kf_method == "Network":
                if not v.hide_network[t][f] and f == (int(fc.label) - 1):
                    move = True
                                    
            if move:                                
                self.selected_feature_index = int(fc.label) - 1
                fc.x_loc = updated_cursor_x
                fc.y_loc = updated_cursor_y
                self.feature_panel.display_data()
            


class FeatureCrosshair():
    def __init__(self, x, y, num_str):
        super().__init__()
        self.l = 10
        self.x_loc = x
        self.y_loc = y
        self.label = str(num_str)