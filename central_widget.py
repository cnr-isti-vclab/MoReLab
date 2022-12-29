from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from user_interface import UserInterface
from movie_panel import MoviePanel
from GL_widget_viewer import GL_Widget
from document import Document
from quad import Quad_Tool
from util.kf_dialogue import KF_dialogue
from util.util import *

import pyautogui



class Widget(QWidget):
    def __init__(self, parent=None):
        # Widget.__init__(self, parent)
        super().__init__(parent)
        self.kf_method = ""
        self.thumbnail_text_stylesheet = """color:black;
                                 font-weight:bold;
                                 background-color:none;"""
        self.thumbnail_height = 96
        self.thumbnail_width = 120
        self.selected_thumbnail_index = -1
        self.monitor_width = pyautogui.size()[0]
        self.monitor_height = pyautogui.size()[1]
        self.main_file = parent   
        self.gl_viewer = GL_Widget(self)
        self.doc = Document(self)

        self.ui = UserInterface(self)
        self.mv_panel = MoviePanel(self)
        self.quad_obj = Quad_Tool(self)
        self.copied_data = {}

        
        
        
    def find_kfs(self):
        if self.kf_method == "Regular":
            kfs = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_regular
        elif self.kf_method == "Network":
            kfs = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx].key_frames_network
        else:
            kfs = []
        return kfs


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
                # print(v1.n_frames)
                if self.kf_method == "Regular":
                    rate_str = dlg.e1.text()
                    sampling_rate = int(rate_str)
                    v1.extract_frames_regularly(sampling_rate)
                    self.ui.radiobutton1.setChecked(True)

                elif self.kf_method == "Network":
                    # print("Going to extract frames")
                    v1.cleanSequence()
                    # print(len(v1.key_frames_network))
                    self.ui.radiobutton2.setChecked(True)

                self.populate_scrollbar()

            else:
                self.kf_method = dlg.kf_met
            
            
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
        self.selected_thumbnail_index = -1
        self.gl_viewer.util_.setPhoto()
        self.gl_viewer.obj.feature_panel.display_data()

            
            
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

        self.gl_viewer.util_.setPhoto(img_file)
        self.gl_viewer.obj.feature_panel.selected_feature_idx = -1
        self.gl_viewer.obj.feature_panel.display_data()
        
        
    def copy_features(self):
        # print("Copy features")
        t = self.selected_thumbnail_index
        if t != -1:
            self.copied_data = {"img_index" : t,
                                "old_kf_method" : self.kf_method,
                                "old_movie_idx" : self.mv_panel.selected_movie_idx}
            copy_dialogue()
        else:
            noImage_dialogue()
        
    def paste_features(self):
        if len(self.copied_data)==0:
            copy_features_dialogue()
        else:
            v = self.mv_panel.movie_caps[self.mv_panel.selected_movie_idx]
            t = self.copied_data["img_index"]
            old_kf = self.copied_data["old_kf_method"]
            old_mv = self.copied_data["old_movie_idx"]
            
            if old_mv != self.mv_panel.selected_movie_idx:
                switch_movie_dialogue()
            else:
                if old_kf == "Regular" and self.kf_method == "Regular":
                    if v.n_objects_kf_regular[self.selected_thumbnail_index] == 0:
                        for i, fc in enumerate(v.features_regular[t]):
                            if not v.hide_regular[t][i]:
                                self.gl_viewer.obj.add_feature(fc.x_loc, fc.y_loc)
                            else:
                                self.gl_viewer.obj.add_feature(fc.x_loc, fc.y_loc)
                                self.gl_viewer.obj.selected_feature_idx = i
                                self.gl_viewer.obj.delete_feature()
                    else:
                        filledImage_dialogue()
                        
                elif old_kf == "Network" and self.kf_method == "Network":
                    if v.n_objects_kf_network[self.selected_thumbnail_index] == 0:
                        for i, fc in enumerate(v.features_network[t]):
                            if not v.hide_network[t][i]:
                                self.gl_viewer.obj.add_feature(fc.x_loc, fc.y_loc)
                            else:
                                self.gl_viewer.obj.add_feature(fc.x_loc, fc.y_loc)
                                self.gl_viewer.obj.feature_panel.selected_feature_idx = i
                                self.gl_viewer.obj.delete_feature()
                    else:
                        filledImage_dialogue()
                    
                else:
                    switch_kf_dialogue()