from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from util.kf_dialogue import Feature_Dialogue, duplicate_dialogue, increment_dialogue

class Label(QGraphicsTextItem):
    def __init__(self, x, y, label_idx, tool_obj, parent):
        super().__init__(str(label_idx))
        self.label = str(label_idx)
        self.create_label(x, y)
        self.tool_obj = tool_obj
        self.parent = parent
        
        
    def create_label(self, x, y):
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.ItemIsMovable)            
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # self.setFlag(QGraphicsItem.ItemIsFocusable)
        self.setVisible(True)

       
    def mousePressEvent(self, event):
        p = self.mapToScene(event.pos()).toPoint()
        
        if event.button() == Qt.RightButton:
            self.tool_obj.selected_feature_index = int(self.label) - 1 
            dlg = Feature_Dialogue()
            if dlg.exec():
                t = self.tool_obj.ctrl_wdg.selected_thumbnail_index
                v = self.tool_obj.ctrl_wdg.movie_caps[self.tool_obj.ctrl_wdg.selected_movie_idx]
                
                l = int(dlg.e2.text())                   
                duplicate = False
                
                # print(t)
                
                if self.tool_obj.ctrl_wdg.kf_method == "Regular":
                    for f in v.features_regular[t]:
                        if int(f.label.label) == l:
                            duplicate = True
                            duplicate_dialogue()  

                elif self.tool_obj.ctrl_wdg.kf_method == "Network":
                    for f in v.features_network[t]:
                        if int(f.label.label) == l:
                            duplicate = True
                            duplicate_dialogue()  
 
                    
                if not duplicate:
                    if l > max(self.tool_obj.labels) + 1:
                        increment_dialogue()
                        l = max(self.tool_obj.labels) + 1
                    last_label = self.label
                    self.label = str(l)
                    self.setPlainText(self.label)
                    
                    # print(t)
                    # print(int(last_label)-1)
                    # print(self.parent.associated_frames[int(last_label)-1])
                    if l not in self.tool_obj.labels:
                        self.tool_obj.selected_feature_index += 1
                        self.tool_obj.labels.append(l)
                    else:
                        self.tool_obj.count_ = self.parent.labels.index(l)
                        self.tool_obj.selected_feature_index = self.tool_obj.labels.index(l)
                        
                    if t not in self.tool_obj.associated_frames[self.tool_obj.count_]:
                        self.tool_obj.associated_frames[self.tool_obj.count_].append(t)
                        self.tool_obj.associated_videos[self.tool_obj.count_].append(self.tool_obj.ctrl_wdg.selected_movie_idx)
                        self.tool_obj.locs[self.tool_obj.count_].append([self.parent.x_loc, self.parent.y_loc])
                    else:
                        self.tool_obj.associated_frames.append([t])
                        self.tool_obj.associated_videos.append([self.tool_obj.ctrl_wdg.selected_movie_idx])
                        self.tool_obj.locs.append([[self.parent.x_loc, self.parent.y_loc]])
                    
                    idx = self.tool_obj.associated_frames[int(last_label)-1].index(t)
                    self.tool_obj.associated_frames[int(last_label)-1].pop(idx)
                    self.tool_obj.associated_videos[int(last_label)-1].pop(idx)
                    self.tool_obj.locs[int(last_label)-1].pop(idx)
                          
                    self.tool_obj.display_data()
