import platform, os, glob, json
import cv2
from util.video import Video
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Document():
    def __init__(self, ctrl_wdg):
        super().__init__()
        self.ctrl_wdg = ctrl_wdg
        
        
        
        
    def get_data(self):
        data = {
            "movies" : self.ctrl_wdg.movie_paths,
            "selected_movie" : self.ctrl_wdg.selected_movie_path,
            "selected_kf_method" : self.ctrl_wdg.kf_method,
            "displayIndex": self.ctrl_wdg.selected_thumbnail_index
            }
        return data
    


    def split_path(self, complete_path):
        op_sys = platform.system()
        if op_sys == "Windows":
            split_path = complete_path.split('\\')[-1]
        else:
            split_path = complete_path.split('/')[-1]

        return split_path
    



    def save_directory(self, name_project):
        out_dir = os.path.join(name_project.split('.')[0], 'extracted_frames')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for i, p in enumerate(self.ctrl_wdg.movie_paths):
            aa = self.split_path(p)
            video_folder = aa.split('.')[0]
            video_folder_path = os.path.join(out_dir, video_folder)
            
            if len(self.ctrl_wdg.movie_caps[i].key_frames_regular) > 0:
                path_regular = os.path.join(video_folder_path , 'Regular')
                if not os.path.exists(path_regular):
                    os.makedirs(path_regular)
                    
                for j, img in enumerate(self.ctrl_wdg.movie_caps[i].key_frames_regular):
                    img_path = os.path.join(path_regular, self.ctrl_wdg.movie_caps[i].key_frame_indices_regular[j] +'.png')
                    cv2.imwrite(img_path, img)
                    
            if len(self.ctrl_wdg.movie_caps[i].key_frames_network) > 0:
                path_network = os.path.join(video_folder_path , 'Network')
                if not os.path.exists(path_network):
                    os.makedirs(path_network)
                for j, img in enumerate(self.ctrl_wdg.movie_caps[i].key_frames_network):
                    img_path = os.path.join(path_network, self.ctrl_wdg.movie_caps[i].key_frame_indices_network[j] +'.png')
                    cv2.imwrite(img_path, img)
                    
                    
                    
    def load_data(self, project_path):
        with open (project_path) as myfile:
            data=json.load(myfile)
            
        self.ctrl_wdg.movie_paths = data["movies"]
        self.ctrl_wdg.selected_movie_path = data["selected_movie"]
        self.ctrl_wdg.kf_method = data["selected_kf_method"]
        self.ctrl_wdg.selected_thumbnail_index = data["displayIndex"]
        
        a = os.path.join(project_path.split('.')[0], 'extracted_frames')
        movie_dirs = os.listdir(a)
    
        for i,p in enumerate(self.ctrl_wdg.movie_paths):
            movie_name = self.split_path(p)
            btn = QPushButton(movie_name)
            self.ctrl_wdg.movie_buttons.append(btn)
            v = Video(p)
            self.ctrl_wdg.movie_caps.append(v)
            self.ctrl_wdg.summary_wdg.setText(v.video_summary())
            
            for j,mv in enumerate(movie_dirs):
                if movie_name.split('.')[0] == mv:
                    movie_dirr = os.path.join(a, mv)
                    img_names_regular = sorted(glob.glob(movie_dirr+'/Regular/*.png'))
                    v.key_frames_regular = [cv2.imread(x) for x in img_names_regular]
                    
                    img_names_network = sorted(glob.glob(movie_dirr+'/Network/*.png'))
                    v.key_frames_network = [cv2.imread(x) for x in img_names_network]
            
        self.ctrl_wdg.select_movie(self.ctrl_wdg.selected_movie_path)
        
        if self.ctrl_wdg.selected_thumbnail_index != -1:
            self.ctrl_wdg.displayThumbnail(self.ctrl_wdg.selected_thumbnail_index)
