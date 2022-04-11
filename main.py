from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from central_widget import Widget, SliderFrame
from PyQt5.QtGui import *
import sys, os, sip, json, glob, cv2
from util.util import Video

# from datetime import datetime



class Window(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setWindowTitle('MoReLab' )
        self.widget = Widget()
        self.create_menu()
        self.create_statusbar()
        
        # self.create_layout()
        

    def create_layout(self):
        self.widget.btn_kf.clicked.connect(self.extract)
        self.vboxLayout1 = QVBoxLayout()
        self.vboxLayout3 = QVBoxLayout()
        for i,btn in enumerate(self.widget.movie_buttons):
            self.vboxLayout1.addWidget(btn, 1)
            btn.clicked.connect(self.make_calluser(btn))
            
        
        v1 = SliderFrame(self.vboxLayout1)
        self.vboxLayout3.addWidget(v1, 1)
        self.vboxLayout3.addWidget(self.widget.summary_wdg)
        self.vboxLayout3.addWidget(self.widget.btn_kf)
        
        self.vboxLayout2 = QVBoxLayout()
        self.vboxLayout2.addWidget(self.widget.scroll_area, 1)
        self.vboxLayout2.addWidget(self.widget.viewer , 4)
        
        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.addLayout(self.vboxLayout3)
        self.hboxLayout.addLayout(self.vboxLayout2)
        self.hboxLayout.addWidget(self.widget.wdg4)
        
        self.widget.setLayout(self.hboxLayout)
        self.setCentralWidget(self.widget)
            
        
    def create_menu(self):
        menuBar = self.menuBar()
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        editMenu = QMenu("&Edit", self)
        menuBar.addMenu(editMenu)
        editMenu = QMenu("&Help", self)
        menuBar.addMenu(editMenu)

        op_project = QAction("&Open Project", self)
        fileMenu.addAction(op_project)
        op_project.triggered.connect(self.open_project)
        op_project.setShortcut("ctrl+o")
        
        sv_project = QAction("&Save Project", self)
        fileMenu.addAction(sv_project)
        sv_project.triggered.connect(self.save_project)
        sv_project.setShortcut("ctrl+s")
        
        op_movie = QAction("&Open Movie", self)
        fileMenu.addAction(op_movie)
        op_movie.triggered.connect(self.open_movie)
        op_movie.setShortcut("ctrl+shift+o")
        
        
    def open_project(self):
        file_types = "json (*.json)"
        response = QFileDialog.getOpenFileName(
            parent = self,
            caption = 'Select project.',
            directory = os.getcwd(),
            filter = file_types
        )
        if response[0] != '':
            project_path = response[0]
            with open (project_path) as myfile:
                data=json.load(myfile)
                
            
            if data["key_frames"]:
                if not os.path.exists(self.widget.out_dir):
                    print("Please create a directory of extracted images and place atleast 5 images in it.")
                else:
                    # Load first column
                    self.widget.movie_paths = data["movies"]
                    for i, p in enumerate(self.widget.movie_paths):
                        if p == data["selected_movie"]:
                            btn = QPushButton(p.split('/')[-1])
                            self.widget.movie_buttons.append(btn)
                        else:
                            bt = QPushButton(p.split('/')[-1])
                            self.widget.movie_buttons.append(bt)                    
                        
                    self.create_layout()
                    self.widget.select_movie(btn)
                    
                    self.widget.kf_extracted_bool = True
                    self.widget.extracted_frames = []
                    file_names = sorted(glob.glob(self.widget.out_dir+'/*'))
                    if len(file_names) > 0:
                        for p in file_names:
                            self.widget.extracted_frames.append(cv2.imread(p))
                        
                        self.widget.populate_scrollbar()
                        
                    # Display thumbnail image
                    idx = data["displayIndex"]                 
                    self.widget.displayThumbnail(idx, self.widget.extracted_frames[idx])
            
            else:
                self.widget.movie_paths = data["movies"]
                for i, p in enumerate(self.widget.movie_paths):
                    bt = QPushButton(p.split('/')[-1])
                    bt.setStyleSheet("color: black; border: none;")
                    self.widget.movie_buttons.append(bt)                    
                    
                self.create_layout()
                

        
    def save_project(self):
        file_types = "json (*.json)"
        response = QFileDialog.getSaveFileName(
            parent = self,
            caption = 'Save project.',
            directory = os.getcwd(),
            filter = file_types
        )
        if response[0] != '':
            name_project = response[0]
            
            display_msg = "Saving "+name_project.split('/')[-1]
            self.statusBar.showMessage(display_msg, 2000)
            
            data = self.widget.get_data()
            json_object = json.dumps(data, indent = 4)
            with open(name_project, "w") as outfile:
                outfile.write(json_object)
                

        
    def open_movie(self):
        if len(self.widget.movie_buttons) > 0:
            for bt in self.widget.movie_buttons:
                bt.setStyleSheet("color: black; border: none;")
        file_types = "ASF (*.asf);;MP4 (*.mp4)"
        response = QFileDialog.getOpenFileName(
           parent = self,
           caption = 'Select movie file.',
           directory = os.getcwd(),
           filter = file_types
        )
        if response[0] != '':
            movie_name = response[0].split('/')[-1]
            btn = QPushButton(movie_name)
            self.widget.movie_buttons.append(btn)
            self.widget.movie_paths.append(response[0])
            self.widget.selected_movie_path = response[0]
            btn.setStyleSheet("color: blue; border: 1px solid blue;")
            
            v = Video(response[0])
            self.widget.summary_wdg.setText(v.video_summary())
            
            if len(self.widget.movie_buttons) == 1:
                self.create_layout()
            else:
                self.vboxLayout1.addWidget(btn, 1)
                btn.clicked.connect(self.make_calluser(btn))
                        
            display_msg = "Opened "+movie_name      
            self.statusBar.showMessage(display_msg, 2000)
        

        
    def create_statusbar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
    def extract(self):
        display_msg = "Extracting key-frames"
        self.statusBar.showMessage(display_msg, 2000)
        self.widget.extract_frames()
        
        
    def make_calluser(self, btn):
        def calluser():
            display_msg = "Selected "+btn.text()
            self.statusBar.showMessage(display_msg, 2000)
            self.widget.select_movie(btn)
        return calluser


if __name__=="__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
