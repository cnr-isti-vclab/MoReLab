from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from OpenGL.GL.shaders import compileProgram, compileShader
from tools import Tools
import pyrr
from TextureLoader import load_texture

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
        

       
        

    def initializeGL(self):
        glClearDepth(1.0)
        glClearColor(0.8, 0.8, 0.8, 1)
        glEnable(GL_DEPTH_TEST)
        
     




    def paintGL(self):        
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT | GL_ACCUM_BUFFER_BIT)
        

        # print(glGetString(GL_VERSION))


        t = self.obj.ctrl_wdg.selected_thumbnail_index
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        

        # cube_buffer = [-0.5, -0.5,  0.5, 0.0, 0.0,
        #              0.5, -0.5,  0.5, 1.0, 0.0,
        #              0.5,  0.5,  0.5, 1.0, 1.0,
        #             -0.5,  0.5,  0.5, 0.0, 1.0,

        #             -0.5, -0.5, -0.5, 0.0, 0.0,
        #              0.5, -0.5, -0.5, 1.0, 0.0,
        #              0.5,  0.5, -0.5, 1.0, 1.0,
        #             -0.5,  0.5, -0.5, 0.0, 1.0,

        #              0.5, -0.5, -0.5, 0.0, 0.0,
        #              0.5,  0.5, -0.5, 1.0, 0.0,
        #              0.5,  0.5,  0.5, 1.0, 1.0,
        #              0.5, -0.5,  0.5, 0.0, 1.0,

        #             -0.5,  0.5, -0.5, 0.0, 0.0,
        #             -0.5, -0.5, -0.5, 1.0, 0.0,
        #             -0.5, -0.5,  0.5, 1.0, 1.0,
        #             -0.5,  0.5,  0.5, 0.0, 1.0,

        #             -0.5, -0.5, -0.5, 0.0, 0.0,
        #              0.5, -0.5, -0.5, 1.0, 0.0,
        #              0.5, -0.5,  0.5, 1.0, 1.0,
        #             -0.5, -0.5,  0.5, 0.0, 1.0,

        #              0.5,  0.5, -0.5, 0.0, 0.0,
        #             -0.5,  0.5, -0.5, 1.0, 0.0,
        #             -0.5,  0.5,  0.5, 1.0, 1.0,
        #              0.5,  0.5,  0.5, 0.0, 1.0]

        # cube_buffer = np.array(cube_buffer, dtype=np.float32)

        # cube_indices = [ 0,  1,  2,  2,  3,  0,
        #                 4,  5,  6,  6,  7,  4,
        #                 8,  9, 10, 10, 11,  8,
        #                12, 13, 14, 14, 15, 12,
        #                16, 17, 18, 18, 19, 16,
        #                20, 21, 22, 22, 23, 20]

        # cube_indices = np.array(cube_indices, dtype=np.uint32)



        vertex_src = """
        # version 330
        layout(location = 0) in vec3 a_position;
        layout(location = 1) in vec2 a_texture;
        uniform mat4 model;
        uniform mat4 projection;
        uniform mat4 view;
        out vec2 v_texture;
        void main()
        {
            gl_Position = projection * view * model * vec4(a_position, 1.0);

            v_texture = a_texture;
        }
        """
        
        fragment_src = """
        # version 330
        in vec2 v_texture;
        out vec4 out_color;
        uniform sampler2D s_texture;
        uniform ivec3 icolor;
        uniform int switcher;
        void main()
        {
            if(switcher == 0){
                out_color = texture(s_texture, v_texture);
            }else{
                out_color = vec4(icolor.r/255.0, icolor.g/255.0, icolor.b/255.0, 1.0);
            }
        }
        """
        
        self.shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))
    

        # textures = glGenTextures(3)
        # crate = load_texture("textures/crate.jpg", textures[0])
        # metal = load_texture("textures/metal.jpg", textures[1])
        # brick = load_texture("textures/brick.jpg", textures[2])


        
        pick_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, pick_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width(), self.height(), 0, GL_RGB, GL_FLOAT, None)
        
        FBO = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, FBO)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, pick_texture, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBindTexture(GL_TEXTURE_2D, 0)
        
        glUseProgram(self.shader)
        
        
        # # projection = pyrr.matrix44.create_perspective_projection_matrix(45, 1280 / 720, 0.1, 100)
        # # view = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -4.0]))

        # cube_positions = [(-2.0, 0.0, 0.0), (0.0, 0.0, 0.0), (2.0, 0.0, 0.0)]
        # pick_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

        # model_loc = glGetUniformLocation(self.shader, "model")
        # # proj_loc = glGetUniformLocation(self.shader, "projection")
        # # view_loc = glGetUniformLocation(self.shader, "view")
        # icolor_loc = glGetUniformLocation(self.shader, "icolor")
        # switcher_loc = glGetUniformLocation(self.shader, "switcher")

        # # glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
        # # glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
        
        
        
        
        
        
        
        
        # glClearColor(0, 0.1, 0.1, 1)
        # glEnable(GL_DEPTH_TEST)
        # glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        

        
        # # draw to the default frame buffer
        # glUniform1i(switcher_loc, 0)
        # for i in range(len(cube_positions)):
        #     model = pyrr.matrix44.create_from_translation(cube_positions[i])
        #     if i == 0:
        #         glBindTexture(GL_TEXTURE_2D, crate)
        #         glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
        #     elif i == 1:
        #         glBindTexture(GL_TEXTURE_2D, metal)
        #         glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
        #     else:
        #         glBindTexture(GL_TEXTURE_2D, brick)
        #         glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

        #     glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)


        # # draw to the custom frame buffer object - pick buffer
        # glUniform1i(switcher_loc, 1)
        
        
        
        glBindFramebuffer(GL_FRAMEBUFFER, FBO)
        # glClearColor(0.0, 0.0, 0.0, 1.0)
        # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # glBindFramebuffer(GL_FRAMEBUFFER, 0)


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
            diff = (self.width()/v.width)*v.height
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
                    colors = np.zeros(shape=(data.shape[0], 3))
                    colors[:,0] = 1
                    
        
                    glPointSize(5)
                    glBegin(GL_POINTS)
                    
                    for i in range(data.shape[0]):
                        glColor3f(colors[i,0], colors[i,1], colors[i,2])
                        glVertex3f(data[i,0], data[i,1], data[i,2])
                    glEnd()

                      
                    for i, pt_tup in enumerate(self.obj.ctrl_wdg.quad_obj.new_points):
                        if i==self.obj.ctrl_wdg.quad_obj.quad_tree.selected_quad_idx:
                            glColor3f(0.38, 0.85, 0.211)
                        else:
                            # c = self.obj.ctrl_wdg.quad_obj.colors[i]
                            glColor3f(0, 0.6352, 1)
                        glBegin(GL_TRIANGLES)      
                        glVertex3f(pt_tup[0][0], pt_tup[0][1], pt_tup[0][2])
                        glVertex3f(pt_tup[1][0], pt_tup[1][1], pt_tup[1][2])
                        glVertex3f(pt_tup[3][0], pt_tup[3][1], pt_tup[3][2])
                        glEnd()
                        
                        glBegin(GL_TRIANGLES)      
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
                    # print("------------------------------")







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
        if self.img_file is not None:
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
            self.obj.ctrl_wdg.quad_obj.select_feature(x, y)
            # x = self.obj.wdg_tree.transform_x(x)
            # y = self.obj.wdg_tree.transform_y(y)
            self.get_color(x, y)
            
            

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
        # height = 1350
        height = v.height*(self.width()/self.height())

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
        

    
    def get_color(self, x, y):
        print(x,y)
        print("Going to get color")
        # glFlush()
        # glFinish()
        # glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        # glBindFramebuffer(GL_READ_FRAMEBUFFER, self.m_depthTexture);
        # glReadBuffer(GL_COLOR_ATTACHMENT0);
        
        data = glReadPixels(x, y, 1, 1,GL_RGB, GL_FLOAT)
        print(data)
        
        # glReadBuffer(GL_NONE);
        # glBindFramebuffer(GL_READ_FRAMEBUFFER, 0);