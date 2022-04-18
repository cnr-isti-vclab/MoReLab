"""
Created on Mon Mar 28 17:25:39 2022
@author: arslan
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from util.util import Video, convert_cv_qt, PhotoViewer
import json, os, glob
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
        self.selected_thumbnail_index = -1
        self.selected_movie_idx = -1
        self.movie_caps = []
        self.viewer = PhotoViewer(self)
        self.thumbnail_height = 64
        self.thumbnail_width = 104
        
        
        self.create_wdg1()
        # self.create_wdg3()
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
            v = self.movie_caps[self.selected_movie_idx]
            v.extract_frames_regularly()
            
            self.populate_scrollbar()
            
            
    def populate_scrollbar(self):
        widget = QWidget()                 
        self.grid_layout = QHBoxLayout()
        row_in_grid_layout = 0
        for i, img in enumerate(self.movie_caps[self.selected_movie_idx].key_frames):
            img_label = QLabel("")
            img_label.setAlignment(Qt.AlignCenter)
            text_label = QLabel("")
            text_label.setAlignment(Qt.AlignCenter)
            # text_label.setText(str(i))
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
        
        self.scroll_area.setWidget(widget)
            
            
    def on_thumbnail_click(self, event, index):
        self.displayThumbnail(index)
    
        
    def displayThumbnail(self, index):
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
        
        img_file = self.movie_caps[self.selected_movie_idx].key_frames[self.selected_thumbnail_index]
        
        # print("Selected image index : "+str(index))
        p = convert_cv_qt(img_file, img_file.shape[1] , img_file.shape[0] )
        self.viewer.setPhoto(p)
        # self.wdg3.setPixmap(self.viewer.setPhoto(p))

        

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

                
    
    def select_movie(self, movie_path):
        self.deselect_movies()
        for i,p in enumerate(self.movie_paths):
            if p == movie_path:
                self.selected_movie_path = p
                self.selected_movie_idx = i
                
                
        self.movie_buttons[self.selected_movie_idx].setStyleSheet("color: blue; border: 1px solid blue;")
        v = self.movie_caps[self.selected_movie_idx]
        self.summary_wdg.setText(v.video_summary())
        if len(v.key_frames) >0:
            self.populate_scrollbar()
        else:
            self.scroll_area.setWidget(QLabel(""))
        self.viewer.setPhoto()
        
        
    def show_dialogue(self):
        msgBox = QMessageBox()
        msgBox.setText("Are you sure you want to extract key-frames again ?")
        msgBox.setWindowTitle("Key-frame extraction")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        # msgBox.buttonClicked.connect(msgButtonClick)
         
        returnValue = msgBox.exec()
        b = False
        if returnValue == QMessageBox.Yes:
           b = True

        return b

    def save_directory(self, name_project):
        out_dir = os.path.join(name_project.split('.')[0], 'extracted_frames')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for i, p in enumerate(self.movie_paths):
            video_folder = p.split('/')[-1].split('.')[0]
            video_folder_path = os.path.join(out_dir, video_folder)
            if len(self.movie_caps[i].key_frames) > 0:
                if not os.path.exists(video_folder_path):
                    os.makedirs(video_folder_path)
                for j, img in enumerate(self.movie_caps[i].key_frames):
                    img_path = os.path.join(video_folder_path, self.movie_caps[i].key_frame_indices[j] +'.png')
                    cv2.imwrite(img_path, img)
        
    def get_data(self):
        data = {
            "movies" : self.movie_paths,
            "selected_movie" : self.selected_movie_path, 
            "displayIndex": self.selected_thumbnail_index
            }
        return data
    
    def load_data(self, project_path):
        with open (project_path) as myfile:
            data=json.load(myfile)
            
        self.movie_paths = data["movies"]
        self.selected_movie_path = data["selected_movie"]
        self.selected_thumbnail_index = data["displayIndex"]
        
        a = os.path.join(project_path.split('.')[0], 'extracted_frames')
        movie_dirs = os.listdir(a)
 
        for i,p in enumerate(self.movie_paths):
            movie_name = p.split('/')[-1]
            btn = QPushButton(movie_name)
            self.movie_buttons.append(btn)
            v = Video(p)
            self.movie_caps.append(v)
            self.summary_wdg.setText(v.video_summary())
            
            for j,mv in enumerate(movie_dirs):
                if movie_name.split('.')[0] == mv:
                    movie_dirr = os.path.join(a, mv)
                    img_names = sorted(glob.glob(movie_dirr+'/*.png'))
                    v.key_frames = [cv2.imread(x) for x in img_names]
            
        self.select_movie(self.selected_movie_path)
        self.populate_scrollbar()
        if self.selected_thumbnail_index != -1:
            self.displayThumbnail(self.selected_thumbnail_index)