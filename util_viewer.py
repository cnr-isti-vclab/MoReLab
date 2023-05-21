from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import Image
from PIL.ImageQt import ImageQt 
import cv2, copy
import numpy as np
from scipy.spatial import distance
from util.util import *
# from OpenGL.GL import *
# from OpenGL.GLU import *
# from PyQt5.QtOpenGL import *




class Util_viewer(QWidget):
    def __init__(self, parent=None):
        # Widget.__init__(self, parent)
        super().__init__(parent)
        self.parent_viewer = parent
        self.mv_pix, self.dist_thresh = 1, 10
        self._zoom, self.offset_x, self.offset_y = 1, 0, 0
        self.x, self.y = 1, 1
        self.w1, self.w2, self.h1, self.h2 = 0, 0, 0, 0
        self.x_zoomed, self.y_zoomed = 1, 1
        self.pick, self.move_feature_bool, self.move_pick = False, False, False
        self.clicked_once = False
        self.last_3d_pos = np.array([0.0,0.0, 0.0])

        self.last_pos = np.array([0.0,0.0])
        self.current_pos = np.array([0.0,0.0])
        self.calibration_factor, self.dist = 1.0, 0.0
        self.bCalibrate = True
        self.measured_distances = []
        self.bFirst_curve = False
        self.curve_lp = np.array([0.0,0.0])
        self.curve_cp = np.array([0.0,0.0])
        
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
            # print("widget Width : "+str(self.parent_viewer.width()))
            # print("widget Height : "+str(self.parent_viewer.height()))
            self.aspect_widget = self.parent_viewer.width()/self.parent_viewer.height()
            self.set_default_view_param()
            w = int(self.w2-self.w1)
            h = int(self.h2-self.h1)
            # print("adjusted width and height of widget")
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
        scale = self._zoom
        # print(K)
        # print(scale, self.offset_x, self.offset_y)
        cx = K[0,2]
        cy = K[1,2]
        # print(cx, cy)
        perspective = np.zeros((4,4))

        
        v = self.parent_viewer.obj.ctrl_wdg.mv_panel.movie_caps[self.parent_viewer.obj.ctrl_wdg.mv_panel.selected_movie_idx]
        width = v.width*(self.parent_viewer.width()/(self.w2 - self.w1))
        height = v.height*(self.parent_viewer.height()/(self.h2-self.h1))
        
        perspective[0][0] =  2.0 * scale * K[0,0] / width
        perspective[1][1] = -2.0 * scale * K[1,1] / height
        perspective[2][0] =  1.0 - 2.0 * cx / width
        perspective[2][1] =  2.0 * cy / height -1.0
        perspective[2][2] =  (zf + zn) / d
        perspective[2][3] =  -1.0
        perspective[3][2] = 2.0 * zn * zf / d
        
        # print(perspective)

        perspective = perspective.transpose()
        # print(perspective)

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
        
        label = QLabel("Enter the distance in inches : ")
        
        self.e1 = QLineEdit("1")
        self.e1.setValidator(QDoubleValidator())
        self.e1.setMaxLength(10)
        self.e1.setFont(QFont("Arial",20))
        
        self.cal_layout = QVBoxLayout()
        self.cal_layout.addWidget(label)
        self.cal_layout.addWidget(self.e1)
        self.cal_layout.addWidget(buttonBox)
        self.cal_dialog.setLayout(self.cal_layout)
        
        
    def set_distance(self, d):
        d = round(d, 3)
        self.dist_label.setText("Measured distance : "+str(d))
        
    
    
    def util_key_press(self, event, ctrl_wdg):
        v = ctrl_wdg.mv_panel.movie_caps[ctrl_wdg.mv_panel.selected_movie_idx]
        f = self.parent_viewer.obj.feature_panel.selected_feature_idx
        t = ctrl_wdg.selected_thumbnail_index
        
        
        if ctrl_wdg.ui.bBezier and event.key() == Qt.Key_F and len(self.parent_viewer.obj.curve_obj.final_bezier) == 0:
            self.parent_viewer.obj.curve_obj.find_final_curve()
            
        if ctrl_wdg.ui.bBezier and len(self.parent_viewer.obj.curve_obj.final_base_centers) > 0 and event.key() == Qt.Key_C and event.modifiers() & Qt.ControlModifier:
            self.parent_viewer.obj.curve_obj.final_base_centers.append(self.parent_viewer.obj.curve_obj.final_base_centers[-1].copy())
            self.parent_viewer.obj.curve_obj.final_top_centers.append(self.parent_viewer.obj.curve_obj.final_top_centers[-1].copy())
            self.parent_viewer.obj.curve_obj.final_cylinder_bases.append(copy.deepcopy(self.parent_viewer.obj.curve_obj.final_cylinder_bases[-1]))
            self.parent_viewer.obj.curve_obj.final_cylinder_tops.append(copy.deepcopy(self.parent_viewer.obj.curve_obj.final_cylinder_tops[-1]))
            
            # print("Count : "+str(len(self.parent_viewer.obj.curve_obj.final_base_centers)))
            
        if ctrl_wdg.ui.bBezier and len(self.parent_viewer.obj.curve_obj.final_base_centers) > 0:
            base_centers = self.parent_viewer.obj.curve_obj.final_base_centers[-1]
            # print(np.asarray(base_centers).shape)
            center = np.mean(np.asarray(base_centers), axis=0)
            # print(center)
            P1 = base_centers[0]
            P4 = base_centers[1]
            P3 = self.parent_viewer.obj.curve_obj.final_cylinder_bases[-1][0][0]
            P2 = np.cross(P4 - P1 , P3 - P1) + P1
            x_axis = (P3 - P1)/np.linalg.norm(P3 - P1)
            y_axis = (P4 - P1)/np.linalg.norm(P4 - P1)
            z_axis = (P2 - P1)/np.linalg.norm(P2 - P1)
            
            if event.key() == Qt.Key_X:
                if event.modifiers() & Qt.ControlModifier:
                    self.parent_viewer.obj.curve_obj.rotate(-0.1, x_axis, center)
                else:
                    self.parent_viewer.obj.curve_obj.rotate(0.1, x_axis, center)
                    
            if event.key() == Qt.Key_Y:
                if event.modifiers() & Qt.ControlModifier:
                    self.parent_viewer.obj.curve_obj.rotate(-0.1, y_axis, center)
                else:
                    self.parent_viewer.obj.curve_obj.rotate(0.1, y_axis, center)
            
            if event.key() == Qt.Key_Z:
                if event.modifiers() & Qt.ControlModifier:
                    self.parent_viewer.obj.curve_obj.rotate(-0.1, z_axis, center)
                else:
                    self.parent_viewer.obj.curve_obj.rotate(0.1, z_axis, center)
                    
            if event.key() == Qt.Key_Right:
                self.parent_viewer.obj.curve_obj.translate(np.array([0.005, 0, 0]))
                    
            if event.key() == Qt.Key_Left:
                self.parent_viewer.obj.curve_obj.translate(np.array([-0.005, 0, 0]))

            if event.key() == Qt.Key_Up:
                self.parent_viewer.obj.curve_obj.translate(np.array([0, 0.005, 0]))

            if event.key() == Qt.Key_Down:
                self.parent_viewer.obj.curve_obj.translate(np.array([0, -0.005, 0]))

            
        
        if ctrl_wdg.ui.cross_hair and event.key() == Qt.Key_Escape:
            self.parent_viewer.obj.feature_panel.selected_feature_idx = -1
            
        if ctrl_wdg.ui.bMeasure and event.key() == Qt.Key_L:
            if ctrl_wdg.kf_method == "Regular":
                v.measured_pos_regular[t].pop()
                v.measured_pos_regular[t].pop()
                v.measured_distances_regular[t].pop()
            elif ctrl_wdg.kf_method == "Network":
                v.measured_pos_network[t].pop()
                v.measured_pos_network[t].pop()
                v.measured_distances_network[t].pop()
            
        if ctrl_wdg.ui.cross_hair and f != -1:
            if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                self.parent_viewer.obj.delete_feature()
                
            elif event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
                if ctrl_wdg.kf_method == "Regular":
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
                        
                    self.parent_viewer.obj.move_feature(x, y, v.features_regular[t][f])

                elif ctrl_wdg.kf_method == "Network":
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

                    self.parent_viewer.obj.move_feature(x, y, v.features_network[t][f])
                
        if ctrl_wdg.ui.cross_hair and event.modifiers() & Qt.ControlModifier:
            self.parent_viewer.obj.feature_panel.selected_feature_idx = -1
            if event.key() == Qt.Key_C:
                ctrl_wdg.copy_features()
            elif event.key() == Qt.Key_V:
                ctrl_wdg.paste_features()
            
            if ctrl_wdg.kf_method == "Regular":
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
                            
            elif ctrl_wdg.kf_method == "Network":
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
            
            self.parent_viewer.obj.feature_panel.display_data()

        if ctrl_wdg.ui.bPick:
            if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                if self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx != -1: 
                    self.parent_viewer.obj.cylinder_obj.delete_cylinder(self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx)
                elif ctrl_wdg.rect_obj.selected_rect_idx != -1:
                    ctrl_wdg.rect_obj.delete_rect(ctrl_wdg.rect_obj.selected_rect_idx)
                elif ctrl_wdg.quad_obj.selected_quad_idx != -1:
                    ctrl_wdg.quad_obj.delete_quad(ctrl_wdg.quad_obj.selected_quad_idx)
                else:
                    del_primitive_dialogue()
                    
            if event.key() == Qt.Key_Escape:                        
                ctrl_wdg.rect_obj.selected_rect_idx = -1
                self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx = -1
                ctrl_wdg.rect_obj.selected_quad_idx = -1
                
                
    def util_mouse_press(self, event, ctrl_wdg):
        a = event.pos()
        x = int((a.x()-self.parent_viewer.width()/2 - self.offset_x)/self._zoom + self.parent_viewer.width()/2) 
        y = int((a.y()-self.parent_viewer.height()/2 - self.offset_y)/self._zoom + self.parent_viewer.height()/2)
        
        v = ctrl_wdg.mv_panel.movie_caps[ctrl_wdg.mv_panel.selected_movie_idx]
        t = ctrl_wdg.selected_thumbnail_index
        
        if event.button() == Qt.RightButton:
            self.press_loc = (a.x(), a.y())
        
        elif event.button() == Qt.LeftButton:
            if ctrl_wdg.ui.cross_hair:
                if ctrl_wdg.kf_method == "Regular":
                    if len(v.features_regular) > 0:
                        for i, fc in enumerate(v.features_regular[t]):
                            if not v.hide_regular[t][i]:
                                d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                                if d < self.dist_thresh:
                                    self.parent_viewer.obj.feature_panel.selected_feature_idx = i
                                    self.parent_viewer.obj.feature_panel.select_feature()
                                    self.move_feature_bool = True
    
    
                elif ctrl_wdg.kf_method == "Network":
                    if len(v.features_network) > 0:
                        for i, fc in enumerate(v.features_network[t]):
                            if not v.hide_network[t][i]:
                                d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                                if d < self.dist_thresh:
                                    self.parent_viewer.obj.feature_panel.selected_feature_idx = i
                                    self.parent_viewer.obj.feature_panel.select_feature()
                                    self.move_feature_bool = True
            
            selected_feature = False
            if (ctrl_wdg.ui.bRect or ctrl_wdg.ui.bQuad or ctrl_wdg.ui.bCylinder or ctrl_wdg.ui.bnCylinder or ctrl_wdg.ui.bMeasure or ctrl_wdg.ui.bPick or ctrl_wdg.ui.bBezier) and len(self.parent_viewer.obj.ply_pts) > 0:
                if ctrl_wdg.ui.bRect:
                    selected_feature = ctrl_wdg.rect_obj.select_feature(x, y)
                if ctrl_wdg.ui.bQuad:
                    selected_feature = ctrl_wdg.quad_obj.select_feature(x, y)
                if ctrl_wdg.ui.bCylinder or ctrl_wdg.ui.bnCylinder:
                    selected_feature = self.parent_viewer.obj.cylinder_obj.select_feature(x, y)
                    
                if ctrl_wdg.ui.bBezier:
                    if len(self.parent_viewer.obj.curve_obj.final_bezier) < 1:
                        # print("Inside")
                        if ctrl_wdg.kf_method == "Regular":
                            if len(v.curve_groups_regular[t]) < 4 and len(v.features_regular[t]) > 0:
                                self.parent_viewer.obj.curve_obj.make_curve(x, y, self.w1, self.w2, self.h1, self.h2)
                                selected_feature = True
                            else:                     
                                bs = self.parent_viewer.obj.curve_obj.select_feature(x, y)
                                selected_feature = not bs
                                
                        elif ctrl_wdg.kf_method == "Network":
                            if len(v.curve_groups_network[t]) < 4 and len(v.features_network[t]) > 0:
                                self.parent_viewer.obj.curve_obj.make_curve(x, y)
                                selected_feature = True
                            else:                     
                                bs = self.parent_viewer.obj.curve_obj.select_feature(x, y, self.w1, self.w2, self.h1, self.h2)
                                selected_feature = not bs
                                
                        
                    
                if not selected_feature:
                    self.x = a.x()
                    self.y = a.y()
                    self.x_zoomed, self.y_zoomed = x, y
                    self.pick = True
             
    
                
    def paint_image(self, v, t, painter, ctrl_wdg):
        if self.img_file is not None:
            painter.begin(self.parent_viewer)
            pen = QPen(QColor(250.0, 255.0, 255.0))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setFont(painter.font())
            painter.setBrush(QBrush(Qt.blue, Qt.SolidPattern))
            
            if self._zoom >=1:
                # Pan the scene
                painter.translate(self.offset_x, self.offset_y)
                # Zoom the scene
                painter.translate(self.parent_viewer.width()/2, self.parent_viewer.height()/2)
                painter.scale(self._zoom, self._zoom)
                painter.translate(-self.parent_viewer.width()/2, -self.parent_viewer.height()/2)
                
            
            painter.drawImage(self.w1, self.h1, self.img_file)
            
            if ctrl_wdg.kf_method == "Regular":
                if len(v.features_regular) > 0:
                    for i, fc in enumerate(v.features_regular[t]):
                        if not v.hide_regular[t][i]:
                            painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
    
            elif ctrl_wdg.kf_method == "Network":
                if len(v.features_network) > 0:
                    for i, fc in enumerate(v.features_network[t]):
                        if not v.hide_network[t][i]:
                            painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc, fc.x_loc + fc.l/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
                                   
            pen = QPen(QColor(0, 255, 0))
            pen.setWidth(2)
            painter.setPen(pen)
            
            # Painting the selected feature
            
            if self.parent_viewer.obj.feature_panel.selected_feature_idx != -1 and ctrl_wdg.ui.cross_hair:
                if ctrl_wdg.kf_method == "Regular" and len(v.features_regular[t]) > 0 and not v.hide_regular[t][self.parent_viewer.obj.feature_panel.selected_feature_idx]:
                    fc = v.features_regular[t][self.parent_viewer.obj.feature_panel.selected_feature_idx]
                    painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc, fc.x_loc + fc.l/2, fc.y_loc))
                    painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                    painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
                
                elif ctrl_wdg.kf_method == "Network" and len(v.features_network[t]) > 0 and not v.hide_network[t][self.parent_viewer.obj.feature_panel.selected_feature_idx]:
                    fc = v.features_network[t][self.parent_viewer.obj.feature_panel.selected_feature_idx]
                    painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc, fc.x_loc + fc.l/2, fc.y_loc))
                    painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                    painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
            
            
            # Painting for Rectangle Tool
            if (len(v.rect_groups_regular) > 0 or len(v.rect_groups_network) > 0) :
                if ctrl_wdg.kf_method == "Regular":
                    for i, fc in enumerate(v.features_regular[t]):
                        if v.rect_groups_regular[t][i] != -1:
                            painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))

                    
                elif ctrl_wdg.kf_method == "Network":
                    for i, fc in enumerate(v.features_network[t]):
                        if v.rect_groups_network[t][i] != -1:
                            painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
                            
                            
            # Painting for Quad Tool
            if (len(v.rect_groups_regular) > 0 or len(v.rect_groups_network) > 0):
                if ctrl_wdg.kf_method == "Regular":
                    for i, fc in enumerate(v.features_regular[t]):
                        if v.quad_groups_regular[t][i] != -1:
                            painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))

                    
                elif ctrl_wdg.kf_method == "Network":
                    for i, fc in enumerate(v.features_network[t]):
                        if v.quad_groups_network[t][i] != -1:
                            painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
                            

            # Painting for Sphere Tool
            if (len(v.cylinder_groups_regular) > 0 or len(v.cylinder_groups_network) > 0) :
                if ctrl_wdg.kf_method == "Regular":
                    for i, fc in enumerate(v.features_regular[t]):
                        if v.cylinder_groups_regular[t][i] != -1:
                            painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))

                    
                elif ctrl_wdg.kf_method == "Network":
                    for i, fc in enumerate(v.features_network[t]):
                        if v.cylinder_groups_network[t][i] != -1:
                            painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
                            


            # Painting for selected curve point
            if (len(v.curve_pts_regular) > 0 or len(v.curve_pts_network) > 0) :
                if ctrl_wdg.kf_method == "Regular":
                    if len(v.curve_pts_regular[t]) > 0:
                        ind = v.curve_pts_regular[t][0]
                        fc = v.features_regular[t][ind]
                        painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                        painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                        painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
                        
                elif ctrl_wdg.kf_method == "Network":
                    if len(v.curve_pts_network[t]) > 0:
                        ind = v.curve_pts_network[t][-1]
                        fc = v.features_network[t][ind]
                        painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                        painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                        painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))


                            
            # #### Painting for Curve
            if len(v.curve_groups_regular) > 0 or len(v.curve_groups_network) > 0:
                # print(v.curve_groups_regular[t])
                if ctrl_wdg.kf_method == "Regular":
                    data_val = v.curve_groups_regular[t]

                elif ctrl_wdg.kf_method == "Network":
                    data_val = v.curve_groups_network[t]

                if 0 < len(data_val) < 4:
                    painter.drawLine(QLineF(data_val[-1][0], data_val[-1][1] ,  self.current_pos[0], self.current_pos[1]))
            
                for i, p in enumerate(data_val):
                    painter.drawEllipse(p[0]-3, p[1]-3, 6, 6)
                
                for j in range(len(data_val) - 1):
                    painter.drawLine(QLineF(data_val[j][0], data_val[j][1] ,  data_val[j+1][0], data_val[j+1][1]))
 
            painter.end()
            
                
    def util_select_3d(self, dd, px, co, ctrl_wdg):
        # print("select and pick")
        v = ctrl_wdg.mv_panel.movie_caps[ctrl_wdg.mv_panel.selected_movie_idx]
        t = ctrl_wdg.selected_thumbnail_index
        if ctrl_wdg.ui.bBezier and len(self.parent_viewer.obj.curve_obj.radius_point) == 0 and dd < 1:
            if len(self.parent_viewer.obj.curve_obj.final_bezier) > 0 and len(self.parent_viewer.obj.curve_obj.radius_point) < 1 :
                self.parent_viewer.obj.curve_obj.radius_point.append(np.array(px))
                if len(self.parent_viewer.obj.curve_obj.radius_point) == 1:
                    self.parent_viewer.obj.curve_obj.make_general_cylinder()
                    
            
            else:
                if dd < 1:
                    if ctrl_wdg.kf_method == "Regular":
                        if len(v.curve_3d_point_regular[t]) < 1:
                            v.curve_3d_point_regular[t].append(np.array(px))
                            for j, tup in enumerate(self.parent_viewer.obj.camera_projection_mat):
                                if tup[0] == t:
                                    G = self.parent_viewer.obj.camera_projection_mat[j][1][0:3, :]
                                    P = np.matmul(self.parent_viewer.obj.K, G)
                                    self.parent_viewer.obj.curve_obj.estimate_plane(P)
                                    
                    elif ctrl_wdg.kf_method == "Network":
                        if len(v.curve_3d_point_network[t]) < 1:
                            v.curve_3d_point_network[t].append(np.array(px))
                            
                            for j, tup in enumerate(self.parent_viewer.obj.camera_projection_mat):
                                if tup[0] == t: 
                                    G = self.parent_viewer.obj.camera_projection_mat[j][1][0:3, :]
                                    P = np.matmul(self.parent_viewer.obj.K, G)
                                    
                                    self.parent_viewer.obj.curve_obj.estimate_plane(P) 
                else:
                    if ctrl_wdg.kf_method == "Regular":
                        v.curve_pts_regular[t].pop()
                    elif ctrl_wdg.kf_method == "Network":
                        v.curve_pts_network[t].pop()
                
        if dd < 1:
            if ctrl_wdg.ui.bnCylinder or ctrl_wdg.ui.bCylinder:
                self.parent_viewer.obj.cylinder_obj.data_val.append(np.array(px))
                if len(self.parent_viewer.obj.cylinder_obj.data_val) == 4:
                    data_val = self.parent_viewer.obj.cylinder_obj.data_val
                    if ctrl_wdg.ui.bnCylinder:
                        bases, tops, center, top_c = self.parent_viewer.obj.cylinder_obj.make_new_cylinder(data_val[0], data_val[1], data_val[2], data_val[3])
                        if len(bases) > 0:
                            self.parent_viewer.obj.cylinder_obj.refresh_cylinder_data(bases, tops, center, top_c)
                        else:
                            straight_line_dialogue()
                            del self.parent_viewer.obj.cylinder_obj.data_val[-1]

                    else:
                        bases, tops, center, top_c = self.parent_viewer.obj.cylinder_obj.make_cylinder(data_val[0], data_val[1], data_val[2], data_val[3])
                        self.parent_viewer.obj.cylinder_obj.refresh_cylinder_data(bases, tops, center, top_c)

                    
            if ctrl_wdg.ui.bPick:
                ID = ctrl_wdg.rect_obj.getIfromRGB(co[0], co[1], co[2])
                # print("ID : "+str(ID))
                # print(self.parent_viewer.obj.curve_obj.curve_count)
                if ID in ctrl_wdg.rect_obj.rect_counts:
                    ctrl_wdg.rect_obj.selected_rect_idx = ctrl_wdg.rect_obj.rect_counts.index(ID)
                    self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx = -1
                    ctrl_wdg.quad_obj.selected_quad_idx = -1
                    self.parent_viewer.obj.curve_obj.selected_curve_idx = -1
                    
                elif ID in self.parent_viewer.obj.cylinder_obj.cylinder_count:
                    cyl_idx = self.parent_viewer.obj.cylinder_obj.cylinder_count.index(ID)
                    self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx = cyl_idx
                    ctrl_wdg.rect_obj.selected_rect_idx = -1
                    ctrl_wdg.quad_obj.selected_quad_idx = -1
                    self.parent_viewer.obj.curve_obj.selected_curve_idx = -1
                    
                    
                elif ID in ctrl_wdg.quad_obj.group_counts:
                    quad_idx = ctrl_wdg.quad_obj.group_counts.index(ID)
                    ctrl_wdg.quad_obj.selected_quad_idx = quad_idx
                    ctrl_wdg.rect_obj.selected_rect_idx = -1
                    self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx = -1
                    self.parent_viewer.obj.curve_obj.selected_curve_idx = -1
                    
                elif ID in self.parent_viewer.obj.curve_obj.curve_count:
                    curve_idx = self.parent_viewer.obj.curve_obj.curve_count.index(ID)
                    # print("Curve idx : "+str(curve_idx))
                    self.parent_viewer.obj.curve_obj.selected_curve_idx = curve_idx
                    print(self.parent_viewer.obj.curve_obj.selected_curve_idx)
                    # ctrl_wdg.rect_obj.selected_rect_idx = -1
                    self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx = -1
                    ctrl_wdg.quad_obj.selected_quad_idx = -1
                    
                    
        if ctrl_wdg.ui.bMeasure and dd < 1:
            # print(self.x_zoomed, self.y_zoomed)
            if self.bCalibrate:
                if self.clicked_once:
                    self.bCalibrate = False
                    self.create_calibration_panel()
                    if self.cal_dialog.exec():
                        measured_dist = float(self.e1.text())
                        # print("Measured distance : "+str(measured_dist))
                        dist = np.sqrt(np.sum(np.square(np.array(px)-self.calc_last_3d_pos)))
                        
                        self.calibration_factor = measured_dist/dist
                        # print("calibration factor : "+str(self.calibration_factor))
                        self.set_distance(measured_dist)
                        if ctrl_wdg.kf_method == "Regular":
                            v.measured_distances_regular[t].append(measured_dist)
                        elif ctrl_wdg.kf_method == "Network":
                            v.measured_distances_network[t].append(measured_dist)

                    self.clicked_once = not self.clicked_once
                else:
                    self.last_pos = np.array([self.x_zoomed, self.y_zoomed])
                    self.calc_last_3d_pos = np.array(px)
                    if ctrl_wdg.kf_method == "Regular":
                        v.measured_pos_regular[t].append((self.x_zoomed, self.y_zoomed))
                    elif ctrl_wdg.kf_method == "Network":
                        v.measured_pos_network[t].append((self.x_zoomed, self.y_zoomed))                        
                
            else:                
                if self.clicked_once and self.calibration_factor != 1:
                    self.dist = self.calibration_factor * np.sqrt(np.sum(np.square(np.array(px)-self.last_3d_pos)))
                    # print("Calculated distance : "+str(self.dist))
                    self.set_distance(self.dist)
                    if ctrl_wdg.kf_method == "Regular":
                        v.measured_pos_regular[t].append((self.x_zoomed, self.y_zoomed))
                        v.measured_distances_regular[t].append(self.dist)
                    elif ctrl_wdg.kf_method == "Network":
                        v.measured_pos_network[t].append((self.x_zoomed, self.y_zoomed))
                        v.measured_distances_network[t].append(self.dist)
                    # print("Distance is measured as : "+str(self.dist))
                else:
                    self.last_pos = np.array([self.x_zoomed, self.y_zoomed])
                    if ctrl_wdg.kf_method == "Regular":
                        v.measured_pos_regular[t].append((self.x_zoomed, self.y_zoomed))
                    elif ctrl_wdg.kf_method == "Network":
                        v.measured_pos_network[t].append((self.x_zoomed, self.y_zoomed))
                    self.last_3d_pos = np.array(px)
                    

             
            self.clicked_once = not self.clicked_once

        self.pick = False