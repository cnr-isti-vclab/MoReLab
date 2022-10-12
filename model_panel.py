from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from util.util import split_path
from util.sfm import scale_data

import numpy as np
import open3d as o3d


class ModelPanel(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setColumnCount(2)
        self.setHeaderLabels(["Models", "Info"])
        self.selected_model_path = ""
        self.model_paths = []
        self.selected_model_idx = -1
        self.vertices_data = []
        self.items = []
        self.add_model('BWR6 - Core Spray Piping.obj')
        # self.itemClicked.connect(self.select_movie)
        
        
    def add_model(self, model_path):
        self.model_paths.append(model_path)
        mesh = o3d.io.read_triangle_mesh(model_path)
        X = np.array(mesh.vertices)
        X = scale_data(50, 300, 150, 400, 0, 100, X)
        self.vertices_data.append(X)
        X_tr = np.array(mesh.triangles)
        
        model_name = split_path(model_path)
        item = QTreeWidgetItem([str(model_name)])
        item.addChild(QTreeWidgetItem(["Vertices ", str(X.shape[0])]))
        item.addChild(QTreeWidgetItem(["Triangles ", str(X_tr.shape[0])]))

        self.items.append(item)
        
        self.insertTopLevelItems(len(self.model_paths) - 1, [item])


    def deselect_models(self):
        if len(self.items) > 0:
            for i,item in enumerate(self.items):
                item.setSelected(False)
                
                
    def select_movie(self, selection):
        self.deselect_models()
        self.selected_model_idx = self.items.index(selection)
        self.selected_model_path = self.model_paths[self.selected_model_idx]   
        self.items[self.selected_model_idx].setSelected(True)
