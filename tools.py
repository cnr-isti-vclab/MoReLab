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
        self.wdg_tree = ObjectPanel(self)
        self.feature_pixmap = QPixmap("icons/small_crosshair.png")
        self.add_tool_icons()
        self.cross_hair = False
        
        self.labels = []
        self.locs = []
        self.associated_frames = []
        self.associated_videos = []
        
        # self.associated_frames2 = [[]]
        self.selected_feature_index =-1
        self.count_ = 0
        
        
        self.features_data = {}
        

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
        self.ctrl_wdg.viewer.setCursor(QCursor(Qt.ArrowCursor))
        
    def feature_tool(self):
        # print('feature')
        self.mv_tool.setStyleSheet(self.tool_btn_style)
        self.ft_tool.setStyleSheet('background-color: rgb(180,180,180); border: 1px solid darkgray; ')
        self.ctrl_wdg.viewer.setCursor(QCursor(Qt.CrossCursor))
        self.ctrl_wdg.viewer.setNoDragMode()
        self.cross_hair = True
        self.hide_features(True)

    
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
            print(label)
                
            if label not in self.labels:
                if len(labels) > label:
                    self.selected_feature_index = label -1
                    if self.labels[self.selected_feature_index] == -1:
                        self.associated_frames[self.selected_feature_index][0] = t
                        self.associated_videos[self.selected_feature_index][0] = self.ctrl_wdg.selected_movie_idx
                        self.locs[self.selected_feature_index][0] = [fc.x_loc, fc.y_loc]
                    else:
                        print("Localllllllllllllllllllllllllllllllllllllllll")
                else:
                    ++self.selected_feature_index
                    self.labels.append(label)
                    self.associated_frames.append([t])
                    self.associated_videos.append([self.ctrl_wdg.selected_movie_idx])
                    self.locs.append([[fc.x_loc, fc.y_loc]])
                
            else:
                self.selected_feature_index = self.labels.index(label)
                self.associated_frames[self.selected_feature_index].append(t)
                self.associated_videos[self.selected_feature_index].append(self.ctrl_wdg.selected_movie_idx)
                self.locs[self.selected_feature_index].append([fc.x_loc, fc.y_loc])

                            
            # Add feature on the scene

            self.ctrl_wdg.viewer._scene.addItem(fc)
            self.ctrl_wdg.viewer._scene.addItem(fc.label)
            
            if self.ctrl_wdg.kf_method == "Regular":
                v.features_regular[t].append(fc)
                v.hide_regular[t].append(False)
                
            elif self.ctrl_wdg.kf_method == "Network":
                v.features_network[t].append(fc)
                v.hide_network[t].append(False)
                
            self.display_data()
            
            
    def display_data(self):
        if (len(self.labels) == len(self.associated_frames)) and (len(self.labels) == len(self.locs)):                
            self.features_data = {"Label": self.labels,
                   "Frames": self.associated_frames,
                   "Videos": self.associated_videos,
                   "Locations": self.locs}
            self.wdg_tree.add_feature_data(self.features_data, self.selected_feature_index)
        else:
            print("Mismatch in dimensions!")
            print(self.labels)
            print(self.associated_frames)
            print(self.locs)
            
            
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
        
        if current:
            if self.ctrl_wdg.kf_method == "Regular":
                for j,f in enumerate(v.features_regular[t]):
                    if not v.hide_regular[t][j]:
                        f.label.setVisible(True)
                        f.setVisible(True)
                            
            elif self.ctrl_wdg.kf_method == "Network":
                for j,f in enumerate(v.features_network[t]):
                    if not v.hide_network[t][j]:
                        f.label.setVisible(True)
                        f.setVisible(True)

    
    def delete_feature(self):
        t = self.ctrl_wdg.selected_thumbnail_index            
        v = self.ctrl_wdg.movie_caps[self.ctrl_wdg.selected_movie_idx]
        i = self.selected_feature_index
        print("To be deleted : "+str(i))
        
        if i != -1:
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
                idd = [m for m, x in enumerate(self.associated_frames[i]) if x == t]
                if len(idd) == 1:
                    pic_idx = idd[0]
                else:
                    idd2 = [n for n, x in enumerate(self.associated_videos[i]) if x == self.ctrl_wdg.selected_movie_idx]
                    d = list(set(idd2).intersection(idd))
                    if len(d) == 1:
                        pic_idx = d[0]
                    else:
                        print("Problem in deleting")

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
            print("Feature Index : "+str(self.selected_feature_index))
            print("Label Index : "+str(self.wdg_tree.label_index))
            self.display_data()


 
            
    
            