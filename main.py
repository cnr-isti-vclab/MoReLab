from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys, os, sip, json, glob, cv2
from central_widget import Widget, SliderFrame

from util.video import Video
from tools import Tools


class Window(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setWindowTitle('MoReLab' )
        self.showMaximized()
        self.widget = Widget()
        
        self.create_menu()
        self.create_statusbar()
        self.create_toolbar() 


    def create_layout(self):
        self.vboxLayout1 = QVBoxLayout()
        self.vboxLayout3 = QVBoxLayout()
        for i,btn in enumerate(self.widget.movie_buttons):
            self.vboxLayout1.addWidget(btn, 1)
            btn.clicked.connect(self.make_calluser(self.widget.movie_paths[i]))   
        
        v1 = SliderFrame(self.vboxLayout1)
        self.vboxLayout3.addWidget(v1, 1)
        self.vboxLayout3.addWidget(self.widget.summary_wdg)
        self.vboxLayout3.addWidget(self.widget.btn_kf)
        
        self.vboxLayout2 = QVBoxLayout()
        self.vboxLayout2.addWidget(self.widget.scroll_area, 1)
        self.vboxLayout2.addWidget(self.widget.viewer , 5)
        
        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.addLayout(self.vboxLayout3, 1 )
        self.hboxLayout.addLayout(self.vboxLayout2, 4)
        self.hboxLayout.addWidget(self.widget.viewer.obj.wdg_tree.tree, 2)
        
        self.widget.setLayout(self.hboxLayout)
        self.setCentralWidget(self.widget)
        
        
    def create_toolbar(self):
        toolbar = QToolBar("&ToolBar", self)
        self.addToolBar( Qt.TopToolBarArea , toolbar )
        toolbar.addAction(self.new_pr)
        toolbar.addAction(self.open_pr)
        toolbar.addAction(self.save_pr)
        toolbar.addAction(self.open_mov)
        toolbar.addAction(self.exit_pr)

        toolbar.addAction(self.widget.viewer.obj.mv_tool)
        toolbar.addAction(self.widget.viewer.obj.ft_tool)
        
        self.addToolBarBreak(Qt.TopToolBarArea) 

        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # self.project_name_label = QLabel(os.path.join(os.getcwd(), "Untitled.json"))
        self.project_name_label = QLabel("untitled.json")
        
        toolbar2 = QToolBar()
        self.addToolBar( Qt.TopToolBarArea , toolbar2)
        toolbar2.addWidget(left_spacer)
        toolbar2.addWidget(self.project_name_label)
        toolbar2.addWidget(right_spacer)  
               
        
    def create_menu(self):
        menuBar = self.menuBar()
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        
        self.new_pr = QAction(QIcon("./icons/new_project.png"),"&New",self)
        fileMenu.addAction(self.new_pr)
        self.new_pr.triggered.connect(self.new_project)
        self.new_pr.setShortcut("ctrl+n")
        

        self.open_pr = QAction(QIcon("./icons/open_project.png"),"&Open",self)
        fileMenu.addAction(self.open_pr)
        self.open_pr.triggered.connect(self.open_project)
        self.open_pr.setShortcut("ctrl+o")
        
        self.save_pr = QAction(QIcon("./icons/save_project.png"),"&Save",self)
        fileMenu.addAction(self.save_pr)
        self.save_pr.triggered.connect(self.save_project)
        self.save_pr.setShortcut("ctrl+s")
        
        self.open_mov = QAction(QIcon("./icons/open_movie.png"),"&Import Movie",self)
        fileMenu.addAction(self.open_mov)
        self.open_mov.triggered.connect(self.open_movie)
        self.open_mov.setShortcut("ctrl+shift+o")
        
        self.exit_pr = QAction(QIcon("./icons/exit_project.png"),"&Exit",self)
        fileMenu.addAction(self.exit_pr)
        self.exit_pr.triggered.connect(self.exit_project)
        self.exit_pr.setShortcut("Esc")
        

        
    
    def ask_save_dialogue(self):
        msgBox = QMessageBox()
        msgBox.setText("Do you want to save your current project ?")
        msgBox.setWindowTitle("Save project")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        # msgBox.buttonClicked.connect(msgButtonClick)
         
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
           self.save_project()

        
    def new_project(self):
        self.ask_save_dialogue()

        self.widget = Widget()
        # self.widget.viewer.obj = Tools(self.widget)
        self.setCentralWidget(self.widget)
        self.project_name_label.setText("untitled.json")
        
    def exit_project(self):
        self.close()
    
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
            self.widget.load_data(project_path)
            self.create_layout() 
            
            display_msg = "Opened "+project_path.split('/')[-1]
            self.statusBar.showMessage(display_msg, 2000)
        
    def save_project(self):
        if self.project_name_label.text() == 'untitled.json':
            file_types = "json (*.json)"
            self.save_response = QFileDialog.getSaveFileName(
                parent = self,
                caption = 'Save project.',
                directory = os.getcwd(),
                filter = file_types
            )
        if self.save_response[0] != '':
            name_project = self.save_response[0]
            self.project_name_label.setText(name_project.split('/')[-1])
            display_msg = "Saving "+name_project.split('/')[-1]
            self.statusBar.showMessage(display_msg, 2000)
            
            self.widget.save_directory(name_project)
            
            data = self.widget.get_data()
            json_object = json.dumps(data, indent = 4)
            with open(name_project, "w") as outfile:
                outfile.write(json_object)
                

        
    def open_movie(self):
        # file_types = "Video files (*.asf *.mp4 *.mov)"
        file_types = "Supported Video files (*.asf *.mp4 *.mov);; MP4 (*.mp4);; ASF (*.asf);; MOV(*.mov)"
        response = QFileDialog.getOpenFileName(
           parent = self,
           caption = 'Select movie file.',
           directory = os.getcwd(),
           filter = file_types
        )
        if response[0] != '':
            movie_path = os.path.relpath(response[0], os.getcwd())
            if movie_path in self.widget.movie_paths:
                msgBox = QMessageBox()
                msgBox.setText("This movie has already been loaded.")
                msgBox.setWindowTitle("Open movie")
                msgBox.setStandardButtons(QMessageBox.Ok)                 
                returnValue = msgBox.exec()
            else:
                movie_name = movie_path.split('/')[-1]
                display_msg = "Opened "+movie_name      
                self.statusBar.showMessage(display_msg, 2000)
                                
                btn = QPushButton(movie_name)
                self.widget.add_movie(movie_path, btn)
                self.widget.select_movie(movie_path)
                
                if len(self.widget.movie_buttons) == 1:
                    self.create_layout()
                else:
                    self.vboxLayout1.addWidget(btn, 1)
                    btn.clicked.connect(self.make_calluser(movie_path))        

        
    def create_statusbar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
    
        
    def make_calluser(self, movie_path):
        def calluser():
            movie_name = movie_path.split('/')[-1]
            display_msg = "Selected "+movie_name
            self.statusBar.showMessage(display_msg, 2000)
            self.widget.select_movie(movie_path)
        return calluser


if __name__=="__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
