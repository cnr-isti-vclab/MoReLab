from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ObjectPanel(QTreeWidget):
    def __init__(self, parent):
        super().__init__()
        self.setColumnCount(2)
        # self.setFixedSize(500, 800)
        self.setHeaderLabels(["Features", "Info"])
        self.label_index = -1
        self.items = []
        self.tool_obj = parent
        self.setMinimumSize(self.tool_obj.ctrl_wdg.monitor_width*0.2, self.tool_obj.ctrl_wdg.monitor_height*0.75)
        self.factor_x = 1
        self.factor_y = 1
        
    
    def add_feature_data(self, data):
        self.clear()
        # if feature_idx != -1:
        labels = data["Label"]
        frames = data["Frames"]
        videos = data["Videos"]
        locs = data["Locations"]
        self.items = []
        
        # selected_label = labels[feature_idx]
        count = 0
        for i,f in enumerate(frames):
            if labels[i] != -1:
                item = QTreeWidgetItem(["Feature "+str(labels[i])])
                child1 = QTreeWidgetItem(["Label", str(labels[i])])
                
                # if selected_label == labels[i]:
                #     self.label_index = count
                
                str_vf = ""
                str_loc = ""
                
                for j,ff in enumerate(f):
                    if j==0:
                        str_vf = str_vf + '('+str(videos[i][j]+1)+','+str(ff+1)+')'
                        str_loc = str_loc + '('+str(self.transform_x(locs[i][j][0]))+ ',' + str(self.transform_y(locs[i][j][1]))+')'
                    else:
                        str_vf = str_vf + ', ('+str(videos[i][j]+1)+','+str(ff+1)+')'
                        str_loc = str_loc + ', ('+str(self.transform_x(locs[i][j][0]))+ ',' + str(self.transform_y(locs[i][j][1]))+')'
                                           
                child2 = QTreeWidgetItem(["Association", str_vf])
                child3 = QTreeWidgetItem(["Locations", str_loc])
                
                item.addChild(child1)
                item.addChild(child2)
                item.addChild(child3)
                count = count + 1
                self.items.append(item)
                
            
        self.insertTopLevelItems(0, self.items)
        self.itemClicked.connect(self.item_selected)
        if self.tool_obj.cross_hair and self.tool_obj.selected_feature_index != -1:
            self.select_feature(self.tool_obj.selected_feature_index)
        else:
            self.deselect_features()


    def deselect_features(self):
        if len(self.items) > 0:
            for i,item in enumerate(self.items):
                item.setSelected(False)        
        
        
    def item_selected(self, selection):
        # print(self.tool_obj.cross_hair)
        if self.tool_obj.cross_hair:
            # print(len(self.items))
            if selection in self.items:
                self.label_index = self.items.index(selection)
                self.deselect_features()
                selection.setSelected(True)
                ch = selection.child(0)
                label = ch.text(1)
                self.tool_obj.selected_feature_index = int(label) - 1
                print(self.tool_obj.selected_feature_index)
        else:
            selection.setSelected(False)
        
    def select_feature(self, i):
        self.deselect_features()
        if len(self.items) > 0:
            self.items[i].setSelected(True)
            

                    
                    
    def wdg_to_img_space(self):
        w1 = self.tool_obj.ctrl_wdg.gl_viewer.w1
        w2 = self.tool_obj.ctrl_wdg.gl_viewer.w2
        h1 = self.tool_obj.ctrl_wdg.gl_viewer.h1
        h2 = self.tool_obj.ctrl_wdg.gl_viewer.h2
        v = self.tool_obj.ctrl_wdg.mv_panel.movie_caps[self.tool_obj.ctrl_wdg.mv_panel.selected_movie_idx]
        self.factor_x = v.width/(w2-w1)
        self.factor_y = v.height/(h2-h1)

    def transform_x(self, x):
        x2 = (x - self.tool_obj.ctrl_wdg.gl_viewer.w1)*self.factor_x
        # x2 = x
        return int(x2)        

    def transform_y(self, y):
        y2 = (y - self.tool_obj.ctrl_wdg.gl_viewer.h1)*self.factor_y
        # y2 = y
        return int(y2)
    
    def inv_trans_x(self, x):
        x2 = self.tool_obj.ctrl_wdg.gl_viewer.w1 + (x/self.factor_x)
        # x2 = x
        return int(x2)        

    def inv_trans_y(self, y):
        y2 = self.tool_obj.ctrl_wdg.gl_viewer.h1 + (y/self.factor_y)
        # y2 = y
        return int(y2)
    
    
    
    # def copy_features(self):
        

