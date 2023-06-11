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
        self.setMinimumSize(self.ctrl_wdg.monitor_width*0.2, self.ctrl_wdg.monitor_height*0.73)
        self.itemClicked.connect(self.select_feature_child)
        self.factor_x = 1
        self.factor_y = 1
        self.labels = []
        self.frames = []
        self.Xs = []
        self.Ys = []


    def display_data(self):
        # print("Movie : "+str(self.ctrl_wdg.mv_panel.selected_movie_idx))
        if self.ctrl_wdg.mv_panel.selected_movie_idx != -1:
            t = self.ctrl_wdg.selected_thumbnail_index
            m_idx = self.ctrl_wdg.mv_panel.selected_movie_idx
            v = self.ctrl_wdg.mv_panel.movie_caps[m_idx]
            self.clear()
            self.items = []
            self.labels = []
            # print(v.n_objects_kf_regular)
            self.labels, self.frames, self.Xs, self.Ys = [], [], [], []
            # print(len(v.features_network))
            if self.ctrl_wdg.kf_method == "Regular":
                if len(v.features_regular) > 0:
                    for i in range(max(v.n_objects_kf_regular)):
                        ls, xs, ys, fr = [], [], [], []
                        for j,fc_list in enumerate(v.features_regular):
                            if len(fc_list) > 0 and len(v.hide_regular[j]) > i:
                                if not v.hide_regular[j][i]:
                                    # print("Label : "+str(fc_list[i].label))
                                    ls.append(int(fc_list[i].label))
                                    fr.append(j+1)
                                    xs.append(self.transform_x(fc_list[i].x_loc))
                                    ys.append(self.transform_y(fc_list[i].y_loc))

                        self.labels.append(ls)
                        self.frames.append(fr)
                        self.Xs.append(xs)
                        self.Ys.append(ys)
            elif self.ctrl_wdg.kf_method == "Network":
                if len(v.features_network) > 0:
                    for i in range(max(v.n_objects_kf_network)):
                        ls, xs, ys, fr = [], [], [], []
                        for j,fc_list in enumerate(v.features_network):
                            if len(fc_list) > 0 and len(v.hide_network[j]) > i:
                                if not v.hide_network[j][i]:
                                    # print("Label : "+str(fc_list[i].label))
                                    ls.append(int(fc_list[i].label))
                                    fr.append(j+1)
                                    xs.append(self.transform_x(fc_list[i].x_loc))
                                    ys.append(self.transform_y(fc_list[i].y_loc))

                        self.labels.append(ls)
                        self.frames.append(fr)
                        self.Xs.append(xs)
                        self.Ys.append(ys)
            if len(self.labels) > 0:
                # print(self.labels)
                # print(self.frames)
                for i,labels in enumerate(self.labels):

                    # print(labels)
                    counts, unique_labels = self.find_unique_elements(labels)
                    # print(counts)
                    # print(unique_labels)
                    # print(self.frames[i])
                    # print("========================================")
                    k_ind = 0
                    for j, count in enumerate(counts):
                        new_frames = []
                        new_Xs = []
                        new_Ys = []
                        new_l = unique_labels[j]
                        for k in range(count):
                            new_frames.append(self.frames[i][k_ind])
                            new_Xs.append(self.Xs[i][k_ind])
                            new_Ys.append(self.Ys[i][k_ind])
                            k_ind += 1

                        # print(k_ind)

                        item = QTreeWidgetItem(["Feature "+str(new_l)])
                        child1 = QTreeWidgetItem(["Label", str(new_l)])
                        str_vf = ""
                        str_loc = ""

                        for h,ff in enumerate(new_frames):
                            if h==0:
                                str_vf = str_vf + str(ff)
                                str_loc = str_loc + '('+str(new_Xs[h])+ ',' + str(new_Ys[h])+')'
                            else:
                                str_vf = str_vf + ', ' +str(ff)
                                str_loc = str_loc + ', ('+str(new_Xs[h])+ ',' + str(new_Ys[h])+')'


                        child2 = QTreeWidgetItem(["Images", str_vf])
                        child3 = QTreeWidgetItem(["Location", str_loc])
                        item.addChild(child1)
                        item.addChild(child2)
                        item.addChild(child3)
                        self.items.append(item)
                    
            self.insertTopLevelItems(0, self.items)
            self.itemClicked.connect(self.select_feature_child)
            
            if self.ctrl_wdg.ui.cross_hair and self.selected_feature_idx != -1:
                self.select_feature()
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
                    self.selected_feature_idx = idx
                    tree_idx = self.items.index(selection)
                    self.items[tree_idx].setSelected(True)
                else:
                    self.deselect_features()
                    self.selected_feature_idx = -1
                

    def select_feature(self): # assuming that selected feature_idx has already been set
        if self.selected_feature_idx != -1 and len(self.items) > 0 and self.ctrl_wdg.ui.cross_hair:
            # print("Selected feature : "+str(self.selected_feature_idx))
            self.deselect_features()
            tree_idx = self.find_tree_idx()
            # print(tree_idx)
            self.items[tree_idx].setSelected(True)
            
    def find_tree_idx(self):
        count = 0
        for i, l in enumerate(self.labels):
            if l != -1:
                if i == self.selected_feature_idx:
                    return count
                count = count + 1
        return count          



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
