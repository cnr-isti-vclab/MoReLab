from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from label import Label


class FeatureCrosshair(QGraphicsPixmapItem):
    def __init__(self, p, x, y, num_str, parent):
        super().__init__(p)
        self.l = 10
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setVisible(True)
        self.x_loc = x
        self.y_loc = y
        self.parent = parent
        self.label = Label(x, y, num_str, parent, self)