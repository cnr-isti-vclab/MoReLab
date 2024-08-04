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
        self.movie_paths = []
        self.selected_movie_idx = -1
        self.movie_caps = []
        self.ctrl_wdg = parent
        self.global_display_bool = []
        self.items = []
        self.setMinimumSize(self.ctrl_wdg.monitor_width*0.15, self.ctrl_wdg.monitor_height*0.7)
        self.itemClicked.connect(self.select_movie_child)
        
    def add_movie(self, movie_path, fps=0, n_frames=0, duration=0, width=0, height=0):
        # self.ctrl_wdg.main_file.logfile.info("Adding a new movie "+movie_path)
        self.movie_paths.append(movie_path)
        v = Video(movie_path)
        self.movie_caps.append(v)
        self.global_display_bool.append([False, False])
        if v.cap_exist:
            v.video_summary()
        else:
            v.fps, v.n_frames, v.duration, v.width, v.height = fps, n_frames, duration, width, height
            
        movie_name = movie_path.split('/')[-1]
        item = QTreeWidgetItem([str(movie_name)])
        item.addChild(QTreeWidgetItem(["FPS", str(v.fps)]))
        item.addChild(QTreeWidgetItem(["Total frames", str(v.n_frames)]))
        item.addChild(QTreeWidgetItem(["Duration", str(v.duration)]))
        item.addChild(QTreeWidgetItem(["Resolution", str(v.width) + ' X ' +str(v.height)]))

        self.items.append(item)
        
        self.insertTopLevelItems(len(self.movie_paths) - 1, [item])
        self.select_movie_child(item)
            
        return v
        
        
        
    def deselect_movies(self):
        if len(self.items) > 0:
            for i,item in enumerate(self.items):
                item.setSelected(False)
        
        
    def select_movie_child(self, selection):
        if selection in self.items:
            temp_idx = self.items.index(selection)
            if temp_idx != self.selected_movie_idx:
                # self.ctrl_wdg.main_file.logfile.info("Selected the movie number "+str(temp_idx+1)+" ....")
                self.selected_movie_idx = temp_idx
                self.ctrl_wdg.selected_thumbnail_index = -1
                self.select_movie()
                # self.ctrl_wdg.gl_viewer.obj.compute_sfm()


    def select_movie(self, disp_idx = -1): # assuming that selected movie_idx has already been set
        if self.selected_movie_idx != -1:
            self.deselect_movies()
            self.items[self.selected_movie_idx].setSelected(True)
            self.ctrl_wdg.set_kf_method()
            self.ctrl_wdg.ui.setClick()
            self.ctrl_wdg.populate_scrollbar(disp_idx)
                