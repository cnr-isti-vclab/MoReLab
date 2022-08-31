from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ObjectPanel(QTreeWidget):
    def __init__(self, parent):
        super().__init__()
        self.setColumnCount(2)
        self.setHeaderLabels(["Features", "Info"])
        self.label_index = -1
        self.items = []
        self.tool_obj = parent
        
    
    def add_feature_data(self, data, feature_idx):
        self.clear()
        if feature_idx != -1:
            labels = data["Label"]
            frames = data["Frames"]
            videos = data["Videos"]
            locs = data["Locations"]
            self.items = []
            
            selected_label = labels[feature_idx]
            count = 0
            for i,f in enumerate(frames):
                if labels[i] != -1:
                    item = QTreeWidgetItem(["Feature "+str(labels[i])])
                    child1 = QTreeWidgetItem(["Label", str(labels[i])])
                    
                    if selected_label == labels[i]:
                        self.label_index = count
                    
                    str_vf = ""
                    str_loc = ""
                    
                    for j,ff in enumerate(f):
                        if j==0:
                            str_vf = str_vf + '('+str(videos[i][j]+1)+','+str(ff+1)+')'
                            str_loc = str_loc + '('+str(locs[i][j][0])+ ',' + str(locs[i][j][1])+')'
                        else:
                            str_vf = str_vf + ', ('+str(videos[i][j]+1)+','+str(ff+1)+')'
                            str_loc = str_loc + ', ('+str(locs[i][j][0])+ ',' + str(locs[i][j][1])+')'
                                               
                    child2 = QTreeWidgetItem(["Association", str_vf])
                    child3 = QTreeWidgetItem(["Locations", str_loc])
                    
                    item.addChild(child1)
                    item.addChild(child2)
                    item.addChild(child3)
                    count = count + 1
                    self.items.append(item)
                    
            
            self.insertTopLevelItems(0, self.items)
            self.itemClicked.connect(self.item_selected)
            
            if self.tool_obj.cross_hair:
                self.item_selected(self.items[self.label_index])
        
        
        
    def item_selected(self, selection):
        if self.tool_obj.cross_hair:
            if selection in self.items:
                self.label_index = self.items.index(selection)
                # print(type(self.label_index))
                # print(self.label_index)
                selection.setSelected(True)
                ch = selection.child(0)
                label = ch.text(1)
                self.tool_obj.selected_feature_index = int(label) - 1
                
                self.select_feature()
        else:
            selection.setSelected(False)
        
        
    
    def select_feature(self):
        t = self.tool_obj.ctrl_wdg.selected_thumbnail_index            
        v = self.tool_obj.ctrl_wdg.mv_panel.movie_caps[self.tool_obj.ctrl_wdg.mv_panel.selected_movie_idx]
        f = self.tool_obj.selected_feature_index
        
        if t!=-1 and f!=-1:
            found = False
            if self.tool_obj.ctrl_wdg.kf_method == "Regular" and len(v.hide_regular[t]) > f:
                if not v.hide_regular[t][f] and f == (int(v.features_regular[t][f].label.label) - 1):
                    found = True
                
            elif self.tool_obj.ctrl_wdg.kf_method == "Network" and len(v.hide_network[t]) > f:
                if not v.hide_network[t][f] and f == (int(v.features_network[t][f].label.label) - 1):
                    found = True
            
            if self.tool_obj.ctrl_wdg.kf_method == "Regular":
                for i,fc in enumerate(v.features_regular[t]):
                    fc.setSelected(False)
                if found:
                    v.features_regular[t][f].setSelected(True)
                    
            elif self.tool_obj.ctrl_wdg.kf_method == "Network":
                for i,fc in enumerate(v.features_network[t]):
                    fc.setSelected(False)
                if found:
                    v.features_network[t][f].setSelected(True)            
