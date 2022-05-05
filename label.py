from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from util.kf_dialogue import Feature_Dialogue, duplicate_dialogue, increment_dialogue

class Label(QGraphicsTextItem):
    def __init__(self, x, y, label_idx, parent, g):
        super().__init__(str(label_idx))
        self.label = str(label_idx)
        self.create_label(x, y)
        self.parent = parent
        self.g = g
        
        
    def create_label(self, x, y):
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.ItemIsMovable)            
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # self.setFlag(QGraphicsItem.ItemIsFocusable)
        self.setVisible(True)

       
    def mousePressEvent(self, event):
        p = self.mapToScene(event.pos()).toPoint()
        if event.button() == Qt.RightButton:
            dlg = Feature_Dialogue()
            if dlg.exec():
                t = self.parent.ctrl_wdg.selected_thumbnail_index
                v = self.parent.ctrl_wdg.movie_caps[self.parent.ctrl_wdg.selected_movie_idx]
                
                l = int(dlg.e2.text())                   
                duplicate = False
                
                # print(t)
                
                if self.parent.ctrl_wdg.kf_method == "Regular":
                    for text_label in v.feature_labels_regular[t]:
                        if int(text_label.label) == l:
                            duplicate = True
                            duplicate_dialogue()  

                elif self.parent.ctrl_wdg.kf_method == "Network":
                    for text_label in v.feature_labels_network[t]:
                        if int(text_label.label) == l:
                            duplicate = True
                            duplicate_dialogue()  
 
                    
                if not duplicate:
                    if l > max(self.parent.labels) + 1:
                        increment_dialogue()
                        l = max(self.parent.labels) + 1
                    last_label = self.label
                    self.label = str(l)
                    self.setPlainText(self.label)
                    
                    # print(t)
                    # print(int(last_label)-1)
                    # print(self.parent.associated_frames[int(last_label)-1])
                    if l not in self.parent.labels:
                        self.parent.selected_feature_index += 1
                        self.parent.labels.append(l)
                    else:
                        self.parent.count_ = self.parent.labels.index(l)
                        self.parent.selected_feature_index = self.parent.labels.index(l)
                        
                    if t not in self.parent.associated_frames[self.parent.count_]:
                        self.parent.associated_frames[self.parent.count_].append(t)
                        self.parent.locs[self.parent.count_].append((self.g.x_loc, self.g.y_loc))
                    else:
                        self.parent.associated_frames.append([t])
                        self.parent.locs.append([(self.g.x_loc, self.g.y_loc)])
                    
                    idx = self.parent.associated_frames[int(last_label)-1].index(t)
                    self.parent.associated_frames[int(last_label)-1].pop(idx)
                    self.parent.locs[int(last_label)-1].pop(idx)
                          
                    self.parent.display_data(v)
