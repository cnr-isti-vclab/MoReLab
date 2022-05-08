from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from feature_crosshair import FeatureCrosshair

import numpy as np
from object_panel import ObjectPanel
import cv2


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
        self.wdg_tree = ObjectPanel()
        self.feature_pixmap = QPixmap("icons/small_crosshair.png")
        self.add_tool_icons()
        self.cross_hair = False
        
        self.labels = []
        self.locs = [[]]
        self.associated_frames = [[]]
        
        self.labels2 = []
        self.locs2 = [[]]
        self.associated_frames2 = [[]]
        self.first_delete = False
        
        # self.associated_frames2 = [[]]
        self.selected_feature_index =-1
        self.count_ = 0
        self.deleted_labels = []
        self.partially_deleted_labels = []
        self.partially_frames = []
        

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
        # self.hide_features(False)
        self.wdg_tree.clear()
        self.ctrl_wdg.viewer.setScrolDragMode()
        self.ctrl_wdg.setCursor(QCursor(Qt.ArrowCursor))
        
    def feature_tool(self):
        # print('feature')
        self.mv_tool.setStyleSheet(self.tool_btn_style)
        self.ft_tool.setStyleSheet('background-color: rgb(180,180,180); border: 1px solid darkgray; ')
        self.ctrl_wdg.setCursor(QCursor(Qt.CrossCursor))
        self.ctrl_wdg.viewer.setNoDragMode()
        self.cross_hair = True
        self.hide_features(True)
        
    def refresh(self):
        self.labels = []
        self.associated_frames = [[]]
        self.selected_feature_index =-1
        self.count_ = 0
        self.wdg_tree.clear()

    
    def add_feature(self, p):
        if self.cross_hair:
            t = self.ctrl_wdg.selected_thumbnail_index
            v = self.ctrl_wdg.movie_caps[self.ctrl_wdg.selected_movie_idx]
            
            if self.ctrl_wdg.kf_method == "Regular":
                v.n_objects_kf_regular[t, 0] += 1
                label = v.n_objects_kf_regular[t, 0]
            elif self.ctrl_wdg.kf_method == "Network":
                v.n_objects_kf_network[t, 0] += 1
                label = v.n_objects_kf_network[t, 0]
                
                
            fc = FeatureCrosshair(self.feature_pixmap, p.x(), p.y(), label, self)
                
            if label not in self.labels:
                self.selected_feature_index += 1
                self.labels.append(label)
            else:
                self.count_ = self.labels.index(label)
                self.selected_feature_index = self.labels.index(label)
                
                
            if t not in self.associated_frames[self.count_]:
                self.associated_frames[self.count_].append(t)
                # self.associated_frames2[self.count_].append(t)
                self.locs[self.count_].append([fc.x_loc, fc.y_loc])
            else:
                self.associated_frames.append([t])
                # self.associated_frames2.append([t])
                self.locs.append([[fc.x_loc, fc.y_loc]])
                            
            # Add feature on the scene

            self.ctrl_wdg.viewer._scene.addItem(fc)
            self.ctrl_wdg.viewer._scene.addItem(fc.label)
            
            if self.ctrl_wdg.kf_method == "Regular":
                v.features_regular[t].append(fc)
                
            elif self.ctrl_wdg.kf_method == "Network":
                v.features_network[t].append(fc)
                
            self.display_data(v)
            
            
    def display_data(self, v):
        if not self.first_delete:
            if (len(self.labels) == len(self.associated_frames)) and (len(self.labels) == len(self.locs)):                
                v.features_data = {"Label": self.labels,
                       "Frames": self.associated_frames,
                       "Locations": self.locs}
                self.wdg_tree.add_feature_data(v.features_data, self.deleted_labels)
            else:
                print("Mismatch in dimensions!")
                print(self.labels)
                print(self.associated_frames)
                print(self.locs)
                
        else:
            if (len(self.labels2) == len(self.associated_frames2)) and (len(self.labels2) == len(self.locs2)):                
                v.features_data = {"Label": self.labels2,
                       "Frames": self.associated_frames2,
                       "Locations": self.locs2}
                self.wdg_tree.add_feature_data(v.features_data, self.deleted_labels)
            else:
                print("Mismatch in dimensions!")
                print(self.labels2)
                print(self.associated_frames2)
                print(self.locs2)
            
            
    def hide_features(self, current=True):
        t = self.ctrl_wdg.selected_thumbnail_index            
        v = self.ctrl_wdg.movie_caps[self.ctrl_wdg.selected_movie_idx]
        
        if self.ctrl_wdg.kf_method == "Regular":
            for i in range(v.n_objects_kf_regular.shape[0]):
                for j,f in enumerate(v.features_regular[i]):
                    f.label.setVisible(False)
                    f.setVisible(False)
        elif self.ctrl_wdg.kf_method == "Network":
            for i in range(v.n_objects_kf_network.shape[0]):
                for j,f in enumerate(v.features_network[i]):
                    f.label.setVisible(False)
                    f.setVisible(False)
        
        print(self.partially_frames)
        if current:
            if self.ctrl_wdg.kf_method == "Regular":
                for j,f in enumerate(v.features_regular[t]):
                    if t in self.partially_frames:
                        if (int(f.label.label) not in self.deleted_labels) and (int(f.label.label) not in self.partially_deleted_labels):
                            f.label.setVisible(True)
                            f.setVisible(True)
                    else:
                        if (int(f.label.label) not in self.deleted_labels):
                            f.label.setVisible(True)
                            f.setVisible(True)
                            
            elif self.ctrl_wdg.kf_method == "Network":
                for j,f in enumerate(v.features_network[t]):
                    if t in self.partially_frames:
                        if (int(f.label.label) not in self.deleted_labels) and (int(f.label.label) not in self.partially_deleted_labels):
                            f.label.setVisible(True)
                            f.setVisible(True)
                    else:
                        if (int(f.label.label) not in self.deleted_labels):
                            f.label.setVisible(True)
                            f.setVisible(True)

    
    def delete_feature(self):
        t = self.ctrl_wdg.selected_thumbnail_index            
        v = self.ctrl_wdg.movie_caps[self.ctrl_wdg.selected_movie_idx]
        i = self.selected_feature_index
        print(i)
        
        if not self.first_delete:
            self.first_delete = True
            self.labels2 = self.labels
            self.associated_frames2 = self.associated_frames
            self.locs2 = self.locs
        
        if i != -1:
            if self.ctrl_wdg.kf_method == "Regular":
                v.features_regular[t][i].label.setVisible(False)
                v.features_regular[t][i].setVisible(False)
                
            elif self.ctrl_wdg.kf_method == "Network":
                v.features_network[t][i].label.setVisible(False)
                v.features_network[t][i].setVisible(False)
                
            if len(self.associated_frames2[i]) > 1:
                pic_idx = self.associated_frames2[i].index(t)
                self.associated_frames2[i].pop(pic_idx)
                self.locs2[i].pop(pic_idx)
                self.partially_deleted_labels.append(self.labels[i])
                self.partially_frames.append(t)
                
            elif len(self.associated_frames2[i]) == 1:
                self.deleted_labels.append(self.labels[i])
                # self.associated_frames2.pop(i)
                # self.locs2.pop(i)
                # self.labels2.pop(i)
                
            
            self.display_data(v)


 
            
    
            