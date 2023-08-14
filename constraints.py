from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.spatial import distance
from scipy.optimize import minimize, least_squares
from scipy.spatial.transform import Rotation as R
from scipy import linalg
import copy

import numpy as np
import math


class Constraint_Tool(QObject):
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        
        
    def get_distances(self):
        t = self.ctrl_wdg.selected_thumbnail_index            
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        
        self.create_constraint_panel()
        
        if self.constraint_dialog.exec():
            label1 = int(self.e1.text())
            label2 = int(self.e2.text())
            label3 = int(self.e3.text())
            label4 = int(self.e4.text())
            
            found1, idx1 = self.ctrl_wdg.gl_viewer.obj.feature_panel.get_feature_index(label1, t)
            found2, idx2 = self.ctrl_wdg.gl_viewer.obj.feature_panel.get_feature_index(label2, t)
            found3, idx3 = self.ctrl_wdg.gl_viewer.obj.feature_panel.get_feature_index(label3, t)
            found4, idx4 = self.ctrl_wdg.gl_viewer.obj.feature_panel.get_feature_index(label4, t)
            
            if found1 and found2 and found3 and found4:
                if self.ctrl_wdg.kf_method == "Regular":
                    if len(v.features_regular) > 0:
                        fc1 = v.features_regular[t][idx1]
                        fc2 = v.features_regular[t][idx2]
                        x_diff_1 = self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc1.x_loc) - self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc2.x_loc)
                        y_diff_1 = self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_y(fc1.y_loc) - self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_y(fc2.y_loc)
                        dist1 = distance.euclidean((self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc1.x_loc), self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_y(fc1.y_loc)), (self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc2.x_loc), self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_y(fc2.y_loc)))

                        fc3 = v.features_regular[t][idx3]
                        fc4 = v.features_regular[t][idx4]
                        x_diff_2 = self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc3.x_loc) - self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc4.x_loc)
                        y_diff_2 = self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_y(fc3.y_loc) - self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_y(fc4.y_loc)
                        dist2 = distance.euclidean((self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc3.x_loc), self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_y(fc3.y_loc)), (self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc4.x_loc), self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_y(fc4.y_loc)))


                        # print(x_diff_1, y_diff_1)
                        # print(x_diff_2, y_diff_2)
                        
                        # print(dist1, dist2)

                        if dist1 > 0 and dist2 > 0:

                            v.constrained_features_regular[t].append((idx1, idx2))
                            v.constrained_features_regular[t].append((idx3, idx4))
                            
                            print(v.constrained_features_regular[t])
                            
                        else:
                            print("Either distance is zero")
    
    
                elif ctrl_wdg.kf_method == "Network":
                    if len(v.features_network) > 0:
                        for i, fc in enumerate(v.features_network[t]):
                            if not v.hide_network[t][i]:
                                d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                                if d < self.dist_thresh:
                                    self.parent_viewer.obj.feature_panel.select_feature(i, fc.label)
                                    self.move_feature_bool = True
                                    
            else:
                print("Please make sure that all features are present on the image.")
                    
    
        

        
    def create_constraint_panel(self):
        self.constraint_dialog = QDialog()
        self.constraint_dialog.setWindowTitle("Constraints Dialogue")

        QBtn = QDialogButtonBox.Ok

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.constraint_dialog.accept)

        label = QLabel("Enter feature labels for constraints : ")

        self.e1 = QLineEdit("0")
        self.e1.setValidator(QIntValidator())
        self.e1.setMaxLength(10)
        self.e1.setFont(QFont("Arial", 20))
        
        self.e2 = QLineEdit("0")
        self.e2.setValidator(QIntValidator())
        self.e2.setMaxLength(10)
        self.e2.setFont(QFont("Arial", 20))
        
        self.e3 = QLineEdit("0")
        self.e3.setValidator(QIntValidator())
        self.e3.setMaxLength(10)
        self.e3.setFont(QFont("Arial", 20))
        
        self.e4 = QLineEdit("0")
        self.e4.setValidator(QIntValidator())
        self.e4.setMaxLength(10)
        self.e4.setFont(QFont("Arial", 20))

        cal_layout = QVBoxLayout()
        cal_layout.addWidget(label)
        cal_layout.addWidget(self.e1)
        cal_layout.addWidget(self.e2)
        cal_layout.addWidget(self.e3)
        cal_layout.addWidget(self.e4)
        cal_layout.addWidget(buttonBox)
        self.constraint_dialog.setLayout(cal_layout)
        
        