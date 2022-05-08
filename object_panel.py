from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ObjectPanel(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(2)
        self.setHeaderLabels(["Features", "Info"])
        
    
    def add_feature_data(self, data, deleted):
        self.clear()
        labels = data["Label"]
        frames = data["Frames"]
        locs = data["Locations"]
        items = []
        # print(deleted)
        # print(labels)
        # print("-----------")
        for i,f in enumerate(frames):
            if labels[i] not in deleted:
                item = QTreeWidgetItem(["Feature "+str(labels[i])])
                child1 = QTreeWidgetItem(["Label", str(labels[i])])
                str_f = ""
                str_loc = ""
                for j,ff in enumerate(f):
                    if j==0:
                        str_f = str_f + str(ff)
                        str_loc = str_loc + '('+str(locs[i][j][0])+ ',' + str(locs[i][j][1])+')'
                    else:
                        str_f = str_f + ', '+ str(ff)
                        str_loc = str_loc + ', ('+str(locs[i][j][0])+ ',' + str(locs[i][j][1])+')'
                                       
                child2 = QTreeWidgetItem(["Associated Frames", str_f])
                child3 = QTreeWidgetItem(["Locations", str_loc])
                
                item.addChild(child1)
                item.addChild(child2)
                item.addChild(child3)
                
                items.append(item)
        self.insertTopLevelItems(0, items)
        
        
        
                