from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from util.video import Video
from util.util import split_path


class MoviePanel(QTreeWidget):
    def __init__(self, parent):
        super().__init__()
        self.setColumnCount(2)
        self.setHeaderLabels(["Movies", "Info"])
        self.selected_movie_path = ""
        self.movie_paths = []
        self.selected_movie_idx = -1
        self.movie_caps = []
        self.ctrl_wdg = parent
        self.items = []
        self.itemClicked.connect(self.select_movie)
    
    
    
    def add_movie(self, movie_path):
        self.movie_paths.append(movie_path)
        v = Video(movie_path)
        self.movie_caps.append(v)
        v.video_summary()
        movie_name = split_path(movie_path)
        
        item = QTreeWidgetItem([str(movie_name)])
        item.addChild(QTreeWidgetItem(["FPS", str(v.fps)]))
        item.addChild(QTreeWidgetItem(["Total frames", str(v.n_frames)]))
        item.addChild(QTreeWidgetItem(["Duration", str(v.duration)]))
        item.addChild(QTreeWidgetItem(["Resolution", str(v.width) + ' X ' +str(v.height)]))

        self.items.append(item)
        
        self.insertTopLevelItems(len(self.movie_paths) - 1, [item])
        self.select_movie(item)
        
        
    def deselect_movies(self):
        if len(self.items) > 0:
            for i,item in enumerate(self.items):
                item.setSelected(False)
                
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
            self.ctrl_wdg.kf_method = "Regular"
        elif len(kfs_regular) == 0 and len(kfs_network) > 0:
            self.ctrl_wdg.kf_method = "Network"            
                
    
                
    def select_movie(self, selection):
        self.deselect_movies()
        self.ctrl_wdg.viewer.obj.hide_features(False)
        
        self.selected_movie_idx = self.items.index(selection)
        self.selected_movie_path = self.movie_paths[self.selected_movie_idx]
        
        # print("selected : "+str(self.selected_movie_idx))
                
        self.switch_kf_method()        
        self.items[self.selected_movie_idx].setSelected(True)
        self.ctrl_wdg.populate_scrollbar()
        
        self.ctrl_wdg.gl_viewer.setPhoto()
        # self.ctrl_wdg.viewer.obj.display_data()
        
    
