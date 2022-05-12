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
        if event.button() == Qt.RightButton:
            self.tool_obj.selected_feature_index = int(self.label) - 1 
            dlg = Feature_Dialogue()
            if dlg.exec():
                t = self.tool_obj.ctrl_wdg.selected_thumbnail_index
                v = self.tool_obj.ctrl_wdg.movie_caps[self.tool_obj.ctrl_wdg.selected_movie_idx]
                
                l = int(dlg.e2.text())                   
                duplicate = False
                
                print("Label : "+str(l))
                print(self.tool_obj.labels)
                print(self.tool_obj.associated_frames)
                print()
                
                if self.tool_obj.ctrl_wdg.kf_method == "Regular":
                    for m, f in enumerate(v.features_regular[t]):
                        if int(f.label.label) == l and not v.hide_regular[t][m]:
                            duplicate = True
                            duplicate_dialogue()  

                elif self.tool_obj.ctrl_wdg.kf_method == "Network":
                    for m, f in enumerate(v.features_network[t]):
                        if int(f.label.label) == l and not v.hide_network[t][m]:
                            duplicate = True
                            duplicate_dialogue()
                    
                if not duplicate:
                    last_label = self.label
                    print("Last label : "+str(last_label))

                    if l > max(self.tool_obj.labels) + 1:
                        increment_dialogue()
                        l = max(self.tool_obj.labels) + 1
                        
                        self.tool_obj.selected_feature_index += 1
                        self.tool_obj.labels.append(l)
                        self.tool_obj.associated_frames.append([t])
                        self.tool_obj.associated_videos.append([self.tool_obj.ctrl_wdg.selected_movie_idx])
                        self.tool_obj.locs.append([[self.parent.x_loc, self.parent.y_loc]])
                        
                        
                    else:
                        if self.tool_obj.ctrl_wdg.kf_method == "Regular":
                            if v.hide_regular[t][l-1]:
                                self.tool_obj.selected_feature_index = l-1
                                v.hide_regular[t][l-1] = False
                        
                        elif self.tool_obj.ctrl_wdg.kf_method == "Network":
                            if v.hide_network[t][l-1]:
                                self.tool_obj.selected_feature_index = l-1
                                v.hide_network[t][l-1] = False
                        
                        if self.tool_obj.labels[l-1] == -1:
                            self.tool_obj.labels[l-1] = l
                            self.tool_obj.associated_frames[l-1] = [t]
                            self.tool_obj.associated_videos[l-1] = [self.tool_obj.ctrl_wdg.selected_movie_idx]
                            self.tool_obj.locs[l-1] = [[self.parent.x_loc, self.parent.y_loc]]
                            
                        else:                                
                            self.tool_obj.associated_frames[self.tool_obj.selected_feature_index].append(t)
                            self.tool_obj.associated_videos[self.tool_obj.selected_feature_index].append(self.tool_obj.ctrl_wdg.selected_movie_idx)
                            self.tool_obj.locs[self.tool_obj.selected_feature_index].append([self.parent.x_loc, self.parent.y_loc])

                    self.label = str(l)    
                    self.setPlainText(self.label)
                    
                    
                    if len(self.tool_obj.associated_frames[int(last_label)-1]) == 1:
                        self.tool_obj.labels[int(last_label)-1] = -1
                        self.tool_obj.associated_frames[int(last_label)-1] = [-1]
                        self.tool_obj.associated_videos[int(last_label)-1] = [-1]
                        self.tool_obj.locs[int(last_label)-1] = [-1]
                        
                    else:
                        idx = self.tool_obj.associated_frames[int(last_label)-1].index(t)
                        self.tool_obj.associated_frames[int(last_label)-1].pop(idx)
                        self.tool_obj.associated_videos[int(last_label)-1].pop(idx)
                        self.tool_obj.locs[int(last_label)-1].pop(idx)

                    print("Label : "+str(l))
                    print(self.tool_obj.labels)
                    print(self.tool_obj.associated_frames)
                    print()                    
    
                    self.tool_obj.display_data()
