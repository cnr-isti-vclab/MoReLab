from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class QuadPanel(QTreeWidget):
    def __init__(self, parent):
        super().__init__()
        self.setColumnCount(2)
        self.setHeaderLabels(["Quad", "Info"])
        self.selected_quad_idx = -1
        self.parent = parent
        self.items = []
        self.itemClicked.connect(self.select_quad)
    
    
    
    def add_quad(self, occ, num_quad):
        item = QTreeWidgetItem(["Quad # "+str(num_quad)])
        item.addChild(QTreeWidgetItem(["Associated features", str(occ[0]+1)+", "+str(occ[1]+1)+", "+str(occ[2]+1)+", "+str(occ[3]+1)]))
        self.items.append(item)
        self.insertTopLevelItem(num_quad - 1, item)
        
    
    def deselect_quads(self):
        if len(self.items) > 0:
            for i,item in enumerate(self.items):
                item.setSelected(False)
                
                
    def select_quad(self, selection):
        if selection in self.items:
            self.deselect_quads()
            self.selected_quad_idx = self.items.index(selection)
            # print("selected Quad # "+str(self.selected_quad_idx))
            self.items[self.selected_quad_idx].setSelected(True)
            
