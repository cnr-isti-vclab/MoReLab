from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from central_widget import Widget
from PyQt5.QtGui import *
import sys, os
# from datetime import datetime



class SliderFrame(QFrame):
    def __init__(self, myslider):
        QFrame.__init__(self)
    
        self.setStyleSheet("border: 1px solid black; margin: 0px; padding: 0px;")
    
        self.layout = QVBoxLayout()
        self.layout.addLayout(myslider)
        self.layout.setContentsMargins(0, 0, 0, 0)
    
        self.setLayout(self.layout)



class Window(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setWindowTitle('MoReLab' )
        self.widget = Widget()
        # self.setStyleSheet('background-color:gray')
        self.create_menu()
        self.create_statusbar()
        
        self.create_layout()
        
    

    def make_calluser(self, btn):
        def calluser():
            for bt in self.widget.movie_buttons:
                bt.setStyleSheet("color: black; border: none;")
            btn.setStyleSheet("color: blue; border: 1px solid blue;")
            self.widget.movie_path = 'sample_movies/'+btn.text()
            display_msg = "Selected "+btn.text()
            # print(movie_path)
            self.statusBar.showMessage(display_msg, 2000)
        return calluser

    def create_layout(self):
        self.widget.btn_kf.clicked.connect(self.extract)
        vboxLayout1 = QVBoxLayout()
        vboxLayout3 = QVBoxLayout()
        for i,btn in enumerate(self.widget.movie_buttons):
            vboxLayout1.addWidget(btn, 1)
            btn.clicked.connect(self.make_calluser(btn))
            
        
        v1 = SliderFrame(vboxLayout1)
        vboxLayout3.addWidget(v1, 1)
        # vboxLayout3.addLayout(vboxLayout1 , 1)
        
        vboxLayout3.addWidget(self.widget.btn_kf, 3)
        
        vboxLayout2 = QVBoxLayout()
        # vboxLayout.setContentsMargins(0,0,0,0)
        # vboxLayout2.addLayout(hboxLayout2)
        vboxLayout2.addWidget(self.widget.scroll_area, 1)
        vboxLayout2.addWidget(self.widget.wdg3, 4)
        

        
        # Outer main layout
        hboxLayout = QHBoxLayout()
        hboxLayout.addLayout(vboxLayout3)
        # hboxLayout.addWidget(self.widget.scroll)
        # hboxLayout.addWidget(self.scroll_area)
        hboxLayout.addLayout(vboxLayout2)
        hboxLayout.addWidget(self.widget.wdg4)
        
        self.widget.setLayout(hboxLayout)
        self.setCentralWidget(self.widget)
        
    def extract(self):
        display_msg = "Extracting key-frames"
        self.statusBar.showMessage(display_msg, 2000)
        self.widget.extract_frames()
    
            
        
    def create_menu(self):
        menuBar = self.menuBar()
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        editMenu = QMenu("&Edit", self)
        menuBar.addMenu(editMenu)
        editMenu = QMenu("&Help", self)
        menuBar.addMenu(editMenu)

        fileMenu.addAction(QAction("&New Project", self))
        op_project = QAction("&Open Project", self)
        fileMenu.addAction(op_project)
        op_project.triggered.connect(self.open_project)
        
        op_movie = QAction("&Open Movie", self)
        fileMenu.addAction(op_movie)
        op_movie.triggered.connect(self.open_movie)
        
        
    def open_project(self):
        dialog = QFileDialog.getOpenFileName(
            parent = self,
            caption = 'Select project.',
            directory = os.getcwd()
        )
        
    def open_movie(self):
        for bt in self.widget.movie_buttons:
            bt.setStyleSheet("color: black; border: none;")
        files_types = "ASF (*.asf);;MP4 (*.mp4)"
        response = QFileDialog.getOpenFileName(
           parent = self,
           caption = 'Select movie file.',
           directory = os.getcwd(),
           filter = files_types
        )
        # print(response)
        self.widget.movie_path = response[0]
        display_msg = "Selected "+self.widget.movie_path.split('/')[-1]
        # print(movie_path)
        self.statusBar.showMessage(display_msg, 2000)
        

        
    def create_statusbar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        # self.statusBar.showMessage("This is a status bar.")


if __name__=="__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
