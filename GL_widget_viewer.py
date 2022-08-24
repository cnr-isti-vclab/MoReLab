from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from tools import Tools

import cv2, sys                   
import numpy as np
from PIL import Image


class GL_Widget(QOpenGLWidget):
    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)

        timer = QTimer(self)
        timer.setInterval(10)   # period, in milliseconds
        timer.timeout.connect(self.update)
        timer.start()

        self.setPhoto()
        self.setFocusPolicy(Qt.StrongFocus)
        self.obj = Tools(parent)
        self.feature_locs = []
        self._zoom = 0

        
    def initializeGL(self):
        glClearDepth(1.0)
        glClearColor(0.8, 0.8, 0.8, 1)
        glEnable(GL_DEPTH_TEST)
        self.initGeometry()

        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0



    def resizeGL(self, width, height):
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / float(height)         
        glOrtho(0, v.width, v.height, 0, -10000, 10000)
        glMatrixMode(GL_MODELVIEW)


    def paintGL(self):
        
        glClearDepth(1.0)
        glClearColor(0.8, 0.8, 0.8, 1)
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT | GL_ACCUM_BUFFER_BIT)

        t = self.obj.ctrl_wdg.selected_thumbnail_index
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        
        
        if self.obj.ctrl_wdg.radiobutton.isChecked():
            
            glPushMatrix() 
            glTranslate(v.width/2, v.height/2, 0)    # third, translate cube to specified depth
            glScale(30.0, 30.0, 30.0)       # second, scale cube
            glRotate(self.rotX, 1.0, 0.0, 0.0)
            glRotate(self.rotY, 0.0, 1.0, 0.0)
            glRotate(self.rotZ, 0.0, 0.0, 1.0)
            # glTranslate(5, 5, -0.5)   # first, translate cube center to origin
    
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_COLOR_ARRAY)
    
            glVertexPointer(3, GL_FLOAT, 0, self.vertVBO)
            glColorPointer(3, GL_FLOAT, 0, self.colorVBO)
    
            glDrawElements(GL_QUADS, len(self.cubeIdxArray), GL_UNSIGNED_INT, self.cubeIdxArray)
    
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_COLOR_ARRAY)
            
            glPopMatrix()    # restore the previous modelview matrix
            
        else:
            
            glLineWidth(2.0)
            glBegin(GL_LINES)
            if self.obj.ctrl_wdg.kf_method == "Regular":
                for i,fc in enumerate(v.features_regular[t]):
                    if not v.hide_regular[t][i]:
                        glVertex2f(fc.x_loc-10, fc.y_loc)
                        glVertex2f(fc.x_loc+10, fc.y_loc)
                        glVertex2f(fc.x_loc, fc.y_loc+10)
                        glVertex2f(fc.x_loc, fc.y_loc-10)
                        
            elif self.obj.ctrl_wdg.kf_method == "Network":
                for i,fc in enumerate(v.features_network[t]):
                    if not v.hide_network[t][i]:
                        glVertex2f(fc.x_loc-10, fc.y_loc)
                        glVertex2f(fc.x_loc+10, fc.y_loc)
                        glVertex2f(fc.x_loc, fc.y_loc+10)
                        glVertex2f(fc.x_loc, fc.y_loc-10)
            glEnd()
            
            
            
            # painter = QPainter()
            # painter.begin(self)
            # painter.setPen(QPen(QColor(255,255,255)))
            # painter.setFont(painter.font())

            # if self.obj.ctrl_wdg.kf_method == "Regular":
            #     for i,fc in enumerate(v.features_regular[t]):
            #         if not v.hide_regular[t][i]:
            #             painter.drawText(fc.x_loc * (self.width()/v.width) - 5, fc.y_loc*(self.height()/v.height) - 20, str(fc.label.label))
                        
            # elif self.obj.ctrl_wdg.kf_method == "Network":
            #     for i,fc in enumerate(v.features_network[t]):
            #         if not v.hide_network[t][i]:
            #             painter.drawText(fc.x_loc * (self.width()/v.width) - 5, fc.y_loc*(self.height()/v.height) - 20, str(fc.label.label))
                        
            # painter.end()   
            
            
            
            if self.img_file is not None:
                texture_id = self.texture_id
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, texture_id)
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0)
                glVertex2f(0,0)
                glTexCoord2f(0, 1)
                glVertex2f(0, v.height-self._zoom)
                glTexCoord2f(1, 1)
                glVertex2f(v.width-self._zoom, v.height-self._zoom)
                glTexCoord2f(1, 0)
                glVertex2f(v.width-self._zoom, 0)
                glEnd()
                glDisable(GL_TEXTURE_2D)
            
            
    def setPhoto(self, img=None):
        if img is None:
            self.img_file = None
        else:
            self.img_file = self.toImgPIL(img)
            image = self.img_file
            v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
                
            print('opened file: size=', image.size, 'format=', image.format)
            imageData = np.array(list(image.getdata()), np.uint8)
        
            textureID = glGenTextures(1)
            # glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
            glBindTexture(GL_TEXTURE_2D, textureID)
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, v.width, v.height, 0, GL_RGB, GL_UNSIGNED_BYTE, imageData)
            
            image.close()
            self.texture_id = textureID
            
        
        
        
    def initGeometry(self):
        self.cubeVtxArray = np.array(
                [[0.0, 0.0, 0.0],
                 [1.0, 0.0, 0.0],
                 [1.0, 1.0, 0.0],
                 [0.0, 1.0, 0.0],
                 [0.0, 0.0, 1.0],
                 [1.0, 0.0, 1.0],
                 [1.0, 1.0, 1.0],
                 [0.0, 1.0, 1.0]])
        self.vertVBO = vbo.VBO(np.reshape(self.cubeVtxArray,
                                          (1, -1)).astype(np.float32))
        self.vertVBO.bind()
        
        self.cubeClrArray = np.array(
                [[0.0, 0.0, 0.0],
                 [1.0, 0.0, 0.0],
                 [1.0, 1.0, 0.0],
                 [0.0, 1.0, 0.0],
                 [0.0, 0.0, 1.0],
                 [1.0, 0.0, 1.0],
                 [1.0, 1.0, 1.0],
                 [0.0, 1.0, 1.0 ]])
        self.colorVBO = vbo.VBO(np.reshape(self.cubeClrArray,
                                           (1, -1)).astype(np.float32))
        self.colorVBO.bind()

        self.cubeIdxArray = np.array(
                [0, 1, 2, 3,
                 3, 2, 6, 7,
                 1, 0, 4, 5,
                 2, 1, 5, 6,
                 0, 3, 7, 4,
                 7, 6, 5, 4 ])

    def setRotX(self, val):
        self.rotX = np.pi * val

    def setRotY(self, val):
        self.rotY = np.pi * val

    def setRotZ(self, val):
        self.rotZ = np.pi * val
        
        
        
        
    def toImgPIL(self, imgOpenCV=None):
        if imgOpenCV is None:
            return imgOpenCV
        else:
            # print(imgOpenCV.shape)
            return Image.fromarray(cv2.cvtColor(imgOpenCV, cv2.COLOR_BGR2RGB))
        
        
    def mouseDoubleClickEvent(self, event):
        # # a = self.mapToParent(event.pos())
        a = event.pos()
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        if self.img_file is not None:
            x = a.x() * (v.width/self.width()) 
            y = a.y() * (v.height/self.height())
            # self.get_feature_texture(self.feature_icon)
            self.obj.add_feature(x, y)
                
        super(GL_Widget, self).mouseDoubleClickEvent(event)
        
        
    def keyPressEvent(self, event):
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        f = self.obj.selected_feature_index
        t = self.obj.ctrl_wdg.selected_thumbnail_index  
        mv_pix = 10
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.obj.delete_feature()
        
        elif event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            if event.key() == Qt.Key_Left:
                x = v.features_regular[t][f].x_loc-20
                y = v.features_regular[t][f].y_loc
            elif event.key() == Qt.Key_Right:
                x = v.features_regular[t][f].x_loc+20
                y = v.features_regular[t][f].y_loc
            elif event.key() == Qt.Key_Up:
                x = v.features_regular[t][f].x_loc
                y = v.features_regular[t][f].y_loc-20
            elif event.key() == Qt.Key_Down:
                x = v.features_regular[t][f].x_loc
                y = v.features_regular[t][f].y_loc+20
            else:
                x = v.features_regular[t][f].x_loc
                y = v.features_regular[t][f].y_loc
            
            self.obj.move_feature(x, y, v.features_regular[t][f])

        super(GL_Widget, self).keyPressEvent(event)
            
        
    # def wheelEvent(self, event):
    #     if self.img_file is not None:
    #         if event.angleDelta().y() > 0:
    #             factor = 1.25
    #             self._zoom += 1
    #         else:
    #             factor = 0.8
    #             self._zoom -= 1
    #         if self._zoom > 0:
    #             self.scale(factor, factor)
                
                
                
    #     self._zoom = 0
        
    #     if self.pixmap and not self.pixmap.isNull():
    #         self._empty = False
    #     elif self._zoom == 0:
    #         self.fitInView()
    #     else:
    #         self._zoom = 0
        
        
        
    def convert_cv_qt(self, cv_img, width, height):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(width, height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
        