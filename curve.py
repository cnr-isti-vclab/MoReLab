from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.spatial import distance
from scipy.optimize import minimize, least_squares
from scipy import linalg

import numpy as np
import math


class Curve_Tool(QObject):
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        self.data_val = []
        self.dist_thresh_select = 10.0
        self.curve_3d_point = []
        self.radius_point = []
        self.planes = []
        self.num_pts = 30
        self.bezier_control_points = []
        self.curve_2d_points = []
        self.final_bezier = []
        self.ctrl_pts_final = []
        self.final_base_centers = []
        self.final_top_centers = []
        self.final_cylinder_bases = []
        self.final_cylinder_tops = []
        self.P1_curve = []
        self.P2_curve = []
        self.P3_curve = []
        self.P4_curve = []
        
        
        
        
        
        
    def make_curve(self, x, y, w1, w2, h1, h2):
        if x > w1 and y > h1 and x < w2 and y < h2:
            v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
            t = self.ctrl_wdg.selected_thumbnail_index
            if self.ctrl_wdg.kf_method == "Regular":
                v.curve_groups_regular[t].append([x,y])
            elif self.ctrl_wdg.kf_method == "Network":
                v.curve_groups_network[t].append([x,y])
            
        
        
            
    def select_feature(self, x, y):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = self.ctrl_wdg.selected_thumbnail_index
        
        feature_selected = False

        if self.ctrl_wdg.kf_method == "Regular":
            for i, fc in enumerate(v.features_regular[t]):
                if not v.hide_regular[t][i]:
                    d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                    if d < self.dist_thresh_select:
                        v.curve_pts_regular[t].append(i)
                        feature_selected = True
                        
        elif self.ctrl_wdg.kf_method == "Network":
            for i, fc in enumerate(v.features_network[t]):
                if not v.hide_network[t][i]:
                    d = distance.euclidean((fc.x_loc, fc.y_loc), (x, y))
                    if d < self.dist_thresh_select and len(self.data_val) == 0:
                        v.curve_pts_network[t].append(i)
                        feature_selected = True
                            
        return feature_selected
    
    def check_vector(self, z):
        # print(z)
        s = np.dot(z, z)
        # print("Sum : "+str(s))
        if 0.99 < s < 1.1:
            return True
        else:
            print("z Vector is not unity")
            return False
        
    def get_z(self, a, b, c, d, x, y):
        z = (-d - a*x - b*y)/c
        # print("z : "+str(z))
        return z
    
    def project_2d(self, Pw, M):

        Pw_ext = np.concatenate((Pw, np.ones(shape=(Pw.shape[0], 1))), axis=1)
        # print(Pw.shape)
        pts1_out = np.matmul(M, Pw_ext.transpose())
        pts1_out = pts1_out.transpose()
        for i in range(pts1_out.shape[0]):
            pts1_out[i,:] = pts1_out[i,:]/pts1_out[i,2]

        pts1_out = pts1_out[:, :-1]
        return pts1_out
        
    
    def estimate_plane(self, M):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        t = self.ctrl_wdg.selected_thumbnail_index
        # print("Projection")
        # print(M)
        pts = []
        data_val = []
        if self.ctrl_wdg.kf_method == "Regular":
            if len(v.curve_groups_regular) > 0:
                pts = v.curve_3d_point_regular[t]
                data_val = v.curve_groups_regular[t]
        if self.ctrl_wdg.kf_method == "Network":
            if len(v.curve_groups_network) > 0:
                pts = v.curve_3d_point_Network[t]
                data_val = v.curve_groups_network[t]
        
        z_vec = M[2, 0:3]
        z_vec = z_vec/np.linalg.norm(z_vec)
            
        if len(pts) > 0 and len(data_val) == 4:
            a, b, c = -z_vec[0], -z_vec[1], -z_vec[2]
            d = np.dot(z_vec, pts[0])
            N = np.array([a, b, c])
            Ps = []
            for i, pp in enumerate(data_val):
                px = self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(pp[0])
                py = self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_y(pp[1])
                # print(px, py)
                A_00 = M[0,0] - px*M[2,0]
                A_01 = M[0,1] - px*M[2,1]
                A_02 = M[0,2] - px*M[2,2]
                A_10 = M[1,0] - py*M[2,0]
                A_11 = M[1,1] - py*M[2,1]
                A_12 = M[1,2] - py*M[2,2]
                
                A = np.array([[A_00, A_01, A_02],[A_10, A_11, A_12], [a, b, c]])
                B = np.array([px*M[2,3] - M[0,3], py*M[2,3] - M[1,3], -d])
                
                X = np.linalg.solve(A, B)
                
                # print(X)
                Ps.append(X)
                if self.ctrl_wdg.kf_method == "Regular":
                    v.curve_3d_point_regular[t].append(X)
                elif self.ctrl_wdg.kf_method == "Network":
                    v.curve_3d_point_network[t].append(X)
            
            self.bezier_curve_range(Ps, v, t)
        


    def find_final_curve(self):
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        proj_tuples = self.ctrl_wdg.gl_viewer.obj.camera_projection_mat
        x0 = []
        cp = []
        points = []
        for i, tup in enumerate(proj_tuples):
            pts = []
            data_val = []
            pts2 = []
            # print("Image index : "+str(tup[0]))
            if self.ctrl_wdg.kf_method == "Regular":
                pts = v.curve_3d_point_regular[tup[0]][5:]
                pts2 = v.curve_3d_point_regular[tup[0]][1:5]
                val_list = v.curve_groups_regular[tup[0]]
                for tup in val_list:
                    data_val.append([self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(tup[0]), self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_y(tup[1])])
                
            elif self.ctrl_wdg.kf_method == "Network":
                pts = v.curve_3d_point_network[tup[0]][5:]
                pts2 = v.curve_3d_point_network[tup[0]][1:5]
                val_list = v.curve_groups_network[tup[0]]
                for tup in val_list:
                    data_val.append([self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_x(tup[0]), self.ctrl_wdg.gl_viewer.obj.feature_panel.transform_y(tup[1])])
                
            if len(pts) > 10:
                # self.bezier_control_points.append(np.vstack(pts2))
                a = np.asarray(data_val)
                self.curve_2d_points.append((i, a))
                x0.append(np.vstack(pts2)) # Control points
        
        if len(x0) > 0:
            x0_array = np.vstack(x0)

            x1 = x0_array.ravel()

            res = least_squares(self.minimize_curve_error, x1, verbose=0, ftol=1e-15, method='trf')
            ctrl_pts = res.x.reshape((int(len(res.x)/3), 3))
            # print(ctrl_pts - x0_array)
            # print(ctrl_pts)
            ctrl_pts = ctrl_pts[:4, :]
            # print("\n\n\n")
            # print(ctrl_pts)
            
            self.ctrl_pts_final.append(ctrl_pts)
            Ps = []
            for j in range(self.num_pts):
                k = j / float(self.num_pts - 1)
                Ps.append(self.bezier(k, ctrl_pts))
            self.final_bezier.append(np.asarray(Ps))
            

    def make_general_cylinder(self):
        
        Ps = self.final_bezier[-1]
        # print(Ps)
        for i in range(0,len(Ps)-1,1):
            P1 = Ps[i]
            if i==0:
                P3 = self.radius_point[0]
                P2 = -1*np.cross(Ps[i] - Ps[i+1], P3 - Ps[i]) + Ps[i]

            else:                
                
                P3 = cyl_tops[0]
                P2 = -1*np.cross(Ps[i] - Ps[i+1], P3 - Ps[i]) + Ps[i]

            self.P2_curve.append(P2)
            self.P3_curve.append(P3)
                
            P4 = Ps[i+1]

            cyl_bases, cyl_tops, center_base, center_top = self.ctrl_wdg.gl_viewer.obj.cylinder_obj.make_cylinder(P1, P2, P3, P4)
                

            # print(cyl_bases)
            # print(center_base)
            # print("\n\n---------------------------\n\n")
            # print(cyl_tops)
            # print(center_top)
            self.final_base_centers.append(center_base)
            self.final_top_centers.append(center_top)
            self.final_cylinder_bases.append(cyl_bases)
            self.final_cylinder_tops.append(cyl_tops)
        
            
            
    
    def minimize_curve_error(self, params):
        error = 0
        control_p = params.reshape((int(len(params)/3), 3))
        
        n_curves = int(control_p.shape[0]/4)
        
        ctrl_points = []
        # ctrl_pts = []
        for i in range(n_curves):
            ctrl_points.append(control_p[i*4 : (i+1)*4, :])

        diff = []
        for i in range(len(ctrl_points) - 1):
            diff.append(ctrl_points[i] - ctrl_points[i+1])
        
        diff.append(ctrl_points[0] - ctrl_points[-1])
        
        diff = np.vstack(diff)
        
        
        proj_tuples = self.ctrl_wdg.gl_viewer.obj.camera_projection_mat
        
        diff2 = []
        for i, tup_2d in enumerate(self.curve_2d_points):
            M = np.matmul(self.ctrl_wdg.gl_viewer.obj.K, proj_tuples[tup_2d[0]][1][0:3, :])
            projected = self.project_2d(ctrl_points[i], M)
            original = tup_2d[1]
            diff2.append(projected - original)
            
        diff2 = np.vstack(diff2)
        diff2 = np.concatenate((diff2, np.zeros(shape=(diff2.shape[0], 1))), axis=1)

        # print(diff.shape)
        final_array = np.concatenate((diff, diff2), axis=0)
        
        error = final_array.ravel()
        
        return error

                
                
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
    
    
    def bezier_curve_range(self, points, v, t):
        """Range of points in a curve bezier"""
        # pts = []
        for i in range(self.num_pts):
            k = i / float(self.num_pts - 1)
            P = self.bezier(k, points)
            
            if self.ctrl_wdg.kf_method == "Regular":
                v.curve_3d_point_regular[t].append(P)
            elif self.ctrl_wdg.kf_method == "Network":
                v.curve_3d_point_network[t].append(P)
            
                