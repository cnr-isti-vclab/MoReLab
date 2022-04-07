"""
Created on Mon Mar 28 17:25:39 2022
@author: arslan
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from util.util import Video
import json, os
import cv2


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        
        with open('input.json') as json_file:
            self.data = json.load(json_file)
            
        self.movie_path = ""
        # self.thumbnail_height = 64
        # self.thumbnail_width = 104
        
        # self.displayImage_height = 300
        # self.displayImage_width = 300
        
        self.create_wdg1()
        # self.create_wdg2()
        self.create_wdg3()
        self.create_wdg4()
        self.create_buttons()
        self.create_scroll_area()
        
        
    def create_wdg1(self):
        movies = self.data['Movies']
        self.movie_buttons = []
        for movie in movies:
            if not os.path.exists(movie):
                print(movie+" not found in folder but specified in input json.")
            else:
                movie_name = movie.split('/')[-1]
                btn = QPushButton(movie_name)
                # btn.clicked.connect(self.select_movie)
                self.movie_buttons.append(btn)
                btn.setStyleSheet("border: none;")
                   

    def create_wdg3(self):
        self.wdg3 = QLabel("Image Window", self)
        self.wdg3.setStyleSheet("border: 1px solid black;")
        self.wdg3.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def create_wdg4(self):
        self.wdg4 = QLabel('Object 01 \n Object 02 ', self)
        self.wdg4.setStyleSheet("border: 1px solid black;")
        self.wdg4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
    def create_buttons(self):
        self.btn_kf = QPushButton("Extract Key-frames")
        
    
    def extract_frames(self):
        if self.movie_path != "":          
            v = Video(self.movie_path)
            self.extracted_frames = v.extract_frames_regularly()
            self.n_frames = len(self.extracted_frames)
            
            self.widget = QWidget()                 
            self.grid_layout = QHBoxLayout()
            row_in_grid_layout = 0
            
            for i, img in enumerate(self.extracted_frames):
                img_label = QLabel("")
                img_label.setAlignment(Qt.AlignCenter)
                text_label = QLabel("")
                text_label.setAlignment(Qt.AlignCenter)
                # text_label.setText(str(i))
                pixmap_scaled = self.convert_cv_qt(img, self.data["Thumbnail"][0], self.data["Thumbnail"][1])
                img_label.setPixmap(pixmap_scaled)
                img_label.mousePressEvent = \
                    lambda e, \
                    index=row_in_grid_layout, \
                    file_img=img: \
                        self.on_thumbnail_click(e, index, file_img)
                
                thumbnail = QBoxLayout(QBoxLayout.TopToBottom)
                thumbnail.addWidget(img_label)
                thumbnail.addWidget(text_label)
                self.grid_layout.addLayout(thumbnail)
                row_in_grid_layout += 1
            self.widget.setLayout(self.grid_layout)
            
            self.scroll_area.setWidget(self.widget)
            
            
    def on_thumbnail_click(self, event, index, img_file):
        ## Deselect all thumbnails in the image selector
        for text_label_index in range(len(self.grid_layout)):
            # print(text_label_index)
            text_label = self.grid_layout.itemAt(text_label_index)\
                .itemAt(1).widget()
            text_label.setStyleSheet("background-color:none;")

        ## Select the single clicked thumbnail
        text_label_of_thumbnail = self.grid_layout.itemAt(index)\
            .itemAt(1).widget()
        text_label_of_thumbnail.setStyleSheet("background-color:blue;")
        
        print("Selected image index : "+str(index))
        
        p = self.convert_cv_qt(self.extracted_frames[index], self.data["DisplayImage"][0] , self.data["DisplayImage"][1] )
        self.wdg3.setPixmap(p)

        ## Update the display's image
        # self.display_image.update_display_image(img_file_path)
    
    def convert_cv_qt(self, cv_img, width, height):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(width, height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
        

    def create_scroll_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(True)
        