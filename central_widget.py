"""
Created on Mon Mar 28 17:25:39 2022
@author: arslan
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from util.util import Video, convert_cv_qt
import json, os
import cv2


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
        self.out_dir = 'extracted_images'
        self.kf_extracted_bool = False
        self.selected_thumbnail_index = 0
        self.thumbnail_height = 64
        self.thumbnail_width = 104
        
        self.displayImage_height = 300
        self.displayImage_width = 400
        
        self.create_wdg1()
        self.create_wdg3()
        self.create_wdg4()
        self.create_buttons()
        self.create_scroll_area()
        
        
    def create_wdg1(self):
        self.summary_wdg = QLabel("")
        self.summary_wdg.setStyleSheet("border: 1px solid gray;")
        self.summary_wdg.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
    def create_buttons(self):
        self.btn_kf = QPushButton("Extract Key-frames")
                   

    def create_wdg3(self):
        self.wdg3 = QLabel("Image Window", self)
        self.wdg3.setStyleSheet("border: 1px solid gray;")
        self.wdg3.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def create_wdg4(self):
        self.wdg4 = QLabel('Object \n Window ', self)
        self.wdg4.setStyleSheet("border: 1px solid gray;")
        self.wdg4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
    
    def extract_frames(self):
        if self.selected_movie_path != "":
            self.kf_extracted_bool = True
            v = Video(self.selected_movie_path)
            self.extracted_frames = v.extract_frames_regularly()
            
            if not os.path.exists(self.out_dir):
                os.mkdir(self.out_dir)
            
            for i, img in enumerate(self.extracted_frames):
                out_path = os.path.join(self.out_dir, str(i).zfill(6)+'.png')
                cv2.imwrite(out_path, img)
            
            self.populate_scrollbar()
            
            
    def populate_scrollbar(self):
        self.widget = QWidget()                 
        self.grid_layout = QHBoxLayout()
        row_in_grid_layout = 0
        for i, img in enumerate(self.extracted_frames):
            img_label = QLabel("")
            img_label.setAlignment(Qt.AlignCenter)
            text_label = QLabel("")
            text_label.setAlignment(Qt.AlignCenter)
            # text_label.setText(str(i))
            pixmap_scaled = convert_cv_qt(img, self.thumbnail_width, self.thumbnail_height)
            img_label.setPixmap(pixmap_scaled)

            img_label.mousePressEvent = lambda e, index=row_in_grid_layout, file_img=img: \
                self.on_thumbnail_click(e, index, file_img)
            
            thumbnail = QBoxLayout(QBoxLayout.TopToBottom)
            thumbnail.addWidget(img_label)
            thumbnail.addWidget(text_label)
            self.grid_layout.addLayout(thumbnail)
            row_in_grid_layout += 1
        self.widget.setLayout(self.grid_layout)
        
        self.scroll_area.setWidget(self.widget)
            
            
    def on_thumbnail_click(self, event, index, img_file):
        self.displayThumbnail(index, img_file)
    
        
    def displayThumbnail(self, index, img_file):
        self.selected_thumbnail_index = index
        ## Deselect all thumbnails in the image selector
        for text_label_index in range(len(self.grid_layout)):
            # print(text_label_index)
            text_label = self.grid_layout.itemAt(text_label_index).itemAt(1).widget()
            text_label.setStyleSheet("background-color:none;")

        ## Select the single clicked thumbnail
        text_label_of_thumbnail = self.grid_layout.itemAt(index)\
            .itemAt(1).widget()
        text_label_of_thumbnail.setStyleSheet("background-color:blue;")
        
        # print("Selected image index : "+str(index))
        
        p = convert_cv_qt(self.extracted_frames[index], self.displayImage_width , self.displayImage_height )
        self.wdg3.setPixmap(p)

        

    def create_scroll_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(True)
    
    def select_movie(self, btn):
        for bt in self.movie_buttons:
            bt.setStyleSheet("color: black; border: none;")
        btn.setStyleSheet("color: blue; border: 1px solid blue;")
        name = btn.text()
        
        for p in self.movie_paths:
            if p.split('/')[-1] == name:
                self.selected_movie_path = p
        
        v = Video(self.selected_movie_path)
        self.summary_wdg.setText(v.video_summary())
        
    def get_data(self):
        if self.kf_extracted_bool:
            data = {
                "movies" : self.movie_paths,
                "key_frames" : self.kf_extracted_bool,
                "displayIndex": self.selected_thumbnail_index
                }
        else:
            data = {
                "movies" : self.movie_paths,
                "key_frames" : self.kf_extracted_bool
                }
        return data