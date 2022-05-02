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
        self.tree.clear()
        labels = data["Label"]
        frames = data["Frames"]
        items = []
        for i,f in enumerate(frames):
            item = QTreeWidgetItem(["Feature "+str(labels[i])])
            
            child1 = QTreeWidgetItem(["Label", str(labels[i])])
            str_f = ""
            for j,ff in enumerate(f):
                if j==0:
                    str_f = str_f + str(ff)
                else:
                    str_f = str_f + ', '+ str(ff) 
            child2 = QTreeWidgetItem(["Associated Frames", str_f])
            
            item.addChild(child1)
            item.addChild(child2)
            
            items.append(item)
        self.tree.insertTopLevelItems(0, items)
        
                