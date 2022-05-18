from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from util.video import Video
from util.photoviewer import PhotoViewer
from util.kf_dialogue import KF_dialogue
from util.util import show_dialogue
from document import Document
from movie_panel import MoviePanel

import json, os, glob
import cv2
import numpy as np



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
        self.mv_panel = MoviePanel(self)
        
        self.thumbnail_text_stylesheet = """color:black;
                                 font-weight:bold;
                                 background-color:none;"""
        self.thumbnail_height = 96
        self.thumbnail_width = 120
        self.kf_method = ""
        
        self.create_wdg1()
        # self.create_wdg4()
        self.create_scroll_area()

        
        
    def create_wdg1(self):
        self.btn_kf = QPushButton("Extract Key-frames")
        self.btn_kf.clicked.connect(self.extract)

            
    def find_kfs(self):
        if self.kf_method == "Regular":
            kfs = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_regular
        elif self.kf_method == "Network":
            kfs = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_network
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
            text_label = QLabel(str(i+1))
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setFont(QFont("Sanserif", 10))
            text_label.setStyleSheet(self.thumbnail_text_stylesheet)
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
        ## Deselect all thumbnails in the image selector
        for text_label_index in range(len(self.grid_layout)):
            # print(text_label_index)
            text_label = self.grid_layout.itemAt(text_label_index).itemAt(1).widget()
            text_label.setStyleSheet(self.thumbnail_text_stylesheet)

        ## Select the single clicked thumbnail
        text_label_of_thumbnail = self.grid_layout.itemAt(index)\
            .itemAt(1).widget()
        text_label_of_thumbnail.setStyleSheet("background-color:rgb(135, 206, 235);"
                                              "font-weight:bold;")
        
        if self.kf_method == "Regular":    
            img_file = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_regular[self.selected_thumbnail_index]
        elif self.kf_method == "Network":
            img_file = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_network[self.selected_thumbnail_index]
        
        # print(img_file.shape)
        p = self.viewer.convert_cv_qt(img_file, img_file.shape[1] , img_file.shape[0] )
        self.viewer.setPhoto(p)
        if not self.viewer.importing:
            self.viewer.fitInView()

        

    def create_scroll_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(True)
        
    
            
    def extract(self):
        b = True
        dlg = KF_dialogue()
        if dlg.exec():
            self.kf_method = dlg.kf_met

            kfs = self.find_kfs()
            if len(kfs) >0:
                b = show_dialogue()
            if b:
                v1 = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx]
                
                if self.kf_method == "Regular":
                    rate_str = dlg.e1.text()
                    sampling_rate = int(rate_str)
                    v1.extract_frames_regularly(sampling_rate)

                elif self.kf_method == "Network":
                    v1.cleanSequence()

        else:
            self.kf_method = dlg.kf_met
            
        self.populate_scrollbar()

            

                