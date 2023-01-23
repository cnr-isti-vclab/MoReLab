from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.spatial import distance
# from quad_panel import QuadPanel
from util.util import straight_line_dialogue
import numpy as np


class Cylinder_Tool(QObject):
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        self.dist_thresh_select = 10.0
        self.selected_cylinder_idx = -1
        self.group_num = 0
        self.order = []
        self.occurrence_groups = []
        self.data_val = []
        self.vertices_cylinder = []
        self.top_vertices = []
        self.centers = []
        self.top_centers = []
        self.base_circles = []
        self.sectorCount = 64
        self.cylinder_count = []
        self.colors = [(0,0,0)]

        
        
    def select_feature(self, x, y):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = self.ctrl_wdg.selected_thumbnail_index
        
        feature_selected = False

        if (len(v.features_regular) > 0 or len(v.features_network) > 0) and len(self.ctrl_wdg.gl_viewer.obj.ply_pts) > 0:
            data = self.ctrl_wdg.gl_viewer.obj.ply_pts[-1]    # 3D data from bundle adjustment
            if self.ctrl_wdg.kf_method == "Regular":
                for i, fc in enumerate(v.features_regular[t]):
                    if not v.hide_regular[t][i]:
                        d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                        if d < self.dist_thresh_select:
                            self.data_val.append(data[i,:])
                            v.cylinder_groups_regular[t][i] = self.group_num
                            self.order.append(i)
                            feature_selected = True
                            
                            if len(self.data_val) == 4:
                                self.refresh_cylinder_data()


                                # print(self.centers)
                                # print(self.top_centers)
             
            elif self.ctrl_wdg.kf_method == "Network":
                for i, fc in enumerate(v.features_network[t]):
                    if not v.hide_network[t][i]:
                        d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                        if d < self.dist_thresh_select:
                            self.data_val.append(data[i,:])
                            v.cylinder_groups_regular[t][i] = self.group_num
                            self.order.append(i)
                            feature_selected = True
                            
                            if len(self.data_val) == 4:
                                self.refresh_cylinder_data()


        return feature_selected
    
    
    def refresh_cylinder_data(self):
        if self.ctrl_wdg.ui.bnCylinder:
            bases, tops, center, top_c = self.make_new_cylinder(self.data_val[0], self.data_val[1], self.data_val[2], self.data_val[3])
        else:
            bases, tops, center, top_c = self.make_cylinder(self.data_val[0], self.data_val[1], self.data_val[2], self.data_val[3])

        if len(bases) > 0:
            self.occurrence_groups.append(self.order)
            # print("Primitive count : "+str(self.ctrl_wdg.quad_obj.primitive_count))
            self.cylinder_count.append(self.ctrl_wdg.quad_obj.primitive_count)
            c = self.ctrl_wdg.quad_obj.getRGBfromI(self.ctrl_wdg.quad_obj.primitive_count)
            self.colors.append(c)
            self.centers.append(center)
            self.top_centers.append(top_c)
            self.vertices_cylinder.append(bases)
            self.top_vertices.append(tops)
            self.data_val = []
            self.order = []
            self.group_num += 1
            self.ctrl_wdg.quad_obj.primitive_count += 1
        else:
            straight_line_dialogue()
            del self.data_val[-1]
            
            
    
    def make_circle(self, center, p1, p2):
        t_vec = p1 - center
        b_vec_temp = p2 - center
        
        radius = np.linalg.norm(b_vec_temp)
        
        t_vec = t_vec/max(0.00005, np.linalg.norm(t_vec))
        b_vec_temp = b_vec_temp/max(0.00005, radius)

        N = np.cross(b_vec_temp, t_vec)
        N = N/max(0.00005, np.linalg.norm(N))
        
        b_vec = np.cross(t_vec, N)          # t_vec, b_vec and N form our x,y,z coordinate system
        sectorStep = 2*np.pi/self.sectorCount
        
        base_points = []
        
        for i in range(self.sectorCount+1):
            sectorAngle = i * sectorStep           # theta
            base_points.append(center + radius*np.cos(sectorAngle)*t_vec + radius*np.sin(sectorAngle)*b_vec)
            
        return base_points, center
        
        
    
    def make_cylinder(self, center, p1, p2, p3): # p1 is anchor and p2 is used for radius
        # print("Center : "+str(center))
        t_vec = p1 - center
        b_vec_temp = p2 - center
        H_vec = p3 - center
        
        radius = np.linalg.norm(b_vec_temp)
        
        t_vec = t_vec/max(0.00005, np.linalg.norm(t_vec))
        b_vec_temp = b_vec_temp/max(0.00005, radius)

        N = np.cross(b_vec_temp, t_vec)
        N = N/max(0.00005, np.linalg.norm(N))
        
        height = np.dot(H_vec, N)
        
        b_vec = np.cross(t_vec, N)          # t_vec, b_vec and N form our x,y,z coordinate system
        
        sectorStep = 2*np.pi/self.sectorCount
        
        base_points = []
        top_points = []
        
        for i in range(self.sectorCount+1):
            sectorAngle = i * sectorStep           # theta
            base_points.append(center + radius*np.cos(sectorAngle)*t_vec + radius*np.sin(sectorAngle)*b_vec)
            top_points.append(center + radius*np.cos(sectorAngle)*t_vec + radius*np.sin(sectorAngle)*b_vec + height*N)
        
        
        return base_points, top_points, center, center + height*N
    
        
    
    def delete_cylinder(self, idx):
        if idx != -1:
            self.centers[idx] = np.array([-1, -1, -1])
            occ = self.occurrence_groups[idx]
            v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
            t = self.ctrl_wdg.selected_thumbnail_index
            if self.ctrl_wdg.kf_method == "Regular":
                for i, c in enumerate(occ):
                    v.cylinder_groups_regular[t][c] = -1
            elif self.ctrl_wdg.kf_method == "Network":
                for i, c in enumerate(occ):
                    v.cylinder_groups_network[t][c] = -1
                    
            self.selected_cylinder_idx = -1
                
                

    def make_new_circle(self, p1, p2, p3):
        t_vec = p2 - p1
        b_vec_temp = p3 - p1
        
        t_vec = t_vec/max(0.000005, np.linalg.norm(t_vec))
        b_vec_temp = b_vec_temp/max(0.000005, np.linalg.norm(b_vec_temp))

        N = np.cross(t_vec, b_vec_temp)
        N = N/max(0.000005, np.linalg.norm(N))
        
        b_vec = np.cross(t_vec, N)          # t_vec, b_vec and N form our x,y,z coordinate system
        
        new_P1 = (0, 0)
        new_P2 = (np.dot(b_vec, p2-p1), np.dot(t_vec, p2-p1))
        new_P3 = (np.dot(b_vec, p3-p1), np.dot(t_vec, p3-p1))
                
        center_2d, radius = self.define_circle(new_P1, new_P2, new_P3)
        if center_2d is None:
            return [], 0
        center = p1 + center_2d[0]*b_vec + center_2d[1]*t_vec
    
        sectorStep = 2*np.pi/self.sectorCount        
        base_points = []
        
        for i in range(self.sectorCount+1):
            sectorAngle = i * sectorStep           # theta
            base_points.append(center + radius*np.cos(sectorAngle)*b_vec + radius*np.sin(sectorAngle)*t_vec)
        
        return base_points, center
    
    
    def make_new_cylinder(self, p1, p2, p3, p4):
        t_vec = p2 - p1
        b_vec_temp = p3 - p1
        H_vec = p4 - p1
        
        t_vec = t_vec/max(0.000005, np.linalg.norm(t_vec))
        b_vec_temp = b_vec_temp/max(0.000005, np.linalg.norm(b_vec_temp))

        N = np.cross(t_vec, b_vec_temp)
        N = N/max(0.000005, np.linalg.norm(N))
        height = np.dot(H_vec, N)

        b_vec = np.cross(t_vec, N)          # t_vec, b_vec and N form our x,y,z coordinate system
        
        new_P1 = (0, 0)
        new_P2 = (np.dot(b_vec, p2-p1), np.dot(t_vec, p2-p1))
        new_P3 = (np.dot(b_vec, p3-p1), np.dot(t_vec, p3-p1))
                
        center_2d, radius = self.define_circle(new_P1, new_P2, new_P3)
        if center_2d is None:
            return [], [], 0, 0
        center = p1 + center_2d[0]*b_vec + center_2d[1]*t_vec

        sectorStep = 2*np.pi/self.sectorCount
        
        base_points = []
        top_points = []
        
        for i in range(self.sectorCount+1):
            sectorAngle = i * sectorStep           # theta
            base_points.append(center + radius*np.cos(sectorAngle)*b_vec + radius*np.sin(sectorAngle)*t_vec)
            top_points.append(center + radius*np.cos(sectorAngle)*b_vec + radius*np.sin(sectorAngle)*t_vec + height*N)
        
        return base_points, top_points, center, center + height*N    
    

    def define_circle(self, p1, p2, p3):
        """
        Returns the center and radius of the circle passing the given 3 points.
        In case the 3 points form a line, returns (None, infinity).
        """
        temp = p2[0] * p2[0] + p2[1] * p2[1]
        bc = (p1[0] * p1[0] + p1[1] * p1[1] - temp) / 2
        cd = (temp - p3[0] * p3[0] - p3[1] * p3[1]) / 2
        det = (p1[0] - p2[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p2[1])
    
        if abs(det) < 1.0e-6:
            return (None, np.inf)
    
        # Center of circle
        cx = (bc*(p2[1] - p3[1]) - cd*(p1[1] - p2[1])) / det
        cy = ((p1[0] - p2[0]) * cd - (p2[0] - p3[0]) * bc) / det
    
        radius = np.sqrt((cx - p1[0])**2 + (cy - p1[1])**2)
        
        # print("Centre = (", cx, ", ", cy, ")");
        # print("Radius = ", radius);
        
        return (cx, cy), radius