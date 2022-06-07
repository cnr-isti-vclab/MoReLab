from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from feature_crosshair import FeatureCrosshair
from util.util import feature_absent_dialogue, numFeature_dialogue, estimateKMatrix, normalize, distance_F, visualize, compute_fundamental_normalized
from util.util import compute_P_from_fundamental, triangulate, compute_parameters, reprojection_error, compute_P_from_essential
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
        u1 = self.pts1[self.pt_idx, 0]
        v1 = self.pts1[self.pt_idx, 1]
        u2 = self.pts2[self.pt_idx, 0]
        v2 = self.pts2[self.pt_idx, 1]
        
        tmp1 = np.square(u1 - (np.dot(self.p1_1.transpose(), M)/np.dot(self.p3_1.transpose(), M)))
        tmp2 = np.square(v1 - (np.dot(self.p2_1.transpose(), M)/np.dot(self.p3_1.transpose(), M)))
        tmp3 = np.square(u2 - (np.dot(self.p1_2.transpose(), M)/np.dot(self.p3_2.transpose(), M)))
        tmp4 = np.square(v2 - (np.dot(self.p2_2.transpose(), M)/np.dot(self.p3_2.transpose(), M)))
        
        res = tmp1 + tmp2 + tmp3 + tmp4
        return res
        
        
    
        
    def calibrate(self):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        
        display = True
        
        img_indices = []
        all_locs = []
        visible_labels = []
        if self.ctrl_wdg.kf_method == "Regular":
            for i,hr in enumerate(v.hide_regular):
                tmp1, tmp2 = [], []
                count = 0
                for j,hide in enumerate(hr):
                    fc = v.features_regular[i][j]
                    tmp1.append([int(fc.x_loc), int(fc.y_loc)])
                    if not hide:
                        tmp2.append(j)
                        count = count + 1
                if count > 7:
                    img_indices.append(i)
                    all_locs.append(tmp1)
                    visible_labels.append(tmp2)

        

        if len(img_indices) < 2:
            numFeature_dialogue()
        else:
            both_visible_idx = []
            for l1 in visible_labels[0]:
                if l1 in visible_labels[1]:
                    both_visible_idx.append(l1)
                    
            if len(both_visible_idx) < 8:
                numFeature_dialogue()
            else:
                pts1 = np.zeros((len(both_visible_idx),2), dtype=int)
                pts2 = np.zeros((len(both_visible_idx),2), dtype=int)
                for i,l in enumerate(both_visible_idx):
                    pts1[i,:] = all_locs[0][l]
                    pts2[i,:] = all_locs[1][l]
                
                f = 35
                K = estimateKMatrix(v.width, v.height, f)
                # print(K)
                # K = np.array([[1780.82576, 9.45554554e+00, 6.55296856e+02],
                #               [0.00000000e+00, 1.77301916e+03, 5.09305248e+02],
                #               [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
                # Cx = K[0,2]
                # Cy = K[1,2]
                # pts1[:,0] = pts1[:,0] - Cx
                # pts1[:,1] = pts1[:,1] - Cy
                # pts2[:,0] = pts2[:,0] - Cx
                # pts2[:,1] = pts2[:,1] - Cy
                
                # print(pts1)
                # print(pts2)
                
                self.pts1 = pts1
                self.pts2 = pts2
                
                pts1_norm = (pts1 - np.min(pts1))/(np.max(pts1)-np.min(pts1))
                pts2_norm = (pts2 - np.min(pts2))/(np.max(pts2)-np.min(pts2))
                

                F, mask = cv2.findFundamentalMat(pts1,pts2,cv2.FM_8POINT)
                # print(F)

                n = pts1.shape[0]
                
                E = np.dot(K.transpose(), np.dot(F, K))
                # print(E)
                # w, v = np.linalg.eig(E)
                # # print(w)
                U, sigma, V_t = np.linalg.svd(E)
                print(sigma)
                # w, v = np.linalg.eig(np.diag(sigma))
                # # print(w)
                
                
                
                # W = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
                # Z = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 0]])
                # R = np.dot(U, np.dot(W.transpose(), V_t))
                # t_matrix = np.dot(U, np.dot(Z, U.transpose()))
                # print(np.dot(t_matrix, R))
                
                # t_3, t_2, t_1 = t_matrix[1,0], t_matrix[0, 2], t_matrix[2, 1]
                # t = np.array([[t_1], [t_2], [t_3]])
                
                G2_list = compute_P_from_essential(E)
                G1 = np.concatenate((np.eye(3), np.zeros((3,1))), axis=1)
                P1 = np.dot(K, G1)
                
                for G2 in G2_list:
                    P2 = np.dot(K, G2)
                    # Pw = cv2.triangulatePoints(P1, P2, pts1_norm.transpose(), pts2_norm.transpose())
                    # Pw = Pw.transpose()
                    # ww = []
                    # for i in range(Pw.shape[0]):
                    #     ww.append(Pw[i,:]/Pw[i,3])
                    # data = np.asarray(ww)
                    # # print(data)
                    # R = G2[:, :3]
                    # t = G2[:,3].reshape((3,1))
                    # reprojection_error(P2, R, t, data)
                    
                    self.p1_1 = P1[0,:].reshape((4,1))
                    self.p2_1 = P1[1,:].reshape((4,1))
                    self.p3_1 = P1[2,:].reshape((4,1))
                    
                    self.p1_2 = P2[0,:].reshape((4,1))
                    self.p2_2 = P2[1,:].reshape((4,1))
                    self.p3_2 = P2[2,:].reshape((4,1))
                    
                    self.pt_idx = 0
                    all_M = []
                    M = np.array([1,1,1,1])
                    
                    n = self.pts1.shape[0]
                    for i in range(n):
                        self.pt_idx = i
                        min_val = optimize.fmin(self.cost_M, M, disp=False)
                        x4 = min_val[3]
                        all_M.append(min_val/x4)
                        
                    data = np.asarray(all_M)
                    # print("All Real word points")
                    # print(Pw)
                    
                    P2 = np.dot(K, G2)
                    R = G2[:, :3]
                    t = G2[:,3].reshape((3,1))
                    projected_pts = reprojection_error(P2, R, t, data)
                
                    visualize(pts1, projected_pts, data, both_visible_idx, display)
                
    
                             
                             
                    
                
            

            
            
            
            
            
        
        
        
        
        
        
        
        
        
        
        

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


 
            
    
            