from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from util.video import Video
from util.photoviewer import PhotoViewer
from util.kf_dialogue import KF_dialogue
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


    def create_wdg4(self):
        self.wdg4 = QLabel('Object \n Window ', self)
        self.wdg4.setStyleSheet("border: 1px solid gray;")
        self.wdg4.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
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
        if self.viewer.obj.cross_hair:
            self.viewer.obj.hide_features(True)
        else:
            self.viewer.obj.hide_features(False)
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
        
        # print("Selected image index : "+str(index))
        
        p = self.viewer.convert_cv_qt(img_file, img_file.shape[1] , img_file.shape[0] )
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

    def switch_kf_method(self):
        kfs_regular = self.movie_caps[self.selected_movie_idx].key_frames_regular
        kfs_network = self.movie_caps[self.selected_movie_idx].key_frames_network
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
            
            if len(self.movie_caps[i].key_frames_regular) > 0:
                path_regular = os.path.join(video_folder_path , 'Regular')
                if not os.path.exists(path_regular):
                    os.makedirs(path_regular)
                    
                for j, img in enumerate(self.movie_caps[i].key_frames_regular):
                    img_path = os.path.join(path_regular, self.movie_caps[i].key_frame_indices_regular[j] +'.png')
                    cv2.imwrite(img_path, img)
                    
            if len(self.movie_caps[i].key_frames_network) > 0:
                path_network = os.path.join(video_folder_path , 'Network')
                if not os.path.exists(path_network):
                    os.makedirs(path_network)
                for j, img in enumerate(self.movie_caps[i].key_frames_network):
                    img_path = os.path.join(path_network, self.movie_caps[i].key_frame_indices_network[j] +'.png')
                    cv2.imwrite(img_path, img)
        
    def get_data(self):
        data = {
            "movies" : self.movie_paths,
            "selected_movie" : self.selected_movie_path,
            "selected_kf_method" : self.kf_method,
            "displayIndex": self.selected_thumbnail_index
            }
        return data
    
    def load_data(self, project_path):
        with open (project_path) as myfile:
            data=json.load(myfile)
            
        self.movie_paths = data["movies"]
        self.selected_movie_path = data["selected_movie"]
        self.kf_method = data["selected_kf_method"]
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
                    
                    img_names_regular = sorted(glob.glob(movie_dirr+'/Regular/*.png'))
                    v.key_frames_regular = [cv2.imread(x) for x in img_names_regular]
                    
                    img_names_network = sorted(glob.glob(movie_dirr+'/Network/*.png'))
                    v.key_frames_network = [cv2.imread(x) for x in img_names_network]
            
        self.select_movie(self.selected_movie_path)
        
        if self.selected_thumbnail_index != -1:
            self.displayThumbnail(self.selected_thumbnail_index)
            
    
            
    def extract(self):
        b = True
        dlg = KF_dialogue()
        if dlg.exec():
            self.kf_method = dlg.kf_met

            kfs = self.find_kfs()
            if len(kfs) >0:
                b = self.show_dialogue()
            if b:
                
                v = Video(self.selected_movie_path)
                v1 = self.movie_caps[self.selected_movie_idx]
                
                if self.kf_method == "Regular":
                    rate_str = dlg.e1.text()
                    sampling_rate = int(rate_str)
                    v1.key_frames_regular, v1.key_frame_indices_regular, v1.features_regular, v1.feature_labels_regular, v1.n_objects_kf_regular = v.extract_frames_regularly(sampling_rate)


                elif self.kf_method == "Network":
                    v1.key_frames_network, v1.key_frame_indices_network, v1.features_network, v1.feature_labels_network, v1.n_objects_kf_network = v.cleanSequence()

        else:
            self.kf_method = dlg.kf_met
            
        self.populate_scrollbar()

            

                