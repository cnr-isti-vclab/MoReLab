from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ObjectPanel(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(2)
        self.setHeaderLabels(["Features", "Info"])
        self.label_index = -1
        self.items = []
        
    
    def add_feature_data(self, data, feature_idx):
        self.clear()
        print(feature_idx)
        labels = data["Label"]
        frames = data["Frames"]
        videos = data["Videos"]
        locs = data["Locations"]
        self.items = []
        # print(deleted)
        # print(labels)
        # print("-----------")
        for i,f in enumerate(frames):
            if labels[i] != -1:
                item = QTreeWidgetItem(["Feature "+str(labels[i])])
                child1 = QTreeWidgetItem(["Label", str(labels[i])])
                str_vf = ""
                str_loc = ""
                
                for j,ff in enumerate(f):
                    if ff != -1:
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
                
                items.append(item)
        self.insertTopLevelItems(0, items)
        
        self.itemClicked.connect(self.item_selected)
        self.items[feature_idx].setSelected(True)
        self.label_index = int(self.items[feature_idx].child(0).text(1)) - 1
        
        
        
    def item_selected(self, selection):
        ch = selection.child(0)
        ch.setSelected(True)
        label = ch.text(1)
        self.label_index = int(label) - 1
        
        
        
        
                