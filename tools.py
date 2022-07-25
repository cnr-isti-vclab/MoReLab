from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from feature_crosshair import FeatureCrosshair
from util.util import feature_absent_dialogue, numFeature_dialogue, write_pointcloud, save_feature_locs
from util.sfm import *
from util.optimize_K import find_optimized_K
from util.bundle_adjustment import bundle_adjustment
import numpy as np
from object_panel import ObjectPanel
import cv2, copy
from scipy import optimize
import matplotlib.pyplot as plt

class Tools(QObject):
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        self.tool_btn_style =  """
                QPushButton:hover   { background-color: rgb(180,180,180); border: 1px solid darkgray;         }
                QPushButton {border:none; padding: 10px;}
                QToolTip { background-color: white; color: black); }
                """
        # print(self.ctrl_wdg.selected_movie_idx)
        self.wdg_tree = ObjectPanel(self)
        self.feature_pixmap = QPixmap("icons/small_crosshair.png")
        # print(type(self.feature_pixmap.size()))
        # print(self.feature_pixmap.size())
        self.add_tool_icons()
        self.cam_btn = QPushButton("Camera Calibration")
        self.cam_btn.clicked.connect(self.calibrate)
        self.cross_hair = False
        
        self.labels = []
        self.locs = []
        self.associated_frames = []
        self.associated_videos = []
        
        # self.associated_frames2 = [[]]
        self.selected_feature_index =-1
        self.count_ = 0
        
        self.features_data = {}
        
    def get_correspondent_pts(self, v):
        display = True
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
                    tmp1.append([int(fc.x_loc), int(fc.y_loc)])
                    if not hide:
                        tmp3.append([int(fc.x_loc), int(fc.y_loc)])
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
                    tmp1.append([int(fc.x_loc), int(fc.y_loc)])
                    if not hide:
                        tmp3.append([int(fc.x_loc), int(fc.y_loc)])
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

        
    def calibrate(self):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        all_pts, img_indices, visible_labels = self.get_correspondent_pts(v)

        # save_feature_locs(all_pts, visible_labels)

        K = estimateKMatrix(v.width, v.height, 30, 23.7, 15.6)
        # K = estimateKMatrix(v.width, v.height, 35)
        # K = find_optimized_K(all_pts, K, '1')

        if len(img_indices) > 0:

            opt_cameras, opt_points = bundle_adjustment(all_pts, visible_labels, K)                
            camera_poses = []
            for i in range(opt_cameras.shape[0]):
                R = getRotation(opt_cameras[i,:3], 'e')
                t = opt_cameras[i,3:].reshape((3,1))
                cm = calc_camera_pos(R, t)
                # print(cm)
                camera_poses.append([cm[0,0], cm[0,1], cm[0,2]])
            
            
            camera_poses = np.asarray(camera_poses)
            print(camera_poses)
            # print(camera_poses.shape)
            ply_pts = np.concatenate((opt_points, camera_poses), axis=0)
            
            write_pointcloud('after_BA.ply', ply_pts) 

        

    def add_tool_icons(self):
        icon_size = 30
        
        self.np_tool = QPushButton()
        self.np_tool.setIcon(QIcon("./icons/new_project.png"))
        self.np_tool.setIconSize(QSize(icon_size, icon_size))
        self.np_tool.setStyleSheet(self.tool_btn_style)
        self.np_tool.setToolTip("New Project")

        self.op_tool = QPushButton()
        self.op_tool.setIcon(QIcon("./icons/open_project.png"))
        self.op_tool.setIconSize(QSize(icon_size, icon_size))
        self.op_tool.setStyleSheet(self.tool_btn_style)
        self.op_tool.setToolTip("Open Project")

        self.om_tool = QPushButton()
        self.om_tool.setIcon(QIcon("./icons/open_movie.png"))
        self.om_tool.setIconSize(QSize(icon_size, icon_size))
        self.om_tool.setStyleSheet(self.tool_btn_style)
        self.om_tool.setToolTip("Open Movie")
        # self.om_tool.setStyleSheet("color: black; border: none; padding: 10px;")
        
        self.sp_tool = QPushButton()
        self.sp_tool.setIcon(QIcon("./icons/save_project.png"))
        self.sp_tool.setIconSize(QSize(icon_size, icon_size))
        self.sp_tool.setStyleSheet(self.tool_btn_style)
        self.sp_tool.setToolTip("Save Project")
        
        self.sp_as_tool = QPushButton()
        self.sp_as_tool.setIcon(QIcon("./icons/save_as.png"))
        self.sp_as_tool.setIconSize(QSize(icon_size, icon_size))
        self.sp_as_tool.setStyleSheet(self.tool_btn_style)
        self.sp_as_tool.setToolTip("Save as")

        self.ep_tool = QPushButton()
        self.ep_tool.setIcon(QIcon("./icons/exit_project.png"))
        self.ep_tool.setIconSize(QSize(icon_size, icon_size))
        self.ep_tool.setStyleSheet(self.tool_btn_style)
        self.ep_tool.setToolTip("Exit Project")


        self.mv_tool = QPushButton()
        self.mv_tool.setIcon(QIcon("./icons/cursor.png"))
        self.mv_tool.setIconSize(QSize(icon_size, icon_size))
        self.mv_tool.clicked.connect(self.move_tool)
        self.mv_tool.setStyleSheet(self.tool_btn_style)
        self.mv_tool.setToolTip("Move Tool")
        
        self.ft_tool = QPushButton()
        self.ft_tool.setIcon(QIcon("./icons/crosshair.png"))
        self.ft_tool.setIconSize(QSize(icon_size, icon_size))
        self.ft_tool.clicked.connect(self.feature_tool)
        self.ft_tool.setStyleSheet(self.tool_btn_style)
        self.ft_tool.setToolTip("Feature Tool")

        
    def move_tool(self):
        self.ft_tool.setStyleSheet(self.tool_btn_style)
        self.mv_tool.setStyleSheet('background-color: rgb(180,180,180); border: 1px solid darkgray; ')
        self.cross_hair = False
        self.hide_features(True)
        # self.hide_features(False)
        self.display_data()
        self.ctrl_wdg.viewer.setScrolDragMode()
        self.ctrl_wdg.viewer.setCursor(QCursor(Qt.ArrowCursor))
        
    def feature_tool(self):
        # print('feature')
        self.mv_tool.setStyleSheet(self.tool_btn_style)
        self.ft_tool.setStyleSheet('background-color: rgb(180,180,180); border: 1px solid darkgray; ')
        self.ctrl_wdg.viewer.setCursor(QCursor(Qt.CrossCursor))
        self.ctrl_wdg.viewer.setNoDragMode()
        self.cross_hair = True
        self.hide_features(True)
        self.display_data()

    
    def add_feature(self, x, y):
        # print(self.selected_feature_index)
        if self.cross_hair:
            t = self.ctrl_wdg.selected_thumbnail_index
            v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
            m_idx = self.ctrl_wdg.mv_panel.selected_movie_idx
            
            if self.ctrl_wdg.kf_method == "Regular":
                v.n_objects_kf_regular[t] += 1
                label = v.n_objects_kf_regular[t]
            elif self.ctrl_wdg.kf_method == "Network":
                v.n_objects_kf_network[t] += 1
                label = v.n_objects_kf_network[t]
                
            fc = FeatureCrosshair(self.feature_pixmap, x, y, label, self)
                
            if label not in self.labels:
                if len(self.labels) > label:
                    self.selected_feature_index = label -1
                    if self.labels[self.selected_feature_index] == -1:
                        self.labels[self.selected_feature_index] = label
                        self.associated_frames[self.selected_feature_index][0] = t
                        self.associated_videos[self.selected_feature_index][0] = m_idx
                        self.locs[self.selected_feature_index][0] = [fc.x_loc, fc.y_loc]
                    else:
                        print("Problem in adding feature...............")
                else:
                    self.selected_feature_index = self.selected_feature_index + 1
                    self.labels.append(label)
                    self.associated_frames.append([t])
                    self.associated_videos.append([m_idx])
                    self.locs.append([[fc.x_loc, fc.y_loc]])
                
            else:
                self.selected_feature_index = self.labels.index(label)
                self.associated_frames[self.selected_feature_index].append(t)
                self.associated_videos[self.selected_feature_index].append(m_idx)
                self.locs[self.selected_feature_index].append([fc.x_loc, fc.y_loc])

                            
            # Add feature on the scene
            

            self.ctrl_wdg.viewer._scene.addItem(fc)
            self.ctrl_wdg.viewer._scene.addItem(fc.label)
            
            if self.ctrl_wdg.kf_method == "Regular":
                v.features_regular[t].append(fc)
                v.hide_regular[t].append(False)
                # v.locs_regular[t].append()
                
            elif self.ctrl_wdg.kf_method == "Network":
                v.features_network[t].append(fc)
                v.hide_network[t].append(False)
                
            self.display_data()
            
            
    def display_data(self):
        # print(self.selected_feature_index)
        if (len(self.labels) == len(self.associated_frames)) and (len(self.labels) == len(self.locs)):                
            self.features_data = {"Label": self.labels,
                   "Frames": self.associated_frames,
                   "Videos": self.associated_videos,
                   "Locations": self.locs}
        
            # print("Feature index: "+str(self.selected_feature_index))
            self.wdg_tree.add_feature_data(self.features_data, self.selected_feature_index)
        else:
            print("Mismatch in dimensions!")
            print(self.labels)
            print(self.associated_frames)
            print(self.locs)
            
            
    def hide_features(self, current=True):
        t = self.ctrl_wdg.selected_thumbnail_index            
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        
        for v1 in self.ctrl_wdg.mv_panel.movie_caps:
            for i in range(len(v1.n_objects_kf_regular)):
                if v1.features_regular !=  []:
                    for j,f in enumerate(v1.features_regular[i]):
                        f.label.setVisible(False)
                        f.setVisible(False)
            for i in range(len(v1.n_objects_kf_network)):
                if v1.features_network !=  []:
                    for j,f in enumerate(v1.features_network[i]):
                        f.label.setVisible(False)
                        f.setVisible(False)
        
        if current:
            if self.ctrl_wdg.kf_method == "Regular":
                if v.features_regular != []:
                    for j,f in enumerate(v.features_regular[t]):
                        if not v.hide_regular[t][j]:
                            f.label.setVisible(True)
                            f.setVisible(True)
                            
            elif self.ctrl_wdg.kf_method == "Network":
                if v.features_network != []:
                    for j,f in enumerate(v.features_network[t]):
                        if not v.hide_network[t][j]:
                            f.label.setVisible(True)
                            f.setVisible(True)


    def find_idx(self, f, t):
        idd = [m for m, x in enumerate(self.associated_frames[f]) if x == t]
        if len(idd) == 1:
            pic_idx = idd[0]
        else:
            idd2 = [n for n, x in enumerate(self.associated_videos[f]) if x == self.ctrl_wdg.mv_panel.selected_movie_idx]
            d = list(set(idd2).intersection(idd))
            if len(d) == 1:
                pic_idx = d[0]
            else:
                print("Problem in Finding index")
        
        return pic_idx
        

    
    def delete_feature(self):
        t = self.ctrl_wdg.selected_thumbnail_index            
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        i = self.selected_feature_index
        # print("To be deleted : "+str(i))
        
        if self.cross_hair:
            found = False
            if self.ctrl_wdg.kf_method == "Regular" and len(v.hide_regular[t]) > i:
                if not v.hide_regular[t][i] and i == (int(v.features_regular[t][i].label.label) - 1):
                    found = True
                
            elif self.ctrl_wdg.kf_method == "Network" and len(v.hide_network[t]) > i:
                if not v.hide_network[t][i] and i == (int(v.features_network[t][i].label.label) - 1):
                    found = True
                    
            if found:
                if self.ctrl_wdg.kf_method == "Regular":
                    v.features_regular[t][i].label.setVisible(False)
                    v.features_regular[t][i].setVisible(False)
                    v.hide_regular[t][i] = True
                    # v.features_regular[t].pop(i)
                    
                elif self.ctrl_wdg.kf_method == "Network":
                    v.features_network[t][i].label.setVisible(False)
                    v.features_network[t][i].setVisible(False)
                    v.hide_network[t][i] = True
                    # v.features_network[t].pop(i)
                    
                if len(self.associated_frames[i]) > 1:
                    pic_idx = self.find_idx(i,t)
                    self.associated_frames[i].pop(pic_idx)
                    self.associated_videos[i].pop(pic_idx)
                    self.locs[i].pop(pic_idx)
    
                    
                elif len(self.associated_frames[i]) == 1:
                    self.labels[i] = -1
                    self.associated_frames[i] = [-1]
                    self.associated_videos[i] = [-1]
                    self.locs[i] = [[-1, -1]]
                    
                    
                self.wdg_tree.label_index = 0
                self.selected_feature_index = int(self.wdg_tree.items[self.wdg_tree.label_index].child(0).text(1)) - 1
                # print(self.associated_frames)
                # print(self.labels)
                # print("Feature Index : "+str(self.selected_feature_index))
                # print("Label Index : "+str(self.wdg_tree.label_index))
                self.display_data()
            else:
                feature_absent_dialogue()


 
            
    
            
