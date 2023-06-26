from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.spatial import distance
from util.util import straight_line_dialogue
import numpy as np
from scipy.spatial.transform import Rotation as R


class Cylinder_Tool(QObject):
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        self.dist_thresh_select = 10.0
        self.selected_cylinder_idx = -1
        self.group_num = 0
        self.order = []
        self.data_val = []
        self.vertices_cylinder = []
        self.top_vertices = []
        self.centers = []
        self.top_centers = []
        self.base_circles = []
        self.sectorCount = 32
        self.cylinder_count = []
        self.colors = [(0,0,0)]
        self.b_vecs = []
        self.t_vecs = []
        self.Ns = []
        self.radii = []
        self.heights = []
        self.bool_cylinder_type = []


    def reset(self, ctrl_wdg):
        self.__init__(ctrl_wdg)

        
    def select_feature(self, x, y):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = self.ctrl_wdg.selected_thumbnail_index
        
        feature_selected = False

        if (len(v.features_regular) > 0 or len(v.features_network) > 0) and len(self.ctrl_wdg.gl_viewer.obj.all_ply_pts) > 0:
            data = self.ctrl_wdg.gl_viewer.obj.all_ply_pts[-1]    # 3D data from bundle adjustment
            cnt = 0
            if self.ctrl_wdg.kf_method == "Regular":
                for i, fc in enumerate(v.features_regular[t]):
                    if not v.hide_regular[t][i]:
                        d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                        if d < self.dist_thresh_select:
                            self.order.append(i)
                            self.data_val.append(data[v.mapping_2d_3d_regular[t][cnt],:])
                            v.cylinder_groups_regular[t][i] = self.group_num
                            feature_selected = True
                            
                            if len(self.data_val) == 4:
                                if self.ctrl_wdg.ui.bnCylinder:
                                    bases, tops, center, top_c, height, radius, b_vec, t_vec, N = self.make_new_cylinder(self.data_val[0], self.data_val[1], self.data_val[2], self.data_val[3])
                                    if len(bases) > 0:

                                        self.bool_cylinder_type.append(False)
                                        self.refresh_cylinder_data(bases, tops, center, top_c, height, radius, b_vec, t_vec, N)
                                    else:
                                        straight_line_dialogue()
                                        del self.data_val[-1]
                                else:

                                    bases, tops, center, top_c, height, radius, b_vec, t_vec, N = self.make_cylinder(self.data_val[0], self.data_val[1], self.data_val[2], self.data_val[3])
                                    self.bool_cylinder_type.append(True)
                                    self.refresh_cylinder_data(bases, tops, center, top_c, height, radius, b_vec, t_vec, N)
                        cnt += 1
             
            elif self.ctrl_wdg.kf_method == "Network":
                for i, fc in enumerate(v.features_network[t]):
                    if not v.hide_network[t][i]:
                        d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                        if d < self.dist_thresh_select:
                            self.data_val.append(data[v.mapping_2d_3d_regular[t][cnt],:])
                            v.cylinder_groups_network[t][i] = self.group_num
                            self.order.append(i)
                            feature_selected = True
                            
                            if len(self.data_val) == 4:
                                if self.ctrl_wdg.ui.bnCylinder:
                                    bases, tops, center, top_c, height, radius, b_vec, t_vec, N = self.make_new_cylinder(self.data_val[0], self.data_val[1], self.data_val[2], self.data_val[3])
                                    if len(bases) > 0:

                                        self.bool_cylinder_type.append(False)
                                        self.refresh_cylinder_data(bases, tops, center, top_c, height, radius, b_vec, t_vec, N)
                                    else:
                                        straight_line_dialogue()
                                        del self.data_val[-1]
                                else:
                                    
                                    v.cylinder_groups_network[t][i] = -1
                                    for order in self.order:
                                        v.cylinder_groups_network[t][order] = -1

                                    bases, tops, center, top_c, height, radius, b_vec, t_vec, N = self.make_cylinder(self.data_val[0], self.data_val[1], self.data_val[2], self.data_val[3])
                                    self.bool_cylinder_type.append(True)
                                    self.refresh_cylinder_data(bases, tops, center, top_c, height, radius, b_vec, t_vec, N)
                        cnt += 1

        return feature_selected
    
    
    def refresh_cylinder_data(self, bases, tops, center, top_c, height, radius, b_vec, t_vec, N):
        
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = self.ctrl_wdg.selected_thumbnail_index
        
        if self.ctrl_wdg.kf_method == "Regular":        
            for order in self.order:
                v.cylinder_groups_regular[t][order] = -1
        elif self.ctrl_wdg.kf_method == "Network":        
            for order in self.order:
                v.cylinder_groups_network[t][order] = -1
        
        self.heights.append(height)
        self.radii.append(radius)
        self.b_vecs.append(b_vec)
        self.t_vecs.append(t_vec)
        self.Ns.append(N)
        # print("Primitive count : "+str(self.ctrl_wdg.rect_obj.primitive_count))
        self.cylinder_count.append(self.ctrl_wdg.rect_obj.primitive_count)
        c = self.ctrl_wdg.rect_obj.getRGBfromI(self.ctrl_wdg.rect_obj.primitive_count)
        self.colors.append(c)
        self.centers.append(center)
        self.top_centers.append(top_c)
        self.vertices_cylinder.append(bases)
        self.top_vertices.append(tops)
        self.data_val = []
        self.order = []
        self.group_num += 1
        self.ctrl_wdg.rect_obj.primitive_count += 1

            
            
    
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
        
        if height < 0:
            # print("Center : "+str(center))
            return self.make_cylinder(center, p2, p1, p3)


        b_vec = np.cross(t_vec, N)          # t_vec, b_vec and N form our x,y,z coordinate system
        sectorStep = 2*np.pi/self.sectorCount
        
        base_points = []
        top_points = []
        
        for i in range(self.sectorCount+1):
            sectorAngle = i * sectorStep           # theta
            base_points.append(center + radius*np.cos(sectorAngle)*t_vec + radius*np.sin(sectorAngle)*b_vec)
            top_points.append(center + radius*np.cos(sectorAngle)*t_vec + radius*np.sin(sectorAngle)*b_vec + height*N)
        
        
        return base_points, top_points, center, center + height*N, height, radius, b_vec, t_vec, N
    
        
    
    def delete_cylinder(self, idx):
        if idx != -1:
            self.centers[idx] = np.array([-1, -1, -1])
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
        # print(height)
        if height > 0:
            return self.make_new_cylinder(p3, p2, p1, p4)

        b_vec = np.cross(t_vec, N)          # t_vec, b_vec and N form our x,y,z coordinate system
        
        new_P1 = (0, 0)
        new_P2 = (np.dot(b_vec, p2-p1), np.dot(t_vec, p2-p1))
        new_P3 = (np.dot(b_vec, p3-p1), np.dot(t_vec, p3-p1))
                
        center_2d, radius = self.define_circle(new_P1, new_P2, new_P3)

        if center_2d is None:
            return [], [], 0, 0, 0, 0, [], [], []
        center = p1 + center_2d[0]*b_vec + center_2d[1]*t_vec

        sectorStep = 2*np.pi/self.sectorCount
        
        base_points = []
        top_points = []
        
        for i in range(self.sectorCount+1):
            sectorAngle = i * sectorStep           # theta
            base_points.append(center + radius*np.cos(sectorAngle)*b_vec + radius*np.sin(sectorAngle)*t_vec)
            top_points.append(center + radius*np.cos(sectorAngle)*b_vec + radius*np.sin(sectorAngle)*t_vec + height*N)
        
        return base_points, top_points, center, center + height*N , height, radius, b_vec, t_vec, N
    

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


    def rotate(self, angle_degrees, rotation_axis):
        if self.selected_cylinder_idx != -1:
            angle_radians = np.radians(angle_degrees)
            rotation_vector = angle_radians * rotation_axis
            rotation = R.from_rotvec(rotation_vector)
            base_center = self.centers[self.selected_cylinder_idx]
            if -1 not in base_center:

                self.t_vecs[self.selected_cylinder_idx] = rotation.apply(self.t_vecs[self.selected_cylinder_idx])
                self.b_vecs[self.selected_cylinder_idx] = rotation.apply(self.b_vecs[self.selected_cylinder_idx])
                self.Ns[self.selected_cylinder_idx] = rotation.apply(self.Ns[self.selected_cylinder_idx])

                base_vertices = self.vertices_cylinder[self.selected_cylinder_idx]
                top_center = self.top_centers[self.selected_cylinder_idx]
                top_vertices = self.top_vertices[self.selected_cylinder_idx]

                cyl_center = 0.5*(base_center + top_center)

                self.centers[self.selected_cylinder_idx] = rotation.apply(base_center - cyl_center) + cyl_center
                self.top_centers[self.selected_cylinder_idx] = rotation.apply(top_center - cyl_center) + cyl_center
                for i, pt in enumerate(base_vertices):
                    self.vertices_cylinder[self.selected_cylinder_idx][i] = rotation.apply(pt - cyl_center) + cyl_center

                for i, pt in enumerate(top_vertices):
                    self.top_vertices[self.selected_cylinder_idx][i] = rotation.apply(pt - cyl_center) + cyl_center


    def translate(self, axis, idx):
        if idx != -1:
            base_center = self.centers[idx]
            if -1 not in base_center:
                base_vertices = self.vertices_cylinder[idx]
                top_center = self.top_centers[idx]
                top_vertices = self.top_vertices[idx]

                self.centers[idx] = base_center + axis
                self.top_centers[idx] = top_center + axis

                for i, pt in enumerate(base_vertices):
                    self.vertices_cylinder[idx][i] = pt + axis

                for i, pt in enumerate(top_vertices):
                    self.top_vertices[idx][i] = pt + axis


    def scale_up(self, scale):
        i = self.selected_cylinder_idx
        # print("Index : "+str(i))
        if i != -1:
            radius = self.radii[i] * scale
            self.radii[i] = radius
            # print("Radius : "+str(radius))
            cyl_axis = (1/scale)*(self.top_centers[i] - self.centers[i])
            self.centers[i] = self.centers[i] - cyl_axis
            self.top_centers[i] = self.top_centers[i] + cyl_axis
            height = np.linalg.norm(self.top_centers[i] - self.centers[i])
            # print("Height : "+str(height))
            center = self.centers[i]
            sectorStep = 2 * np.pi / self.sectorCount
            t_vec, b_vec, N = self.t_vecs[i], self.b_vecs[i], self.Ns[i]

            if self.bool_cylinder_type[i]:
                for j in range(self.sectorCount + 1):
                    sectorAngle = j * sectorStep  # theta
                    self.vertices_cylinder[i][self.sectorCount - j] = center + radius * np.cos(sectorAngle) * b_vec + radius * np.sin(
                        sectorAngle) * t_vec
                    self.top_vertices[i][self.sectorCount - j] = center + radius * np.cos(sectorAngle) * b_vec + radius * np.sin(
                        sectorAngle) * t_vec + height * N

            else:
                for j in range(self.sectorCount + 1):
                    sectorAngle = j * sectorStep  # theta
                    self.vertices_cylinder[i][j] = center + radius * np.cos(sectorAngle) * b_vec + radius*np.sin(sectorAngle) * t_vec
                    self.top_vertices[i][j] = center + radius * np.cos(sectorAngle) * b_vec + radius*np.sin(sectorAngle) * t_vec - height * N


    def scale_down(self, scale):
        i = self.selected_cylinder_idx
        if i != -1:
            radius = self.radii[i] / scale
            self.radii[i] = radius

            cyl_axis = (1/scale)*(self.top_centers[i] - self.centers[i])
            self.centers[i] = self.centers[i] + cyl_axis
            self.top_centers[i] = self.top_centers[i] - cyl_axis

            height = np.linalg.norm(self.top_centers[i] - self.centers[i])
            # print(height)
            center = self.centers[i]
            sectorStep = 2 * np.pi / self.sectorCount
            t_vec, b_vec, N = self.t_vecs[i], self.b_vecs[i], self.Ns[i]

            if self.bool_cylinder_type[i]:
                for j in range(self.sectorCount + 1):
                    sectorAngle = j * sectorStep  # theta
                    self.vertices_cylinder[i][self.sectorCount - j] = center + radius * np.cos(sectorAngle) * b_vec + radius * np.sin(
                        sectorAngle) * t_vec
                    self.top_vertices[i][self.sectorCount - j] = center + radius * np.cos(sectorAngle) * b_vec + radius * np.sin(
                        sectorAngle) * t_vec + height * N

            else:
                for j in range(self.sectorCount + 1):
                    sectorAngle = j * sectorStep  # theta
                    self.vertices_cylinder[i][j] = center + radius * np.cos(sectorAngle) * b_vec + radius*np.sin(sectorAngle) * t_vec
                    self.top_vertices[i][j] = center + radius * np.cos(sectorAngle) * b_vec + radius*np.sin(sectorAngle) * t_vec - height * N

