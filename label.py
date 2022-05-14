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


    def set_visibility(self, v, t, f, visibility):
        if self.tool_obj.ctrl_wdg.kf_method == "Regular":
            v.hide_regular[t][f] = visibility
        elif self.tool_obj.ctrl_wdg.kf_method == "Network":
            v.hide_network[t][f] = visibility

       
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.tool_obj.selected_feature_index = int(self.label) - 1 
            dlg = Feature_Dialogue()
            if dlg.exec():
                t = self.tool_obj.ctrl_wdg.selected_thumbnail_index
                v = self.tool_obj.ctrl_wdg.movie_caps[self.tool_obj.ctrl_wdg.selected_movie_idx]
                
                l = int(dlg.e2.text())                   
                duplicate = False
                
                # print("Label : "+str(l))
                # print(self.tool_obj.labels)
                # print(self.tool_obj.associated_frames)
                # print()
                
                if self.tool_obj.ctrl_wdg.kf_method == "Regular":
                    n_current = v.n_objects_kf_regular[t]
                    for m, f in enumerate(v.features_regular[t]):
                        if int(f.label.label) == l and not v.hide_regular[t][m]:
                            duplicate = True
                            duplicate_dialogue()  

                elif self.tool_obj.ctrl_wdg.kf_method == "Network":
                    n_current = v.n_objects_kf_network[t]
                    for m, f in enumerate(v.features_network[t]):
                        if int(f.label.label) == l and not v.hide_network[t][m]:
                            duplicate = True
                            duplicate_dialogue()
                    
                if not duplicate:
                    last_label = self.label
                    # print("Last label : "+str(last_label))
                    self.set_visibility(v, t, int(last_label)-1, True)
                    
                    
                    # Add new Label
                    
                    if l > n_current:
                        if l > max(self.tool_obj.labels) + 1:
                            increment_dialogue()
                            l = max(self.tool_obj.labels) + 1  
                            
                        self.setVisible(False)
                        self.parent.setVisible(False)
                        
                        for idxx in range(n_current, l):
                            self.tool_obj.add_feature(self.parent.x_loc+int(self.parent.l/2), self.parent.y_loc+int(self.parent.l/2))
                            if idxx < l-1:
                                self.tool_obj.delete_feature()
                    else:
                        if self.tool_obj.labels[l-1] == -1:
                            self.tool_obj.labels[l-1] = l
                            self.tool_obj.associated_frames[l-1] = [t]
                            self.tool_obj.associated_videos[l-1] = [self.tool_obj.ctrl_wdg.selected_movie_idx]
                            self.tool_obj.locs[l-1] = [[self.parent.x_loc, self.parent.y_loc]]
                        else:                                
                            self.tool_obj.associated_frames[l-1].append(t)
                            self.tool_obj.associated_videos[l-1].append(self.tool_obj.ctrl_wdg.selected_movie_idx)
                            self.tool_obj.locs[l-1].append([self.parent.x_loc, self.parent.y_loc])

                    
                    self.tool_obj.selected_feature_index = l-1
                    self.set_visibility(v, t, self.tool_obj.selected_feature_index, False)
                                        
                    self.label = str(l)    
                    self.setPlainText(self.label)
                    
                    # Remove previous label
                    
                    if len(self.tool_obj.associated_frames[int(last_label)-1]) == 1:
                        self.tool_obj.labels[int(last_label)-1] = -1
                        self.tool_obj.associated_frames[int(last_label)-1] = [-1]
                        self.tool_obj.associated_videos[int(last_label)-1] = [-1]
                        self.tool_obj.locs[int(last_label)-1] = [[-1, -1]]
                        
                    else:
                        idx = self.tool_obj.find_idx(int(last_label)-1, t)
                        self.tool_obj.associated_frames[int(last_label)-1].pop(idx)
                        self.tool_obj.associated_videos[int(last_label)-1].pop(idx)
                        self.tool_obj.locs[int(last_label)-1].pop(idx)
    
                    # print("Label : "+str(l))
                    # print(self.tool_obj.labels)
                    # print(self.tool_obj.associated_frames)
                    # print()                    
    
                    self.tool_obj.display_data()
