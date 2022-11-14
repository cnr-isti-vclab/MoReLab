from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.spatial import distance
# from quad_panel import QuadPanel
import numpy as np


class Cylinder_Tool(QObject):
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        self.dist_thresh_select = 10.0
        self.group_num = 0
        self.order = []
        self.data_val = []
        self.vertices_cylinder = []
        self.top_vertices = []
        self.centers = []
        self.top_centers = []

        
        
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
                        if d < self.dist_thresh_select and v.cylinder_groups_regular[t][i] == -1:
                            self.order.append(i)
                            self.data_val.append(data[i,:])
                            v.cylinder_groups_regular[t][i] = self.group_num
                            feature_selected = True
                            
                            if len(self.data_val) == 4:
                                self.centers.append(self.data_val[0])
                                bases, tops = self.make_circle(self.data_val[0], self.data_val[1], self.data_val[2], self.data_val[3])
                                self.vertices_cylinder.append(bases)
                                self.top_vertices.append(tops)
                                
  
                                # self.occurence_groups.append(self.order)
                                # print("Group number:")
                                # print(self.group_num+1)
                                # self.order = []
                                self.data_val = []
                                self.group_num += 1
             
            elif self.ctrl_wdg.kf_method == "Network":
                for i, fc in enumerate(v.features_network[t]):
                    if not v.hide_network[t][i]:
                        d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))

        return feature_selected
    
    
    def make_circle(self, center, p1, p2, p3, sectorCount = 16): # p1 is anchor and p2 is used for radius
        t_vec = p1 - center
        b_vec_temp = p2 - center
        H_vec = p3 - center
        
        radius = np.linalg.norm(b_vec_temp)
        
        t_vec = t_vec/np.linalg.norm(t_vec)
        b_vec_temp = b_vec_temp/np.linalg.norm(b_vec_temp)

        N = np.cross(b_vec_temp, t_vec)
        N = N/np.linalg.norm(N)
        
        height = np.dot(H_vec, N)/np.linalg.norm(N)
        
        b_vec = np.cross(t_vec, N)          # t_vec, b_vec and N form our x,y,z coordinate system
        
        sectorStep = 2*np.pi/sectorCount
        
        base_points = []
        top_points = []
        
        for i in range(sectorCount+1):
            sectorAngle = i * sectorStep           # theta
            base_points.append(center + radius*np.cos(sectorAngle)*t_vec + radius*np.sin(sectorAngle)*b_vec)
            top_points.append(center + radius*np.cos(sectorAngle)*t_vec + radius*np.sin(sectorAngle)*b_vec + height*N)
        
        self.top_centers.append(center + height*N)
        
        return base_points, top_points
        
        
    
    
    
    def getUnitCircleVertices(self, radius, sectorCount = 8):
        sectorStep = 2*np.pi/sectorCount
        cos_values = []
        sin_values = []
        for i in range(sectorCount+1):
            sectorAngle = i * sectorStep           # theta
            cos_values.append(np.cos(sectorAngle))
            sin_values.append(np.sin(sectorAngle))

        return cos_values, sin_values
                
