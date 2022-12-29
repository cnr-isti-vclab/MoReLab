from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

from features import Features
from util_viewer import Util_viewer
from scipy.spatial import distance




class GL_Widget(QOpenGLWidget):
    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)

        timer = QTimer(self)
        timer.setInterval(10)   # period, in milliseconds
        timer.timeout.connect(self.update)
        timer.start()

        self.setFocusPolicy(Qt.StrongFocus)
        self.showMaximized()
        

        self.obj = Features(parent)
        self.util_ = Util_viewer(self)
        self.setMouseTracking(True)
        self.setMinimumSize(self.obj.ctrl_wdg.monitor_width*0.56, self.obj.ctrl_wdg.monitor_height*0.67)
        self.util_.setPhoto()

        self.painter = QPainter()
        self.setAutoFillBackground(False) 
        
        self._zoom, self.offset_x, self.offset_y = 1, 0, 0

        self.dist_thresh, self.mv_pix = 10, 1
        self.pick, self.move_feature_bool, self.move_pick = False, False, False
        self.x, self.y = 1, 1
        self.move_x, self.move_y = 1, 1
        self.cylinder_point = []
        self.clicked_once = False
        self.last_3d_pos = np.array([0.0,0.0, 0.0])
        self.last_pos = np.array([0.0,0.0])
        self.current_pos = np.array([0.0,0.0])

        self.flag_g = False
        self.bCalibrate = True
        self.calibration_factor, self.dist = 1.0, 0.0
        self.fill_color = (0.0, 0.6252, 1.0)
        self.boundary_color = (0.0, 0.0, 0.0)
        self.selected_color = (0.38, 0.85, 0.211)
  

            
    def paintGL(self):
        t = self.obj.ctrl_wdg.selected_thumbnail_index
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        
######################################################################################
        # Offscreen rendering
        if not self.flag_g:
            self.flag_g = True
            self.FBO = glGenFramebuffers(1)
            glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)
            # Texture for Color Information
            self.pick_texture = glGenTextures(1)        
            glBindTexture(GL_TEXTURE_2D, self.pick_texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width(), self.height(), 0, GL_RGB, GL_FLOAT, None)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.pick_texture, 0)
            # Texture for Depth Information
            self.depth_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.depth_texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.width(), self.height(), 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depth_texture, 0)

        glBindTexture(GL_TEXTURE_2D, self.pick_texture)
        glBindTexture(GL_TEXTURE_2D, self.depth_texture)        
        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        if len(self.obj.ply_pts) > 0 and len(self.obj.camera_projection_mat) > 0:
            for j, tup in enumerate(self.obj.camera_projection_mat):
                if tup[0] == t:
                    self.render_points()
                    
                    if self.obj.ctrl_wdg.ui.bQuad or self.obj.ctrl_wdg.ui.bMeasure or self.obj.ctrl_wdg.ui.bPick or self.obj.ctrl_wdg.ui.bCylinder or self.obj.ctrl_wdg.ui.bnCylinder or self.obj.ctrl_wdg.ui.bBezier:
                        self.render_quads(True)
                        
                    if self.obj.ctrl_wdg.ui.bCylinder or self.obj.ctrl_wdg.ui.bMeasure or self.obj.ctrl_wdg.ui.bPick or self.obj.ctrl_wdg.ui.bnCylinder or self.obj.ctrl_wdg.ui.bBezier:
                        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL)
                        self.render_cylinders(True, True)
                        glPolygonMode( GL_FRONT_AND_BACK, GL_LINE)
                        self.render_cylinders(True, False)
                        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL)
                        
                    if self.obj.ctrl_wdg.ui.bBezier or self.obj.ctrl_wdg.ui.bPick:
                        self.render_bezier(True)

        if self.pick:
            self.select_3d_point()
        
        bases = []
        center = [0,0,0]
        center_base = center
        center_top = center
        cyl_bases, cyl_tops = [], []
        trans_bezier_points = []
        if self.move_pick:
            # glEnable
            dd = glReadPixels(self.move_x, self.height()-self.move_y, 1, 1,GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
            px = (0, 0, 0)
            if dd < 1.0:
                px = gluUnProject(self.move_x, self.height()-self.move_y, dd)
                if self.obj.ctrl_wdg.ui.bnCylinder:
                    if len(self.obj.cylinder_obj.data_val) == 2:
                        bases, center = self.obj.cylinder_obj.make_new_circle(self.obj.cylinder_obj.data_val[0], self.obj.cylinder_obj.data_val[1], np.array(px))

                    elif len(self.obj.cylinder_obj.data_val) == 3:
                        cyl_bases, cyl_tops, center_base, center_top = self.obj.cylinder_obj.make_new_cylinder(self.obj.cylinder_obj.data_val[0], self.obj.cylinder_obj.data_val[1], self.obj.cylinder_obj.data_val[2], np.array(px))

                elif self.obj.ctrl_wdg.ui.bCylinder:
                    if len(self.obj.cylinder_obj.data_val) == 2:
                        bases, center = self.obj.cylinder_obj.make_circle(self.obj.cylinder_obj.data_val[0], self.obj.cylinder_obj.data_val[1], np.array(px))
                    elif len(self.obj.cylinder_obj.data_val) == 3:
                        cyl_bases, cyl_tops, center_base, center_top = self.obj.cylinder_obj.make_cylinder(self.obj.cylinder_obj.data_val[0], self.obj.cylinder_obj.data_val[1], self.obj.cylinder_obj.data_val[2], np.array(px))
                        
                if self.obj.ctrl_wdg.ui.bBezier or self.obj.ctrl_wdg.ui.bPick:
                    if len(self.obj.bezier_obj.data_val) == 3:
                        trans_bezier_points = self.obj.bezier_obj.bezier_curve_range(self.obj.bezier_obj.num_pts, self.obj.bezier_obj.data_val[0], self.obj.bezier_obj.data_val[1], self.obj.bezier_obj.data_val[2], np.array(px))


        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBindTexture(GL_TEXTURE_2D, 0)

######################################################################################

# ------------------------------------------------------------------------------------------------------------------------
        glClearColor(0.8, 0.8, 0.8, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT| GL_STENCIL_BUFFER_BIT | GL_ACCUM_BUFFER_BIT )
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        

        self.paint_image(v, t)
        
        
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK) 
        glFrontFace(GL_CCW)
        
        if len(self.obj.ply_pts) > 0 and len(self.obj.camera_projection_mat) > 0:
            for j, tup in enumerate(self.obj.camera_projection_mat):
                if tup[0] == t:                    
                    self.util_.computeOpenGL_fromCV(self.obj.K, self.obj.camera_projection_mat[j][1])
                    glMatrixMode(GL_PROJECTION)
                    glLoadIdentity()
                    load_mat = self.util_.opengl_intrinsics
                    glLoadMatrixf(load_mat)
                    
                    glMatrixMode(GL_MODELVIEW)
                    glLoadIdentity()
                    load_mat = self.util_.opengl_extrinsics
                    glLoadMatrixf(load_mat)
                    
                    self.render_points()
        
                    if self.obj.ctrl_wdg.ui.bQuad or self.obj.ctrl_wdg.ui.bPick or self.obj.ctrl_wdg.ui.bMeasure:
                        self.render_quads(False)
                        
                    if self.obj.ctrl_wdg.ui.bCylinder or self.obj.ctrl_wdg.ui.bMeasure or self.obj.ctrl_wdg.ui.bPick or self.obj.ctrl_wdg.ui.bnCylinder:
                        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL)
                        if self.obj.ctrl_wdg.ui.bCylinder or self.obj.ctrl_wdg.ui.bnCylinder:
                            self.render_transient_circle(bases, center, self.fill_color)
                            self.render_transient_cylinders(cyl_bases, cyl_tops, center_base, center_top, self.fill_color)
                        self.render_cylinders(False, True)
                        glPolygonMode( GL_FRONT_AND_BACK, GL_LINE)
                        if self.obj.ctrl_wdg.ui.bCylinder or self.obj.ctrl_wdg.ui.bnCylinder:
                            self.render_transient_circle(bases, center, self.boundary_color)
                            self.render_transient_cylinders(cyl_bases, cyl_tops, center_base, center_top, self.boundary_color)
                        self.render_cylinders(False, False)
                        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL)
                        
                    if self.obj.ctrl_wdg.ui.bBezier:
                        self.render_bezier(False)
                        
                        if len(trans_bezier_points) > 0:
                            glColor3f(0.0, 0.0, 0.0)
                            glBegin(GL_LINE_STRIP)
                            for point in trans_bezier_points:
                                glVertex3f(point[0], point[1], point[2])
                            glEnd()

        glDisable(GL_CULL_FACE)

        # Draw Measuring Line
        if self.obj.ctrl_wdg.ui.bMeasure and self.clicked_once and len(self.obj.ply_pts) > 0:
            self.painter.begin(self)
            pen = QPen(QColor(0, 0, 255))
            pen.setWidth(2)
            self.painter.setPen(pen)
            # print(self.last_pos)
            # print(self.current_pos)
            # print("===================================")
            self.painter.drawLine(QLineF(self.last_pos[0], self.last_pos[1], self.current_pos[0], self.current_pos[1]))
            self.painter.end()


    def mouseDoubleClickEvent(self, event):
        a = event.pos()
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        if self.util_.img_file is not None and self.obj.ctrl_wdg.ui.cross_hair:
            # print(a.x(), a.y())
            if a.x() > 0 and a.y() > 0:
                x = int((a.x()-self.width()/2 - self.offset_x)/self._zoom + self.width()/2) 
                y = int((a.y()-self.height()/2 - self.offset_y)/self._zoom + self.height()/2)
                if x > self.util_.w1 and y > self.util_.h1 and x < self.util_.w2 and y < self.util_.h2:
                    self.obj.add_feature(x, y)


    def keyPressEvent(self, event):
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        f = self.obj.feature_panel.selected_feature_idx
        t = self.obj.ctrl_wdg.selected_thumbnail_index

        if self.obj.ctrl_wdg.ui.cross_hair and f != -1:
            if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                self.obj.delete_feature()
                
            elif event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
                if self.obj.ctrl_wdg.kf_method == "Regular":
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

                elif self.obj.ctrl_wdg.kf_method == "Network":
                    if event.key() == Qt.Key_Left:
                        x = v.features_network[t][f].x_loc-self.mv_pix
                        y = v.features_network[t][f].y_loc
                    elif event.key() == Qt.Key_Right:
                        x = v.features_network[t][f].x_loc+self.mv_pix
                        y = v.features_network[t][f].y_loc
                    elif event.key() == Qt.Key_Up:
                        x = v.features_network[t][f].x_loc
                        y = v.features_network[t][f].y_loc-self.mv_pix
                    elif event.key() == Qt.Key_Down:
                        x = v.features_network[t][f].x_loc
                        y = v.features_network[t][f].y_loc+self.mv_pix
                    else:
                        x = v.features_network[t][f].x_loc
                        y = v.features_network[t][f].y_loc

                    self.obj.move_feature(x, y, v.features_network[t][f])
                
        if self.obj.ctrl_wdg.ui.cross_hair and event.modifiers() & Qt.ControlModifier:
            self.obj.feature_panel.selected_feature_idx = -1
            if event.key() == Qt.Key_C:
                self.obj.ctrl_wdg.copy_features()
            elif event.key() == Qt.Key_V:
                self.obj.ctrl_wdg.paste_features()
            
            if self.obj.ctrl_wdg.kf_method == "Regular":
                if event.key() == Qt.Key_Left:
                    for i,fc in enumerate(v.features_regular[t]):
                        if not v.hide_regular[t][i]:
                            fc.x_loc = fc.x_loc - self.mv_pix
                            fc.y_loc = fc.y_loc
                            
                elif event.key() == Qt.Key_Right:
                    for i,fc in enumerate(v.features_regular[t]):
                        if not v.hide_regular[t][i]:
                            fc.x_loc = fc.x_loc + self.mv_pix
                            fc.y_loc = fc.y_loc
                            
                elif event.key() == Qt.Key_Up:
                    for i,fc in enumerate(v.features_regular[t]):
                        if not v.hide_regular[t][i]:
                            fc.x_loc = fc.x_loc 
                            fc.y_loc = fc.y_loc - self.mv_pix
                elif event.key() == Qt.Key_Down:
                    for i,fc in enumerate(v.features_regular[t]):
                        if not v.hide_regular[t][i]:
                            fc.x_loc = fc.x_loc 
                            fc.y_loc = fc.y_loc + self.mv_pix
                            
            elif self.obj.ctrl_wdg.kf_method == "Network":
                if event.key() == Qt.Key_Left:
                    for i,fc in enumerate(v.features_network[t]):
                        if not v.hide_network[t][i]:
                            fc.x_loc = fc.x_loc - self.mv_pix
                            fc.y_loc = fc.y_loc
                            
                elif event.key() == Qt.Key_Right:
                    for i,fc in enumerate(v.features_network[t]):
                        if not v.hide_network[t][i]:
                            fc.x_loc = fc.x_loc + self.mv_pix
                            fc.y_loc = fc.y_loc
                            
                elif event.key() == Qt.Key_Up:
                    for i,fc in enumerate(v.features_network[t]):
                        if not v.network[t][i]:
                            fc.x_loc = fc.x_loc 
                            fc.y_loc = fc.y_loc - self.mv_pix
                        
                elif event.key() == Qt.Key_Down:
                    for i,fc in enumerate(v.features_network[t]):
                        if not v.hide_network[t][i]:
                            fc.x_loc = fc.x_loc 
                            fc.y_loc = fc.y_loc + self.mv_pix
            
            self.obj.feature_panel.display_data()
                
        if self.obj.ctrl_wdg.ui.bPick:
            if self.obj.cylinder_obj.selected_cylinder_idx != -1: 
                self.obj.cylinder_obj.delete_cylinder(self.obj.cylinder_obj.selected_cylinder_idx)
            elif self.obj.ctrl_wdg.quad_obj.selected_quad_idx != -1:
                self.obj.ctrl_wdg.quad_obj.delete_quad(self.obj.ctrl_wdg.quad_obj.selected_quad_idx)
            else:
                print("No 3D object has been selected")

        super(GL_Widget, self).keyPressEvent(event)


    def wheelEvent(self, event):
        if self.util_.img_file is not None and (self.obj.ctrl_wdg.ui.move_bool or self.obj.ctrl_wdg.ui.cross_hair):
            if event.angleDelta().y() > 0:
                self._zoom += 0.1
            else:
                self._zoom -= 0.1
            # print(self.width()/2)
            if self._zoom < 1:
                self._zoom = 1
                self.offset_x = 0
                self.offset_y = 0
                self.util_.set_default_view_param()
                
        if self.obj.ctrl_wdg.quad_obj.selected_quad_idx != -1 and self.obj.ctrl_wdg.ui.bPick:
            if event.angleDelta().y() > 0:
                self.obj.ctrl_wdg.quad_obj.scale_up()
            else:
                self.obj.ctrl_wdg.quad_obj.scale_down()


    # overriding the mousePressEvent method
    def mousePressEvent(self, event):
        a = event.pos()
        x = int((a.x()-self.width()/2 - self.offset_x)/self._zoom + self.width()/2) 
        y = int((a.y()-self.height()/2 - self.offset_y)/self._zoom + self.height()/2)
        
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        t = self.obj.ctrl_wdg.selected_thumbnail_index
        
        if event.button() == Qt.RightButton:
            self.press_loc = (a.x(), a.y())
        
        elif event.button() == Qt.LeftButton and self.obj.ctrl_wdg.ui.cross_hair:
            if self.obj.ctrl_wdg.kf_method == "Regular":
                if len(v.features_regular) > 0:
                    for i, fc in enumerate(v.features_regular[t]):
                        if not v.hide_regular[t][i]:
                            d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                            if d < self.dist_thresh:
                                self.obj.feature_panel.selected_feature_idx = i
                                self.obj.feature_panel.select_feature()
                                self.move_feature_bool = True


            elif self.obj.ctrl_wdg.kf_method == "Network":
                if len(v.features_network) > 0:
                    for i, fc in enumerate(v.features_network[t]):
                        if not v.hide_network[t][i]:
                            d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                            if d < self.dist_thresh:
                                self.obj.feature_panel.selected_feature_idx = i
                                self.obj.feature_panel.select_feature()
                                self.move_feature_bool = True

        if self.obj.ctrl_wdg.ui.bQuad:
            selected_feature = self.obj.ctrl_wdg.quad_obj.select_feature(x, y)
            if not selected_feature:
                self.x = a.x()
                self.y = a.y()
                self.pick = True
                
        if self.obj.ctrl_wdg.ui.bCylinder or self.obj.ctrl_wdg.ui.bnCylinder:
            selected_feature = self.obj.cylinder_obj.select_feature(x, y)
            if not selected_feature:
                self.x = a.x()
                self.y = a.y()
                self.pick = True
                
        if self.obj.ctrl_wdg.ui.bBezier:
            selected_feature = self.obj.bezier_obj.select_feature(x, y)
            if not selected_feature:
                self.x = a.x()
                self.y = a.y()
                self.pick = True

            
        if self.obj.ctrl_wdg.ui.bMeasure or self.obj.ctrl_wdg.ui.bPick:
            self.x = a.x()
            self.y = a.y()
            self.pick = True


    def mouseMoveEvent(self, event):
        a = event.pos()
        x = int((a.x()-self.width()/2 - self.offset_x)/self._zoom + self.width()/2) 
        y = int((a.y()-self.height()/2 - self.offset_y)/self._zoom + self.height()/2)
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        if self.obj.ctrl_wdg.ui.bMeasure and len(self.obj.ply_pts) > 0:    
            self.current_pos = np.array([a.x(), a.y()])
            
        if len(v.quad_groups_regular) > 0 or len(v.quad_groups_network) > 0:
            self.move_x = a.x()
            self.move_y = a.y()
            self.move_pick = True
            
        if self.obj.ctrl_wdg.ui.cross_hair:
            if self.obj.ctrl_wdg.kf_method == "Regular":
                if len(v.features_regular) > 0 and self.move_feature_bool:
                    self.obj.move_feature(x, y, v.features_regular[self.obj.ctrl_wdg.selected_thumbnail_index][self.obj.feature_panel.selected_feature_idx])
               
            elif self.obj.ctrl_wdg.kf_method == "Network":
                if len(v.features_network) > 0 and self.move_feature_bool:
                    self.obj.move_feature(x, y, v.features_network[self.obj.ctrl_wdg.selected_thumbnail_index][self.obj.feature_panel.selected_feature_idx])



                
    def mouseReleaseEvent(self, event):
        a = event.pos()
        if self.obj.ctrl_wdg.ui.move_bool or self.obj.ctrl_wdg.ui.cross_hair:
            if event.button() == Qt.RightButton:
                self.release_loc = (a.x(), a.y())
                if self._zoom >= 1:
                    self.offset_x += (self.release_loc[0] - self.press_loc[0])
                    self.offset_y += (self.release_loc[1] - self.press_loc[1])
                    
            elif event.button() == Qt.LeftButton:
                self.move_feature_bool = False
                

    def paint_image(self, v, t):
        if self.util_.img_file is not None:
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
                
            
            self.painter.drawImage(self.util_.w1, self.util_.h1, self.util_.img_file)
            
            if self.obj.ctrl_wdg.kf_method == "Regular":
                if len(v.features_regular) > 0:
                    for i, fc in enumerate(v.features_regular[t]):
                        if not v.hide_regular[t][i]:
                            self.painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            self.painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            self.painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
    
            elif self.obj.ctrl_wdg.kf_method == "Network":
                if len(v.features_network) > 0:
                    for i, fc in enumerate(v.features_network[t]):
                        if not v.hide_network[t][i]:
                            self.painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc, fc.x_loc + fc.l/2, fc.y_loc))
                            self.painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            self.painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
                                   
            pen = QPen(QColor(0, 0, 255))
            pen.setWidth(2)
            self.painter.setPen(pen)
            if self.obj.feature_panel.selected_feature_idx != -1 and self.obj.ctrl_wdg.ui.cross_hair:
                if self.obj.ctrl_wdg.kf_method == "Regular" and len(v.features_regular[t]) > 0 and not v.hide_regular[t][self.obj.feature_panel.selected_feature_idx]:
                    fc = v.features_regular[t][self.obj.feature_panel.selected_feature_idx]
                    self.painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc, fc.x_loc + fc.l/2, fc.y_loc))
                    self.painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                    self.painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
                elif self.obj.ctrl_wdg.kf_method == "Network" and len(v.features_network[t]) > 0 and not v.hide_network[t][self.obj.feature_panel.selected_feature_idx]:
                    fc = v.features_network[t][self.obj.feature_panel.selected_feature_idx]
                    self.painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc, fc.x_loc + fc.l/2, fc.y_loc))
                    self.painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                    self.painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
            
            
            
            # Painting for Quad Tool
            if (len(v.quad_groups_regular) > 0 or len(v.quad_groups_network) > 0) and (self.obj.ctrl_wdg.ui.bQuad or self.obj.ctrl_wdg.ui.bPick) :
                if self.obj.ctrl_wdg.kf_method == "Regular":
                    for i, fc in enumerate(v.features_regular[t]):
                        if v.quad_groups_regular[t][i] != -1:
                            self.painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            self.painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            self.painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))

                    
                elif self.obj.ctrl_wdg.kf_method == "Network":
                    for i, fc in enumerate(v.features_network[t]):
                        if v.quad_groups_network[t][i] != -1:
                            self.painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            self.painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            self.painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))                      

            # Painting for Sphere Tool
            
            if (len(v.cylinder_groups_regular) > 0 or len(v.cylinder_groups_network) > 0) and (self.obj.ctrl_wdg.ui.bCylinder or self.obj.ctrl_wdg.ui.bnCylinder or self.obj.ctrl_wdg.ui.bPick or self.obj.ctrl_wdg.ui.bMeasure) :
                if self.obj.ctrl_wdg.kf_method == "Regular":
                    for i, fc in enumerate(v.features_regular[t]):
                        if v.cylinder_groups_regular[t][i] != -1:
                            self.painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            self.painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            self.painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))

                    
                elif self.obj.ctrl_wdg.kf_method == "Network":
                    for i, fc in enumerate(v.features_network[t]):
                        if v.cylinder_groups_network[t][i] != -1:
                            self.painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            self.painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            self.painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
                            
            # Bezier tool
            if (len(v.bezier_groups_regular) > 0 or len(v.bezier_groups_network) > 0) and self.obj.ctrl_wdg.ui.bBezier:
                if self.obj.ctrl_wdg.kf_method == "Regular":
                    for i, fc in enumerate(v.features_regular[t]):
                        if v.bezier_groups_regular[t][i] != -1:
                            self.painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            self.painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            self.painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))


                    
                elif self.obj.ctrl_wdg.kf_method == "Network":
                    for i, fc in enumerate(v.features_network[t]):
                        if v.bezier_groups_network[t][i] != -1:
                            self.painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            self.painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            self.painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))            
            
            
            self.painter.end()
                
    def select_color(self, i, offscreen_bool = False, fill_flag = True):
        if offscreen_bool:
            color = self.obj.cylinder_obj.colors[i+1]
            color = (color[0]/255, color[1]/255, color[2]/255)
        else:
            if fill_flag:
                if i==self.obj.cylinder_obj.selected_cylinder_idx:
                    color = self.selected_color
                else:
                    color = self.fill_color
            else:
                 color = self.boundary_color 
        return color

  
    def render_cylinders(self, offscreen_bool = False, fill_flag = True):
        # Draw cylinder strips 
        for i, vertices in enumerate(self.obj.cylinder_obj.vertices_cylinder):
            base_center = self.obj.cylinder_obj.centers[i]
            if -1 not in base_center:
                top_vertices = self.obj.cylinder_obj.top_vertices[i]
                color = self.select_color(i, offscreen_bool, fill_flag)
                glColor4f(color[0], color[1], color[2], 0.1)
                glBegin(GL_TRIANGLE_STRIP)
                for k in range(0,len(vertices), 1):
                    glVertex3f(vertices[k][0], vertices[k][1], vertices[k][2])
                    glVertex3f(top_vertices[k][0], top_vertices[k][1], top_vertices[k][2])
                glEnd()
            
        
        # Draw cylinder bases
        for i, vertices in enumerate(self.obj.cylinder_obj.vertices_cylinder):
            base_center = self.obj.cylinder_obj.centers[i]
            if -1 not in base_center:
                color = self.select_color(i, offscreen_bool, fill_flag)
                glColor4f(color[0], color[1], color[2], 0.1)
                glBegin(GL_TRIANGLES)
                for k in range(1,len(vertices)):                                
                    glVertex3f(base_center[0], base_center[1], base_center[2])
                    glVertex3f(vertices[k-1][0], vertices[k-1][1], vertices[k-1][2])
                    glVertex3f(vertices[k][0], vertices[k][1], vertices[k][2])
    
                glEnd()

        # Draw cylinder tops
        for i, vertices in enumerate(self.obj.cylinder_obj.top_vertices):
            base_center = self.obj.cylinder_obj.centers[i]
            if -1 not in base_center:
                top_center = self.obj.cylinder_obj.top_centers[i]
                color = self.select_color(i, offscreen_bool, fill_flag)
                # print(top_center)
                glColor4f(color[0], color[1], color[2], 0.1)
                glBegin(GL_TRIANGLES)
                for k in range(1,len(vertices)):                                
                    glVertex3f(top_center[0], top_center[1], top_center[2])
                    glVertex3f(vertices[k][0], vertices[k][1], vertices[k][2])
                    glVertex3f(vertices[k-1][0], vertices[k-1][1], vertices[k-1][2])
    
                glEnd()

    
    # Draw transient circle    
    def render_transient_circle(self, bases, center, color):
        if len(bases) > 0:
            glColor4f(color[0], color[1], color[2], 0.1)
            glBegin(GL_TRIANGLES)                

            for i in range(1,len(bases)):                           
                glVertex3f(center[0], center[1], center[2])
                glVertex3f(bases[i-1][0], bases[i-1][1], bases[i-1][2])
                glVertex3f(bases[i][0], bases[i][1], bases[i][2])
            glEnd()
            
    
    # Draw transient cylinder
    def render_transient_cylinders(self, cyl_bases, cyl_tops, center_base, center_top, color):        
        if len(cyl_bases) > 0:
            # Draw cylinder strips
            vertices = cyl_bases
            top_vertices = cyl_tops
            glColor4f(color[0], color[1], color[2], 0.1)
            glBegin(GL_TRIANGLE_STRIP)
            for k in range(0,len(vertices), 1):
                glVertex3f(vertices[k][0], vertices[k][1], vertices[k][2])
                glVertex3f(top_vertices[k][0], top_vertices[k][1], top_vertices[k][2])
            glEnd()


            # Draw cylinder bases
            base_center = center_base
            top_center = center_top
            glColor4f(color[0], color[1], color[2], 0.1)
            glBegin(GL_TRIANGLES)
            for k in range(1,len(vertices)):                                
                glVertex3f(base_center[0], base_center[1], base_center[2])
                glVertex3f(vertices[k-1][0], vertices[k-1][1], vertices[k-1][2])
                glVertex3f(vertices[k][0], vertices[k][1], vertices[k][2])
            glEnd()

            
            # Draw cylinder tops
            vertices = top_vertices
            glColor4f(color[0], color[1], color[2], 0.1)
            glBegin(GL_TRIANGLES)
            for k in range(1,len(vertices)):                                
                glVertex3f(top_center[0], top_center[1], top_center[2])
                glVertex3f(vertices[k][0], vertices[k][1], vertices[k][2])
                glVertex3f(vertices[k-1][0], vertices[k-1][1], vertices[k-1][2])
            glEnd()  




    def render_points(self):
        data = self.obj.ply_pts[-1]
        
        # # print(bezier_points)
        
        glColor3f(0.0, 1.0, 0.0)
        glPointSize(5)
        glBegin(GL_POINTS)
        
        for i in range(data.shape[0]):
            glVertex3f(data[i,0], data[i,1], data[i,2])
        glEnd()
        

    def render_quads(self, offscreen_bool = False):
        for i, pt_tup in enumerate(self.obj.ctrl_wdg.quad_obj.new_points):
            if not self.obj.ctrl_wdg.quad_obj.deleted[i]:
                if offscreen_bool:
                    co = self.obj.ctrl_wdg.quad_obj.colors[i+1]
                    glColor3f(co[0]/255, co[1]/255, co[2]/255)
                else:
                    if i==self.obj.ctrl_wdg.quad_obj.selected_quad_idx:
                        glColor3f(0.38, 0.85, 0.211)
                    else:
                        glColor3f(0, 0.6352, 1)                
                glBegin(GL_TRIANGLES)      
                glVertex3f(pt_tup[0][0], pt_tup[0][1], pt_tup[0][2])
                glVertex3f(pt_tup[3][0], pt_tup[3][1], pt_tup[3][2])
                glVertex3f(pt_tup[1][0], pt_tup[1][1], pt_tup[1][2])
        
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

    def render_bezier(self, offscreen_bool = False):
        if not offscreen_bool:
            glColor3f(0.0, 0.0, 0.0)
            for i,bezier_points in enumerate(self.obj.bezier_obj.bezier_points):            
                glBegin(GL_LINE_STRIP)
                for point in bezier_points:
                    glVertex3f(point[0], point[1], point[2])
                glEnd()
            
        if offscreen_bool:
            glPointSize(15)
        else:
            glPointSize(6)
        glBegin(GL_POINTS)
        
        for i, data_val in enumerate(self.obj.bezier_obj.all_data_val):    
            co1 = self.obj.bezier_obj.colors[2*i+1]
            co2 = self.obj.bezier_obj.colors[2*i+2]

            # print("---------------------")
            for j, pt in enumerate(data_val):
                if j==1 and offscreen_bool:
                    glColor3f(co1[0]/255, co1[1]/255, co1[2]/255)
                elif j==2 and offscreen_bool:
                    glColor3f(co2[0]/255, co2[1]/255, co2[2]/255)
                else:
                    glColor3f(0.0, 0.0, 1.0)
                glVertex3f(pt[0], pt[1], pt[2])
        if self.obj.bezier_obj.selected_curve_idx != -1 and not offscreen_bool:
            glColor3f(1.0, 0.0, 0.0)
            pt = self.obj.bezier_obj.all_data_val[self.obj.bezier_obj.selected_curve_idx][self.obj.bezier_obj.selected_point_idx]
            glVertex3f(pt[0], pt[1], pt[2])
        glEnd()         
                
                
                
    def select_3d_point(self):
        dd = glReadPixels(self.x, self.height()-self.y, 1, 1,GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
        px = gluUnProject(self.x, self.height()-self.y, dd)
        # print("select and pick")
        if dd < 1:
            if self.obj.ctrl_wdg.ui.bBezier:
                co = glReadPixels(self.x, self.height()-self.y, 1, 1,GL_RGB, GL_UNSIGNED_BYTE)
                ID = self.obj.ctrl_wdg.quad_obj.getIfromRGB(co[0], co[1], co[2])
                # print("ID : "+str(ID))
                
                if ID in self.obj.bezier_obj.bezier_count:
                    idx = self.obj.bezier_obj.bezier_count.index(ID)
                    self.obj.bezier_obj.selected_curve_idx = int(idx/2)
                    self.obj.bezier_obj.selected_point_idx = idx % 2 + 1

                else:    
                    dist = []
                    min_d = 0.0
                    for i, data_val in enumerate(self.obj.bezier_obj.all_data_val):
                        for j, pt in enumerate(data_val):
                            d = distance.euclidean(pt, px)
                            # print("Distance : "+str(d))
                            dist.append(d)
                    if len(dist) > 0:
                        min_d = min(dist)
                        
                    if min_d > 0.02 or len(dist) == 0:
                        self.obj.bezier_obj.data_val.append(np.array(px))
                        if len(self.obj.bezier_obj.data_val) == 4:
                            self.obj.bezier_obj.refresh_bezier_data()
                    # else:
                    #     print("This must be a bezier curve point")


            
            if self.obj.ctrl_wdg.ui.bCylinder or self.obj.ctrl_wdg.ui.bnCylinder:
                self.obj.cylinder_obj.data_val.append(np.array(px))
                if len(self.obj.cylinder_obj.data_val) == 4:
                    self.obj.cylinder_obj.refresh_cylinder_data()
                    
            if self.obj.ctrl_wdg.ui.bPick:
                co = glReadPixels(self.x, self.height()-self.y, 1, 1,GL_RGB, GL_UNSIGNED_BYTE)
                
                ID = self.obj.ctrl_wdg.quad_obj.getIfromRGB(co[0], co[1], co[2])
                # print("ID : "+str(ID))
                if ID in self.obj.ctrl_wdg.quad_obj.quad_counts:
                    self.obj.ctrl_wdg.quad_obj.selected_quad_idx = self.obj.ctrl_wdg.quad_obj.quad_counts.index(ID)
                    self.obj.cylinder_obj.selected_cylinder_idx = -1
                    
                elif ID in self.obj.cylinder_obj.cylinder_count:
                    cyl_idx = self.obj.cylinder_obj.cylinder_count.index(ID)
                    self.obj.cylinder_obj.selected_cylinder_idx = cyl_idx
                    self.obj.ctrl_wdg.quad_obj.selected_quad_idx = -1


        if self.obj.ctrl_wdg.ui.bMeasure and dd < 1:
            if self.bCalibrate:
                if self.clicked_once:
                    self.bCalibrate = False
                    self.util_.create_calibration_panel()
                    if self.util_.cal_dialog.exec():
                        measured_dist = int(self.util_.e1.text())
                        dist = np.sqrt(np.sum(np.square(np.array(px)-self.calc_last_3d_pos)))
                        self.calibration_factor = measured_dist/dist
                        self.util_.set_distance(measured_dist)
                    self.clicked_once = not self.clicked_once
                else:
                    self.last_pos = np.array([self.x, self.y])
                    self.calc_last_3d_pos = np.array(px)
                
            else:                
                if self.clicked_once and self.calibration_factor != 1:
                    self.dist = round(self.calibration_factor * np.sqrt(np.sum(np.square(np.array(px)-self.last_3d_pos))), 2)
                    self.util_.set_distance(self.dist)
                    # print("Distance is measured as : "+str(self.dist))
                else:
                    self.last_pos = np.array([self.x, self.y])
                    self.last_3d_pos = np.array(px)
 
            self.clicked_once = not self.clicked_once

        self.pick = False