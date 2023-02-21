from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import Image
from PIL.ImageQt import ImageQt 
import cv2
import numpy as np
from scipy.spatial import distance



class Util_viewer(QWidget):
    def __init__(self, parent=None):
        # Widget.__init__(self, parent)
        super().__init__(parent)
        self.parent_viewer = parent
        self.mv_pix, self.dist_thresh = 1, 10
        self._zoom, self.offset_x, self.offset_y = 1, 0, 0
        self.x, self.y = 1, 1
        self.pick, self.move_feature_bool, self.move_pick = False, False, False
        self.clicked_once = False
        self.last_3d_pos = np.array([0.0,0.0, 0.0])
        self.last_pos = np.array([0.0,0.0])
        self.current_pos = np.array([0.0,0.0])
        self.calibration_factor, self.dist = 1.0, 0.0
        self.bCalibrate = True
        self.measured_pos = []
        self.measured_distances = []
        
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
        scale = self._zoom
        # print(K)
        # print(scale, self.offset_x, self.offset_y)
        cx = K[0,2] + self.offset_x*scale
        cy = K[1,2] + self.offset_y*scale
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
        
        if ctrl_wdg.ui.cross_hair and event.key() == Qt.Key_Escape:
            self.parent_viewer.obj.feature_panel.selected_feature_idx = -1
            
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
                elif ctrl_wdg.quad_obj.selected_quad_idx != -1:
                    ctrl_wdg.quad_obj.delete_quad(ctrl_wdg.quad_obj.selected_quad_idx)
                elif ctrl_wdg.connect_obj.selected_connect_idx != -1:
                    ctrl_wdg.connect_obj.delete_connect_group(ctrl_wdg.connect_obj.selected_connect_idx)
                else:
                    print("No 3D object has been selected")
                    
            if event.key() == Qt.Key_Escape:                        
                ctrl_wdg.quad_obj.selected_quad_idx = -1
                self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx = -1
                ctrl_wdg.connect_obj.selected_connect_idx = -1
                
                
    def util_mouse_press(self, event, ctrl_wdg):
        a = event.pos()
        x = int((a.x()-self.parent_viewer.width()/2 - self.offset_x)/self._zoom + self.parent_viewer.width()/2) 
        y = int((a.y()-self.parent_viewer.height()/2 - self.offset_y)/self._zoom + self.parent_viewer.height()/2)
        
        v = ctrl_wdg.mv_panel.movie_caps[ctrl_wdg.mv_panel.selected_movie_idx]
        t = ctrl_wdg.selected_thumbnail_index
        
        if event.button() == Qt.RightButton:
            self.press_loc = (a.x(), a.y())
        
        elif event.button() == Qt.LeftButton and ctrl_wdg.ui.cross_hair:
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

        if ctrl_wdg.ui.bQuad:
            selected_feature = ctrl_wdg.quad_obj.select_feature(x, y)
            if not selected_feature:
                self.x = a.x()
                self.y = a.y()
                self.pick = True
                
        if ctrl_wdg.ui.bConnect:
            selected_feature = ctrl_wdg.connect_obj.select_feature(x, y)
            if not selected_feature:
                self.x = a.x()
                self.y = a.y()
                self.pick = True
                
        if ctrl_wdg.ui.bCylinder or ctrl_wdg.ui.bnCylinder:
            selected_feature = self.parent_viewer.obj.cylinder_obj.select_feature(x, y)
            if not selected_feature:
                self.x = a.x()
                self.y = a.y()
                self.pick = True
                
        if ctrl_wdg.ui.bBezier:
            selected_feature = self.parent_viewer.obj.bezier_obj.select_feature(x, y)
            if not selected_feature:
                self.x = a.x()
                self.y = a.y()
                self.pick = True

            
        if ctrl_wdg.ui.bMeasure or ctrl_wdg.ui.bPick:
            self.x = a.x()
            self.y = a.y()
            self.pick = True
         
    
                
    def paint_image(self, v, t, painter, ctrl_wdg):
        if self.img_file is not None:
            painter.begin(self.parent_viewer)
            pen = QPen(QColor(250.0, 255.0, 255.0))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setFont(painter.font())
            
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
                                   
            pen = QPen(QColor(0, 0, 255))
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
            
            
            # Painting for Quad Tool
            if (len(v.quad_groups_regular) > 0 or len(v.quad_groups_network) > 0) and (ctrl_wdg.ui.bQuad or ctrl_wdg.ui.bPick or ctrl_wdg.ui.bMeasure) :
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
                            
                            
            # Painting for Dots Connecting Tool
            if (len(v.quad_groups_regular) > 0 or len(v.quad_groups_network) > 0) and (ctrl_wdg.ui.bConnect or ctrl_wdg.ui.bPick or ctrl_wdg.ui.bMeasure):
                if ctrl_wdg.kf_method == "Regular":
                    for i, fc in enumerate(v.features_regular[t]):
                        if v.connect_groups_regular[t][i] != -1:
                            painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))

                    
                elif ctrl_wdg.kf_method == "Network":
                    for i, fc in enumerate(v.features_network[t]):
                        if v.connect_groups_network[t][i] != -1:
                            painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
                            
   

            # Painting for Sphere Tool
            if (len(v.cylinder_groups_regular) > 0 or len(v.cylinder_groups_network) > 0) and (ctrl_wdg.ui.bCylinder or ctrl_wdg.ui.bnCylinder or ctrl_wdg.ui.bPick or ctrl_wdg.ui.bMeasure) :
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
                            
            # Bezier tool
            if (len(v.bezier_groups_regular) > 0 or len(v.bezier_groups_network) > 0) and ctrl_wdg.ui.bBezier:
                if ctrl_wdg.kf_method == "Regular":
                    for i, fc in enumerate(v.features_regular[t]):
                        if v.bezier_groups_regular[t][i] != -1:
                            painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))


                    
                elif ctrl_wdg.kf_method == "Network":
                    for i, fc in enumerate(v.features_network[t]):
                        if v.bezier_groups_network[t][i] != -1:
                            painter.drawLine(QLineF(fc.x_loc - fc.l/2, fc.y_loc , fc.x_loc + fc.l/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc-fc.l/2, fc.x_loc, fc.y_loc+fc.l/2))
                            painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))            
            
            
            painter.end()
            
                
    def util_select_3d(self, dd, px, co, ctrl_wdg):
        # print("select and pick")
        if dd < 1:
            if ctrl_wdg.ui.bBezier:
                ID = ctrl_wdg.quad_obj.getIfromRGB(co[0], co[1], co[2])
                # print("ID : "+str(ID))
                
                if ID in self.parent_viewer.obj.bezier_obj.bezier_count:
                    idx = self.parent_viewer.obj.bezier_obj.bezier_count.index(ID)
                    self.parent_viewer.obj.bezier_obj.selected_curve_idx = int(idx/2)
                    self.parent_viewer.obj.bezier_obj.selected_point_idx = idx % 2 + 1

                else:    
                    dist = []
                    min_d = 0.0
                    for i, data_val in enumerate(self.parent_viewer.obj.bezier_obj.all_data_val):
                        for j, pt in enumerate(data_val):
                            d = distance.euclidean(pt, px)
                            # print("Distance : "+str(d))
                            dist.append(d)
                    if len(dist) > 0:
                        min_d = min(dist)
                        
                    if min_d > 0.02 or len(dist) == 0:
                        self.parent_viewer.obj.bezier_obj.data_val.append(np.array(px))
                        if len(self.parent_viewer.obj.bezier_obj.data_val) == 4:
                            self.parent_viewer.obj.bezier_obj.refresh_bezier_data()
                    # else:
                    #     print("This must be a bezier curve point")


            
            if ctrl_wdg.ui.bCylinder or ctrl_wdg.ui.bnCylinder:
                self.parent_viewer.obj.cylinder_obj.data_val.append(np.array(px))
                if len(self.parent_viewer.obj.cylinder_obj.data_val) == 4:
                    self.parent_viewer.obj.cylinder_obj.refresh_cylinder_data()
                    
            if ctrl_wdg.ui.bPick:
                
                ID = ctrl_wdg.quad_obj.getIfromRGB(co[0], co[1], co[2])
                # print("ID : "+str(ID))
                if ID in ctrl_wdg.quad_obj.quad_counts:
                    ctrl_wdg.quad_obj.selected_quad_idx = ctrl_wdg.quad_obj.quad_counts.index(ID)
                    self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx = -1
                    ctrl_wdg.connect_obj.selected_connect_idx = -1
                    
                elif ID in self.parent_viewer.obj.cylinder_obj.cylinder_count:
                    cyl_idx = self.parent_viewer.obj.cylinder_obj.cylinder_count.index(ID)
                    self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx = cyl_idx
                    ctrl_wdg.quad_obj.selected_quad_idx = -1
                    ctrl_wdg.connect_obj.selected_connect_idx = -1
                    
                elif ID in ctrl_wdg.connect_obj.group_counts:
                    connect_idx = ctrl_wdg.connect_obj.group_counts.index(ID)
                    ctrl_wdg.connect_obj.selected_connect_idx = connect_idx
                    ctrl_wdg.quad_obj.selected_quad_idx = -1
                    self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx = -1
                    

        if ctrl_wdg.ui.bMeasure and dd < 1:
            if self.bCalibrate:
                if self.clicked_once:
                    self.bCalibrate = False
                    self.create_calibration_panel()
                    if self.cal_dialog.exec():
                        measured_dist = float(self.e1.text())
                        print("Measured distance : "+str(measured_dist))
                        dist = np.sqrt(np.sum(np.square(np.array(px)-self.calc_last_3d_pos)))
                        print("Calculated distance : "+str(dist))
                        self.calibration_factor = measured_dist/dist
                        self.set_distance(measured_dist)
                        self.measured_distances.append(measured_dist)

                    self.clicked_once = not self.clicked_once
                else:
                    self.last_pos = np.array([self.x, self.y])
                    self.measured_pos.append((self.x, self.y))
                    self.calc_last_3d_pos = np.array(px)
                
            else:                
                if self.clicked_once and self.calibration_factor != 1:
                    self.dist = self.calibration_factor * np.sqrt(np.sum(np.square(np.array(px)-self.last_3d_pos)))
                    print("Calculated distance : "+str(self.dist))
                    self.measured_distances.append(self.dist)
                    self.set_distance(self.dist)
                    self.measured_pos.append((self.x, self.y))
                    # print("Distance is measured as : "+str(self.dist))
                else:
                    self.last_pos = np.array([self.x, self.y])
                    self.measured_pos.append((self.x, self.y))
                    self.last_3d_pos = np.array(px)
                    
            # print(self.measured_pos)
            # print(self.measured_distances)
 
            self.clicked_once = not self.clicked_once

        self.pick = False