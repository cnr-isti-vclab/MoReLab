from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from collections import Counter


class FeaturePanel(QTreeWidget):
    def __init__(self, parent):
        super().__init__()
        self.setColumnCount(2)
        self.setHeaderLabels(["Features", "Info"])
        self.selected_feature_idx = -1
        self.ctrl_wdg = parent
        self.items = []
        self.setMinimumSize(self.ctrl_wdg.monitor_width*0.2, self.ctrl_wdg.monitor_height*0.67)
        self.itemClicked.connect(self.select_feature_child)
        self.factor_x = 1
        self.factor_y = 1
        self.labels = []
        self.frames = []
        self.Xs = []
        self.Ys = []
        self.selected_feature_group = []


    def display_data(self):
        # print("Movie : "+str(self.ctrl_wdg.mv_panel.selected_movie_idx))
        if self.ctrl_wdg.mv_panel.selected_movie_idx != -1:
            t = self.ctrl_wdg.selected_thumbnail_index
            m_idx = self.ctrl_wdg.mv_panel.selected_movie_idx
            v = self.ctrl_wdg.mv_panel.movie_caps[m_idx]
            self.clear()
            self.items = []
            self.labels = []
            tmp2, tmp3 = [], []
            
            
            if self.ctrl_wdg.kf_method == "Regular":
                for i,hr in enumerate(v.hide_regular):
                    for j,hide in enumerate(hr):
                        fc = v.features_regular[i][j]
                        if not hide:
                            tmp2.append(i)
                            tmp3.append(int(fc.label))

                        
            elif self.ctrl_wdg.kf_method == "Network":
                for i,hr in enumerate(v.hide_network):
                    for j,hide in enumerate(hr):
                        fc = v.features_network[i][j]
                        if not hide:
                            tmp2.append(i)
                            tmp3.append(int(fc.label))
                            
            if len(tmp2) > 0:         
                final_img_indices_set =set(tmp2)
                final_img_indices = sorted(final_img_indices_set)
                
                all_labels_set = set(tmp3)            
                all_labels = sorted(all_labels_set)
                
                for i, label in enumerate(all_labels):
                    tmp6, tmp7 = [], []
                    self.labels.append(label)
                    for j, img_idx in enumerate(final_img_indices):
                        found, idx = self.get_feature_index(label, img_idx)
                        if found:
                            tmp6.append(img_idx + 1) # +1 is to get image number instead of index
                            
                            if self.ctrl_wdg.kf_method == "Regular":
                                tmp7.append([self.transform_x(v.features_regular[img_idx][idx].x_loc), self.transform_y(v.features_regular[img_idx][idx].y_loc)])
    
                            elif self.ctrl_wdg.kf_method == "Network":
                                tmp7.append([self.transform_x(v.features_network[img_idx][idx].x_loc), self.transform_y(v.features_network[img_idx][idx].y_loc)])
       
    
                    item = QTreeWidgetItem(["Feature "+str(label)])
                    child1 = QTreeWidgetItem(["Label", str(label)])
                    str_vf = ""
                    str_loc = ""
    
                    for h,ff in enumerate(tmp6):
                        if h==0:
                            str_vf = str_vf + str(ff)
                            str_loc = str_loc + '('+str(tmp7[h][0])+ ',' + str(tmp7[h][1])+')'
                        else:
                            str_vf = str_vf + ', ' +str(ff)
                            str_loc = str_loc + ', ('+str(tmp7[h][0])+ ',' + str(tmp7[h][0])+')'
    
    
                    child2 = QTreeWidgetItem(["Images", str_vf])
                    child3 = QTreeWidgetItem(["Location", str_loc])
                    item.addChild(child1)
                    item.addChild(child2)
                    item.addChild(child3)
                    self.items.append(item)
                    
                self.insertTopLevelItems(0, self.items)
                self.itemClicked.connect(self.select_feature_child)
                
                if self.ctrl_wdg.ui.cross_hair and self.selected_feature_idx != -1:
                    hide, label = self.get_feature_label(self.selected_feature_idx, t)
                    if not hide:
                        tree_idx = self.find_tree_idx(label)
                        if tree_idx != -1:
                            self.items[tree_idx].setSelected(True)
                else:
                    self.deselect_features()


    def deselect_features(self):
        if len(self.items) > 0:
            for i,item in enumerate(self.items):
                item.setSelected(False)
                        
                    
    def select_feature_child(self, selection):
        if selection in self.items:
            self.deselect_features()
            if self.ctrl_wdg.ui.cross_hair:
                ch = selection.child(0)
                label = int(ch.text(1))
                found, idx = self.get_feature_index(label, self.ctrl_wdg.selected_thumbnail_index)
                if found:
                    self.select_feature(idx, label)
                else:
                    self.deselect_features()
                    self.selected_feature_idx = -1
                

    def select_feature(self, feature_idx, feature_label): # assuming that selected feature_idx has already been set
        if feature_idx != -1 and len(self.items) > 0 and self.ctrl_wdg.ui.cross_hair:
            self.deselect_features()
            self.selected_feature_idx = feature_idx
            tree_idx = self.find_tree_idx(feature_label)
            if tree_idx != -1:
                self.items[tree_idx].setSelected(True)
            
            
    def find_tree_idx(self, query_label):         # query_label must be integer
        idx = -1
        for i, l in enumerate(self.labels):     # labels are in integers
            if query_label == l:
                idx = i

        return idx          



    def wdg_to_img_space(self):
        w1 = self.ctrl_wdg.gl_viewer.util_.w1
        w2 = self.ctrl_wdg.gl_viewer.util_.w2
        h1 = self.ctrl_wdg.gl_viewer.util_.h1
        h2 = self.ctrl_wdg.gl_viewer.util_.h2
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        self.factor_x = v.width/(w2-w1)
        self.factor_y = v.height/(h2-h1)

    def transform_x(self, x):
        x2 = (x - self.ctrl_wdg.gl_viewer.util_.w1)*self.factor_x
        # x2 = x
        return int(x2)        

    def transform_y(self, y):
        y2 = (y - self.ctrl_wdg.gl_viewer.util_.h1)*self.factor_y
        # y2 = y
        return int(y2)
    
    def inv_trans_x(self, x):
        x2 = self.ctrl_wdg.gl_viewer.util_.w1 + (x/self.factor_x)
        # x2 = x
        return int(x2)        

    def inv_trans_y(self, y):
        y2 = self.ctrl_wdg.gl_viewer.util_.h1 + (y/self.factor_y)
        # y2 = y
        return int(y2)


    def find_unique_elements(self, input_list):
        unique_list = list(Counter(input_list).keys())
        count_list = list(Counter(input_list).values())

        return count_list, unique_list

    def get_feature_index(self, label_int, img_idx):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = img_idx
        found = False
        idx = -1
        if self.ctrl_wdg.kf_method == "Regular" and len(v.features_regular) > 0:
            for i, fc in enumerate(v.features_regular[t]):
                if not v.hide_regular[t][i] and not found:
                    if int(v.features_regular[t][i].label) == label_int:
                        found = True
                        idx = i

        elif self.ctrl_wdg.kf_method == "Network" and len(v.features_network) > 0:
            for i, fc in enumerate(v.features_network[t]):
                if not v.hide_network[t][i] and not found:
                    if int(v.features_network[t][i].label) == label_int:
                        found = True
                        idx = i

        return found, idx
    
    def get_feature_label(self, ft_idx, img_idx):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = img_idx
        hide = True
        label = -1
        if self.ctrl_wdg.kf_method == "Regular" and len(v.features_regular) > 0:
            if len(v.features_regular[t]) > 0:
                label = v.features_regular[t][ft_idx]
                hide = v.hide_regular[t][ft_idx]

        elif self.ctrl_wdg.kf_method == "Network" and len(v.features_network) > 0:
            if len(v.features_network[t]) > 0:
                label = v.features_network[t][ft_idx]
                hide = v.hide_network[t][ft_idx]    
                
        return hide, label
