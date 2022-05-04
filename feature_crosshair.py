from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class FeatureCrosshair(QGraphicsPixmapItem):
    def __init__(self, p, x, y):
        super().__init__(p)
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setVisible(True)
        
        
        def mousePressEvent(self, event):
            if self.isUnderMouse():
                p = self.mapToScene(event.pos()).toPoint()
                print(p)
        
        
 

        
        
    
