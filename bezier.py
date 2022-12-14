from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.spatial import distance
import math


class Bezier_Tool(QObject):
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        self.data_val = []
        self.all_data_val = []
        self.order = []
        self.occurrence_groups = []
        self.num_pts = 30
        self.dist_thresh_select = 10.0
        self.group_num = 0
        self.bezier_points = []
        self.selected_curve_idx = -1
        self.selected_point_idx = -1
        self.colors = [(0,0,0)]
        self.bezier_count = []


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
                        if d < self.dist_thresh_select and v.bezier_groups_regular[t][i] == -1:
                            self.data_val.append(data[i,:])
                            v.bezier_groups_regular[t][i] = self.group_num
                            self.order.append(i)
                            feature_selected = True
                            # self.node_selected = -1
                            
                            if len(self.data_val) == 4:
                                self.refresh_bezier_data()
                                
        return feature_selected
                                
                                
    def refresh_bezier_data(self):
        self.occurrence_groups.append(self.order)
        bezier_points = self.bezier_curve_range(self.num_pts, self.data_val[0], self.data_val[1], self.data_val[2], self.data_val[3])
        self.bezier_points.append(bezier_points)
        
        # print("Start : "+str(self.ctrl_wdg.quad_obj.primitive_count))
        
        self.bezier_count.append(self.ctrl_wdg.quad_obj.primitive_count)
        c1 = self.ctrl_wdg.quad_obj.getRGBfromI(self.ctrl_wdg.quad_obj.primitive_count)
        self.colors.append(c1)
        
        self.bezier_count.append(self.ctrl_wdg.quad_obj.primitive_count+1)
        c2 = self.ctrl_wdg.quad_obj.getRGBfromI(self.ctrl_wdg.quad_obj.primitive_count+1)
        self.colors.append(c2)
        
        self.all_data_val.append(self.data_val)
        self.group_num += 1
        self.data_val = []
        self.order = []
        self.ctrl_wdg.quad_obj.primitive_count = self.ctrl_wdg.quad_obj.primitive_count + 2
        
        # print("End : "+str(self.ctrl_wdg.quad_obj.primitive_count))
        
        
        
        
        
    def binomial(self, i, n):
        """Binomial coefficient"""
        return math.factorial(n) / float(
            math.factorial(i) * math.factorial(n - i))
    
    
    def bernstein(self, t, i, n):
        """Bernstein polynom"""
        return self.binomial(i, n) * (t ** i) * ((1 - t) ** (n - i))
    
    
    def bezier(self, t, points):
        """Calculate coordinate of a point in the bezier curve"""
        n = len(points) - 1
        x = y = z = 0
        for i, pos in enumerate(points):
            bern = self.bernstein(t, i, n)
            x += pos[0] * bern
            y += pos[1] * bern
            z += pos[2] * bern
        return [x, y, z]
    
    
    def bezier_curve_range(self, n, P1, P2, P3, P4):
        """Range of points in a curve bezier"""
        points = [P1, P2, P3, P4]
        pts = []
        for i in range(n):
            t = i / float(n - 1)
            pts.append(self.bezier(t, points))
            
        return pts
    
    
    def getRGBfromI(self, RGBint):
        blue =  RGBint & 255
        green = (RGBint >> 8) & 255
        red =   (RGBint >> 16) & 255
        c = (red, green, blue)
        # print(c)
        return c
        
    def getIfromRGB(self, r, g, b):
        RGBint = int(r * 256*256 + g * 256 + b)
        # print("ID : "+str(RGBint))
        return RGBint
    
    
    # def triangulate(self, K, Rt, x2d):
        
        
    
    
    