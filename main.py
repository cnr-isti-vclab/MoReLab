from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys, os, sip, json, glob, cv2
from central_widget import Widget
from util.util import movie_dialogue, split_path

from util.video import Video
from tools import Tools



class Window(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setWindowTitle('MoReLab')
        self.showMaximized()
        self.widget = Widget()
        
        
        self.create_menu()
        self.create_statusbar()
        self.create_toolbar()


    def create_layout(self):
        self.vboxLayout3 = QVBoxLayout()
        self.vboxLayout3.addWidget(self.widget.mv_panel)
        self.vboxLayout3.addWidget(self.widget.btn_kf)
        
        self.vboxLayout2 = QVBoxLayout()
        self.vboxLayout2.addWidget(self.widget.scroll_area, 1)
        self.vboxLayout2.addWidget(self.widget.viewer , 5)
        
        vert1 = QVBoxLayout()
        vert1.addWidget(self.widget.viewer.obj.wdg_tree)
        vert1.addWidget(self.widget.viewer.obj.cam_btn)
        
        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.addLayout(self.vboxLayout3, 1 )
        self.hboxLayout.addLayout(self.vboxLayout2, 4)
        self.hboxLayout.addLayout(vert1, 2)
        
        self.widget.setLayout(self.hboxLayout)
        self.setCentralWidget(self.widget)
        
        
    def create_toolbar(self):
        toolbar = QToolBar("&ToolBar", self)
        self.addToolBar(Qt.TopToolBarArea , toolbar )

        
        
        # self.om_tool = self.newButton("open_movie.png",     "Open Movie",  flatbuttonstyle1, self.open_movie)
        
        self.widget.viewer.obj.np_tool.clicked.connect(self.new_project)
        self.widget.viewer.obj.op_tool.clicked.connect(self.open_project)
        self.widget.viewer.obj.om_tool.clicked.connect(self.open_movie)
        self.widget.viewer.obj.sp_tool.clicked.connect(self.save_project)
        self.widget.viewer.obj.sp_as_tool.clicked.connect(self.save_as_project)
        self.widget.viewer.obj.ep_tool.clicked.connect(self.exit_project)
        

        toolbar.addWidget(self.widget.viewer.obj.np_tool)
        toolbar.addWidget(self.widget.viewer.obj.op_tool)
        toolbar.addWidget(self.widget.viewer.obj.om_tool)
        # toolbar.addWidget(self.widget.viewer.obj.om_tool)
        toolbar.addWidget(self.widget.viewer.obj.sp_tool)
        toolbar.addWidget(self.widget.viewer.obj.sp_as_tool)
        toolbar.addWidget(self.widget.viewer.obj.ep_tool)
        toolbar.addWidget(self.widget.viewer.obj.mv_tool)
        toolbar.addWidget(self.widget.viewer.obj.ft_tool)
        
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
        
        self.save_as = QAction(QIcon("./icons/save_as.png"),"&Save as",self)
        fileMenu.addAction(self.save_as)
        self.save_as.triggered.connect(self.save_as_project)
        self.save_as.setShortcut("ctrl+shift+s")
        
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
            
            name_project = os.path.relpath(project_path, os.getcwd())
            disp_name_project = split_path(name_project)
            self.project_name_label.setText(disp_name_project)
            
            self.widget.doc.load_data(project_path)
            self.create_layout() 
            
            display_msg = "Opened "+split_path(project_path)
            self.statusBar.showMessage(display_msg, 2000)
            
    
    def implement_save(self, p):
        name_project = os.path.relpath(p, os.getcwd())
        
        disp_name_project = split_path(name_project)
        
        display_msg = "Saving "+disp_name_project
        self.statusBar.showMessage(display_msg, 2000)
        
        self.widget.doc.save_directory(name_project)
        
        data = self.widget.doc.get_data()
        json_object = json.dumps(data, indent = 4)
        with open(name_project, "w") as outfile:
            outfile.write(json_object)        
    
    
        
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
            name_project = os.path.relpath(self.save_response[0], os.getcwd())
            disp_name_project = split_path(name_project)
            self.project_name_label.setText(disp_name_project)

            self.implement_save(self.save_response[0])

                
                
    def save_as_project(self):
        if self.project_name_label.text() == 'untitled.json':
            self.save_project()
        else:
            file_types = "json (*.json)"
            save_as_response = QFileDialog.getSaveFileName(
                parent = self,
                caption = 'Save as.',
                directory = os.getcwd(),
                filter = file_types
            )
            if save_as_response[0] != '':
                self.implement_save(save_as_response[0])        

        
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
            if movie_path in self.widget.mv_panel.movie_paths:
                movie_dialogue()
            else:
                movie_name = split_path(movie_path)
                display_msg = "Opened "+movie_name      
                self.statusBar.showMessage(display_msg, 2000)
                self.widget.mv_panel.add_movie(movie_path)
                
                if len(self.widget.mv_panel.movie_paths) == 1:
                    self.create_layout()      

        
    def create_statusbar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
    


if __name__=="__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
