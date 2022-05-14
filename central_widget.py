from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from util.video import Video
from util.photoviewer import PhotoViewer
from util.kf_dialogue import KF_dialogue, show_dialogue
from document import Document
import json, os, glob
import cv2
import numpy as np




class SliderFrame(QFrame):
    def __init__(self, myslider):
        QFrame.__init__(self)
    
        self.setStyleSheet("border: 1px solid black; margin: 0px; padding: 0px;")
   
        self.layout = QVBoxLayout()
        self.layout.addLayout(myslider)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)


class Widget(QWidget):
    def __init__(self):
        super().__init__()
            
        self.selected_movie_path = ""
        self.movie_buttons = []
        self.movie_paths = []
        self.selected_thumbnail_index = -1
        self.selected_movie_idx = -1
        self.movie_caps = []
        self.viewer = PhotoViewer(self)
        self.doc = Document(self)
        
        self.thumbnail_height = 64
        self.thumbnail_width = 104
        self.kf_method = ""
        
        self.create_wdg1()
        # self.create_wdg4()
        self.create_scroll_area()

        
        
    def create_wdg1(self):
        self.summary_wdg = QLabel("")
        self.summary_wdg.setStyleSheet("border: 1px solid gray;")
        self.summary_wdg.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.btn_kf = QPushButton("Extract Key-frames")
        self.btn_kf.clicked.connect(self.extract)

            
    def find_kfs(self):
        if self.kf_method == "Regular":
            kfs = self.movie_caps[self.selected_movie_idx].key_frames_regular
        elif self.kf_method == "Network":
            kfs = self.movie_caps[self.selected_movie_idx].key_frames_network
        else:
            kfs = []
            
        return kfs
            
            
    def populate_scrollbar(self):
        widget = QWidget()                 
        self.grid_layout = QHBoxLayout()
        row_in_grid_layout = 0
        kfs = self.find_kfs()
        # print("Number of thumbnails: "+str(len(kfs)))
        for i, img in enumerate(kfs):
            img_label = QLabel("")
            img_label.setAlignment(Qt.AlignCenter)
            text_label = QLabel("")
            text_label.setAlignment(Qt.AlignCenter)
            # text_label.setText(str(i))
            pixmap_scaled = self.viewer.convert_cv_qt(img, self.thumbnail_width, self.thumbnail_height)
            img_label.setPixmap(pixmap_scaled)

            img_label.mousePressEvent = lambda e, index=row_in_grid_layout, file_img=img: \
                self.on_thumbnail_click(e, index)
            
            thumbnail = QBoxLayout(QBoxLayout.TopToBottom)
            thumbnail.addWidget(img_label)
            thumbnail.addWidget(text_label)
            self.grid_layout.addLayout(thumbnail)
            row_in_grid_layout += 1
        widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(widget)
            
            
    def on_thumbnail_click(self, event, index):
        self.displayThumbnail(index)
    
        
    def displayThumbnail(self, index):
        self.selected_thumbnail_index = index
        self.viewer.obj.hide_features(True)
        if self.viewer.obj.features_data != {}:
            self.viewer.obj.wdg_tree.add_feature_data(self.viewer.obj.features_data, self.viewer.obj.selected_feature_index)
        ## Deselect all thumbnails in the image selector
        for text_label_index in range(len(self.grid_layout)):
            # print(text_label_index)
            text_label = self.grid_layout.itemAt(text_label_index).itemAt(1).widget()
            text_label.setStyleSheet("background-color:none;")

        ## Select the single clicked thumbnail
        text_label_of_thumbnail = self.grid_layout.itemAt(index)\
            .itemAt(1).widget()
        text_label_of_thumbnail.setStyleSheet("background-color:blue;")
        
        if self.kf_method == "Regular":    
            img_file = self.movie_caps[self.selected_movie_idx].key_frames_regular[self.selected_thumbnail_index]
        elif self.kf_method == "Network":
            img_file = self.movie_caps[self.selected_movie_idx].key_frames_network[self.selected_thumbnail_index]
        else:
            img_file = np.zeros(shape=(400, 400))
        
        
        p = self.viewer.convert_cv_qt(img_file, img_file.shape[1] , img_file.shape[0] )
        self.viewer.setPhoto(p)
        

        

    def create_scroll_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(True)
        

    def deselect_movies(self):
        if len(self.movie_buttons) > 0:
            for bt in self.movie_buttons:
                bt.setStyleSheet("color: black; border: none;")
                
                
    def add_movie(self, movie_path, btn):
        # btn.setStyleSheet("color: blue; border: 1px solid blue;")
        self.movie_buttons.append(btn)
        self.movie_paths.append(movie_path)
        v = Video(movie_path)
        self.movie_caps.append(v)
        self.summary_wdg.setText(v.video_summary())

    def switch_kf_method(self):
        kfs_regular = self.movie_caps[self.selected_movie_idx].key_frames_regular
        kfs_network = self.movie_caps[self.selected_movie_idx].key_frames_network
        # print(len(kfs_regular))
        # print(len(kfs_network))
        if len(kfs_regular) > 0 and len(kfs_network) > 0:
            return
        elif len(kfs_regular) == 0 and len(kfs_network) == 0:
            return 
        elif len(kfs_regular) > 0 and len(kfs_network) == 0:
            self.kf_method = "Regular"
        elif len(kfs_regular) == 0 and len(kfs_network) > 0:
            self.kf_method = "Network"
            
                
    
    def select_movie(self, movie_path):
        self.deselect_movies()
        self.viewer.obj.hide_features(False)
        # self.viewer.obj.refresh()
        self.viewer.obj.wdg_tree.clear()
        
        for i,p in enumerate(self.movie_paths):
            if p == movie_path:
                self.selected_movie_path = p
                self.selected_movie_idx = i
                
        self.switch_kf_method()        
        self.movie_buttons[self.selected_movie_idx].setStyleSheet("color: blue; border: 1px solid blue;")
        v = self.movie_caps[self.selected_movie_idx]
        self.summary_wdg.setText(v.video_summary())
        self.populate_scrollbar()
        
        self.viewer.setPhoto()
        
    
            
    def extract(self):
        b = True
        dlg = KF_dialogue()
        if dlg.exec():
            self.kf_method = dlg.kf_met

            kfs = self.find_kfs()
            if len(kfs) >0:
                b = show_dialogue()
            if b:
                
                v = Video(self.selected_movie_path)
                v1 = self.movie_caps[self.selected_movie_idx]
                
                if self.kf_method == "Regular":
                    rate_str = dlg.e1.text()
                    sampling_rate = int(rate_str)
                    v1.key_frames_regular, v1.key_frame_indices_regular, v1.features_regular, v1.hide_regular,  v1.n_objects_kf_regular = v.extract_frames_regularly(sampling_rate)

                elif self.kf_method == "Network":
                    v1.key_frames_network, v1.key_frame_indices_network, v1.features_network, v1.hide_network,  v1.n_objects_kf_network = v.cleanSequence()

        else:
            self.kf_method = dlg.kf_met
            
        self.populate_scrollbar()

            

                