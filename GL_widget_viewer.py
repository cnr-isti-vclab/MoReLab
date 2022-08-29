from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from tools import Tools

import cv2
import sys
import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt 


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

        self.start = True
        self._zoom = 1
        self.offset_x = 0
        self.offset_y = 0
        self.press_loc = (self.width()/2, self.height()/2)
        self.release_loc = (self.width()/2, self.height()/2)
        self.mv_pix = 10

        self.aspect_image = 0
        self.aspect_widget = 0

    def initializeGL(self):
        glClearDepth(1.0)
        glClearColor(0.8, 0.8, 0.8, 1)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, width, height):
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.aspect_widget = width / float(height)
        glOrtho(0, v.width, v.height, 0, 0, 100)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        # glClearDepth(1.0)
        # glClearColor(0.8, 0.8, 0.8, 1)
        # glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT |
                GL_STENCIL_BUFFER_BIT | GL_ACCUM_BUFFER_BIT)
        
        glPushMatrix()

        t = self.obj.ctrl_wdg.selected_thumbnail_index
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        
        
        if self.img_file is not None:
            painter = QPainter()
            painter.begin(self)
    
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.setFont(painter.font())
    
            if self._zoom >=1:
                # Zoom the scene
                painter.translate(self.width()/2, self.height()/2)
                painter.scale(self._zoom, self._zoom)
                painter.translate(-self.width()/2, -self.height()/2)
                # Pan the scene
                painter.translate(self.offset_x, self.offset_y)
    
            painter.drawImage(self.w1, self.h1, self.img_file)
            
            if self.obj.ctrl_wdg.kf_method == "Regular":
                if len(v.features_regular) > 0:
                    for i, fc in enumerate(v.features_regular[t]):
                        if not v.hide_regular[t][i]:
                            painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc, fc.x_loc + fc.l/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            painter.drawText(fc.x_loc - 5, fc.y_loc - 18, str(fc.label.label))
    
            elif self.obj.ctrl_wdg.kf_method == "Network":
                if len(v.features_network) > 0:
                    for i, fc in enumerate(v.features_network[t]):
                        if not v.hide_network[t][i]:
                            painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc, fc.x_loc + fc.l/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            painter.drawText(
                                fc.x_loc - 5, fc.y_loc - 18, str(fc.label.label))
            painter.end()
        
        glPopMatrix()

    def setPhoto(self, image=None):
        if image is None:
            self.img_file = None
        else:
            self.aspect_image = image.shape[1]/image.shape[0]
            self.set_default_view_param()
            w = int(self.w2-self.w1)
            h = int(self.h2-self.h1)
            image = cv2.resize(image, (w, h), interpolation = cv2.INTER_AREA)
            PIL_image = self.toImgPIL(image).convert('RGB')
            self.img_file = ImageQt(PIL_image)
            self.update()
            

    def set_default_view_param(self):
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]

        if self.aspect_image > self.aspect_widget:
            self.w1 = 0
            self.w2 = self.width()
            diff = (self.aspect_image - self.aspect_widget)*self.height()
            self.h1 = diff/2
            self.h2 = self.height() - self.h1
        else:
            diff = (self.aspect_widget - self.aspect_image)*self.width()
            self.w1 = diff/2
            self.w2 = self.width() - self.w1
            self.h1 = 0
            self.h2 = self.height()


    def mouseDoubleClickEvent(self, event):
        # # a = self.mapToParent(event.pos())
        a = event.pos()
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        if self.img_file is not None:
            x = a.x() - self.offset_x  
            y = a.y() - self.offset_y 
            self.obj.add_feature(x, y)

        super(GL_Widget, self).mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        f = self.obj.selected_feature_index
        t = self.obj.ctrl_wdg.selected_thumbnail_index

        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.obj.delete_feature()

        elif event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            if event.key() == Qt.Key_Left:
                x = v.features_regular[t][f].x_loc-self.mv_pix
                y = v.features_regular[t][f].y_loc
            elif event.key() == Qt.Key_Right:
                x = v.features_regular[t][f].x_loc+self.mv_pix
                y = v.features_regular[t][f].y_loc
            elif event.key() == Qt.Key_Up:
                x = v.features_regular[t][f].x_loc
                y = v.features_regular[t][f].y_loc-self.mv_pix
            elif event.key() == Qt.Key_Down:
                x = v.features_regular[t][f].x_loc
                y = v.features_regular[t][f].y_loc+self.mv_pix
            else:
                x = v.features_regular[t][f].x_loc
                y = v.features_regular[t][f].y_loc

            self.obj.move_feature(x, y, v.features_regular[t][f])

        super(GL_Widget, self).keyPressEvent(event)

    def wheelEvent(self, event):
        if self.img_file is not None:
            if event.angleDelta().y() > 0:
                self._zoom += 0.1
            else:
                self._zoom -= 0.1

            if self._zoom < 1:
                self._zoom = 1
                self.offset_x = 0
                self.offset_y = 0
                self.set_default_view_param()



    # overriding the mousePressEvent method
    def mousePressEvent(self, event):
        a = event.pos()
        self.press_loc = (a.x(), a.y())

    # overriding the mousePressEvent method
    def mouseReleaseEvent(self, event):
        a = event.pos()
        self.release_loc = (a.x(), a.y())
        if self._zoom >= 1:
            self.offset_x += (self.release_loc[0] - self.press_loc[0])/2
            self.offset_y += (self.release_loc[1] - self.press_loc[1])/2
                    
                    
                    
    def convert_cv_qt(self, cv_img, width, height):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(width, height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    


    def toImgPIL(self, imgOpenCV=None):
        if imgOpenCV is None:
            return imgOpenCV
        else:
            # print(imgOpenCV.shape)
            return Image.fromarray(cv2.cvtColor(imgOpenCV, cv2.COLOR_BGR2RGB))
