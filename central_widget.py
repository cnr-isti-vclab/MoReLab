from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from util.video import Video
from util.photoviewer import PhotoViewer
from util.kf_dialogue import KF_dialogue
from util.util import show_dialogue, copy_dialogue
from document import Document
from movie_panel import MoviePanel
from GL_widget_viewer import GL_Widget
from quad import Quad_Tool

import json, os, glob
import cv2, pyautogui
import numpy as np



class Widget(QWidget):
    def __init__(self):
        super().__init__()
            
        self.selected_thumbnail_index = -1
        self.monitor_width = pyautogui.size()[0]
        self.monitor_height = pyautogui.size()[1]

        self.create_scroll_area()
        self.gl_viewer = GL_Widget(self)
        # self.gt_viewer = GT_Widget(self)
        
        self.doc = Document(self)
        self.mv_panel = MoviePanel(self)
        self.quad_obj = Quad_Tool(self)
        self.create_wdg1()
        
        self.thumbnail_text_stylesheet = """color:black;
                                 font-weight:bold;
                                 background-color:none;"""
        self.thumbnail_height = 96
        self.thumbnail_width = 120
        self.kf_method = ""
        self.copied_data = {}
        

        
    def create_wdg1(self):
        self.btn_kf = QPushButton("Extract Key-frames")
        self.btn_kf.setStyleSheet("""
                                  QPushButton:hover   { background-color: rgb(145,224,255)}
                                  QPushButton {background-color: rgb(230,230,230); border-radius: 20px; padding: 15px; border: 1px solid black; color:black; font-size: 15px;}
                                  """)
        self.btn_kf.clicked.connect(self.extract)


        # self.scale_up_btn = QPushButton("Copy features")
        # self.scale_up_btn.clicked.connect(self.copy_features)
       
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
            pixmap_scaled = self.gl_viewer.convert_cv_qt(img, self.thumbnail_width, self.thumbnail_height)
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
        self.gl_viewer.obj.wdg_tree.clear()
            
            
    def on_thumbnail_click(self, event, index):
        self.displayThumbnail(index)
    
        
    def displayThumbnail(self, index):
        self.selected_thumbnail_index = index
        ## Deselect all thumbnails in the image selector
        for text_label_index in range(len(self.grid_layout)):
            # print(text_label_index)
            text_label = self.grid_layout.itemAt(text_label_index).itemAt(1).widget()
            text_label.setStyleSheet(self.thumbnail_text_stylesheet)

        ## Select the single clicked thumbnail
        text_label_of_thumbnail = self.grid_layout.itemAt(index).itemAt(1).widget()
        text_label_of_thumbnail.setStyleSheet("background-color:rgb(135, 206, 235);"
                                              "font-weight:bold;")
        
        if self.kf_method == "Regular":    
            img_file = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_regular[self.selected_thumbnail_index]
        elif self.kf_method == "Network":
            img_file = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_network[self.selected_thumbnail_index]
        
        # print(img_file.shape)
        self.gl_viewer.setPhoto(img_file)
        self.gl_viewer.obj.selected_feature_index = 0
        self.gl_viewer.obj.display_data()
        self.gl_viewer.obj.selected_feature_index = -1
        self.gl_viewer.obj.wdg_tree.deselect_features()

        

    def create_scroll_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumSize(self.monitor_width*0.56, self.monitor_height*0.13)
        
    
            
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

                self.populate_scrollbar()
                self.gl_viewer.obj.labels = []
                self.gl_viewer.obj.locs = []
                self.gl_viewer.obj.associated_frames = []
                self.gl_viewer.obj.associated_videos = []
                
                # self.associated_frames2 = [[]]
                self.gl_viewer.obj.selected_feature_index =-1
                self.gl_viewer.obj.count_ = 0
                
                self.gl_viewer.obj.features_data = {}

        else:
            self.kf_method = dlg.kf_met
            
            
    def copy_features(self):
        # print("Copy features")
        t = self.selected_thumbnail_index
        if t != -1:
            self.copied_data = {"img_index" : t}
            copy_dialogue()
        else:
            self.copied_data = {}
            print("No image selected")
        
    def paste_features(self):
        # print("Past features")
        if len(self.copied_data)==0:
            print("Data not copied")
        else:
            v = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx]
            t = self.copied_data["img_index"]
            if t == self.selected_thumbnail_index:
                print("Same image")
            else:
                if self.kf_method == "Regular":
                    for i, fc in enumerate(v.features_regular[t]):
                        if not v.hide_regular[t][i]:
                            self.gl_viewer.obj.add_feature(fc.x_loc, fc.y_loc)
                        else:
                            self.gl_viewer.obj.add_feature(fc.x_loc, fc.y_loc)
                            self.gl_viewer.obj.selected_feature_index = i
                            self.gl_viewer.obj.delete_feature()
                elif self.kf_method == "Network":
                    for i, fc in enumerate(v.features_network[t]):
                        if not v.hide_network[t][i]:
                            self.gl_viewer.obj.add_feature(fc.x_loc, fc.y_loc)
                        else:
                            v.hide_network[self.selected_thumbnail_index].append(True)
                            v.n_objects_kf_network[self.selected_thumbnail_index] += 1

                        