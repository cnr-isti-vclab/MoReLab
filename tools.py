from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from feature_crosshair import FeatureCrosshair
from util.util import feature_absent_dialogue, numFeature_dialogue, estimateKMatrix, normalize, distance_F

import numpy as np
from object_panel import ObjectPanel
import cv2
from scipy import optimize

class Tools(QObject):
    
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        self.tool_btn_style =  """
                QPushButton:hover   { background-color: rgb(180,180,180); border: 1px solid darkgray;         }
                QPushButton {border:none; padding: 10px;}
                QToolTip { background-color: white; color: black); }
                """
        # print(self.ctrl_wdg.selected_movie_idx)
        self.wdg_tree = ObjectPanel(self)
        self.feature_pixmap = QPixmap("icons/small_crosshair.png")
        # print(type(self.feature_pixmap.size()))
        # print(self.feature_pixmap.size())
        self.add_tool_icons()
        self.cam_btn = QPushButton("Camera Calibration")
        self.cam_btn.clicked.connect(self.calibrate)
        self.cross_hair = False
        
        self.labels = []
        self.locs = []
        self.associated_frames = []
        self.associated_videos = []
        
        # self.associated_frames2 = [[]]
        self.selected_feature_index =-1
        self.count_ = 0
        
        self.features_data = {}
        
        

    def cost_F(self, F):
        F = np.reshape(F, newshape = (3,3))
        
        n = self.pts1_norm.shape[0]
        pts1 = np.concatenate((self.pts1_norm, np.ones(shape=(n,1))), axis=1)
        pts2 = np.concatenate((self.pts2_norm, np.ones(shape=(n,1))), axis=1)

        lines1 = np.dot(pts1, F)
        lines2 = np.dot(pts2, F)
        
        res = 0
        for i in range(n):
            res = res + distance_F(lines1[i,:], pts2[i,:]) + distance_F(lines2[i,:], pts1[i,:])

        return res
    
    
    
    
    def cost_M(self, M):
        u1 = self.pts1_norm[self.pt_idx, 0]
        v1 = self.pts1_norm[self.pt_idx, 1]
        u2 = self.pts2_norm[self.pt_idx, 0]
        v2 = self.pts2_norm[self.pt_idx, 1]
        
        tmp1 = np.square(u1 - (np.dot(self.p1_1.transpose(), M)/np.dot(self.p3_1.transpose(), M)))
        tmp2 = np.square(v1 - (np.dot(self.p2_1.transpose(), M)/np.dot(self.p3_1.transpose(), M)))
        tmp3 = np.square(u2 - (np.dot(self.p1_2.transpose(), M)/np.dot(self.p3_2.transpose(), M)))
        tmp4 = np.square(v2 - (np.dot(self.p2_2.transpose(), M)/np.dot(self.p3_2.transpose(), M)))
        
        res = tmp1 + tmp2 + tmp3 + tmp4
        return res
        
        
    
        
    def calibrate(self):
        indices = []
        for i,x in enumerate(self.locs):
            if len(x) > 1:
                indices.append(i)

        if (len(self.locs) < 8 or len(indices) < 8):
            numFeature_dialogue()
        else:
            v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
            
            pts1 = np.zeros(shape=(len(indices), 2), dtype=int)
            pts2 = np.zeros(shape=(len(indices), 2), dtype=int)
            for i,x in enumerate(indices):
                pts1[i,:] = self.locs[x][0]
                pts2[i,:] = self.locs[x][1]
                
            
            # --------------- Estimate Essential Matrix --------------------
            
            
            self.pts1_norm = normalize(pts1)
            self.pts2_norm = normalize(pts2)
            F, mask = cv2.findFundamentalMat(self.pts1_norm,self.pts2_norm,cv2.FM_8POINT)

            f = 35
            K = estimateKMatrix(v.width, v.height, f)
            
            E = np.dot(K.transpose(), np.dot(F, K))
            w,v = np.linalg.eig(E)
            # print("Eigen values")
            # print(w)
            
            # print("\n\n\n")

            # minimum = optimize.fmin(self.cost_F, F, disp=False)
            # F = minimum.reshape((3,3))
            
            # E = np.dot(K.transpose(), np.dot(F, K))
            # w,v = np.linalg.eig(E)
            # print("Eigen values")
            # print(w)


            
            # ---------------- Compute R and t now ------------------------
            
            U, sigma, V_t = np.linalg.svd(E)
            
            W = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]]) # Francesco's lecture
            R = np.dot(U, np.dot(W, V_t))
            
            t_matrix = np.dot(E, np.linalg.inv(R))
            t_3, t_2, t_1 = t_matrix[1,0], t_matrix[0, 2], t_matrix[2, 1]
            t = np.array([[t_1], [t_2], [t_3]])
            
            G1 = np.concatenate((np.eye(3), np.zeros((3,1))), axis=1)
            G2 = np.concatenate((R,t), axis=1)
            # print(G.shape)
            P1 = np.dot(K, G1)
            P2 = np.dot(K, G2)
            
            # print(P1)
            # print(P2)
            
            
            # -------------------- Triangulation -------------------------
            
            self.p1_1 = P1[0,:].reshape((4,1))
            self.p2_1 = P1[1,:].reshape((4,1))
            self.p3_1 = P1[2,:].reshape((4,1))
            
            self.p1_2 = P2[0,:].reshape((4,1))
            self.p2_2 = P2[1,:].reshape((4,1))
            self.p3_2 = P2[2,:].reshape((4,1))
            
            self.pt_idx = 0
            all_M = []
            M = np.array([1,1,1,1])
            
            n = self.pts1_norm.shape[0]
            for i in range(n):
                self.pt_idx = i
                all_M.append(optimize.fmin(self.cost_M, M, disp=False))
                
            Pw = np.asarray(all_M)
            print("All Real word points")
            print(Pw)
            

                             
                             
                    
                
            

            
            
            
            
            
        
        
        
        
        
        
        
        
        
        
        

    def add_tool_icons(self):
        icon_size = 30
        
        self.np_tool = QPushButton()
        self.np_tool.setIcon(QIcon("./icons/new_project.png"))
        self.np_tool.setIconSize(QSize(icon_size, icon_size))
        self.np_tool.setStyleSheet(self.tool_btn_style)
        self.np_tool.setToolTip("New Project")

        self.op_tool = QPushButton()
        self.op_tool.setIcon(QIcon("./icons/open_project.png"))
        self.op_tool.setIconSize(QSize(icon_size, icon_size))
        self.op_tool.setStyleSheet(self.tool_btn_style)
        self.op_tool.setToolTip("Open Project")

        self.om_tool = QPushButton()
        self.om_tool.setIcon(QIcon("./icons/open_movie.png"))
        self.om_tool.setIconSize(QSize(icon_size, icon_size))
        self.om_tool.setStyleSheet(self.tool_btn_style)
        self.om_tool.setToolTip("Open Movie")
        # self.om_tool.setStyleSheet("color: black; border: none; padding: 10px;")
        
        self.sp_tool = QPushButton()
        self.sp_tool.setIcon(QIcon("./icons/save_project.png"))
        self.sp_tool.setIconSize(QSize(icon_size, icon_size))
        self.sp_tool.setStyleSheet(self.tool_btn_style)
        self.sp_tool.setToolTip("Save Project")
        
        self.sp_as_tool = QPushButton()
        self.sp_as_tool.setIcon(QIcon("./icons/save_as.png"))
        self.sp_as_tool.setIconSize(QSize(icon_size, icon_size))
        self.sp_as_tool.setStyleSheet(self.tool_btn_style)
        self.sp_as_tool.setToolTip("Save as")

        self.ep_tool = QPushButton()
        self.ep_tool.setIcon(QIcon("./icons/exit_project.png"))
        self.ep_tool.setIconSize(QSize(icon_size, icon_size))
        self.ep_tool.setStyleSheet(self.tool_btn_style)
        self.ep_tool.setToolTip("Exit Project")


        self.mv_tool = QPushButton()
        self.mv_tool.setIcon(QIcon("./icons/cursor.png"))
        self.mv_tool.setIconSize(QSize(icon_size, icon_size))
        self.mv_tool.clicked.connect(self.move_tool)
        self.mv_tool.setStyleSheet(self.tool_btn_style)
        self.mv_tool.setToolTip("Move Tool")
        
        self.ft_tool = QPushButton()
        self.ft_tool.setIcon(QIcon("./icons/crosshair.png"))
        self.ft_tool.setIconSize(QSize(icon_size, icon_size))
        self.ft_tool.clicked.connect(self.feature_tool)
        self.ft_tool.setStyleSheet(self.tool_btn_style)
        self.ft_tool.setToolTip("Feature Tool")

        
    def move_tool(self):
        self.ft_tool.setStyleSheet(self.tool_btn_style)
        self.mv_tool.setStyleSheet('background-color: rgb(180,180,180); border: 1px solid darkgray; ')
        self.cross_hair = False
        self.hide_features(True)
        # self.hide_features(False)
        self.display_data()
        self.ctrl_wdg.viewer.setScrolDragMode()
        self.ctrl_wdg.viewer.setCursor(QCursor(Qt.ArrowCursor))
        
    def feature_tool(self):
        # print('feature')
        self.mv_tool.setStyleSheet(self.tool_btn_style)
        self.ft_tool.setStyleSheet('background-color: rgb(180,180,180); border: 1px solid darkgray; ')
        self.ctrl_wdg.viewer.setCursor(QCursor(Qt.CrossCursor))
        self.ctrl_wdg.viewer.setNoDragMode()
        self.cross_hair = True
        self.hide_features(True)
        self.display_data()

    
    def add_feature(self, x, y):
        # print(self.selected_feature_index)
        if self.cross_hair:
            t = self.ctrl_wdg.selected_thumbnail_index
            v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
            m_idx = self.ctrl_wdg.mv_panel.selected_movie_idx
            
            if self.ctrl_wdg.kf_method == "Regular":
                v.n_objects_kf_regular[t] += 1
                label = v.n_objects_kf_regular[t]
            elif self.ctrl_wdg.kf_method == "Network":
                v.n_objects_kf_network[t] += 1
                label = v.n_objects_kf_network[t]
                
            fc = FeatureCrosshair(self.feature_pixmap, x, y, label, self)
                
            if label not in self.labels:
                if len(self.labels) > label:
                    self.selected_feature_index = label -1
                    if self.labels[self.selected_feature_index] == -1:
                        self.labels[self.selected_feature_index] = label
                        self.associated_frames[self.selected_feature_index][0] = t
                        self.associated_videos[self.selected_feature_index][0] = m_idx
                        self.locs[self.selected_feature_index][0] = [fc.x_loc, fc.y_loc]
                    else:
                        print("Problem in adding feature...............")
                else:
                    self.selected_feature_index = self.selected_feature_index + 1
                    self.labels.append(label)
                    self.associated_frames.append([t])
                    self.associated_videos.append([m_idx])
                    self.locs.append([[fc.x_loc, fc.y_loc]])
                
            else:
                self.selected_feature_index = self.labels.index(label)
                self.associated_frames[self.selected_feature_index].append(t)
                self.associated_videos[self.selected_feature_index].append(m_idx)
                self.locs[self.selected_feature_index].append([fc.x_loc, fc.y_loc])

                            
            # Add feature on the scene

            self.ctrl_wdg.viewer._scene.addItem(fc)
            self.ctrl_wdg.viewer._scene.addItem(fc.label)
            
            if self.ctrl_wdg.kf_method == "Regular":
                v.features_regular[t].append(fc)
                v.hide_regular[t].append(False)
                # v.locs_regular[t].append()
                
            elif self.ctrl_wdg.kf_method == "Network":
                v.features_network[t].append(fc)
                v.hide_network[t].append(False)
                
            self.display_data()
            
            
    def display_data(self):
        # print(self.selected_feature_index)
        if (len(self.labels) == len(self.associated_frames)) and (len(self.labels) == len(self.locs)):                
            self.features_data = {"Label": self.labels,
                   "Frames": self.associated_frames,
                   "Videos": self.associated_videos,
                   "Locations": self.locs}
        
            # print("Feature index: "+str(self.selected_feature_index))
            self.wdg_tree.add_feature_data(self.features_data, self.selected_feature_index)
        else:
            print("Mismatch in dimensions!")
            print(self.labels)
            print(self.associated_frames)
            print(self.locs)
            
            
    def hide_features(self, current=True):
        t = self.ctrl_wdg.selected_thumbnail_index            
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        
        for v1 in self.ctrl_wdg.mv_panel.movie_caps:
            for i in range(len(v1.n_objects_kf_regular)):
                if v1.features_regular !=  []:
                    for j,f in enumerate(v1.features_regular[i]):
                        f.label.setVisible(False)
                        f.setVisible(False)
            for i in range(len(v1.n_objects_kf_network)):
                if v1.features_network !=  []:
                    for j,f in enumerate(v1.features_network[i]):
                        f.label.setVisible(False)
                        f.setVisible(False)
        
        if current:
            if self.ctrl_wdg.kf_method == "Regular":
                if v.features_regular != []:
                    for j,f in enumerate(v.features_regular[t]):
                        if not v.hide_regular[t][j]:
                            f.label.setVisible(True)
                            f.setVisible(True)
                            
            elif self.ctrl_wdg.kf_method == "Network":
                if v.features_network != []:
                    for j,f in enumerate(v.features_network[t]):
                        if not v.hide_network[t][j]:
                            f.label.setVisible(True)
                            f.setVisible(True)


    def find_idx(self, f, t):
        idd = [m for m, x in enumerate(self.associated_frames[f]) if x == t]
        if len(idd) == 1:
            pic_idx = idd[0]
        else:
            idd2 = [n for n, x in enumerate(self.associated_videos[f]) if x == self.ctrl_wdg.mv_panel.selected_movie_idx]
            d = list(set(idd2).intersection(idd))
            if len(d) == 1:
                pic_idx = d[0]
            else:
                print("Problem in Finding index")
        
        return pic_idx
        

    
    def delete_feature(self):
        t = self.ctrl_wdg.selected_thumbnail_index            
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        i = self.selected_feature_index
        # print("To be deleted : "+str(i))
        
        if self.cross_hair:
            found = False
            if self.ctrl_wdg.kf_method == "Regular" and len(v.hide_regular[t]) > i:
                if not v.hide_regular[t][i] and i == (int(v.features_regular[t][i].label.label) - 1):
                    found = True
                
            elif self.ctrl_wdg.kf_method == "Network" and len(v.hide_network[t]) > i:
                if not v.hide_network[t][i] and i == (int(v.features_network[t][i].label.label) - 1):
                    found = True
                    
            if found:
                if self.ctrl_wdg.kf_method == "Regular":
                    v.features_regular[t][i].label.setVisible(False)
                    v.features_regular[t][i].setVisible(False)
                    v.hide_regular[t][i] = True
                    # v.features_regular[t].pop(i)
                    
                elif self.ctrl_wdg.kf_method == "Network":
                    v.features_network[t][i].label.setVisible(False)
                    v.features_network[t][i].setVisible(False)
                    v.hide_network[t][i] = True
                    # v.features_network[t].pop(i)
                    
                if len(self.associated_frames[i]) > 1:
                    pic_idx = self.find_idx(i,t)
                    self.associated_frames[i].pop(pic_idx)
                    self.associated_videos[i].pop(pic_idx)
                    self.locs[i].pop(pic_idx)
    
                    
                elif len(self.associated_frames[i]) == 1:
                    self.labels[i] = -1
                    self.associated_frames[i] = [-1]
                    self.associated_videos[i] = [-1]
                    self.locs[i] = [[-1, -1]]
                    
                    
                self.wdg_tree.label_index = 0
                self.selected_feature_index = int(self.wdg_tree.items[self.wdg_tree.label_index].child(0).text(1)) - 1
                # print(self.associated_frames)
                # print(self.labels)
                # print("Feature Index : "+str(self.selected_feature_index))
                # print("Label Index : "+str(self.wdg_tree.label_index))
                self.display_data()
            else:
                feature_absent_dialogue()


 
            
    
            