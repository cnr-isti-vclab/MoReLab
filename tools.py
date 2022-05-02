from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ellipse import Ellipse
from label import Label
import numpy as np
from object_panel import ObjectPanel


class Tools(QObject):
    
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        # print(self.ctrl_wdg.selected_movie_idx)
        self.wdg_tree = ObjectPanel()
        self.add_tool_icons()
        self.cross_hair = False
        self.labels = []
        self.associated_frames = [[]]
        self.selected_feature_index =-1
        self.count_ = 0
        

    def add_tool_icons(self):
        self.mv_tool = QAction(QIcon("./icons/cursor.png"),"&Move",self)
        self.mv_tool.triggered.connect(self.move_tool)
        self.ft_tool = QAction(QIcon("./icons/crosshair.png"),"&Feature Point",self)
        self.ft_tool.triggered.connect(self.feature_tool)

        
    def move_tool(self):
        # print('move')
        self.cross_hair = False
        self.hide_features(False)
        self.wdg_tree.tree.clear()
        self.ctrl_wdg.viewer.setScrolDragMode()
        self.ctrl_wdg.setCursor(QCursor(Qt.ArrowCursor))
        
    def feature_tool(self):
        # print('feature')
        self.ctrl_wdg.setCursor(QCursor(Qt.CrossCursor))
        self.ctrl_wdg.viewer.setNoDragMode()
        self.cross_hair = True
        self.hide_features(True)
        
    def refresh(self):
        self.labels = []
        self.associated_frames = [[]]
        self.selected_feature_index =-1
        self.count_ = 0
        self.wdg_tree.tree.clear()

    
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
                
                
                
            if label not in self.labels:
                self.selected_feature_index += 1
                self.labels.append(label)
            else:
                self.count_ = self.labels.index(label)
                self.selected_feature_index = self.labels.index(label)
                
                
            if t not in self.associated_frames[self.count_]:
                self.associated_frames[self.count_].append(t)
            else:
                self.associated_frames.append([t])
                

            # print(self.count_)
            # print(self.selected_feature_index)
            # print(self.associated_frames)
            
                
            l = 10
            x = p.x() - int(l/2)
            y = p.y() - int(l/2)
            
            ellipse = Ellipse(x, y, l, l)            
            text = Label(x-int(l/2), y-2*l, label, self)

            self.ctrl_wdg.viewer._scene.addItem(ellipse)
            self.ctrl_wdg.viewer._scene.addItem(text)
            
            if self.ctrl_wdg.kf_method == "Regular":
                v.features_regular[t].append(ellipse)
                v.feature_labels_regular[t].append(text)
                
            elif self.ctrl_wdg.kf_method == "Network":
                v.features_network[t].append(ellipse)
                v.feature_labels_network[t].append(text)
                
            if len(self.labels) == len(self.associated_frames):                
                v.features_data = {"Label": self.labels,
                       "Frames": self.associated_frames}
                self.wdg_tree.add_feature_data(v.features_data)
            else:
                print("Mismatch in dimensions!")   
            
            
    def hide_features(self, current=True):
        t = self.ctrl_wdg.selected_thumbnail_index            
        v = self.ctrl_wdg.movie_caps[self.ctrl_wdg.selected_movie_idx]
        
        if self.ctrl_wdg.kf_method == "Regular":
            for i in range(v.n_objects_kf_regular.shape[0]):
                for j,f in enumerate(v.features_regular[i]):
                    f.setVisible(False)
                    v.feature_labels_regular[i][j].setVisible(False)
        elif self.ctrl_wdg.kf_method == "Network":
            for i in range(v.n_objects_kf_network.shape[0]):
                for j,f in enumerate(v.features_network[i]):
                    f.setVisible(False)
                    v.feature_labels_network[i][j].setVisible(False)
                    
        if current:
            if self.ctrl_wdg.kf_method == "Regular":
                for j,f in enumerate(v.features_regular[t]):
                    f.setVisible(True)
                    v.feature_labels_regular[t][j].setVisible(True)
            elif self.ctrl_wdg.kf_method == "Network":
                for j,f in enumerate(v.features_network[t]):
                    f.setVisible(True)
                    v.feature_labels_network[t][j].setVisible(True)

    
    def delete_feature(self, i):
        if len(self.features) > i:
            self.ctrl_wdg.viewer._scene.removeItem(self.features[i])
            self.features.pop(i)
            self.ctrl_wdg.viewer._scene.removeItem(self.feature_labels[i])
            self.feature_labels.pop(i)
        
 
            
    
            