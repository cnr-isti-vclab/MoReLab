from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Ellipse(QGraphicsEllipseItem):
    def __init__(self, x,y,w,h):
        super().__init__(0,0,w,h)
        self.create_ellipse(x,y)
        self.associated_frames = []
    
        
    def create_ellipse(self, x, y):
        self.setPos(x, y)
        self.setBrush(Qt.red)
        self.setFlag(QGraphicsItem.ItemIsMovable)            
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setVisible(True)
        
    
    def hide_feature(self):
        self.setVisible(False)
        
        
 

        
        
    
