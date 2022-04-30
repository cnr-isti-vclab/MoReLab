from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ObjectPanel:
    def __init__(self):
        super().__init__()
        self.create_tree()
        
        
    def create_tree(self):
        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Features", "Info"])
        
    
    def add_feature_data(self, data):
        item = QTreeWidgetItem(["Feature"])