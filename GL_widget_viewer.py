from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *


from OpenGL.GL import *
from OpenGL import GLU
from OpenGL.arrays import vbo
from tools import Tools


import cv2, sys                   
import numpy as np
from PIL import Image


class GL_Widget(QGLWidget):
    def __init__(self, parent=None):
        QGLWidget.__init__(self, parent)
        self.setPhoto()
        self.obj = Tools(parent)
        self.feature_icon = "icons/small_crosshair.png"
        self.get_feature_texture(self.feature_icon)
        self._zoom = 0
        
        timer = QTimer(self)
        timer.setInterval(10)   # period, in milliseconds
        timer.timeout.connect(self.updateGL)
        timer.start()
        
        
    def initializeGL(self):
        glClearColor(0.8, 0.8, 0.8, 1)
        glEnable(GL_DEPTH_TEST)


    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / float(height)
        glOrtho(0.0, self.width, self.height, 0.0, 0.0, 100)
        # GLU.gluPerspective(45.0, aspect, 1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)
        

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        if self.img_file is not None:
            texture_id = self.texture_id
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0)
            glVertex2f(0,0)
            glTexCoord2f(0, 1)
            glVertex2f(0,self.height-self._zoom)
            glTexCoord2f(1, 1)
            glVertex2f(self.width-self._zoom,self.height-self._zoom)
            glTexCoord2f(1, 0)
            glVertex2f(self.width-self._zoom,0)
            glEnd()        
            glDisable(GL_TEXTURE_2D)
                
            
    def setPhoto(self, img=None):
        if img is None:
            self.height = 100
            self.width = 100
            self.img_file = None
        else:
            self.img_file = self.toImgPIL(img)
            image = self.img_file
                
            print('opened file: size=', image.size, 'format=', image.format)
            imageData = np.array(list(image.getdata()), np.uint8)
            self.width = image.size[0]
            self.height = image.size[1]
        
            textureID = glGenTextures(1)
            # glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
            glBindTexture(GL_TEXTURE_2D, textureID)
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, imageData)
            
            image.close()
            self.texture_id = textureID
            
    def get_feature_texture(self, filename):
        image = Image.open(filename)
        self.feature_width = image.size[0]
        self.feature_height = image.size[1]
        imageData = np.array(list(image.getdata()), np.uint8)
        f_textureID = glGenTextures(1)
        # glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
        glBindTexture(GL_TEXTURE_2D, f_textureID)
        glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);
        glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
        glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);
        glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.feature_width, self.feature_height, 0, GL_RGB, GL_UNSIGNED_BYTE, imageData)
        
        image.close()
        self.feature_texture = f_textureID
        
        
    
        
        
        
        
    def toImgPIL(self, imgOpenCV=None):
        if imgOpenCV is None:
            return imgOpenCV
        else:
            print(imgOpenCV.shape)
            return Image.fromarray(cv2.cvtColor(imgOpenCV, cv2.COLOR_BGR2RGB));
