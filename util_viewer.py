from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import Image
from PIL.ImageQt import ImageQt 
import cv2
import numpy as np


class Util_viewer(QWidget):
    def __init__(self, parent=None):
        # Widget.__init__(self, parent)
        super().__init__(parent)
        self.parent_viewer = parent
        
        self.aspect_image = 0
        self.aspect_widget = self.parent_viewer.width()/self.parent_viewer.height()
        self.opengl_intrinsics = np.eye(4)
        self.opengl_extrinsics = np.eye(4)
        self.dist_label = QLabel("Measured distance : "+str(0.00))
        self.dist_label.setMinimumSize(self.parent_viewer.obj.ctrl_wdg.monitor_width*0.2, self.parent_viewer.obj.ctrl_wdg.monitor_height*0.02)
        self.dist_label.setAlignment(Qt.AlignCenter)

        
        
        
    def setPhoto(self, image=None):
        if image is None:
            self.img_file = None
        else:
            self.aspect_image = image.shape[1]/image.shape[0]
            # print("Width : "+str(self.parent_viewer.width()))
            # print("Height : "+str(self.parent_viewer.height()))
            self.aspect_widget = self.parent_viewer.width()/self.parent_viewer.height()
            self.set_default_view_param()
            w = int(self.w2-self.w1)
            h = int(self.h2-self.h1)
            # print(image.shape)
            # print(w,h)
    
            image = cv2.resize(image, (w, h), interpolation = cv2.INTER_AREA)
            # print("Image size after resizing: Width: "+str(image.shape[1])+ " , Height: "+str(image.shape[0]))
            PIL_image = self.toImgPIL(image).convert('RGB')
            self.img_file = ImageQt(PIL_image)
    

    def toImgPIL(self, imgOpenCV=None):
        if imgOpenCV is None:
            return imgOpenCV
        else:
            return Image.fromarray(cv2.cvtColor(imgOpenCV, cv2.COLOR_BGR2RGB))
        
        
        
    def set_default_view_param(self):
        v = self.parent_viewer.obj.ctrl_wdg.mv_panel.movie_caps[self.parent_viewer.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        self.aspect_widget = self.parent_viewer.width()/self.parent_viewer.height()
        if self.aspect_image > self.aspect_widget:
            self.w1 = 0
            self.w2 = self.parent_viewer.width()

            diff = self.parent_viewer.height() - (self.parent_viewer.width()/v.width)*v.height
            self.h1 = diff/2
            self.h2 = self.parent_viewer.height() - self.h1
            
        else:
            diff = (self.aspect_widget - self.aspect_image)*self.parent_viewer.width()
            self.w1 = diff/2
            self.w2 = self.parent_viewer.width() - self.w1
            self.h1 = 0
            self.h2 = self.parent_viewer.height()
            
        self.parent_viewer.obj.feature_panel.wdg_to_img_space()
        
        
    def computeOpenGL_fromCV(self, K, Rt):
        zn = -1 #self.near
        zf = 1 #self.far
        d = zn - zf
        cx = K[0,2]
        cy = K[1,2]
        perspective = np.zeros((4,4))
        
        v = self.parent_viewer.obj.ctrl_wdg.mv_panel.movie_caps[self.parent_viewer.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        width = v.width*(self.parent_viewer.width()/(self.w2 - self.w1))
        height = v.height*(self.parent_viewer.height()/(self.h2-self.h1))


        perspective[0][0] =  2.0 * K[0,0] / width
        perspective[1][1] = -2.0 * K[1,1] / height
        perspective[2][0] =  1.0 - 2.0 * cx / width
        perspective[2][1] =  2.0 * cy / height -1.0
        perspective[2][2] =  (zf + zn) / d
        perspective[2][3] =  -1.0
        perspective[3][2] = 2.0 * zn * zf / d

        perspective = perspective.transpose()

        self.opengl_intrinsics = perspective
        #self.opengl_intrinsics = np.matmul(NDC, perspective)
        out = Rt.transpose()

        self.opengl_extrinsics = out #np.matmul(self.opengl_intrinsics, Rt)

    def create_calibration_panel(self):
        self.cal_dialog = QDialog()
        
        self.cal_dialog.setWindowTitle("Calibration panel")

        QBtn = QDialogButtonBox.Ok

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.cal_dialog.accept)
        
        label = QLabel("Enter measured distance : ")
        
        self.e1 = QLineEdit("1")
        self.e1.setValidator(QIntValidator())
        self.e1.setMaxLength(6)
        self.e1.setFont(QFont("Arial",20))
        
        self.cal_layout = QVBoxLayout()
        self.cal_layout.addWidget(label)
        self.cal_layout.addWidget(self.e1)
        self.cal_layout.addWidget(buttonBox)
        self.cal_dialog.setLayout(self.cal_layout)
        
        
    def set_distance(self, d):
        self.dist_label.setText("Measured distance : "+str(d))
        