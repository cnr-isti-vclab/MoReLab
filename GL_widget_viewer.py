from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from OpenGL.GL.shaders import compileProgram, compileShader
from tools import Tools

# import open3d as o3d
import cv2
import sys
import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt 
from util.sfm import scale_data



class GL_Widget(QOpenGLWidget):
    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)

        timer = QTimer(self)
        timer.setInterval(10)   # period, in milliseconds
        timer.timeout.connect(self.update)
        timer.start()

        self.setPhoto()
        self.setFocusPolicy(Qt.StrongFocus)
        self.showMaximized()
        self.obj = Tools(parent)
        self.color_label = QLabel("X :        Y :        Color:           Selected Quad ID : ")
        self.color_label.setAlignment(Qt.AlignCenter)
        self.pick = False
        self.x = 1
        self.y = 1

        self._zoom = 1
        self.painter = QPainter()
        self.setAutoFillBackground(False) 
        self.offset_x = 0
        self.offset_y = 0
        self.near = -1
        self.far = 1
        self.opengl_intrinsics = np.eye(4)
        self.opengl_extrinsics = np.eye(4)
        self.press_loc = (self.width()/2, self.height()/2)
        self.release_loc = (self.width()/2, self.height()/2)
        self.mv_pix = 1
        self.aspect_image = 0
        self.aspect_widget = self.width()/self.height()
        self.flag_g = False



    def paintGL(self):    
        

        t = self.obj.ctrl_wdg.selected_thumbnail_index
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]


######################################################################################        

        # picking texture and a frame buffer object
        
        if not self.flag_g:
            self.pick_texture = glGenTextures(1)
            self.FBO = glGenFramebuffers(1)
            self.flag_g = True
        
            glBindTexture(GL_TEXTURE_2D, self.pick_texture)
            glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)
    
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width(), self.height(), 0, GL_RGB, GL_FLOAT, None)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.pick_texture, 0)


        glBindTexture(GL_TEXTURE_2D, self.pick_texture)        
        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)

        
   
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        
        if len(self.obj.ply_pts) > 0 and len(self.obj.camera_projection_mat) > 0 and self.obj.up_pt_bool:
            for j, tup in enumerate(self.obj.camera_projection_mat):
                if tup[0] == t:
                    for i, pt_tup in enumerate(self.obj.ctrl_wdg.quad_obj.new_points):
                        co = self.obj.ctrl_wdg.quad_obj.colors[i+1]
                        glColor3f(co[0]/255, co[1]/255, co[2]/255)
                        glBegin(GL_TRIANGLES)      
                        glVertex3f(pt_tup[0][0], pt_tup[0][1], pt_tup[0][2])
                        glVertex3f(pt_tup[1][0], pt_tup[1][1], pt_tup[1][2])
                        glVertex3f(pt_tup[3][0], pt_tup[3][1], pt_tup[3][2])
    
                        glVertex3f(pt_tup[2][0], pt_tup[2][1], pt_tup[2][2])
                        glVertex3f(pt_tup[1][0], pt_tup[1][1], pt_tup[1][2])
                        glVertex3f(pt_tup[3][0], pt_tup[3][1], pt_tup[3][2])
                        glEnd()
                        
                        glLineWidth(2.0)
                        glColor3f(0.0, 0.0, 0.0)
                        glBegin(GL_LINE_LOOP)
                        glVertex3f(pt_tup[0][0], pt_tup[0][1], pt_tup[0][2])
                        glVertex3f(pt_tup[1][0], pt_tup[1][1], pt_tup[1][2])
                        glVertex3f(pt_tup[2][0], pt_tup[2][1], pt_tup[2][2])
                        glVertex3f(pt_tup[3][0], pt_tup[3][1], pt_tup[3][2])
        
                        glEnd()

        if self.pick:
            ID = self.get_ID()
            

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBindTexture(GL_TEXTURE_2D, 0)

        
######################################################################################
        
        
        glClearDepth(1.0)
        glClearColor(0.8, 0.8, 0.8, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT| GL_STENCIL_BUFFER_BIT | GL_ACCUM_BUFFER_BIT )
        glEnable(GL_DEPTH_TEST)  

        if self.img_file is not None:
            self.painter.begin(self)
            pen = QPen(QColor(0, 0, 0))
            pen.setWidth(2)
            self.painter.setPen(pen)
            self.painter.setFont(self.painter.font())
            
            if self._zoom >=1:
                # Pan the scene
                self.painter.translate(self.offset_x, self.offset_y)
                # Zoom the scene
                self.painter.translate(self.width()/2, self.height()/2)
                self.painter.scale(self._zoom, self._zoom)
                self.painter.translate(-self.width()/2, -self.height()/2)
                
    
            self.painter.drawImage(self.w1, self.h1, self.img_file)

            if self.obj.ctrl_wdg.kf_method == "Regular":
                if len(v.features_regular) > 0:
                    for i, fc in enumerate(v.features_regular[t]):
                        if not v.hide_regular[t][i]:
                            self.painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            self.painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            self.painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label.label))
    
            elif self.obj.ctrl_wdg.kf_method == "Network":
                if len(v.features_network) > 0:
                    for i, fc in enumerate(v.features_network[t]):
                        if not v.hide_network[t][i]:
                            self.painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc, fc.x_loc + fc.l/2, fc.y_loc))
                            self.painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            self.painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label.label))

            # Painting for Quad Tool
            
            if (len(v.quad_groups_regular) > 0 or len(v.quad_groups_network) > 0) and self.obj.up_pt_bool:
                pen = QPen(QColor(0, 0, 255))
                pen.setWidth(2)
                self.painter.setPen(pen)
                
                if self.obj.ctrl_wdg.kf_method == "Regular":
                    for i, fc in enumerate(v.features_regular[t]):
                        if v.quad_groups_regular[t][i] != -1:
                            self.painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            self.painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            self.painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label.label))

                    
                elif self.obj.ctrl_wdg.kf_method == "Network":
                    for i, fc in enumerate(v.features_network[t]):
                        if v.quad_groups_network[t][i] != -1:
                            self.painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            self.painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            self.painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label.label))                      
            
            self.painter.end()
            
            
            
            
        if len(self.obj.ply_pts) > 0 and len(self.obj.camera_projection_mat) > 0:
            for j, tup in enumerate(self.obj.camera_projection_mat):
                if tup[0] == t:                    
                    self.computeOpenGL_fromCV(self.obj.K, self.obj.camera_projection_mat[j][1])
                    glMatrixMode(GL_PROJECTION)
                    glLoadIdentity()
                    load_mat = self.opengl_intrinsics
                    glLoadMatrixf(load_mat)
                    
                    glMatrixMode(GL_MODELVIEW)
                    glLoadIdentity()
                    load_mat = self.opengl_extrinsics
                    glLoadMatrixf(load_mat)
                    
                    data = self.obj.ply_pts[0]
                    
                    
                    glColor3f(1.0, 0.0, 0.0)
                    glPointSize(5)
                    glBegin(GL_POINTS)
                    
                    for i in range(data.shape[0]):
                        glVertex3f(data[i,0], data[i,1], data[i,2])
                    glEnd()

                    if self.obj.up_pt_bool:
                        for i, pt_tup in enumerate(self.obj.ctrl_wdg.quad_obj.new_points):
                            if i==self.obj.ctrl_wdg.quad_obj.quad_tree.selected_quad_idx:
                                glColor3f(0.38, 0.85, 0.211)
                            else:
                                glColor3f(0, 0.6352, 1)
                            glBegin(GL_TRIANGLES)      
                            glVertex3f(pt_tup[0][0], pt_tup[0][1], pt_tup[0][2])
                            glVertex3f(pt_tup[1][0], pt_tup[1][1], pt_tup[1][2])
                            glVertex3f(pt_tup[3][0], pt_tup[3][1], pt_tup[3][2])
        
                            glVertex3f(pt_tup[2][0], pt_tup[2][1], pt_tup[2][2])
                            glVertex3f(pt_tup[1][0], pt_tup[1][1], pt_tup[1][2])
                            glVertex3f(pt_tup[3][0], pt_tup[3][1], pt_tup[3][2])
                            glEnd()
                            
                            glLineWidth(2.0)
                            glColor3f(0.0, 0.0, 0.0)
                            glBegin(GL_LINE_LOOP)
                            glVertex3f(pt_tup[0][0], pt_tup[0][1], pt_tup[0][2])
                            glVertex3f(pt_tup[1][0], pt_tup[1][1], pt_tup[1][2])
                            glVertex3f(pt_tup[2][0], pt_tup[2][1], pt_tup[2][2])
                            glVertex3f(pt_tup[3][0], pt_tup[3][1], pt_tup[3][2])
                            glEnd()

                
                           
    def setPhoto(self, image=None):
        if image is None:
            self.img_file = None
        else:
            self.aspect_image = image.shape[1]/image.shape[0]
            self.aspect_widget = self.width()/self.height()
            self.set_default_view_param()
            w = int(self.w2-self.w1)
            h = int(self.h2-self.h1)
    
            image = cv2.resize(image, (w, h), interpolation = cv2.INTER_AREA)
            # print("Image size after resizing: Width: "+str(image.shape[1])+ " , Height: "+str(image.shape[0]))
            PIL_image = self.toImgPIL(image).convert('RGB')
            self.img_file = ImageQt(PIL_image)
            

    def set_default_view_param(self):
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        self.aspect_widget = self.width()/self.height()
        if self.aspect_image > self.aspect_widget:
            self.w1 = 0
            self.w2 = self.width()

            diff = self.height() - (self.width()/v.width)*v.height
            self.h1 = diff/2
            self.h2 = self.height() - self.h1
            
        else:
            diff = (self.aspect_widget - self.aspect_image)*self.width()
            self.w1 = diff/2
            self.w2 = self.width() - self.w1
            self.h1 = 0
            self.h2 = self.height()
            
        self.obj.wdg_tree.wdg_to_img_space()


    def mouseDoubleClickEvent(self, event):
        a = event.pos()
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        if self.img_file is not None and self.obj.cross_hair:
            # print(a.x(), a.y())
            if a.x() > 0 and a.y() > 0:
                x = int((a.x()-self.width()/2 - self.offset_x)/self._zoom + self.width()/2) 
                y = int((a.y()-self.height()/2 - self.offset_y)/self._zoom + self.height()/2)
                if x > self.w1 and y > self.h1 and x < self.w2 and y < self.h2:
                    self.obj.add_feature(x, y)

        super(GL_Widget, self).mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        f = self.obj.selected_feature_index
        t = self.obj.ctrl_wdg.selected_thumbnail_index

        if self.obj.cross_hair:
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
        if self.img_file is not None and not self.obj.up_pt_bool:
            if event.angleDelta().y() > 0:
                self._zoom += 0.1
            else:
                self._zoom -= 0.1
            # print(self.width()/2)
            if self._zoom < 1:
                self._zoom = 1
                self.offset_x = 0
                self.offset_y = 0
                self.set_default_view_param()


    # overriding the mousePressEvent method
    def mousePressEvent(self, event):
        a = event.pos()
        self.press_loc = (a.x(), a.y())
        if self.obj.up_pt_bool:
            x = int((a.x()-self.width()/2 - self.offset_x)/self._zoom + self.width()/2) 
            y = int((a.y()-self.height()/2 - self.offset_y)/self._zoom + self.height()/2)
            selected_feature = self.obj.ctrl_wdg.quad_obj.select_feature(x, y)
            if not selected_feature:
                self.pick = True
                self.x = a.x()
                self.y = a.y()

    # overriding the mousePressEvent method
    def mouseReleaseEvent(self, event):
        a = event.pos()
        if not self.obj.up_pt_bool:
            self.release_loc = (a.x(), a.y())
            if self._zoom >= 1:
                self.offset_x += (self.release_loc[0] - self.press_loc[0])
                self.offset_y += (self.release_loc[1] - self.press_loc[1])
        
          
                    
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
            return Image.fromarray(cv2.cvtColor(imgOpenCV, cv2.COLOR_BGR2RGB))
        
        
    def computeOpenGL_fromCV(self, K, Rt):
        zn = -1 #self.near
        zf = 1 #self.far
        d = zn - zf
        cx = K[0,2]
        cy = K[1,2]
        perspective = np.zeros((4,4))
        
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        width = v.width
        # height = 1080
        height = v.height*(self.width()/self.height())
        
        # width = self.width()
        # height = self.height()

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
        

    
    def get_ID(self):
        co = glReadPixels(self.x, self.height()-self.y, 1, 1,GL_RGB, GL_UNSIGNED_BYTE)
        ID = self.obj.ctrl_wdg.quad_obj.getIfromRGB(co[0], co[1], co[2])
        if ID > 0:
            self.obj.ctrl_wdg.quad_obj.quad_tree.select_quad(self.obj.ctrl_wdg.quad_obj.quad_tree.items[ID-1])
            self.color_label.setText("X : "+str(int(self.x))+"    Y : "+str(int(self.y))+"   Color : ("+str(co[0])+", "+str(co[1])+", "+str(co[2])+")      Selected Quad ID : "+str(ID))            
        else:
            self.color_label.setText("X : "+str(int(self.x))+"    Y : "+str(int(self.y))+"   Color : ("+str(co[0])+", "+str(co[1])+", "+str(co[2])+")      Background ")
        self.pick = False
        return ID