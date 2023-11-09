from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.spatial import distance
from scipy.optimize import minimize, least_squares
from scipy.spatial.transform import Rotation as R
from scipy import linalg
from util.util import *
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
                    fc1 = v.features_regular[t][idx1]
                    fc2 = v.features_regular[t][idx2]
                    fc3 = v.features_regular[t][idx3]
                    fc4 = v.features_regular[t][idx4]
                                                
                elif ctrl_wdg.kf_method == "Network":
                    fc1 = v.features_network[t][idx1]
                    fc2 = v.features_network[t][idx2]
                    fc3 = v.features_network[t][idx3]
                    fc4 = v.features_network[t][idx4]

                x1_transformed, x2_transformed = self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc1.x_loc), self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc2.x_loc)
                y1_transformed, y2_transformed = self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc1.y_loc), self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc2.y_loc)
                dist1 = distance.euclidean((x1_transformed, y1_transformed), (x2_transformed, y2_transformed))
                    
                x3_transformed, x4_transformed = self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc3.x_loc), self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc4.x_loc)
                y3_transformed, y4_transformed = self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc3.y_loc), self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(fc4.y_loc)
                dist2 = distance.euclidean((x3_transformed, y3_transformed), (x4_transformed, y4_transformed))

                if dist1 > 0 and dist2 > 0:
                    if self.ctrl_wdg.kf_method == "Regular":
                        v.constrained_features_regular[t].append((idx1, idx2))
                        v.constrained_features_regular[t].append((idx3, idx4))
                    elif self.ctrl_wdg.kf_method == "Network":
                        v.constrained_features_network[t].append((idx1, idx2))
                        v.constrained_features_network[t].append((idx3, idx4))
                        
                    
                else:
                    constraint_labels_different()
                    
            else:
                constraint_labels()
                    
    
        

        
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
        
        