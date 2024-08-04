from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from feature_panel import FeaturePanel
from util.util import *
from util.sfm import *
from cylinder import Cylinder_Tool
from curve import Curve_Tool
from rectangle import Rectangle_Tool
from quad import Quad_Tool
from util.bundle_adjustment import BA_class
from scipy.spatial.transform import Rotation

# import matplotlib.pyplot as plt

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
        
        self.img_indices = []
        self.all_ply_pts = []
        self.camera_poses = []
        self.camera_projection_mat = []
        self.global_indices = []
        self.epipolar_last = []
        self.epipolar_current = []
        self.last_img_idx = -1
        self.current_img_epipolar = -1
        self.fundamental_mat = None
        self.dist_thresh = 20
        self.K = np.eye(3)
        self.BA_obj = BA_class()
        self.cylinder_obj = Cylinder_Tool(self.ctrl_wdg)
        self.curve_obj = Curve_Tool(self.ctrl_wdg)
        
        
    
        
    def initialize_mats(self):
        self.img_indices = []
        self.ctrl_wdg.gl_viewer.util_.bCalibrate, self.ctrl_wdg.gl_viewer.util_.measured_distances = True, []
        self.ctrl_wdg.gl_viewer.util_.last_pos = self.ctrl_wdg.gl_viewer.util_.current_pos = np.array([0.0, 0.0])
        self.ctrl_wdg.gl_viewer.util_.calibration_factor, self.ctrl_wdg.gl_viewer.util_.dist = 1, 0
        self.all_ply_pts = []
        self.camera_poses = []
        self.camera_projection_mat = []
        self.global_indices = []
        self.cylinder_obj.reset(self.ctrl_wdg)
        self.curve_obj.reset(self.ctrl_wdg)
        self.ctrl_wdg.rect_obj.reset(self.ctrl_wdg)
        self.ctrl_wdg.quad_obj.reset(self.ctrl_wdg)
        

        t = self.ctrl_wdg.selected_thumbnail_index
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        
        for i in range(len(self.ctrl_wdg.mv_panel.movie_caps)):
            self.ctrl_wdg.mv_panel.global_display_bool[i][0] = False
            self.ctrl_wdg.mv_panel.global_display_bool[i][1] = False
        
        if self.ctrl_wdg.kf_method == "Regular":
            v.init_3D_regular(len(v.key_frames_regular))
            for t in range(len(v.features_regular)):
                for i, fc in enumerate(v.features_regular[t]):
                    self.init_3D_feature_regular(v, t)


        elif self.ctrl_wdg.kf_method == "Network":
            v.init_3D_network(len(v.key_frames_network))
            for t in range(len(v.features_network)):
                for i, fc in enumerate(v.features_network[t]):
                    self.init_3D_feature_network(v, t)

        
    def get_correspondent_pts(self, v):
        final_visible_labels = []
        final_all_pts = []
        final_img_indices = []
        num_labels_on_images = []
        bReturn = False
        tmp2, tmp3 = [], []
        
        if self.ctrl_wdg.kf_method == "Regular":
            for i,hr in enumerate(v.hide_regular):
                for j,hide in enumerate(hr):
                    fc = v.features_regular[i][j]
                    if not hide:
                        tmp2.append(i)
                        tmp3.append(int(fc.label))

                    
        elif self.ctrl_wdg.kf_method == "Network":
            for i,hr in enumerate(v.hide_network):
                for j,hide in enumerate(hr):
                    fc = v.features_network[i][j]
                    if not hide:
                        tmp2.append(i)
                        tmp3.append(int(fc.label))

        if len(tmp2) > 0:         
            all_img_indices_set =set(tmp2)
            all_img_indices = sorted(all_img_indices_set)
            
            all_labels_set = set(tmp3)
            all_labels = sorted(all_labels_set)
            
            for i, img_idx in enumerate(all_img_indices):
                cnt_labels = 0
                tmp6, tmp7 = [], []  
                for j, label in enumerate(all_labels):
                    found, idx = self.feature_panel.get_feature_index(label, img_idx)
                    if found:
                        tmp6.append(label)
                        
                        if self.ctrl_wdg.kf_method == "Regular":
                            tmp7.append([self.feature_panel.transform_x(v.features_regular[img_idx][idx].x_loc), self.feature_panel.transform_y(v.features_regular[img_idx][idx].y_loc)])

                        elif self.ctrl_wdg.kf_method == "Network":
                            tmp7.append([self.feature_panel.transform_x(v.features_network[img_idx][idx].x_loc), self.feature_panel.transform_y(v.features_network[img_idx][idx].y_loc)])
                        
                        cnt_labels += 1
                        
                if cnt_labels > 7:  
                    final_img_indices.append(img_idx)
                    num_labels_on_images.append(cnt_labels)
                    
                    a = np.asarray(tmp6)
                    final_visible_labels.append(a)
                    
                    tmp_arr = np.zeros((len(tmp7), 2), dtype=float)
                    for cnt in range(len(tmp7)):
                        tmp_arr[cnt, :] = tmp7[cnt]
                    # print(tmp_arr.shape)
                    final_all_pts.append(tmp_arr)
                    
            
            if len(num_labels_on_images) < 2:
                bReturn = True
                    
        if bReturn:
            # numFeature_dialogue()
            return np.zeros((1,1)), [], [], []         # Dummy return
        
        else:
            return final_all_pts, final_img_indices, final_visible_labels, num_labels_on_images


        
    def compute_sfm(self):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = self.ctrl_wdg.selected_thumbnail_index
        
        # self.ctrl_wdg.main_file.logfile.info("Obtaining correspondences ....")
        all_pts, img_indices, visible_labels, num_labels = self.get_correspondent_pts(v)

        self.K = estimateKMatrix(v.width, v.height, 30, 23.7, 15.6)
        
        if len(img_indices) > 0:
            
            self.initialize_mats()
            # self.ctrl_wdg.main_file.logfile.info("Performing bundle adjustment ....")

            w = Dialog()
            w.show()
            
            opt_cameras, all_points = self.BA_obj.bundle_adjustment(all_pts, visible_labels, img_indices, self.K)
            # self.ctrl_wdg.main_file.logfile.info("There are "+str(all_points.shape[0])+" points for SfM ....")
            w.done(0)
            # self.ctrl_wdg.main_file.logfile.info("bundle adjustment has been computed ....")

            self.all_ply_pts.append(all_points)

            if self.ctrl_wdg.kf_method == "Regular":
                self.ctrl_wdg.mv_panel.global_display_bool[self.ctrl_wdg.mv_panel.selected_movie_idx][0] = True
                        
            elif self.ctrl_wdg.kf_method == "Network":
                self.ctrl_wdg.mv_panel.global_display_bool[self.ctrl_wdg.mv_panel.selected_movie_idx][1] = True
                
            
            for i, img_idx in enumerate(img_indices):
                for j in range(all_points.shape[0]):
                    if self.ctrl_wdg.kf_method == "Regular":
                        for k, fc in enumerate(v.features_regular[img_idx]):
                            if not v.hide_regular[img_idx][k]:
                                if j == int(fc.label) - 1:
                                    v.mapping_2d_3d_regular[img_idx].append(j)
                                    
                    elif self.ctrl_wdg.kf_method == "Network":
                        for k, fc in enumerate(v.features_network[img_idx]):
                            if not v.hide_network[img_idx][k]:
                                if j == int(fc.label) - 1:
                                    v.mapping_2d_3d_network[img_idx].append(j)                                
            
            # print("mapping : ")
            # for i, mapping in enumerate(v.mapping_2d_3d_regular):
            #     print(mapping)
            
            # print(v.count_deleted_regular)
            self.img_indices = img_indices
            self.ctrl_wdg.populate_scrollbar(self.ctrl_wdg.selected_thumbnail_index)
        
            cam_pos_list = []
            for i in range(opt_cameras.shape[0]):
                R = getRotation(opt_cameras[i,:3], 'e')
                
                t = opt_cameras[i,3:].reshape((3,1))
                cam_ext = np.concatenate((np.concatenate((R, t), axis=1), np.array([0,0,0,1]).reshape((1,4))), axis=0)
                self.camera_projection_mat.append((img_indices[i], cam_ext))
        
                cm = calc_camera_pos(R, t)
                cam_pos_list.append([cm[0,0], cm[0,1], cm[0,2]])
        
            array_camera_poses = np.asarray(cam_pos_list)

            self.camera_poses.append(array_camera_poses)
            
        else:
            numFeature_dialogue()
            


    def init_3D_feature_regular(self, v, t):
        v.rect_groups_regular[t].append(-1)
        v.quad_groups_regular[t].append(-1)
        v.cylinder_groups_regular[t].append(-1)


    def init_3D_feature_network(self, v, t):
        v.rect_groups_network[t].append(-1)
        v.quad_groups_network[t].append(-1)
        v.cylinder_groups_network[t].append(-1)

        
    def add_feature(self,x,y,label=-1, img_idx=-1):
        if img_idx == -1:
            img_idx = self.ctrl_wdg.selected_thumbnail_index
        m_idx = self.ctrl_wdg.mv_panel.selected_movie_idx
        v = self.ctrl_wdg.mv_panel.movie_caps[m_idx]


        if self.ctrl_wdg.kf_method == "Regular":
            v.n_objects_kf_regular[img_idx] += 1
            if label == -1:    
                label = v.n_objects_kf_regular[img_idx]
            
            # self.ctrl_wdg.main_file.logfile.info("Adding a feature with label "+str(label)+" on the image "+str(img_idx + 1)+" ....")
            fc = FeatureCrosshair(x, y, label)
            v.features_regular[img_idx].append(fc)
            v.hide_regular[img_idx].append(False)
            self.init_3D_feature_regular(v, img_idx)

        elif self.ctrl_wdg.kf_method == "Network":
            v.n_objects_kf_network[img_idx] += 1
            if label == -1:
                label = v.n_objects_kf_network[img_idx]
            
            # self.ctrl_wdg.main_file.logfile.info("Adding a feature with label "+str(label)+" on the image "+str(img_idx + 1)+" ....")
            fc = FeatureCrosshair(x, y, label)
            v.features_network[img_idx].append(fc)
            v.hide_network[img_idx].append(False)
            self.init_3D_feature_network(v, img_idx)


        self.feature_panel.selected_feature_idx = -1
        self.feature_panel.display_data()
    

            
    def count_visible_features(self, img_idx):
        m_idx = self.ctrl_wdg.mv_panel.selected_movie_idx
        v = self.ctrl_wdg.mv_panel.movie_caps[m_idx]
        num_features = 0
        if self.ctrl_wdg.kf_method == "Regular":
            hide_list = v.hide_regular[img_idx]
        elif self.ctrl_wdg.kf_method == "Network":
            hide_list = v.hide_network[img_idx]

        for bool_hide in hide_list:
            if not bool_hide:
                num_features = num_features + 1

        return num_features


    def delete_feature(self):
        t = self.ctrl_wdg.selected_thumbnail_index            
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        i = self.feature_panel.selected_feature_idx
        
        if self.ctrl_wdg.ui.cross_hair:
            if i != -1:
                # self.ctrl_wdg.main_file.logfile.info("Delete feature with index : "+str(i)+" on the image "+str(t+1)+" ....")
                if self.ctrl_wdg.kf_method == "Regular":
                    v.hide_regular[t][i] = True
                    v.count_deleted_regular[t].append(i)
                    
                elif self.ctrl_wdg.kf_method == "Network":
                    v.hide_network[t][i] = True
                    v.count_deleted_network[t].append(i)
                    
                self.feature_panel.selected_feature_idx = -1
                self.feature_panel.display_data()


    def move_feature(self, updated_cursor_x, updated_cursor_y, fc):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        f = self.feature_panel.selected_feature_idx
        t = self.ctrl_wdg.selected_thumbnail_index

        if self.ctrl_wdg.ui.cross_hair and f != -1:                               
            fc.x_loc = updated_cursor_x
            fc.y_loc = updated_cursor_y
            # self.ctrl_wdg.main_file.logfile.info("Moved feature with label : "+str(fc.label)+" on the image "+str(t+1)+" ....")

            self.feature_panel.display_data()

    def rename_feature(self, x, y):
        # print("Double mouse right click")
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = self.ctrl_wdg.selected_thumbnail_index
        bExit = False

        if self.ctrl_wdg.kf_method == "Regular" and len(v.features_regular) > 0:
            for i, fc in enumerate(v.features_regular[t]):
                if not v.hide_regular[t][i] and not bExit:
                    d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                    if d < self.dist_thresh:
                        self.create_renaming_panel()
                        if self.rename_dialog.exec():
                            new_label = int(self.e1.text())
                            found, idx = self.feature_panel.get_feature_index(new_label, t)
                            if found:
                                duplicate_dialogue()
                            else:
                                fc.label = str(new_label)
                                # self.ctrl_wdg.main_file.logfile.info("Renaming the feature to new label : "+str(new_label)+" ....")
                            bExit = True


        elif self.ctrl_wdg.kf_method == "Network" and len(v.features_network) > 0:
            for i, fc in enumerate(v.features_network[t]):
                if not v.hide_network[t][i] and not bExit:
                    d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                    if d < self.dist_thresh:
                        self.create_renaming_panel()
                        if self.rename_dialog.exec():
                            new_label = int(self.e1.text())
                            found, idx = self.feature_panel.get_feature_index(new_label, t)
                            if found:
                                duplicate_dialogue()
                            else:
                                fc.label = str(new_label)
                                # self.ctrl_wdg.main_file.logfile.info("Renaming the feature to new label : "+str(new_label)+" ....")
                            bExit = True
                                
        self.feature_panel.display_data()



    def create_renaming_panel(self):
        self.rename_dialog = QDialog()
        self.rename_dialog.setWindowTitle("Rename a feature panel")

        QBtn = QDialogButtonBox.Ok

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.rename_dialog.accept)

        label = QLabel("Enter the new label of the feature greater than 0 : ")

        self.e1 = QLineEdit("1")
        self.e1.setValidator(QIntValidator())
        self.e1.setMaxLength(10)
        self.e1.setFont(QFont("Arial", 20))

        cal_layout = QVBoxLayout()
        cal_layout.addWidget(label)
        cal_layout.addWidget(self.e1)
        cal_layout.addWidget(buttonBox)
        self.rename_dialog.setLayout(cal_layout)
        
        
        
    def get_epipolar_correspondences(self, v, t):
        current_pts, last_pts, found_labels = [], [], []
        all_labels = []
        temp_last_idx = -1
        # self.ctrl_wdg.main_file.logfile.info("Getting correspondences for epipolar line ....")
        if self.ctrl_wdg.kf_method == "Regular" and len(v.hide_regular) > 0 :            
            for i in range(t-1, -1, -1):
                if len(v.hide_regular[i]) > 0 and temp_last_idx == -1:
                    temp_last_idx = i
                    for j,hide in enumerate(v.hide_regular[i]):
                        fc = v.features_regular[i][j]
                        if not hide:
                            all_labels.append(int(fc.label))
                            
                            
            hide_list = v.hide_regular[t]
            for j,hide in enumerate(hide_list):
                fc = v.features_regular[t][j]
                if not hide:
                    all_labels.append(int(fc.label))
            
            if temp_last_idx == -1:
                epipolar_dialogue()
                return [], []
            else:
                all_labels_set = set(all_labels)            
                all_labels_unique = sorted(all_labels_set)
                
                for i, label in enumerate(all_labels_unique):
                    found_current, idx_current = self.feature_panel.get_feature_index(label, t)
                    found_last, idx_last = self.feature_panel.get_feature_index(label, temp_last_idx)
                    
                    if found_current and found_last:
                        found_labels.append(label)
                        if self.ctrl_wdg.kf_method == "Regular":
                            last_pts.append([v.features_regular[temp_last_idx][idx_last].x_loc, v.features_regular[temp_last_idx][idx_last].y_loc])
                            current_pts.append([v.features_regular[t][idx_current].x_loc, v.features_regular[t][idx_current].y_loc])

                
                if len(found_labels) > 7:
                    self.last_img_idx = temp_last_idx
                    self.current_img_epipolar = t
                    return last_pts, current_pts
                else:
                    epipolar_dialogue()
                    return [], []


        
        
    def compute_fundamental_mat(self):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = self.ctrl_wdg.selected_thumbnail_index
        last_pts, current_pts = self.get_epipolar_correspondences(v, t)
        self.fundamental_mat = None
        if len(last_pts) > 0 and len(current_pts) > 0:
            # self.ctrl_wdg.main_file.logfile.info("Computing fundamental matrix ....")
            self.epipolar_current = []
            last_pts_array = np.array(last_pts)
            current_pts_array = np.array(current_pts)
            F, mask = cv2.findFundamentalMat(last_pts_array, current_pts_array, cv2.FM_8POINT)
            self.fundamental_mat = F
            fundamental_dialogue()
                    


class FeatureCrosshair():
    def __init__(self, x, y, num_str):
        super().__init__()
        self.x_loc = x
        self.y_loc = y
        self.label = str(num_str)