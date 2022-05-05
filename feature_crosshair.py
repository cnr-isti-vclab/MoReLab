from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from label import Label


class FeatureCrosshair(QGraphicsPixmapItem):
    def __init__(self, p, x, y, num_str, parent):
        super().__init__(p)
        self.l = 10
        self.setPos(x-int(self.l/2), y-int(self.l/2))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setVisible(True)
        self.x_loc = x-int(self.l/2)
        self.y_loc = y-int(self.l/2)
        self.parent = parent
        self.label = Label(x-int(self.l/2), y-int((5*self.l)/2), num_str, parent, self)
        
     

        
        
    def mouseMoveEvent(self, event):
        # print("Moving")
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        orig_position = self.scenePos()

        updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        self.setPos(QPointF(updated_cursor_x, updated_cursor_y))
        self.label.setPos(QPointF(updated_cursor_x, updated_cursor_y-2*self.l))
        
        self.x_loc = int(updated_cursor_x)
        self.y_loc = int(updated_cursor_y)
        
        thresh = 3
        for i,loc in enumerate(self.parent.locs):
            if abs(loc[0]-self.x_loc) < thresh or abs(loc[1]-self.y_loc) < thresh:
                self.parent.selected_feature_index = i        
                self.parent.locs[i] = (self.x_loc, self.y_loc)
        
        
        t = self.parent.ctrl_wdg.selected_thumbnail_index
        v = self.parent.ctrl_wdg.movie_caps[self.parent.ctrl_wdg.selected_movie_idx]
        
    
        self.parent.display_data(v)
        

            

            
    
        
    
