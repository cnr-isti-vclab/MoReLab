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
        
        labels = data["Label"]
        frames = data["Frames"]
        videos = data["Videos"]
        locs = data["Locations"]
        self.items = []
        
        selected_label = labels[feature_idx]
        print("Treeeeeeeeee")
        print(labels)
        print(self.label_index)
        print(feature_idx)

        # print(deleted)
        # print(labels)
        # print("-----------")
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
        
        print(count)
        print(self.label_index)
        self.insertTopLevelItems(0, self.items)
        self.itemClicked.connect(self.item_selected)
        
        
        self.items[self.label_index].setSelected(True)
        
        
        
    def item_selected(self, selection):
        self.label_index = self.items.index(selection)
        selection.setSelected(True)
        ch = selection.child(0)
        label = ch.text(1)
        self.tool_obj.selected_feature_index = int(label) - 1
        
        
        
        
                