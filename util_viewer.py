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
        self.calibration_factors = []
        self.bbCalibrate = True

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
        self.bRadius = False
        self.ft_dist = 10
        self.selected_primitive_loc = np.array([0.0,0.0])
        
        self.bRightClick = False
        self.contextMenuPosition = None
        
        
        
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
        
        
        if ctrl_wdg.ui.bBezier and event.key() == Qt.Key_F :
            bfinal_curve = False
            if ctrl_wdg.kf_method == "Regular":
                if False in v.bAssignDepth_regular:
                    bfinal_curve = True
            elif ctrl_wdg.kf_method == "Network":
                if False in v.bAssignDepth_network:
                    bfinal_curve = True

            if bfinal_curve:
                self.parent_viewer.obj.curve_obj.find_final_curve()

        if ctrl_wdg.ui.bPick and event.key() == Qt.Key_C and event.modifiers() & Qt.ControlModifier:
            if self.parent_viewer.obj.curve_obj.selected_curve_idx != -1:
                idx = self.parent_viewer.obj.curve_obj.selected_curve_idx
                self.parent_viewer.obj.curve_obj.final_base_centers.append(self.parent_viewer.obj.curve_obj.final_base_centers[idx].copy())
                self.parent_viewer.obj.curve_obj.final_top_centers.append(self.parent_viewer.obj.curve_obj.final_top_centers[idx].copy())
                self.parent_viewer.obj.curve_obj.final_cylinder_bases.append(copy.deepcopy(self.parent_viewer.obj.curve_obj.final_cylinder_bases[idx]))
                self.parent_viewer.obj.curve_obj.final_cylinder_tops.append(copy.deepcopy(self.parent_viewer.obj.curve_obj.final_cylinder_tops[idx]))
                
                self.parent_viewer.obj.curve_obj.curve_count.append(ctrl_wdg.rect_obj.primitive_count)
                c = ctrl_wdg.rect_obj.getRGBfromI(ctrl_wdg.rect_obj.primitive_count)
                self.parent_viewer.obj.curve_obj.colors.append(c)
                ctrl_wdg.rect_obj.primitive_count += 1
                self.parent_viewer.obj.curve_obj.selected_curve_idx = len(self.parent_viewer.obj.curve_obj.final_base_centers) - 1
                self.parent_viewer.obj.curve_obj.deleted.append(False)
                
            elif self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx != -1:
                idx = self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx
                
                self.parent_viewer.obj.cylinder_obj.vertices_cylinder.append(copy.deepcopy(self.parent_viewer.obj.cylinder_obj.vertices_cylinder[idx]))
                self.parent_viewer.obj.cylinder_obj.top_vertices.append(copy.deepcopy(self.parent_viewer.obj.cylinder_obj.top_vertices[idx]))
                self.parent_viewer.obj.cylinder_obj.centers.append(copy.deepcopy(self.parent_viewer.obj.cylinder_obj.centers[idx]))
                self.parent_viewer.obj.cylinder_obj.top_centers.append(copy.deepcopy(self.parent_viewer.obj.cylinder_obj.top_centers[idx]))
                self.parent_viewer.obj.cylinder_obj.heights.append(self.parent_viewer.obj.cylinder_obj.heights[idx])
                self.parent_viewer.obj.cylinder_obj.radii.append(self.parent_viewer.obj.cylinder_obj.radii[idx])
                self.parent_viewer.obj.cylinder_obj.t_vecs.append(self.parent_viewer.obj.cylinder_obj.t_vecs[idx].copy())
                self.parent_viewer.obj.cylinder_obj.b_vecs.append(self.parent_viewer.obj.cylinder_obj.b_vecs[idx].copy())
                self.parent_viewer.obj.cylinder_obj.Ns.append(self.parent_viewer.obj.cylinder_obj.Ns[idx].copy())

                self.parent_viewer.obj.cylinder_obj.bool_cylinder_type.append(self.parent_viewer.obj.cylinder_obj.bool_cylinder_type[idx])
                self.parent_viewer.obj.cylinder_obj.cylinder_count.append(ctrl_wdg.rect_obj.primitive_count)
                c = ctrl_wdg.rect_obj.getRGBfromI(ctrl_wdg.rect_obj.primitive_count)
                self.parent_viewer.obj.cylinder_obj.colors.append(c)
                ctrl_wdg.rect_obj.primitive_count += 1
                self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx = len(self.parent_viewer.obj.cylinder_obj.vertices_cylinder) - 1

            elif ctrl_wdg.rect_obj.selected_rect_idx != -1:
                idx = ctrl_wdg.rect_obj.selected_rect_idx

                ctrl_wdg.rect_obj.tangents.append(ctrl_wdg.rect_obj.tangents[idx].copy())
                ctrl_wdg.rect_obj.binormals.append(ctrl_wdg.rect_obj.binormals[idx].copy())
                ctrl_wdg.rect_obj.normals.append(ctrl_wdg.rect_obj.normals[idx].copy())
                ctrl_wdg.rect_obj.centers.append(ctrl_wdg.rect_obj.centers[idx].copy())
                ctrl_wdg.rect_obj.min_Ts.append(ctrl_wdg.rect_obj.min_Ts[idx].copy())
                ctrl_wdg.rect_obj.max_Ts.append(ctrl_wdg.rect_obj.max_Ts[idx].copy())
                ctrl_wdg.rect_obj.min_Bs.append(ctrl_wdg.rect_obj.min_Bs[idx].copy())
                ctrl_wdg.rect_obj.max_Bs.append(ctrl_wdg.rect_obj.max_Bs[idx].copy())
                
                ctrl_wdg.rect_obj.new_points.append(copy.deepcopy(ctrl_wdg.rect_obj.new_points[idx]))
                ctrl_wdg.rect_obj.rect_counts.append(ctrl_wdg.rect_obj.primitive_count)
                c = ctrl_wdg.rect_obj.getRGBfromI(ctrl_wdg.rect_obj.primitive_count)
                ctrl_wdg.rect_obj.colors.append(c)
                ctrl_wdg.rect_obj.primitive_count += 1
                ctrl_wdg.rect_obj.selected_rect_idx = len(ctrl_wdg.rect_obj.new_points) - 1
                ctrl_wdg.rect_obj.deleted.append(False)
                ctrl_wdg.rect_obj.group_num += 1
                
            elif ctrl_wdg.quad_obj.selected_quad_idx != -1:
                idx = ctrl_wdg.quad_obj.selected_quad_idx

                data_val = ctrl_wdg.quad_obj.all_pts[idx]
                c1, c2, c3, c4 = 0.5 * (data_val[0] + data_val[1]), 0.5 * (data_val[1] + data_val[2]), 0.5 * (data_val[2] + data_val[3]), 0.5 * (data_val[3] + data_val[0])
                ctrl_wdg.quad_obj.vector1s.append([data_val[0] - c4, data_val[1] - c2, data_val[3] - c4, data_val[2] - c2, data_val[0] - c1, data_val[1] - c1, data_val[3] - c3, data_val[2] - c3])

                ctrl_wdg.quad_obj.all_pts.append(copy.deepcopy(ctrl_wdg.quad_obj.all_pts[idx]))
                ctrl_wdg.quad_obj.group_counts.append(ctrl_wdg.rect_obj.primitive_count)
                c = ctrl_wdg.rect_obj.getRGBfromI(ctrl_wdg.rect_obj.primitive_count)
                ctrl_wdg.quad_obj.colors.append(c)
                ctrl_wdg.rect_obj.primitive_count += 1
                ctrl_wdg.quad_obj.selected_quad_idx = len(ctrl_wdg.quad_obj.all_pts) - 1
                ctrl_wdg.quad_obj.deleted.append(False)
                ctrl_wdg.quad_obj.group_num += 1
                
            else:
                del_primitive_dialogue()

                

            
        ######################## Transformation of primitives ########################
            
        if ctrl_wdg.ui.bPick:
            if event.key() == Qt.Key_T:
                self.create_translate_panel()
            elif event.key() == Qt.Key_R:
                self.create_rotation_panel()
            elif event.key() == Qt.Key_S:
                self.create_scale_panel()
                
                
            if event.key() == Qt.Key_X:
                if event.modifiers() & Qt.ControlModifier:
                    self.rotate_x_opposite_axis()
                else:
                    self.rotate_x_axis()
                    
            elif event.key() == Qt.Key_Y:
                if event.modifiers() & Qt.ControlModifier:
                    self.rotate_y_opposite_axis()
                else:
                    self.rotate_y_axis()
            
            elif event.key() == Qt.Key_Z:
                if event.modifiers() & Qt.ControlModifier:
                    self.rotate_z_opposite_axis()
                else:
                    self.rotate_z_axis()
                    
            elif event.key() == Qt.Key_Left:
                self.translate_along_axis(-1, 0, 0, True)

            elif event.key() == Qt.Key_Right:
                self.translate_along_axis(1, 0, 0, True)

            elif event.key() == Qt.Key_Up:
                self.translate_along_axis(0, 1, 0, True)

            elif event.key() == Qt.Key_Down:
                self.translate_along_axis(0, -1, 0, True)

                
                    
                    
            
        if ctrl_wdg.ui.bMeasure and event.key() == Qt.Key_L:
            if ctrl_wdg.kf_method == "Regular":
                if len(v.measured_pos_regular[t]) > 0:
                    v.measured_pos_regular[t].pop()
                    v.measured_pos_regular[t].pop()
                    v.measured_distances_regular[t].pop()
            elif ctrl_wdg.kf_method == "Network":
                if len(v.measured_pos_network) > 0:
                    v.measured_pos_network[t].pop()
                    v.measured_pos_network[t].pop()
                    v.measured_distances_network[t].pop()
            
        if ctrl_wdg.ui.cross_hair and f != -1:
            if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                self.parent_viewer.obj.delete_feature()

            ######################## Move Features  ########################

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

        ######################## Copy and Pase features  ########################

        if ctrl_wdg.ui.cross_hair and event.modifiers() & Qt.ControlModifier:
            self.parent_viewer.obj.feature_panel.selected_feature_idx = -1
            if event.key() == Qt.Key_C:
                ctrl_wdg.copy_features()
            elif event.key() == Qt.Key_V:
                ctrl_wdg.paste_features()

        ######################## Move all features on a frame ########################

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
                        if not v.hide_network[t][i]:
                            fc.x_loc = fc.x_loc 
                            fc.y_loc = fc.y_loc - self.mv_pix
                        
                elif event.key() == Qt.Key_Down:
                    for i,fc in enumerate(v.features_network[t]):
                        if not v.hide_network[t][i]:
                            fc.x_loc = fc.x_loc 
                            fc.y_loc = fc.y_loc + self.mv_pix
            
            self.parent_viewer.obj.feature_panel.display_data()

        ######################## Delete primitives ########################

        if ctrl_wdg.ui.bPick:
            if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                if self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx != -1: 
                    self.parent_viewer.obj.cylinder_obj.delete_cylinder(self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx)
                    self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx = -1
                    
                elif ctrl_wdg.rect_obj.selected_rect_idx != -1:
                    ctrl_wdg.rect_obj.delete_rect(ctrl_wdg.rect_obj.selected_rect_idx)
                    ctrl_wdg.rect_obj.selected_rect_idx = -1
                    
                elif ctrl_wdg.quad_obj.selected_quad_idx != -1:
                    ctrl_wdg.quad_obj.delete_quad(ctrl_wdg.quad_obj.selected_quad_idx)
                    ctrl_wdg.quad_obj.selected_quad_idx = -1
                    
                elif self.parent_viewer.obj.curve_obj.selected_curve_idx != -1:
                    self.parent_viewer.obj.curve_obj.deleted[self.parent_viewer.obj.curve_obj.selected_curve_idx] = True
                    self.parent_viewer.obj.curve_obj.selected_curve_idx = -1
                    
                else:
                    del_primitive_dialogue()


        ######################## Deselect primitives and feature ########################

        if ctrl_wdg.ui.bPick and event.key() == Qt.Key_Escape:
            ctrl_wdg.rect_obj.selected_rect_idx = -1
            self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx = -1
            self.parent_viewer.obj.curve_obj.selected_curve_idx = -1
            ctrl_wdg.quad_obj.selected_quad_idx = -1
                
        if ctrl_wdg.ui.cross_hair and event.key() == Qt.Key_Escape:
            self.parent_viewer.obj.feature_panel.selected_feature_idx = -1
                
                

    def util_mouse_press(self, event, ctrl_wdg):
        a = event.pos()
        x = int((a.x()-self.parent_viewer.width()/2 - self.offset_x)/self._zoom + self.parent_viewer.width()/2) 
        y = int((a.y()-self.parent_viewer.height()/2 - self.offset_y)/self._zoom + self.parent_viewer.height()/2)
        
        v = ctrl_wdg.mv_panel.movie_caps[ctrl_wdg.mv_panel.selected_movie_idx]
        t = ctrl_wdg.selected_thumbnail_index
        
        if event.button() == Qt.RightButton:
            self.press_loc = (a.x(), a.y())
            self.bRightClick = True
            self.x = a.x()
            self.y = a.y()
            self.x_zoomed, self.y_zoomed = x, y
            self.pick = True
            # print("Pressed right button")
            
        
        elif event.button() == Qt.LeftButton:
            if ctrl_wdg.ui.cross_hair:
                if ctrl_wdg.kf_method == "Regular":
                    if len(v.features_regular) > 0:
                        for i, fc in enumerate(v.features_regular[t]):
                            if not v.hide_regular[t][i]:
                                d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                                if d < self.dist_thresh:
                                    self.parent_viewer.obj.feature_panel.select_feature(i, fc.label)
                                    self.move_feature_bool = True
    
    
                elif ctrl_wdg.kf_method == "Network":
                    if len(v.features_network) > 0:
                        for i, fc in enumerate(v.features_network[t]):
                            if not v.hide_network[t][i]:
                                d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                                if d < self.dist_thresh:
                                    self.parent_viewer.obj.feature_panel.select_feature(i, fc.label)
                                    self.move_feature_bool = True
            
            selected_feature = False
            if (ctrl_wdg.ui.bRect or ctrl_wdg.ui.bQuad or ctrl_wdg.ui.bCylinder or ctrl_wdg.ui.bnCylinder or ctrl_wdg.ui.bMeasure or ctrl_wdg.ui.bPick or ctrl_wdg.ui.bBezier or ctrl_wdg.ui.bAnchor) and len(self.parent_viewer.obj.ply_pts) > 0:
                if ctrl_wdg.ui.bRect:
                    selected_feature = ctrl_wdg.rect_obj.select_feature(x, y)
                if ctrl_wdg.ui.bQuad:
                    selected_feature = ctrl_wdg.quad_obj.select_feature(x, y)
                if ctrl_wdg.ui.bCylinder or ctrl_wdg.ui.bnCylinder:
                    selected_feature = self.parent_viewer.obj.cylinder_obj.select_feature(x, y)
                    
                if ctrl_wdg.ui.bBezier:
                    if ctrl_wdg.kf_method == "Regular":
                        if v.bPaint_regular[t]:
                            selected_feature = self.parent_viewer.obj.curve_obj.mark_point(x, y, self.w1, self.w2, self.h1, self.h2)

                    elif ctrl_wdg.kf_method == "Network":
                        if v.bPaint_network[t]:
                            selected_feature = self.parent_viewer.obj.curve_obj.mark_point(x, y, self.w1, self.w2, self.h1, self.h2)

                    
                if not selected_feature:
                    # print("Not selected ")
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
                # print(len(v.features_regular))
                if len(v.features_regular) > 0:
                    for i, fc in enumerate(v.features_regular[t]):
                        # print(i)
                        #
                        # print(v.hide_regular[t][i])
                        # print("------------------------------------------")
                        if not v.hide_regular[t][i]:
                            painter.drawLine(QLineF(fc.x_loc - self.ft_dist/2 , fc.y_loc , fc.x_loc + self.ft_dist/2 , fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc - self.ft_dist/2, fc.x_loc, fc.y_loc + self.ft_dist/2))
                            painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
    
            elif ctrl_wdg.kf_method == "Network":
                if len(v.features_network) > 0:
                    for i, fc in enumerate(v.features_network[t]):
                        if not v.hide_network[t][i]:
                            painter.drawLine(QLineF(fc.x_loc - self.ft_dist/2, fc.y_loc, fc.x_loc + self.ft_dist/2, fc.y_loc))
                            painter.drawLine(QLineF(fc.x_loc , fc.y_loc - self.ft_dist/2, fc.x_loc, fc.y_loc + self.ft_dist/2))
                            painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
                                   
            pen = QPen(QColor(0, 255, 0))
            pen.setWidth(2)
            painter.setPen(pen)
            
            # Painting the selected feature
            
            if self.parent_viewer.obj.feature_panel.selected_feature_idx != -1 and ctrl_wdg.ui.cross_hair:
                if ctrl_wdg.kf_method == "Regular" and len(v.features_regular[t]) > 0 and not v.hide_regular[t][self.parent_viewer.obj.feature_panel.selected_feature_idx]:
                    fc = v.features_regular[t][self.parent_viewer.obj.feature_panel.selected_feature_idx]
                    painter.drawLine(QLineF(fc.x_loc - self.ft_dist/2, fc.y_loc, fc.x_loc + self.ft_dist/2, fc.y_loc))
                    painter.drawLine(QLineF(fc.x_loc , fc.y_loc - self.ft_dist/2, fc.x_loc, fc.y_loc + self.ft_dist/2))
                    painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
                
                elif ctrl_wdg.kf_method == "Network" and len(v.features_network[t]) > 0 and not v.hide_network[t][self.parent_viewer.obj.feature_panel.selected_feature_idx]:
                    fc = v.features_network[t][self.parent_viewer.obj.feature_panel.selected_feature_idx]
                    painter.drawLine(QLineF(fc.x_loc - self.ft_dist/2, fc.y_loc, fc.x_loc + self.ft_dist/2, fc.y_loc))
                    painter.drawLine(QLineF(fc.x_loc , fc.y_loc - self.ft_dist/2, fc.x_loc, fc.y_loc + self.ft_dist/2))
                    painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
            
            
            # Painting for Rectangle Tool
            if (len(v.rect_groups_regular) > 0 or len(v.rect_groups_network) > 0) :
                if ctrl_wdg.kf_method == "Regular":
                    if len(v.rect_groups_regular[t]) > 0:
                        for i, fc in enumerate(v.features_regular[t]):
                            if v.rect_groups_regular[t][i] != -1:
                                painter.drawLine(QLineF(fc.x_loc - self.ft_dist/2, fc.y_loc , fc.x_loc + self.ft_dist/2, fc.y_loc))
                                painter.drawLine(QLineF(fc.x_loc , fc.y_loc - self.ft_dist/2, fc.x_loc, fc.y_loc + self.ft_dist/2))
                                painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))

                    
                elif ctrl_wdg.kf_method == "Network":
                    if len(v.rect_groups_network[t]) > 0:
                        for i, fc in enumerate(v.features_network[t]):
                            if v.rect_groups_network[t][i] != -1:
                                painter.drawLine(QLineF(fc.x_loc - self.ft_dist/2, fc.y_loc , fc.x_loc + self.ft_dist/2, fc.y_loc))
                                painter.drawLine(QLineF(fc.x_loc , fc.y_loc - self.ft_dist/2, fc.x_loc, fc.y_loc + self.ft_dist/2))
                                painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
                            
                            
            # Painting for Quad Tool
            if (len(v.rect_groups_regular) > 0 or len(v.rect_groups_network) > 0):
                if ctrl_wdg.kf_method == "Regular":
                    if len(v.quad_groups_regular[t]) > 0:
                        for i, fc in enumerate(v.features_regular[t]):
                            if v.quad_groups_regular[t][i] != -1:
                                painter.drawLine(QLineF(fc.x_loc - self.ft_dist/2, fc.y_loc , fc.x_loc + self.ft_dist/2, fc.y_loc))
                                painter.drawLine(QLineF(fc.x_loc , fc.y_loc - self.ft_dist/2, fc.x_loc, fc.y_loc + self.ft_dist/2))
                                painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))

                    
                elif ctrl_wdg.kf_method == "Network":
                    if len(v.quad_groups_network[t]) > 0:
                        for i, fc in enumerate(v.features_network[t]):
                            if v.quad_groups_network[t][i] != -1:
                                painter.drawLine(QLineF(fc.x_loc - self.ft_dist/2, fc.y_loc , fc.x_loc + self.ft_dist/2, fc.y_loc))
                                painter.drawLine(QLineF(fc.x_loc , fc.y_loc - self.ft_dist/2, fc.x_loc, fc.y_loc + self.ft_dist/2))
                                painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))
                            

            # Painting for Cylinder Tool
            if (len(v.cylinder_groups_regular) > 0 or len(v.cylinder_groups_network) > 0) :
                if ctrl_wdg.kf_method == "Regular":
                    if len(v.cylinder_groups_regular[t]) > 0:
                        for i, fc in enumerate(v.features_regular[t]):
                            if v.cylinder_groups_regular[t][i] != -1:
                                painter.drawLine(QLineF(fc.x_loc - self.ft_dist/2, fc.y_loc , fc.x_loc + self.ft_dist/2, fc.y_loc))
                                painter.drawLine(QLineF(fc.x_loc , fc.y_loc - self.ft_dist/2, fc.x_loc, fc.y_loc + self.ft_dist/2))
                                painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))

                    
                elif ctrl_wdg.kf_method == "Network":
                    if len(v.cylinder_groups_network[t]) > 0:
                        for i, fc in enumerate(v.features_network[t]):
                            if v.cylinder_groups_network[t][i] != -1:
                                painter.drawLine(QLineF(fc.x_loc - self.ft_dist/2, fc.y_loc , fc.x_loc + self.ft_dist/2, fc.y_loc))
                                painter.drawLine(QLineF(fc.x_loc , fc.y_loc - self.ft_dist/2, fc.x_loc, fc.y_loc + self.ft_dist/2))
                                painter.drawText(fc.x_loc - 4, fc.y_loc - 8, str(fc.label))


                            
            # #### Painting for Curve
            
            if len(v.curve_groups_regular) > 0 or len(v.curve_groups_network) > 0:
                # print(v.curve_groups_regular[t])
                # print(v.bPaint_regular[t])
                if ctrl_wdg.kf_method == "Regular":
                    data_val = self.parent_viewer.obj.curve_obj.data_val_regular
                    original_list = v.curve_groups_regular[t]
                    bool_temp = v.bPaint_regular[t]

                elif ctrl_wdg.kf_method == "Network":
                    data_val = self.parent_viewer.obj.curve_obj.data_val_network
                    original_list = v.curve_groups_network[t]
                    bool_temp = v.bPaint_network[t]

                if len(data_val) > 0:
                    painter.drawLine(QLineF(data_val[-1][0], data_val[-1][1] ,  self.current_pos[0], self.current_pos[1]))

                for i, p in enumerate(data_val):
                    if len(p) > 0:
                        painter.drawEllipse(p[0]-3, p[1]-3, 6, 6)
                
                for j in range(len(data_val) - 1):
                    if len(data_val[j+1]) > 0:
                        painter.drawLine(QLineF(data_val[j][0], data_val[j][1] ,  data_val[j+1][0], data_val[j+1][1]))
                
                if len(original_list) > 0 and not bool_temp:
                    data_val = original_list[-1]
                    for i, p in enumerate(data_val):
                        # print(p)
                        if len(p) > 0 :
                            painter.drawEllipse(p[0] - 3, p[1] - 3, 6, 6)
    
                    for j in range(len(data_val) - 1):
                        if len(data_val[j + 1]) > 0:
                            painter.drawLine(QLineF(data_val[j][0], data_val[j][1], data_val[j + 1][0], data_val[j + 1][1]))
 
            painter.end()
            
                
    def util_select_3d(self, dd, px, co, ctrl_wdg):
        v = ctrl_wdg.mv_panel.movie_caps[ctrl_wdg.mv_panel.selected_movie_idx]
        t = ctrl_wdg.selected_thumbnail_index
                
        if dd < 1:
            if ctrl_wdg.ui.bBezier:
                assign_depth = False

                if ctrl_wdg.kf_method == "Regular":
                    assign_depth = v.bAssignDepth_regular[t]

                elif ctrl_wdg.kf_method == "Network":
                    assign_depth = v.bAssignDepth_network[t]

                if assign_depth:
                    # print("Assign depth")
                    if ctrl_wdg.kf_method == "Regular":
                        v.curve_3d_point_regular[t].append(np.array(px))

                        for j, tup in enumerate(self.parent_viewer.obj.camera_projection_mat):
                            if tup[0] == t:
                                G = self.parent_viewer.obj.camera_projection_mat[j][1][0:3, :]
                                P = np.matmul(self.parent_viewer.obj.K, G)
                                self.parent_viewer.obj.curve_obj.estimate_plane(P)

                    elif ctrl_wdg.kf_method == "Network":
                        v.curve_3d_point_network[t].append(np.array(px))
                        for j, tup in enumerate(self.parent_viewer.obj.camera_projection_mat):
                            if tup[0] == t:
                                G = self.parent_viewer.obj.camera_projection_mat[j][1][0:3, :]
                                P = np.matmul(self.parent_viewer.obj.K, G)
                                self.parent_viewer.obj.curve_obj.estimate_plane(P)

                if self.bRadius:
                    self.parent_viewer.obj.curve_obj.radius_point.append(np.array(px))
                    self.parent_viewer.obj.curve_obj.make_general_cylinder()
                    self.bRadius = False
                    if ctrl_wdg.kf_method == "Regular":
                        for i in range(len(v.key_frames_regular)):
                            v.bPaint_regular[i] = True

                    elif ctrl_wdg.kf_method == "Network":
                        for i in range(len(v.key_frames_network)):
                            v.bPaint_network[i] = True
                            
                            
                            
                
            elif ctrl_wdg.ui.bnCylinder or ctrl_wdg.ui.bCylinder:
                self.parent_viewer.obj.cylinder_obj.data_val.append(np.array(px))
                if len(self.parent_viewer.obj.cylinder_obj.data_val) == 4:
                    data_val = self.parent_viewer.obj.cylinder_obj.data_val
                    if ctrl_wdg.ui.bnCylinder:
                        bases, tops, center, top_c, height, radius, b_vec, t_vec, N = self.parent_viewer.obj.cylinder_obj.make_new_cylinder(data_val[0], data_val[1], data_val[2], data_val[3])
                        if len(bases) > 0:
                            self.parent_viewer.obj.cylinder_obj.bool_cylinder_type.append(False)
                            self.parent_viewer.obj.cylinder_obj.refresh_cylinder_data(bases, tops, center, top_c, height, radius, b_vec, t_vec, N)

                        else:
                            straight_line_dialogue()
                            del self.parent_viewer.obj.cylinder_obj.data_val[-1]

                    else:
                        bases, tops, center, top_c, height, radius, b_vec, t_vec, N = self.parent_viewer.obj.cylinder_obj.make_cylinder(data_val[0], data_val[1], data_val[2], data_val[3])
                        self.parent_viewer.obj.cylinder_obj.bool_cylinder_type.append(True)
                        self.parent_viewer.obj.cylinder_obj.refresh_cylinder_data(bases, tops, center, top_c, height, radius, b_vec, t_vec, N)

                    


            elif ctrl_wdg.ui.bPick:
                ID = ctrl_wdg.rect_obj.getIfromRGB(co[0], co[1], co[2])

                if ID in ctrl_wdg.rect_obj.rect_counts:
                    ctrl_wdg.rect_obj.selected_rect_idx = ctrl_wdg.rect_obj.rect_counts.index(ID)
                    self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx = -1
                    ctrl_wdg.quad_obj.selected_quad_idx = -1
                    self.parent_viewer.obj.curve_obj.selected_curve_idx = -1
                    # print( self.bRightClick)
                    # if self.bRightClick:
                    #     # print("Need to transform a rectangle")
                        
                    #     self.openContextMenu__()
                    #     print("After the function")
                    #     self.bRightClick = False

                    
                    
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
                    self.parent_viewer.obj.curve_obj.selected_curve_idx = curve_idx
                    ctrl_wdg.rect_obj.selected_rect_idx = -1
                    self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx = -1
                    ctrl_wdg.quad_obj.selected_quad_idx = -1

                    
                    
                    
            elif ctrl_wdg.ui.bMeasure:
                # print(self.x_zoomed, self.y_zoomed)
                if self.bCalibrate:
                    if self.clicked_once:
                        # print("IFFFFFFFFFFFFFFFFFF")
                        self.bCalibrate = False
                        self.create_calibration_panel()
                        if self.cal_dialog.exec():
                            measured_dist = float(self.e1.text())
                            # print("Measured distance : "+str(measured_dist))
                            dist = np.sqrt(np.sum(np.square(np.array(px)-self.calc_last_3d_pos)))
                            
                            # self.calibration_factor = measured_dist/dist
                            self.calibration_factors.append(measured_dist/dist)
                            
            

                            # print("calibration factor : "+str(self.calibration_factor))
                            self.set_distance(measured_dist)
                            if ctrl_wdg.kf_method == "Regular":
                                v.measured_distances_regular[t].append(measured_dist)
                            elif ctrl_wdg.kf_method == "Network":
                                v.measured_distances_network[t].append(measured_dist)
                                
                            
                                                        
                        self.clicked_once = not self.clicked_once
                        self.bCalibrate = True
                        
                        if len(self.calibration_factors) == 3:
                            # print("Take average")
                            self.bCalibrate = False
                            self.calibration_factor = (1/3)*(self.calibration_factors[0] + self.calibration_factors[1] + self.calibration_factors[2])        


    

                    else:
                        # print("In ELSE")
                        self.last_pos = np.array([self.x_zoomed, self.y_zoomed])
                        self.calc_last_3d_pos = np.array(px)
                        if ctrl_wdg.kf_method == "Regular":
                            v.measured_pos_regular[t].append((self.x_zoomed, self.y_zoomed))
                        elif ctrl_wdg.kf_method == "Network":
                            v.measured_pos_network[t].append((self.x_zoomed, self.y_zoomed))                        
                
                    
                             
                else:
                    # print("Going to measure ")
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

                    
            
            elif ctrl_wdg.ui.bAnchor:
                if ctrl_wdg.rect_obj.bFirstAnchor and not ctrl_wdg.rect_obj.bSecondAnchor:    
                    ctrl_wdg.rect_obj.first_anchor = np.array(px)
                    ctrl_wdg.rect_obj.bFirstAnchor = False
                    ctrl_wdg.rect_obj.bSecondAnchor = True
                    
                elif ctrl_wdg.rect_obj.bSecondAnchor and not ctrl_wdg.rect_obj.bFirstAnchor:
                    ctrl_wdg.rect_obj.second_anchor = np.array(px)
                    ctrl_wdg.rect_obj.bFirstAnchor = True
                    ctrl_wdg.rect_obj.bSecondAnchor = False
                    
                    vec = ctrl_wdg.rect_obj.first_anchor - ctrl_wdg.rect_obj.second_anchor
                    
                    ID = ctrl_wdg.rect_obj.getIfromRGB(co[0], co[1], co[2])
                    

                    if ID in ctrl_wdg.rect_obj.rect_counts:
                        idx = ctrl_wdg.rect_obj.rect_counts.index(ID)
                        # print("Index : "+str(idx))
                        ctrl_wdg.rect_obj.translate(vec, idx)
                        
                    elif ID in ctrl_wdg.quad_obj.group_counts:
                        idx = ctrl_wdg.quad_obj.group_counts.index(ID)
                        # print("Index : "+str(idx))
                        ctrl_wdg.quad_obj.translate(vec, idx)   
                        
                    elif ID in ctrl_wdg.gl_viewer.obj.cylinder_obj.cylinder_count:
                        idx = ctrl_wdg.gl_viewer.obj.cylinder_obj.cylinder_count.index(ID)
                        # print("Index : "+str(idx))
                        ctrl_wdg.gl_viewer.obj.cylinder_obj.translate(vec, idx)   

                    elif ID in ctrl_wdg.gl_viewer.obj.curve_obj.curve_count:
                        idx = ctrl_wdg.gl_viewer.obj.curve_obj.curve_count.index(ID)
                        # print("Index : "+str(idx))
                        ctrl_wdg.gl_viewer.obj.curve_obj.translate(vec, idx)                                       

        self.pick = False
        # self.bCalibrate = True
        
    def openContextMenu__(self, position):
        if self.parent_viewer.obj.ctrl_wdg.ui.bPick:
            if (self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx != -1) or (self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx != -1) \
            or (self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx != -1) or (self.parent_viewer.obj.curve_obj.selected_curve_idx != -1):
                menu = QMenu(self)
                menu.setAutoFillBackground(True)
                
                str_ = "QMenu::item:selected{\
                    background-color: rgb(110, 110, 120);\
                    color: rgb(255, 255, 255);\
                    } QMenu::item:disabled { color:rgb(150, 150, 150); }"
                
                menu.setStyleSheet(str_)
                
                new_pr = QAction("Translate", self)
                menu.addAction(new_pr)
                new_pr.triggered.connect(self.create_translate_panel)
                new_pr.setShortcut("t")
        
                open_pr = QAction("Rotate", self)
                menu.addAction(open_pr)
                open_pr.triggered.connect(self.create_rotation_panel)
                open_pr.setShortcut("r")
                
                scale_action = QAction("Scale", self)
                menu.addAction(scale_action)
                scale_action.triggered.connect(self.create_scale_panel)
                scale_action.setShortcut("s")



                tx_action = QAction("Translate along x-axis", self)
                menu.addAction(tx_action)
                tx_action.triggered.connect(self.translate_x_axis)
                tx_action.setShortcut("ctrl+x")
                
                ty_action = QAction("Translate along y-axis", self)
                menu.addAction(ty_action)
                ty_action.triggered.connect(self.translate_y_axis)
                ty_action.setShortcut("ctrl+y")

                tz_action = QAction("Translate along z-axis", self)
                menu.addAction(tz_action)
                tz_action.triggered.connect(self.translate_z_axis)
                tz_action.setShortcut("ctrl+z")


                
                rx_action = QAction("Rotate along x-axis", self)
                menu.addAction(rx_action)
                rx_action.triggered.connect(self.rotate_x_axis)
                rx_action.setShortcut("x")

                ry_action = QAction("Rotate along y-axis", self)
                menu.addAction(ry_action)
                ry_action.triggered.connect(self.rotate_y_axis)
                ry_action.setShortcut("y")

                rz_action = QAction("Rotate along z-axis", self)
                menu.addAction(rz_action)
                rz_action.triggered.connect(self.rotate_z_axis)
                rz_action.setShortcut("z")
                
                
    
                
                menu.addAction(new_pr)
                menu.addAction(open_pr)
                menu.addAction(scale_action)
                menu.addAction(tx_action)
                menu.addAction(ty_action)
                menu.addAction(tz_action)
                menu.addAction(rx_action)
                menu.addAction(ry_action)
                menu.addAction(rz_action)
        
                viewer = self.parent_viewer.sender()
                self.contextMenuPosition = viewer.mapToGlobal(position)
                action = menu.exec_(self.contextMenuPosition)
        
        
                # self.bRightClick = False
                # self.pick = False
                
            else:
                del_primitive_dialogue()
                
                
    def rotate_x_axis(self):
        self.rotate_along_axis(3, 0, 0)

    def rotate_y_axis(self):
        self.rotate_along_axis(0, 3, 0)

    def rotate_z_axis(self):
        self.rotate_along_axis(0, 0, 3)
        
    def rotate_x_opposite_axis(self):
        self.rotate_along_axis(-3, 0, 0)

    def rotate_y_opposite_axis(self):
        self.rotate_along_axis(0, -3, 0)

    def rotate_z_opposite_axis(self):
        self.rotate_along_axis(0, 0, -3)


    def translate_x_axis(self):
        self.translate_along_axis(0.5, 0, 0, True)

    def translate_y_axis(self):
        self.translate_along_axis(0, 0.5, 0, True)

    def translate_z_axis(self):
        self.translate_along_axis(0, 0, 0.5, True)                    


    def create_translate_panel(self):
        self.translate_dialog = QDialog()
        self.translate_dialog.setWindowTitle("Translation panel")

        QBtn = QDialogButtonBox.Ok

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.translate_dialog.accept)
        
        
        
        check_box = QCheckBox("Relative values")
        check_box.setChecked(True)
        
        
        
        txt = ""
        if self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx != -1:
            self.selected_primitive_loc = self.parent_viewer.obj.ctrl_wdg.rect_obj.centers[self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx]
            txt = "Center of rectangle"
            
        elif self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx != -1:
            P1 = self.parent_viewer.obj.ctrl_wdg.quad_obj.all_pts[self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx][0]
            P2 = self.parent_viewer.obj.ctrl_wdg.quad_obj.all_pts[self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx][1]
            P3 = self.parent_viewer.obj.ctrl_wdg.quad_obj.all_pts[self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx][2]
            P4 = self.parent_viewer.obj.ctrl_wdg.quad_obj.all_pts[self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx][3]
            self.selected_primitive_loc = 0.25*(P1 + P2 + P3 + P4)
            txt = "Center of quadrilateral"
            
        elif self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx != -1:
            self.selected_primitive_loc = 0.5*(self.parent_viewer.obj.cylinder_obj.centers[self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx] + self.parent_viewer.obj.cylinder_obj.top_centers[self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx])
            txt = "Center of cylinder"
        
        elif self.parent_viewer.obj.curve_obj.selected_curve_idx != -1:
            curve_list = self.parent_viewer.obj.curve_obj.final_bezier[self.parent_viewer.obj.curve_obj.selected_curve_idx]
            self.selected_primitive_loc = sum(curve_list) / len(curve_list)
            txt = "Center of curved cylinder"
            
        label_1 = QLabel(txt)
        
        label_x = QLabel(str(round(self.selected_primitive_loc[0], 3)))
        label_x.setAlignment(Qt.AlignCenter)
        label_x.setStyleSheet("border: 1px solid black; ")
        label_y = QLabel(str(round(self.selected_primitive_loc[1], 3)))
        label_y.setAlignment(Qt.AlignCenter)
        label_y.setStyleSheet("border: 1px solid black; ")
        label_z = QLabel(str(round(self.selected_primitive_loc[2], 3)))
        label_z.setAlignment(Qt.AlignCenter)
        label_z.setStyleSheet("border: 1px solid black; ")
        
        h_layout_1 = QHBoxLayout()
        h_layout_1.addWidget(label_x)
        h_layout_1.addWidget(label_y)
        h_layout_1.addWidget(label_z)

        label_top = QLabel("Enter translation values ")
        
        label_tx = QLabel("Tx : ")
        label_ty = QLabel("Ty : ")
        label_tz = QLabel("Tz : ")
        

        self.tx = QLineEdit("0")
        self.tx.setValidator(QDoubleValidator())
        self.tx.setMaxLength(6)
        self.tx.setFont(QFont("Arial", 10))
        
        self.ty = QLineEdit("0")
        self.ty.setValidator(QDoubleValidator())
        self.ty.setMaxLength(6)
        self.ty.setFont(QFont("Arial", 10))

        self.tz = QLineEdit("0")
        self.tz.setValidator(QDoubleValidator())
        self.tz.setMaxLength(6)
        self.tz.setFont(QFont("Arial", 10))
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(label_tx)
        h_layout.addWidget(self.tx)
        h_layout.addWidget(label_ty)
        h_layout.addWidget(self.ty)
        h_layout.addWidget(label_tz)
        h_layout.addWidget(self.tz)

        cal_layout = QVBoxLayout()
        cal_layout.addWidget(label_1)
        cal_layout.addLayout(h_layout_1)
        cal_layout.addWidget(QLabel("\n"))
        cal_layout.addWidget(check_box)
        cal_layout.addWidget(label_top)
        cal_layout.addLayout(h_layout)
        cal_layout.addWidget(buttonBox)
        self.translate_dialog.setLayout(cal_layout)
        

        if self.translate_dialog.exec():
            tx = float(self.tx.text())
            ty = float(self.ty.text())
            tz = float(self.tz.text())
            
            self.translate_along_axis(tx, ty, tz, check_box.isChecked())
            
      

    def translate_along_axis(self, tx, ty, tz, bool_cb):
        if self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx != -1:
            P1 = self.parent_viewer.obj.ctrl_wdg.rect_obj.new_points[self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx][0]
            P2 = self.parent_viewer.obj.ctrl_wdg.rect_obj.new_points[self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx][1]
            P3 = self.parent_viewer.obj.ctrl_wdg.rect_obj.new_points[self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx][2]
            P4 = self.parent_viewer.obj.ctrl_wdg.rect_obj.new_points[self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx][3]
            if bool_cb: 
                self.parent_viewer.obj.ctrl_wdg.rect_obj.translate(tx*(P2 - P1), self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx)
                self.parent_viewer.obj.ctrl_wdg.rect_obj.translate(ty*(P4 - P1), self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx)
                self.parent_viewer.obj.ctrl_wdg.rect_obj.translate(tz*(np.cross((P2 - P1), (P4 - P1))), self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx)
            else:
                self.parent_viewer.obj.ctrl_wdg.rect_obj.translate(tx*((P2 - P1)/np.linalg.norm(P2-P1)), self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx)
                self.parent_viewer.obj.ctrl_wdg.rect_obj.translate(ty*((P4 - P1)/np.linalg.norm(P4-P1)), self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx)
                self.parent_viewer.obj.ctrl_wdg.rect_obj.translate(tz*(np.cross((P2 - P1)/np.linalg.norm(P2-P1), (P4 - P1)/np.linalg.norm(P4-P1))), self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx)


        elif self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx != -1:
            P1 = self.parent_viewer.obj.ctrl_wdg.quad_obj.all_pts[self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx][0]
            P2 = self.parent_viewer.obj.ctrl_wdg.quad_obj.all_pts[self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx][1]
            P3 = self.parent_viewer.obj.ctrl_wdg.quad_obj.all_pts[self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx][2]
            P4 = self.parent_viewer.obj.ctrl_wdg.quad_obj.all_pts[self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx][3]
            if bool_cb: 
                self.parent_viewer.obj.ctrl_wdg.quad_obj.translate(tx*(P2 - P1), self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx)
                self.parent_viewer.obj.ctrl_wdg.quad_obj.translate(ty*(P4 - P1), self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx)
                self.parent_viewer.obj.ctrl_wdg.quad_obj.translate(tz*(np.cross(P2 - P1, P4 - P1)), self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx)
            else:
                self.parent_viewer.obj.ctrl_wdg.quad_obj.translate(tx*((P2 - P1)/np.linalg.norm(P2-P1)), self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx)
                self.parent_viewer.obj.ctrl_wdg.quad_obj.translate(ty*((P4 - P1)/np.linalg.norm(P4-P1)), self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx)
                self.parent_viewer.obj.ctrl_wdg.quad_obj.translate(tz*(np.cross((P2 - P1)/np.linalg.norm(P2-P1), (P4 - P1)/np.linalg.norm(P4-P1))), self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx)
                
            

        elif self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx != -1:
            P1 = self.parent_viewer.obj.cylinder_obj.centers[self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx]
            P4 = self.parent_viewer.obj.cylinder_obj.top_centers[self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx]
            P3 = self.parent_viewer.obj.cylinder_obj.vertices_cylinder[self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx][0]
            P2 = np.cross(P4 - P1, P3 - P1) + P1
            if bool_cb:
                self.parent_viewer.obj.cylinder_obj.translate(tx*(P3 - P1), self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx)
                self.parent_viewer.obj.cylinder_obj.translate(ty*(P4 - P1), self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx)
                self.parent_viewer.obj.cylinder_obj.translate(tz*(P2 - P1), self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx)
                
            else:
                self.parent_viewer.obj.cylinder_obj.translate(tx*((P3 - P1)/np.linalg.norm(P3-P1)), self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx)
                self.parent_viewer.obj.cylinder_obj.translate(ty*((P4 - P1)/np.linalg.norm(P4-P1)), self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx)
                self.parent_viewer.obj.cylinder_obj.translate(tz*((P2 - P1)/np.linalg.norm(P2-P1)), self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx)



        elif self.parent_viewer.obj.curve_obj.selected_curve_idx != -1:
            base_centers = self.parent_viewer.obj.curve_obj.final_base_centers[self.parent_viewer.obj.curve_obj.selected_curve_idx]
            center = np.mean(np.asarray(base_centers), axis=0)
            P1 = base_centers[0]
            P4 = base_centers[int(0.5*self.parent_viewer.obj.curve_obj.num_pts)]
            P3 = self.parent_viewer.obj.curve_obj.final_cylinder_bases[self.parent_viewer.obj.curve_obj.selected_curve_idx][0][0]
            P2 = np.cross(P4 - P1 , P3 - P1) + P1
            if bool_cb:
                x_axis = 2*(P3 - P1)
                y_axis = P4 - P1
                z_axis = P2 - P1
            else:
                x_axis = (P3 - P1)/np.linalg.norm(P3 - P1)
                y_axis = (P4 - P1)/np.linalg.norm(P4 - P1)
                z_axis = (P2 - P1)/np.linalg.norm(P2 - P1)
            self.parent_viewer.obj.curve_obj.translate(tx*x_axis, self.parent_viewer.obj.curve_obj.selected_curve_idx)
            self.parent_viewer.obj.curve_obj.translate(ty*y_axis, self.parent_viewer.obj.curve_obj.selected_curve_idx)
            self.parent_viewer.obj.curve_obj.translate(tz*z_axis, self.parent_viewer.obj.curve_obj.selected_curve_idx)
            
            
        else:
            del_primitive_dialogue()



        



    def create_rotation_panel(self):
        self.rotate_dialog = QDialog()
        self.rotate_dialog.setWindowTitle("Rotation panel")

        QBtn = QDialogButtonBox.Ok

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.rotate_dialog.accept)

        label_top = QLabel("Enter rotation angles in degrees ")
        
        label_rx = QLabel("Rx : ")
        label_ry = QLabel("Ry : ")
        label_rz = QLabel("Rz : ")

        self.rx = QLineEdit("0")
        self.rx.setValidator(QDoubleValidator())
        self.rx.setMaxLength(6)
        self.rx.setFont(QFont("Arial", 10))
        
        self.ry = QLineEdit("0")
        self.ry.setValidator(QDoubleValidator())
        self.ry.setMaxLength(6)
        self.ry.setFont(QFont("Arial", 10))

        self.rz = QLineEdit("0")
        self.rz.setValidator(QDoubleValidator())
        self.rz.setMaxLength(6)
        self.rz.setFont(QFont("Arial", 10))
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(label_rx)
        h_layout.addWidget(self.rx)
        h_layout.addWidget(label_ry)
        h_layout.addWidget(self.ry)
        h_layout.addWidget(label_rz)
        h_layout.addWidget(self.rz)

        cal_layout = QVBoxLayout()
        cal_layout.addWidget(label_top)
        cal_layout.addLayout(h_layout)
        cal_layout.addWidget(buttonBox)
        self.rotate_dialog.setLayout(cal_layout)
        
        if self.rotate_dialog.exec():
            rx = float(self.rx.text())
            ry = float(self.ry.text())
            rz = float(self.rz.text())
            # print(rx, ry, rz)
            self.rotate_along_axis(rx, ry, rz)
            
            
            
    def rotate_along_axis(self, rx, ry, rz):
        if self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx != -1:
            P1 = self.parent_viewer.obj.ctrl_wdg.rect_obj.new_points[self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx][0]
            P2 = self.parent_viewer.obj.ctrl_wdg.rect_obj.new_points[self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx][1]
            P3 = self.parent_viewer.obj.ctrl_wdg.rect_obj.new_points[self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx][2]
            P4 = self.parent_viewer.obj.ctrl_wdg.rect_obj.new_points[self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx][3]
            self.parent_viewer.obj.ctrl_wdg.rect_obj.rotate(rx, (P2 - P1)/np.linalg.norm(P2-P1))
            self.parent_viewer.obj.ctrl_wdg.rect_obj.rotate(ry, (P4 - P1)/np.linalg.norm(P4-P1))
            self.parent_viewer.obj.ctrl_wdg.rect_obj.rotate(rz, np.cross((P2 - P1)/np.linalg.norm(P2-P1), (P4 - P1)/np.linalg.norm(P4-P1)))

        elif self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx != -1:
            P1 = self.parent_viewer.obj.ctrl_wdg.quad_obj.all_pts[self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx][0]
            P2 = self.parent_viewer.obj.ctrl_wdg.quad_obj.all_pts[self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx][1]
            P3 = self.parent_viewer.obj.ctrl_wdg.quad_obj.all_pts[self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx][2]
            P4 = self.parent_viewer.obj.ctrl_wdg.quad_obj.all_pts[self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx][3]
            self.parent_viewer.obj.ctrl_wdg.quad_obj.rotate(rx, (P2 - P1)/np.linalg.norm(P2-P1))
            self.parent_viewer.obj.ctrl_wdg.quad_obj.rotate(ry, (P4 - P1)/np.linalg.norm(P4-P1))
            self.parent_viewer.obj.ctrl_wdg.quad_obj.rotate(rz, np.cross((P2 - P1)/np.linalg.norm(P2-P1), (P4 - P1)/np.linalg.norm(P4-P1)))
            
        elif self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx != -1:
            P1 = self.parent_viewer.obj.cylinder_obj.centers[self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx]
            P4 = self.parent_viewer.obj.cylinder_obj.top_centers[self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx]
            P3 = self.parent_viewer.obj.cylinder_obj.vertices_cylinder[self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx][0]
            P2 = np.cross(P4 - P1, P3 - P1) + P1
            self.parent_viewer.obj.cylinder_obj.rotate(rx, (P3 - P1)/np.linalg.norm(P3-P1))
            self.parent_viewer.obj.cylinder_obj.rotate(ry, (P4 - P1)/np.linalg.norm(P4-P1))
            self.parent_viewer.obj.cylinder_obj.rotate(rz, (P2 - P1)/np.linalg.norm(P2-P1))
            
            
        elif self.parent_viewer.obj.curve_obj.selected_curve_idx != -1:
            base_centers = self.parent_viewer.obj.curve_obj.final_base_centers[self.parent_viewer.obj.curve_obj.selected_curve_idx]
            center = np.mean(np.asarray(base_centers), axis=0)
            P1 = base_centers[0]
            P4 = base_centers[1]
            P3 = self.parent_viewer.obj.curve_obj.final_cylinder_bases[self.parent_viewer.obj.curve_obj.selected_curve_idx][0][0]
            P2 = np.cross(P4 - P1 , P3 - P1) + P1
            x_axis = (P3 - P1)/np.linalg.norm(P3 - P1)
            y_axis = (P4 - P1)/np.linalg.norm(P4 - P1)
            z_axis = (P2 - P1)/np.linalg.norm(P2 - P1)
            
            self.parent_viewer.obj.curve_obj.rotate(rx, x_axis, center)
            self.parent_viewer.obj.curve_obj.rotate(ry, y_axis, center)
            self.parent_viewer.obj.curve_obj.rotate(rz, z_axis, center)

        
        else:
            del_primitive_dialogue()
                
                
                
                
                
                
                
                
    def create_scale_panel(self):
        self.scale_dialog = QDialog()
        self.scale_dialog.setWindowTitle("scaling panel")

        QBtn = QDialogButtonBox.Ok

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.scale_dialog.accept)

        label_top = QLabel("Enter the scale ")
        
        label_up = QLabel("Up : ")
        label_down = QLabel("Down : ")

        self.rx = QLineEdit("1")
        self.rx.setValidator(QDoubleValidator())
        self.rx.setMaxLength(6)
        self.rx.setFont(QFont("Arial", 10))
        
        self.ry = QLineEdit("1")
        self.ry.setValidator(QDoubleValidator())
        self.ry.setMaxLength(6)
        self.ry.setFont(QFont("Arial", 10))
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(label_up)
        h_layout.addWidget(self.rx)
        h_layout.addWidget(label_down)
        h_layout.addWidget(self.ry)

        cal_layout = QVBoxLayout()
        cal_layout.addWidget(label_top)
        cal_layout.addLayout(h_layout)
        cal_layout.addWidget(buttonBox)
        self.scale_dialog.setLayout(cal_layout)
        
        if self.scale_dialog.exec():
            s_up = float(self.rx.text())
            s_down = float(self.ry.text())
            # print(rx, ry, rz)
            
            if self.parent_viewer.obj.ctrl_wdg.rect_obj.selected_rect_idx != -1:
                self.parent_viewer.obj.ctrl_wdg.rect_obj.scale_up(s_up)
                self.parent_viewer.obj.ctrl_wdg.rect_obj.scale_down(s_down)


            elif self.parent_viewer.obj.ctrl_wdg.quad_obj.selected_quad_idx != -1:
                self.parent_viewer.obj.ctrl_wdg.quad_obj.scale_up(s_up)
                self.parent_viewer.obj.ctrl_wdg.quad_obj.scale_down(s_down)
                
                
            elif self.parent_viewer.obj.cylinder_obj.selected_cylinder_idx != -1:
                self.parent_viewer.obj.cylinder_obj.scale_up(s_up)
                self.parent_viewer.obj.cylinder_obj.scale_down(s_down)
                
                
            elif self.parent_viewer.obj.curve_obj.selected_curve_idx != -1:
                self.parent_viewer.obj.curve_obj.scale_up(s_up)
                self.parent_viewer.obj.curve_obj.scale_down(s_down)


            else:
                del_primitive_dialogue()

            