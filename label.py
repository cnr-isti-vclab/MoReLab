from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Label(QGraphicsTextItem):
    def __init__(self, x, y, label_idx):
        super().__init__(str(label_idx))
        self.label = str(label_idx)
        self.create_label(x, y)
        
        
    def create_label(self, x, y):
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.ItemIsMovable)            
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setVisible(True)
        
            
    def hide_feature(self):
        self.setVisible(False)
        
    def get_label(self):
        return int(self.label)
        
    def mousePressEvent(self, event):
        if self.isUnderMouse():
            p = self.mapToScene(event.pos()).toPoint()
            print(p)