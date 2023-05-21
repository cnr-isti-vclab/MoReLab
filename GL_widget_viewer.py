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

        self.x_shift = -0.5

        self.move_x, self.move_y = 1, 1
        self.fill_color = (0.0, 0.6252, 1.0)
        self.boundary_color = (0.0, 0.0, 0.0)
        self.selected_color = (0.38, 0.85, 0.211)

        self.flag_g = False

  

            
    def paintGL(self):
        t = self.obj.ctrl_wdg.selected_thumbnail_index
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        # print("Movie index : "+str(self.obj.ctrl_wdg.mv_panel.selected_movie_idx))
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
                    
                    # if self.obj.ctrl_wdg.ui.bRect or self.obj.ctrl_wdg.ui.bPick or self.obj.ctrl_wdg.ui.bMeasure or self.obj.ctrl_wdg.ui.bCylinder or self.obj.ctrl_wdg.ui.bnCylinder or self.obj.ctrl_wdg.ui.bBezier or self.obj.ctrl_wdg.ui.bQuad:
                    self.render_rect(True)

                    # if self.obj.ctrl_wdg.ui.bRect or self.obj.ctrl_wdg.ui.bPick or self.obj.ctrl_wdg.ui.bMeasure or self.obj.ctrl_wdg.ui.bCylinder or self.obj.ctrl_wdg.ui.bnCylinder or self.obj.ctrl_wdg.ui.bBezier or self.obj.ctrl_wdg.ui.bQuad:
                    self.render_quads(True)
                        
                    # if self.obj.ctrl_wdg.ui.bCylinder or self.obj.ctrl_wdg.ui.bPick or self.obj.ctrl_wdg.ui.bMeasure or self.obj.ctrl_wdg.ui.bnCylinder or self.obj.ctrl_wdg.ui.bBezier or self.obj.ctrl_wdg.ui.bRect or self.obj.ctrl_wdg.ui.bQuad:
                    glPolygonMode( GL_FRONT, GL_FILL)
                    self.render_cylinders(True, True)
                    glPolygonMode( GL_FRONT, GL_LINE)
                    self.render_cylinders(True, False)
                    glPolygonMode( GL_FRONT, GL_FILL)

                    if len(self.obj.curve_obj.final_cylinder_bases) > 0:
                        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                        self.render_general_cylinder(True, True)
                        glPolygonMode( GL_FRONT_AND_BACK, GL_LINE)
                        self.render_general_cylinder(True, False)
                        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL)
                        

        if self.util_.pick:
            dd = glReadPixels(self.util_.x, self.height()-self.util_.y, 1, 1,GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
            px = gluUnProject(self.util_.x, self.height()-self.util_.y, dd)
            co = glReadPixels(self.util_.x, self.height()-self.util_.y, 1, 1,GL_RGB, GL_UNSIGNED_BYTE)
            
            self.util_.util_select_3d(dd, px, co, self.obj.ctrl_wdg)
        
        bases = []
        center = [0,0,0]
        center_base = center
        center_top = center
        cyl_bases, cyl_tops = [], []
        if self.util_.move_pick:
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
                        

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBindTexture(GL_TEXTURE_2D, 0)

######################################################################################

# ------------------------------------------------------------------------------------------------------------------------
        glClearColor(0.8, 0.8, 0.8, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT| GL_STENCIL_BUFFER_BIT | GL_ACCUM_BUFFER_BIT )
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        

        self.util_.paint_image(v, t, self.painter, self.obj.ctrl_wdg)
        
        
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK) 
        glFrontFace(GL_CCW)
        
        
        if len(self.obj.ply_pts) > 0 and len(self.obj.camera_projection_mat) > 0:
            for j, tup in enumerate(self.obj.camera_projection_mat):
                if tup[0] == t: 
                    glViewport(int(self.util_.offset_x), -1*int(self.util_.offset_y), int(self.width()), int(self.height()))
                    # print(tup[1].shape)
                    # print(tup[1])

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

                    # if self.obj.ctrl_wdg.ui.bRect or self.obj.ctrl_wdg.ui.bPick :
                    self.render_rect(False)
                    
                    # if self.obj.ctrl_wdg.ui.bQuad or self.obj.ctrl_wdg.ui.bPick :
                    self.render_quads(False)
                    
                    # if self.obj.ctrl_wdg.ui.bCylinder or self.obj.ctrl_wdg.ui.bPick or self.obj.ctrl_wdg.ui.bnCylinder:
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
                        
                    # if self.obj.ctrl_wdg.ui.bBezier:
                    self.render_bezier(v, t)
                    if len(self.obj.curve_obj.final_cylinder_bases) > 0:
                        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                        self.render_general_cylinder(False, True)
                        glPolygonMode( GL_FRONT_AND_BACK, GL_LINE)
                        self.render_general_cylinder(False, False)
                        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL)


        glDisable(GL_CULL_FACE)


        self.painter.begin(self)
        pen = QPen(QColor(0, 255, 0))
        pen.setWidth(3)
        self.painter.setPen(pen)
        self.painter.setFont(QFont("times",10))
    
                
        if self.util_._zoom >=1:
            # Pan the scene
            self.painter.translate(self.util_.offset_x, self.util_.offset_y)
            # Zoom the scene
            self.painter.translate(self.width()/2, self.height()/2)
            self.painter.scale(self.util_._zoom, self.util_._zoom)
            self.painter.translate(-self.width()/2, -self.height()/2)
        
        # Draw all lines
        measured_pos = []
        measured_dist = []
        
        if self.obj.ctrl_wdg.kf_method == "Regular":
            if len(v.measured_pos_regular) > 0:
                measured_pos = v.measured_pos_regular[t]
                measured_dist = v.measured_distances_regular[t]
        elif self.obj.ctrl_wdg.kf_method == "Network":
            if len(v.measured_pos_network) > 0:
                measured_pos = v.measured_pos_network[t]
                measured_dist = v.measured_distances_network[t]
            
        if len(measured_pos) > 1 and self.obj.ctrl_wdg.ui.bMeasure:
            for i in range(1,len(measured_pos),2):
                p1 = measured_pos[i-1]
                p2 = measured_pos[i]
                self.painter.drawLine(QLineF(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1])))
                idx_t = int(i/2)
                if len(measured_dist) > 0:
                    self.painter.drawText(p2[0]-20, p2[1]+20, str(round(measured_dist[idx_t], 3)))

        # Draw transient Measuring Line
        if self.obj.ctrl_wdg.ui.bMeasure and self.util_.clicked_once:            
            self.painter.drawLine(QLineF(self.util_.last_pos[0], self.util_.last_pos[1], self.util_.current_pos[0], self.util_.current_pos[1]))

        self.painter.end()


    def mouseDoubleClickEvent(self, event):
        a = event.pos()
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        if self.util_.img_file is not None and self.obj.ctrl_wdg.ui.cross_hair:
            # print(a.x(), a.y())
            if a.x() > 0 and a.y() > 0:
                x = int((a.x()-self.width()/2 - self.util_.offset_x)/self.util_._zoom + self.width()/2) 
                y = int((a.y()-self.height()/2 - self.util_.offset_y)/self.util_._zoom + self.height()/2)
                if x > self.util_.w1 and y > self.util_.h1 and x < self.util_.w2 and y < self.util_.h2:
                    self.obj.add_feature(x, y)


    def keyPressEvent(self, event):
        self.util_.util_key_press(event, self.obj.ctrl_wdg)

        super(GL_Widget, self).keyPressEvent(event)


    def wheelEvent(self, event):
        if self.util_.img_file is not None:
            if self.obj.ctrl_wdg.rect_obj.selected_rect_idx != -1 and self.obj.ctrl_wdg.ui.bPick:
                if event.angleDelta().y() > 0:
                    self.obj.ctrl_wdg.rect_obj.scale_up()
                else:
                    self.obj.ctrl_wdg.rect_obj.scale_down()


            else:
                if event.angleDelta().y() > 0:
                    self.util_._zoom += 0.1
                else:
                    self.util_._zoom -= 0.1
                # print(self.width()/2)
                if self.util_._zoom < 1:
                    self.util_._zoom = 1
                    self.util_.offset_x = 0
                    self.util_.offset_y = 0
                    self.util_.set_default_view_param()
                



    # overriding the mousePressEvent method
    def mousePressEvent(self, event):
        self.util_.util_mouse_press(event, self.obj.ctrl_wdg)


    def mouseMoveEvent(self, event):
        a = event.pos()
        x = int((a.x()-self.width()/2 - self.util_.offset_x)/self.util_._zoom + self.width()/2) 
        y = int((a.y()-self.height()/2 - self.util_.offset_y)/self.util_._zoom + self.height()/2)
        v = self.obj.ctrl_wdg.mv_panel.movie_caps[self.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        if (self.obj.ctrl_wdg.ui.bMeasure or self.obj.ctrl_wdg.ui.bBezier) and len(self.obj.ply_pts) > 0:    
            self.util_.current_pos = np.array([x, y])
    
        if len(v.rect_groups_regular) > 0 or len(v.rect_groups_network) > 0:
            self.move_x = a.x()
            self.move_y = a.y()
            self.util_.move_pick = True
            
        if self.obj.ctrl_wdg.ui.cross_hair:
            if self.obj.ctrl_wdg.kf_method == "Regular":
                if len(v.features_regular) > 0 and self.util_.move_feature_bool:
                    self.obj.move_feature(x, y, v.features_regular[self.obj.ctrl_wdg.selected_thumbnail_index][self.obj.feature_panel.selected_feature_idx])
               
            elif self.obj.ctrl_wdg.kf_method == "Network":
                if len(v.features_network) > 0 and self.util_.move_feature_bool:
                    self.obj.move_feature(x, y, v.features_network[self.obj.ctrl_wdg.selected_thumbnail_index][self.obj.feature_panel.selected_feature_idx])



                
    def mouseReleaseEvent(self, event):
        a = event.pos()

        if event.button() == Qt.RightButton:
            self.release_loc = (a.x(), a.y())
            if self.util_._zoom >= 1:
                self.util_.offset_x += (self.release_loc[0] - self.util_.press_loc[0])
                self.util_.offset_y += (self.release_loc[1] - self.util_.press_loc[1])

        if self.obj.ctrl_wdg.ui.move_bool or self.obj.ctrl_wdg.ui.cross_hair:
            if event.button() == Qt.LeftButton:
                self.util_.move_feature_bool = False

                    

                

                
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
        glPointSize(5*self.util_._zoom)
        glBegin(GL_POINTS)
        
        for i in range(data.shape[0]):
            glVertex3f(data[i,0], data[i,1], data[i,2])
        glEnd()
        

    def render_rect(self, offscreen_bool = False):
        for i, pt_tup in enumerate(self.obj.ctrl_wdg.rect_obj.new_points):
            if not self.obj.ctrl_wdg.rect_obj.deleted[i]:
                if offscreen_bool:
                    co = self.obj.ctrl_wdg.rect_obj.colors[i+1]
                    glColor3f(co[0]/255, co[1]/255, co[2]/255)
                else:
                    if i==self.obj.ctrl_wdg.rect_obj.selected_rect_idx:
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
                
                
                glColor3f(self.boundary_color[0], self.boundary_color[1], self.boundary_color[2])
                glPointSize(5*self.util_._zoom)
                glBegin(GL_POINTS)
                
                for pt in pt_tup:
                    glVertex3f(pt[0], pt[1], pt[2])
                glEnd()
                
                
                glLineWidth(2.0)
                glColor3f(self.boundary_color[0], self.boundary_color[1], self.boundary_color[2])
                glBegin(GL_LINE_LOOP)
                glVertex3f(pt_tup[0][0], pt_tup[0][1], pt_tup[0][2])
                glVertex3f(pt_tup[1][0], pt_tup[1][1], pt_tup[1][2])
                glVertex3f(pt_tup[2][0], pt_tup[2][1], pt_tup[2][2])
                glVertex3f(pt_tup[3][0], pt_tup[3][1], pt_tup[3][2])
                glEnd()
                
                
                
                
                
    def render_quads(self, offscreen_bool = False):
        for i, pt_tup in enumerate(self.obj.ctrl_wdg.quad_obj.all_pts):
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

                glColor3f(self.boundary_color[0], self.boundary_color[1], self.boundary_color[2])

                glPointSize(5*self.util_._zoom)
                glBegin(GL_POINTS)
                
                for pt in pt_tup:
                    glVertex3f(pt[0], pt[1], pt[2])
                glEnd()


                
                glLineWidth(2.0)
                glColor3f(self.boundary_color[0], self.boundary_color[1], self.boundary_color[2])
                glBegin(GL_LINE_LOOP)
                glVertex3f(pt_tup[0][0], pt_tup[0][1], pt_tup[0][2])
                glVertex3f(pt_tup[1][0], pt_tup[1][1], pt_tup[1][2])
                glVertex3f(pt_tup[2][0], pt_tup[2][1], pt_tup[2][2])
                glVertex3f(pt_tup[3][0], pt_tup[3][1], pt_tup[3][2])
                glEnd()      
                
                
    def render_curve_planes(self):
        for i, pt_tup in enumerate(self.obj.curve_obj.planes):
            glColor3f(0.38, 0.85, 0.211)
            glBegin(GL_TRIANGLES)      
            glVertex3f(pt_tup[0][0], pt_tup[0][1], pt_tup[0][2])
            glVertex3f(pt_tup[3][0], pt_tup[3][1], pt_tup[3][2])
            glVertex3f(pt_tup[1][0], pt_tup[1][1], pt_tup[1][2])
    
            glVertex3f(pt_tup[2][0], pt_tup[2][1], pt_tup[2][2])
            glVertex3f(pt_tup[1][0], pt_tup[1][1], pt_tup[1][2])
            glVertex3f(pt_tup[3][0], pt_tup[3][1], pt_tup[3][2])
            glEnd()
            
            
    def render_bezier(self, v, t):
        
        glColor3f(0.0, 0.0, 0.0)
        pts = []
        if self.obj.ctrl_wdg.kf_method == "Regular":
            pts = v.curve_3d_point_regular[t]
        elif self.obj.ctrl_wdg.kf_method == "Network":
            pts = v.curve_3d_point_network[t]
        
        if len(pts) > 4:
            glBegin(GL_LINE_STRIP)
            for i in range(5, len(pts), 1):
                point = pts[i]
                glVertex3f(point[0], point[1], point[2])
            glEnd()
    
            glColor(0.0, 0.0, 0.0)
            # glPointSize(10)
            glPointSize(5*self.util_._zoom)
            glBegin(GL_POINTS)
            for i in range(1,5,1):
                p = pts[i]
                glVertex3f(p[0], p[1], p[2])
            glEnd()
            
        if len(self.obj.curve_obj.final_bezier) > 0:
            ctrl_pts = self.obj.curve_obj.ctrl_pts_final[-1]
            glColor3f(1.0, 0.0, 0.0)
            glPointSize(5*self.util_._zoom)
            glBegin(GL_POINTS)
            for i in range(ctrl_pts.shape[0]):
                p = ctrl_pts[i]
                glVertex3f(p[0], p[1], p[2])
            glEnd()

            
            glColor3f(1.0, 0.0, 0.0)        
            glBegin(GL_LINE_STRIP)
            points = self.obj.curve_obj.final_bezier[-1]
            for i in range(points.shape[0]):
                glVertex3f(points[i,0], points[i,1], points[i,2])
            glEnd()
            
        
    def render_general_cylinder(self, offscreen_bool = False, fill_flag=False):
        ##### Draw initial base of the cylinder
        for i, cylinder_bases in enumerate(self.obj.curve_obj.final_cylinder_bases):
            # print(i)
            if not self.obj.curve_obj.deleted[i]:
                if offscreen_bool:
                    co = self.obj.curve_obj.colors[i+1]
                    color = (co[0]/255, co[1]/255, co[2]/255)
                else:
                    if fill_flag:
                        if i==self.obj.curve_obj.selected_curve_idx:
                            color = self.selected_color
                        else:
                            color = self.fill_color
                    else:
                        color = self.boundary_color 
                        
                # print(self.obj.curve_obj.selected_curve_idx)
                glColor3f(color[0], color[1], color[2])
                
                vertices = cylinder_bases[0]
                base_center = self.obj.curve_obj.final_base_centers[i][0]
                glBegin(GL_TRIANGLES)
                for k in range(1,len(vertices)):                                
                    glVertex3f(base_center[0], base_center[1], base_center[2])
                    glVertex3f(vertices[k-1][0], vertices[k-1][1], vertices[k-1][2])
                    glVertex3f(vertices[k][0], vertices[k][1], vertices[k][2])
        
                glEnd()
            
            
                for j in range(1, len(cylinder_bases)):
                    base_1 = cylinder_bases[j-1]
                    base_2 = cylinder_bases[j]
                    
                    # print(len(base_1))
                    glColor3f(color[0], color[1], color[2])
                    glBegin(GL_TRIANGLE_STRIP)
                    sectorCount = self.obj.cylinder_obj.sectorCount
                    for k, vertex in enumerate(base_1):
                        if k < int(0.75*sectorCount) :
                            glVertex3f(vertex[0], vertex[1], vertex[2])
                            glVertex3f(base_2[k + int(0.25*sectorCount)][0], base_2[k + int(0.25*sectorCount)][1], base_2[k + int(0.25*sectorCount) ][2])
                        else:
                            glVertex3f(vertex[0], vertex[1], vertex[2])
                            glVertex3f(base_2[k - int(0.75*sectorCount) ][0], base_2[k - int(0.75*sectorCount)][1], base_2[k - int(0.75*sectorCount) ][2])
                    glEnd()
    
    
        
                #### Draw last cylinder between base and top
                vertices = cylinder_bases[-1]
                top_vertices = self.obj.curve_obj.final_cylinder_tops[i][-1]
                glColor3f(color[0], color[1], color[2])
                glBegin(GL_TRIANGLE_STRIP)
                for k in range(0,len(vertices), 1):
                    glVertex3f(vertices[k][0], vertices[k][1], vertices[k][2])
                    glVertex3f(top_vertices[k][0], top_vertices[k][1], top_vertices[k][2])
                glEnd()
                
                
                
                #### Draw final top of the cylinder
                glColor3f(color[0], color[1], color[2])
                vertices = self.obj.curve_obj.final_cylinder_tops[i][-1]
                # print("Number of nodes: ")
                top_center = self.obj.curve_obj.final_top_centers[i][-1]
                glBegin(GL_TRIANGLES)
                for k in range(1,len(vertices)):                                
                    glVertex3f(top_center[0], top_center[1], top_center[2])
                    glVertex3f(vertices[k][0], vertices[k][1], vertices[k][2])
                    glVertex3f(vertices[k-1][0], vertices[k-1][1], vertices[k-1][2])
    
        
                glEnd()
                
                