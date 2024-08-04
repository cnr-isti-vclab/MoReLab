from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from user_interface import UserInterface
from movie_panel import MoviePanel
from GL_widget_viewer import GL_Widget
from document import Document
from rectangle import Rectangle_Tool
from quad import Quad_Tool
from util.kf_dialogue import KF_dialogue
from util.util import *
import cv2, time, copy, os
import numpy as np
import pyautogui
from scipy.spatial import distance
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import torch

torch.set_grad_enabled(False)



class Widget(QWidget):
    def __init__(self, parent=None):
        # Widget.__init__(self, parent)
        super().__init__(parent)
        self.kf_method = ""
        self.thumbnail_text_stylesheet = """color:black;
                                 font-weight:bold;
                                 background-color:none;"""
        self.featured_frame_stylesheet = """color:red;
                                 font-weight:bold;
                                 background-color:none;"""
                                 

        self.thumbnail_height = 96
        self.thumbnail_width = 120
        self.copied_data = {}
        self.selected_thumbnail_index = -1
        self.monitor_width = pyautogui.size()[0]
        self.monitor_height = pyautogui.size()[1]
        self.main_file = parent   
        self.gl_viewer = GL_Widget(self)
        self.doc = Document(self)
        
        self.ui = UserInterface(self)
        self.mv_panel = MoviePanel(self)
        self.rect_obj = Rectangle_Tool(self)
        self.quad_obj = Quad_Tool(self)
        self.old_thumbnail_index = -1
        self.bool_shift_pressed = False
        
        
        
    def find_kfs(self):
        
        if self.kf_method == "Regular":
            kfs = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_regular
        elif self.kf_method == "Network":
            kfs = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_network
        else:
            kfs = []
        return kfs
    
    def set_kf_method(self):
        if len(self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_regular) > 0:
            self.kf_method = "Regular"
        elif len(self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_network) > 0:
            self.kf_method = "Network"
        else:
            self.kf_method = ""


    def extract(self):
        b = True
        old_method = self.kf_method
        if self.kf_method == "":
            self.kf_method = "Regular"
        dlg = KF_dialogue(self.kf_method)
        if dlg.exec():
            self.kf_method = dlg.kf_met
            kfs = self.find_kfs()
            if len(kfs) >0:
                b = show_dialogue()
            if b:
                v1 = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx]
                if v1.cap_exist:
                    w = Dialog()
                    w.show()
                    if self.kf_method == "Regular":
                        num_img = int(dlg.e1.text())
                        bool_extracted = v1.extract_frames_regularly(num_img)
                        if bool_extracted:
                            self.ui.radiobutton1.setChecked(True)
                            # self.main_file.logfile.info("Frames extracted by regular extraction method ....")
                        else:
                            numberOfFrames_dialogue()
    
                    elif self.kf_method == "Network":
                        # print("Going to extract frames")
                        v1.cleanSequence()
                        # print(len(v1.key_frames_network))
                        self.ui.radiobutton2.setChecked(True)
                        # self.main_file.logfile.info("Frames extracted by Network extraction method ....")
                    
                    w.done(0)
                    self.selected_thumbnail_index = -1
                    self.populate_scrollbar()
                    
                else:
                    not_extractKF_dialogue()
                    self.kf_method = old_method
                    # self.main_file.logfile.info("Not extracting frames. Frame extraction method is : "+self.kf_method+" ....")

            else:
                self.kf_method = dlg.kf_met
                # self.main_file.logfile.info("Not extracting frames. Frame extraction method is : "+self.kf_method+" ....")
        # else:
        #     self.main_file.logfile.info("Not extracting frames. Frame extraction method is : "+self.kf_method+" ....")
            
    def populate_scrollbar(self, disp_idx = -1):
        widget = QWidget()                 
        self.grid_layout = QHBoxLayout()
        row_in_grid_layout = 0
        kfs = self.find_kfs()
        if len(kfs) > 0:
            # self.main_file.logfile.info("Populating scrolbar ....")
            for i, img in enumerate(kfs):
                img_label = QLabel("")
                img_label.setAlignment(Qt.AlignCenter)
                text_label = QLabel(str(i+1))
                text_label.setAlignment(Qt.AlignCenter)
                text_label.setFont(QFont("Sanserif", 10))
                if i in self.gl_viewer.obj.img_indices and self.gl_viewer.is_display():
                    text_label.setStyleSheet(self.featured_frame_stylesheet)
                else:
                    text_label.setStyleSheet(self.thumbnail_text_stylesheet)
                pixmap_scaled = convert_cv_qt(img, self.thumbnail_width, self.thumbnail_height)
                img_label.setPixmap(pixmap_scaled)
    
                img_label.mousePressEvent = lambda e, index=row_in_grid_layout, file_img=img: \
                    self.on_thumbnail_click(e, index)
                
                thumbnail = QBoxLayout(QBoxLayout.TopToBottom)
                thumbnail.addWidget(img_label)
                thumbnail.addWidget(text_label)
                self.grid_layout.addLayout(thumbnail)
                row_in_grid_layout += 1

        
        widget.setLayout(self.grid_layout)
        self.ui.scroll_area.setWidget(widget)    
        self.gl_viewer.obj.feature_panel.display_data()

        if disp_idx != -1:
            self.displayThumbnail(disp_idx)
        else:
            self.gl_viewer.util_.setPhoto()
            
    def on_thumbnail_click(self, event, index):
        if self.selected_thumbnail_index != -1:
            self.old_thumbnail_index = self.selected_thumbnail_index
        self.displayThumbnail(index)
    
        
    def displayThumbnail(self, index):
        # self.main_file.logfile.info("Display image number : "+str(index+1)+" ....")
        self.selected_thumbnail_index = index
        # print(self.old_thumbnail_index, self.selected_thumbnail_index)
        # print(self.gl_viewer.util_.bool_shift_pressed)
        if self.bool_shift_pressed:
            self.bool_shift_pressed = False
            self.superglue_detection(self.old_thumbnail_index, self.selected_thumbnail_index)

        ## Deselect all thumbnails in the image selector
        for text_label_index in range(len(self.grid_layout)):
            # print(text_label_index)
            text_label = self.grid_layout.itemAt(text_label_index).itemAt(1).widget()
            if text_label_index in self.gl_viewer.obj.img_indices and self.gl_viewer.is_display():
                # print(text_label_index)
                text_label.setStyleSheet(self.featured_frame_stylesheet)
            else:
                text_label.setStyleSheet(self.thumbnail_text_stylesheet)

        ## Select the single clicked thumbnail
        text_label_of_thumbnail = self.grid_layout.itemAt(index).itemAt(1).widget()
        if index in self.gl_viewer.obj.img_indices and self.gl_viewer.is_display():
            text_label_of_thumbnail.setStyleSheet("background-color:rgb(135, 206, 235);"
                                                  "color:red;"
                                                  "font-weight:bold;")
        else:
            text_label_of_thumbnail.setStyleSheet("background-color:rgb(135, 206, 235);"
                                                  "color:black;"
                                                  "font-weight:bold;")                

        if self.kf_method == "Regular" and len(self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_regular) > 0:    
            img_file = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_regular[self.selected_thumbnail_index]
        elif self.kf_method == "Network" and len(self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_network) > 0:
            img_file = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_network[self.selected_thumbnail_index]
        else:
            img_file = None

        self.gl_viewer.util_.setPhoto(img_file)
        if self.gl_viewer.obj.fundamental_mat is None:
            self.gl_viewer.obj.feature_panel.selected_feature_idx = -1
        
        self.bool_shift_pressed = False


        
        
    def copy_features(self):
        # print("Copy features")
        t = self.selected_thumbnail_index
        self.copied_data = {}
        if t != -1:
            self.copied_data = {"img_index" : t,
                                "old_kf_method" : self.kf_method,
                                "old_movie_idx" : self.mv_panel.selected_movie_idx}
            copy_dialogue()
            # self.main_file.logfile.info("-------------------- Copied feature data on the frame "+str(t+1)+" ---------------------------------- ....")
        else:
            noImage_dialogue()
        
    def paste_features(self):
        if len(self.copied_data)==0:
            copy_features_dialogue()
        else:
            # self.main_file.logfile.info("--------------------- Pasting feature data on the frame "+str(self.selected_thumbnail_index+1)+" --------------------------- ....")
            v = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx]
            t = self.copied_data["img_index"]
            old_kf = self.copied_data["old_kf_method"]
            old_mv = self.copied_data["old_movie_idx"]
            
            sliding_window_size = 1
            resize_scale = 1/8
            search_pixels = int(resize_scale*64)
            
            if old_mv != self.mv_panel.selected_movie_idx:
                switch_movie_dialogue()
            else:
                
                if old_kf == "Regular" and self.kf_method == "Regular":
                    if v.n_objects_kf_regular[self.selected_thumbnail_index] == 0:
                        sift = cv2.SIFT_create()
                        old_frame = v.key_frames_regular[t]
                        old_frame = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
                        old_frame = cv2.resize(old_frame, None, fx=resize_scale, fy=resize_scale, interpolation = cv2.INTER_AREA)
                        
                        
                        new_frame = v.key_frames_regular[self.selected_thumbnail_index]
                        new_frame = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)
                        new_frame = cv2.resize(new_frame, None, fx=resize_scale, fy=resize_scale, interpolation = cv2.INTER_AREA)
                        
                        w = Dialog()
                        w.show()
                        
                        for i, fc in enumerate(v.features_regular[t]):
                            if not v.hide_regular[t][i]:
                                x_loc, y_loc = int(resize_scale*self.gl_viewer.obj.feature_panel.transform_x(fc.x_loc)), int(resize_scale*self.gl_viewer.obj.feature_panel.transform_y(fc.y_loc))
                                old_patch = old_frame[y_loc - search_pixels:y_loc + search_pixels, x_loc - search_pixels:x_loc + search_pixels]
                                # cv2.imwrite('old_patch_'+str(i)+'.jpg', old_patch)
                                kp1 = cv2.KeyPoint.convert([(x_loc, y_loc)])
                                (kps1, patch1_desc) = sift.compute(old_frame, kp1)
                                distance_matrix = 100000*np.ones(shape=(4*search_pixels , 4*search_pixels))
                                j_idx = 0
                                all_kps2 = []
                                all_desc2 = []
                                # print(x_loc, y_loc)
                                for j in range(-2*search_pixels, 2*search_pixels, sliding_window_size):
                                    k_idx = 0
                                    kps2_temp = []
                                    desc2_temp = []
                                    for k in range(-2*search_pixels, 2*search_pixels, sliding_window_size):
                                        kp2 = cv2.KeyPoint.convert([(x_loc + j, y_loc + k)])
                                        (kps2, patch2_desc) = sift.compute(new_frame, kp2)
                                        # print(patch2_desc.shape)
                                        # print("==========================")
                                        kps2_temp.append(kps2)
                                        desc2_temp.append(patch2_desc)
                                        dist = np.linalg.norm(patch1_desc - patch2_desc)
                                        distance_matrix[j_idx, k_idx] = dist
                                        k_idx += 1
                                    all_kps2.append(kps2_temp)
                                    all_desc2.append(desc2_temp)
                                    j_idx = j_idx + 1
                                
                                
                                min_indices = np.unravel_index(distance_matrix.argmin(), distance_matrix.shape)

                                kps2 = all_kps2[min_indices[0]][min_indices[1]]
                                desc2 = all_desc2[min_indices[0]][min_indices[1]]
                                
                                # cv2.imwrite('final_img_'+str(i)+'.jpg', out)

                                x_shift, y_shift = self.gl_viewer.obj.feature_panel.inv_trans_x(kps2[0].pt[0]*(1/resize_scale)) + 2 , self.gl_viewer.obj.feature_panel.inv_trans_y(kps2[0].pt[1]*(1/resize_scale)) + 2

                                # x_shift, y_shift = self.calc_shifts(patch1_rgb, patch2_rgb, i, patch_size, search_patch_factor)
                                self.gl_viewer.obj.add_feature(x_shift, y_shift)
                            else:
                                # print("Adding and deleting feature")
                                self.gl_viewer.obj.add_feature(fc.x_loc, fc.y_loc)
                                self.gl_viewer.obj.feature_panel.selected_feature_idx = i
                                self.gl_viewer.obj.delete_feature()
                        w.done(0)
                    else:
                        filledImage_dialogue()
                        
                elif old_kf == "Network" and self.kf_method == "Network":
                    if v.n_objects_kf_network[self.selected_thumbnail_index] == 0:
                        sift = cv2.SIFT_create()
                        old_frame = v.key_frames_network[t]
                        old_frame = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
                        old_frame = cv2.resize(old_frame, None, fx=resize_scale, fy=resize_scale, interpolation = cv2.INTER_AREA)
                        
                        
                        new_frame = v.key_frames_network[self.selected_thumbnail_index]
                        new_frame = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)
                        new_frame = cv2.resize(new_frame, None, fx=resize_scale, fy=resize_scale, interpolation = cv2.INTER_AREA)

                        w = Dialog()
                        w.show()

                        for i, fc in enumerate(v.features_network[t]):
                            if not v.hide_network[t][i]:
                                x_loc, y_loc = int(resize_scale*self.gl_viewer.obj.feature_panel.transform_x(fc.x_loc)), int(resize_scale*self.gl_viewer.obj.feature_panel.transform_y(fc.y_loc))
                                old_patch = old_frame[y_loc - search_pixels:y_loc + search_pixels, x_loc - search_pixels:x_loc + search_pixels]
                                kp1 = cv2.KeyPoint.convert([(x_loc, y_loc)])
                                (kps1, patch1_desc) = sift.compute(old_frame, kp1)
                                distance_matrix = 100000*np.ones(shape=(4*search_pixels , 4*search_pixels))
                                j_idx = 0
                                all_kps2 = []
                                all_desc2 = []
                                # print(x_loc, y_loc)
                                for j in range(-2*search_pixels, 2*search_pixels, sliding_window_size):
                                    k_idx = 0
                                    kps2_temp = []
                                    desc2_temp = []
                                    for k in range(-2*search_pixels, 2*search_pixels, sliding_window_size):
                                        kp2 = cv2.KeyPoint.convert([(x_loc + j, y_loc + k)])
                                        (kps2, patch2_desc) = sift.compute(new_frame, kp2)
                                        kps2_temp.append(kps2)
                                        desc2_temp.append(patch2_desc)
                                        dist = np.linalg.norm(patch1_desc - patch2_desc)
                                        distance_matrix[j_idx, k_idx] = dist
                                        k_idx += 1
                                    all_kps2.append(kps2_temp)
                                    all_desc2.append(desc2_temp)
                                    j_idx = j_idx + 1
                                
                                
                                min_indices = np.unravel_index(distance_matrix.argmin(), distance_matrix.shape)

                                kps2 = all_kps2[min_indices[0]][min_indices[1]]
                                desc2 = all_desc2[min_indices[0]][min_indices[1]]
                                
                                # cv2.imwrite('final_img_'+str(i)+'.jpg', out)

                                x_shift, y_shift = self.gl_viewer.obj.feature_panel.inv_trans_x(kps2[0].pt[0]*(1/resize_scale)) + 2 , self.gl_viewer.obj.feature_panel.inv_trans_y(kps2[0].pt[1]*(1/resize_scale)) + 2
                                self.gl_viewer.obj.add_feature(x_shift, y_shift)
                                
                                
                            else:
                                # print("Adding and deleting feature")
                                self.gl_viewer.obj.add_feature(fc.x_loc, fc.y_loc)
                                self.gl_viewer.obj.feature_panel.selected_feature_idx = i
                                self.gl_viewer.obj.delete_feature()
                        
                        w.done(0)

                    else:
                        filledImage_dialogue()
                    
                else:
                    switch_kf_dialogue()
            
    def read_image_for_superglue(self, image_rgb, device, resize, rotation, resize_float):
        image = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2GRAY)
        if image is None:
            return None, None, None
        w, h = image.shape[1], image.shape[0]
        w_new, h_new = w, h
        # w_new, h_new = process_resize(w, h, resize)
        scales = (float(w) / float(w_new), float(h) / float(h_new))
    
        if resize_float:
            image = cv2.resize(image.astype('float32'), (w_new, h_new))
        else:
            image = cv2.resize(image, (w_new, h_new)).astype('float32')
    
        if rotation != 0:
            image = np.rot90(image, k=rotation)
            if rotation % 2:
                scales = scales[::-1]
    
        inp = torch.from_numpy(image/255.).float()[None, None].to(device)
        return image, inp, scales
            
                    
    def superglue_detection(self, idx0, idx1):
        v = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx]
        if idx0 != idx1:
            if self.kf_method == "Regular":
                images = v.key_frames_regular
                x1_idx0, x1_idx1 = v.select_x1_regular[idx0], v.select_x1_regular[idx1]
                y1_idx0, y1_idx1 = v.select_y1_regular[idx0], v.select_y1_regular[idx1]
                w_idx0, w_idx1 = v.select_w_regular[idx0], v.select_w_regular[idx1]
                h_idx0, h_idx1 = v.select_h_regular[idx0], v.select_h_regular[idx1]
                
            elif self.kf_method == "Network":
                images = v.key_frames_network
                x1_idx0, x1_idx1 = v.select_x1_network[idx0], v.select_x1_network[idx1]
                y1_idx0, y1_idx1 = v.select_y1_network[idx0], v.select_y1_network[idx1]
                w_idx0, w_idx1 = v.select_w_network[idx0], v.select_w_network[idx1]
                h_idx0, h_idx1 = v.select_h_network[idx0], v.select_h_network[idx1]
                
            if len(images) == 0:
                no_keyframe_dialogue()
            else:
                if not os.path.exists(os.path.join(os.getcwd(), 'models')):
                    # self.main_file.logfile.info("User did not place models folder inside MoReLab ....")
                    models_folder_dialogue()
                else:
                    from models.matching import Matching
                    from models.utils import (compute_pose_error, compute_epipolar_error,
                                              estimate_pose, make_matching_plot_fast,
                                              error_colormap, AverageTimer, pose_auc, read_image,
                                              rotate_intrinsics, rotate_pose_inplane,
                                              scale_intrinsics, process_resize, frame2tensor)
                    # self.main_file.logfile.info("AI-based automatic detection is starting ....")
                    w = Dialog()
                    w.show()
                
                    image0, image1 = images[idx0], images[idx1]
                    
                    if x1_idx0 != -1:
                        image0 = image0[self.gl_viewer.obj.feature_panel.transform_y(y1_idx0) : self.gl_viewer.obj.feature_panel.transform_y(y1_idx0+h_idx0), self.gl_viewer.obj.feature_panel.transform_x(x1_idx0) : self.gl_viewer.obj.feature_panel.transform_x(x1_idx0+w_idx0)]
                    
                    if x1_idx1 != -1:
                        image1 = image1[self.gl_viewer.obj.feature_panel.transform_y(y1_idx1) : self.gl_viewer.obj.feature_panel.transform_y(y1_idx1+h_idx1), self.gl_viewer.obj.feature_panel.transform_x(x1_idx1) : self.gl_viewer.obj.feature_panel.transform_x(x1_idx1+w_idx1)]
                    
                    # Load the SuperPoint and SuperGlue models.
                    if torch.cuda.is_available():
                        device = 'cuda'
                    else:
                        device = 'cpu'
                    
                    # self.main_file.logfile.info("Detection is being done on device "+device+" ....")
                    
                    
                    config = {
                        'superpoint': {
                            'nms_radius': 4,
                            'keypoint_threshold': 0.005,
                            'max_keypoints': 1024
                        },
                        'superglue': {
                            'weights': "indoor",
                            'sinkhorn_iterations': 20,
                            'match_threshold': 0.2,
                        }
                    }
                    matching = Matching(config).eval().to(device)
                    
                    # Load the image pair.
                    image0, inp0, scales0 = self.read_image_for_superglue(image0, device, [-1], 0, False)
                    image1, inp1, scales1 = self.read_image_for_superglue(image1, device, [-1], 0, False)
        
                    pred = matching({'image0': inp0, 'image1': inp1})
                    pred = {k: v[0].cpu().numpy() for k, v in pred.items()}
                    kpts0, kpts1 = pred['keypoints0'], pred['keypoints1']
                    matches, conf = pred['matches0'], pred['matching_scores0']
        
                    # Keep the matching keypoints.
                    valid = matches > -1
                    mkpts0 = kpts0[valid]
                    mkpts1 = kpts1[matches[valid]]
                    mconf = conf[valid]
                    
                    if self.kf_method == "Regular":
                        fc_list_idx0 = v.features_regular[idx0]
                        fc_list_idx1 = v.features_regular[idx1]
                        num_idx0 = v.n_objects_kf_regular[idx0]
                        num_idx1 = v.n_objects_kf_regular[idx1]
        
                    elif self.kf_method == "Network":
                        fc_list_idx0 = v.features_network[idx0]
                        fc_list_idx1 = v.features_network[idx1]
                        num_idx0 = v.n_objects_kf_network[idx0]
                        num_idx1 = v.n_objects_kf_network[idx1]
                        
                    # print("Number of matching keypoints detected : "+str(mkpts0.shape[0]))
                    # self.main_file.logfile.info("Number of matching keypoints detected : "+str(mkpts0.shape[0])+" ....")
                
                    max_label = 0
                    if num_idx0 > 0 or num_idx1 > 1:
                        labels_idx0, labels_idx1 = [], []
        
                        for fc_idx0 in fc_list_idx0:
                            labels_idx0.append(int(fc_idx0.label))
                        for fc_idx1 in fc_list_idx1:
                            labels_idx1.append(int(fc_idx1.label))
                            
                        max_label = max(max(labels_idx0, default=0), max(labels_idx1, default=0))
                    
                    # print("Maximum label : "+str(max_label))
                    # self.main_file.logfile.info("Maximum label : "+str(max_label)+" ....")
                    
                    i_idx = 0
                    for i in range(mkpts0.shape[0]):
                        if x1_idx0 != -1:
                            x0, y0 = self.gl_viewer.obj.feature_panel.inv_trans_x(mkpts0[i, 0]) - self.gl_viewer.util_.w1 + x1_idx0, self.gl_viewer.obj.feature_panel.inv_trans_y(mkpts0[i, 1]) - self.gl_viewer.util_.h1 + y1_idx0
                        else:
                            x0, y0 = self.gl_viewer.obj.feature_panel.inv_trans_x(mkpts0[i, 0]) + x1_idx0, self.gl_viewer.obj.feature_panel.inv_trans_y(mkpts0[i, 1]) + y1_idx0
                        
                        if x1_idx1 != -1:
                            x1, y1 = self.gl_viewer.obj.feature_panel.inv_trans_x(mkpts1[i, 0]) - self.gl_viewer.util_.w1 + x1_idx1, self.gl_viewer.obj.feature_panel.inv_trans_y(mkpts1[i, 1]) - self.gl_viewer.util_.h1 + y1_idx1
                        else:
                            x1, y1 = self.gl_viewer.obj.feature_panel.inv_trans_x(mkpts1[i, 0]) + x1_idx1, self.gl_viewer.obj.feature_panel.inv_trans_y(mkpts1[i, 1]) + y1_idx1
                            
                        new_label_0, x0, y0 = self.check_neighbour(x0, y0, fc_list_idx0)
                        new_label_1, x1, y1 = self.check_neighbour(x1, y1, fc_list_idx1)
                            
                        if new_label_0 != -1 and new_label_1 == -1:
                            self.gl_viewer.obj.add_feature(x0, y0, new_label_0, idx0)
                            self.gl_viewer.obj.add_feature(x1, y1, new_label_0, idx1)
        
                        elif new_label_0 == -1 and new_label_1 != -1:
                            self.gl_viewer.obj.add_feature(x0, y0, new_label_1, idx0)
                            self.gl_viewer.obj.add_feature(x1, y1, new_label_1, idx1)
                        else:
                            self.gl_viewer.obj.add_feature(x0, y0, max_label+i_idx+1, idx0)
                            self.gl_viewer.obj.add_feature(x1, y1, max_label+i_idx+1, idx1)
                            i_idx += 1
                            
                    w.done(0)
    
                    # self.main_file.logfile.info("AI-based automatic detection has been completed ....")
        else:
            same_image_dialogue()
            
    def check_neighbour(self, x, y, fc_list):
        threshold = 2
        label = -1
        for i, fc in enumerate(fc_list):
            dist = np.sqrt(np.square(x - fc.x_loc) + np.square(y - fc.y_loc))
            if dist < threshold:
                label = int(fc.label)
                x = fc.x_loc
                y = fc.y_loc
                break
        
        return label, x, y
            
    
    def keyReleaseEvent(self, event):
        if self.bool_shift_pressed:
            self.bool_shift_pressed = False
        super(Widget, self).keyReleaseEvent(event)                        
        


    def keyPressEvent(self, event):
        
        ######################## Copy and Pase features  ########################

        if self.ui.cross_hair and event.modifiers() & Qt.ControlModifier:
            self.gl_viewer.obj.feature_panel.selected_feature_idx = -1
            if event.key() == Qt.Key_C:
                self.copy_features()
            elif event.key() == Qt.Key_V:
                self.paste_features()
        
        ######################## SuperGlue Detection using Shift Key  ########################
        
        
        if event.modifiers() & Qt.ShiftModifier :
            self.bool_shift_pressed = True


        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_R:
            if self.selected_thumbnail_index == -1:
                noFrameSelected_dialogue()
            else:
                v = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx]
                idx0 = self.selected_thumbnail_index
                
                # self.main_file.logfile.info("--------------- Resetting the frame number : "+str(idx0+1)+" --------------------- ....")
                
                if self.kf_method == "Regular":
                    v.n_objects_kf_regular[idx0] = 0
                    v.measured_pos_regular[idx0] = []
                    v.measured_distances_regular[idx0] = []
                    v.features_regular[idx0] = []
                    v.hide_regular[idx0] = []
                    v.count_deleted_regular[idx0] = []
                                
                elif self.kf_method == "Network":
                    v.n_objects_kf_network[idx0] = 0
                    v.measured_pos_network[idx0] = []
                    v.measured_distances_network[idx0] = []
                    v.features_network[idx0] = []
                    v.hide_network[idx0] = []
                    v.count_deleted_network[idx0] = []

                self.gl_viewer.obj.initialize_mats()
                self.populate_scrollbar(idx0)
                resetFrame_dialogue()

            

        super(Widget, self).keyPressEvent(event)
            
        
