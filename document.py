import os, cv2, platform, json, glob
import numpy as np
from util.util import split_path, adjust_op
from util.sfm import *
from PyQt5.QtWidgets import *
from features import FeatureCrosshair





class Document(QWidget):
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        
    def get_data(self):
        data_movies = []
        for i,v in enumerate(self.ctrl_wdg.mv_panel.movie_caps):
            x_locs = []
            y_locs = []
            x_locs_n = []
            y_locs_n = []
            for fc_list in v.features_regular:
                a = []
                b = []
                for fc in fc_list:
                    a.append(str(fc.x_loc/(self.ctrl_wdg.gl_viewer.util_.w2 - self.ctrl_wdg.gl_viewer.util_.w1)))
                    b.append(str(fc.y_loc/(self.ctrl_wdg.gl_viewer.util_.h2 - self.ctrl_wdg.gl_viewer.util_.h1)))
                    
                x_locs.append(a)
                y_locs.append(b)
                
            
            for fc_list in v.features_network:
                a = []
                b = []
                for fc in fc_list:
                    a.append(str(fc.x_loc/(self.ctrl_wdg.gl_viewer.util_.w2 - self.ctrl_wdg.gl_viewer.util_.w1)))
                    b.append(str(fc.y_loc/(self.ctrl_wdg.gl_viewer.util_.h2 - self.ctrl_wdg.gl_viewer.util_.h1)))
                    
                x_locs_n.append(a)
                y_locs_n.append(b)
                
            movie_feature_data = {"hide_regular": v.hide_regular,
                                  "hide_network": v.hide_network,
                                  "x_locs" : x_locs,
                                  "y_locs" : y_locs,
                                  "x_locs_network" : x_locs_n,
                                  "y_locs_network" : y_locs_n,
                                  }
            data_movies.append(movie_feature_data)
        
        # #### --------------------- Save 3D data --------------------------
        b3D = False
        if len(self.ctrl_wdg.gl_viewer.obj.all_ply_pts) > 0:
            b3D = True
        
        
        str_img_indices = []
        if len(self.ctrl_wdg.gl_viewer.obj.img_indices) > 0:
            for x in self.ctrl_wdg.gl_viewer.obj.img_indices:
                str_img_indices.append(str(x))
        
            
        bRect = False
        rect_pts = self.ctrl_wdg.rect_obj.new_points
        for i, rect_ in enumerate(rect_pts):
            if not self.ctrl_wdg.rect_obj.deleted[i]:
                bRect = True


        bQuad = False
        quad_pts = self.ctrl_wdg.quad_obj.all_pts
        for i, quad_ in enumerate(quad_pts):
            if not self.ctrl_wdg.quad_obj.deleted[i]:
                bQuad = True



        bCyl = False
        num_cyl = 0
        for i, center in enumerate(self.ctrl_wdg.gl_viewer.obj.cylinder_obj.centers):
            if -1 not in center:
                num_cyl += 1
                bCyl = True


        bCurvedCyl = False
        n_curved_cyl = 0
        if len(self.ctrl_wdg.gl_viewer.obj.curve_obj.final_cylinder_bases) > 0:
            bCurvedCyl = True
            base_centers = np.vstack(self.ctrl_wdg.gl_viewer.obj.curve_obj.final_base_centers[0])
            n_curved_cyl = base_centers.shape[0]


        data = {
            "movies" : self.ctrl_wdg.mv_panel.movie_paths,
            "selected_movie" : self.ctrl_wdg.mv_panel.selected_movie_idx,
            "platform" : platform.system(),
            "selected_kf_method" : self.ctrl_wdg.kf_method,
            "selected_thumbnail": self.ctrl_wdg.selected_thumbnail_index,
            "feature_dict" : data_movies,
            "h1" : self.ctrl_wdg.gl_viewer.util_.h1,
            "w1" : self.ctrl_wdg.gl_viewer.util_.w1,
            "bool_3D" : b3D,
            "img_indices" : str_img_indices,
            "bool_rect" : bRect,
            "bool_cyl" : bCyl,
            "n_cyl" : num_cyl,
            "bool_curved_cyl" : bCurvedCyl,
            "n_curved" : n_curved_cyl,
            "bool_quad" : bQuad,
            }
        
        return data
        
    
    def save_3D(self, name_project):
        out_dir = os.path.join(name_project.split('.')[0], '3D_data')
        b_out = os.path.join(out_dir, 'camera_parameters')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
            os.makedirs(b_out)
        
        if len(self.ctrl_wdg.gl_viewer.obj.all_ply_pts) > 0:
            ply_data_all = self.ctrl_wdg.gl_viewer.obj.all_ply_pts[-1]
            ply_data = self.ctrl_wdg.gl_viewer.obj.ply_pts[-1]
            camera_pose = self.ctrl_wdg.gl_viewer.obj.camera_poses[-1]
            projections = self.ctrl_wdg.gl_viewer.obj.camera_projection_mat
            
            np.savetxt(os.path.join(out_dir, 'ply_all.csv'), ply_data_all, delimiter=',')
            np.savetxt(os.path.join(out_dir, 'ply.csv'), ply_data, delimiter=',')
            np.savetxt(os.path.join(out_dir, 'cam_poses.csv'), camera_pose, delimiter=',')

            
            for i, tup in enumerate(projections):
                np.savetxt(os.path.join(b_out, 'ext_'+str(tup[0])+'.csv'), tup[1], delimiter=',')
                
            
            ##### PLY Data for Rectangles
            
            rect_pts = self.ctrl_wdg.rect_obj.new_points
            rect_path = os.path.join(out_dir, 'rectangles')
            occ_temp = []
            for i, rect_ in enumerate(rect_pts):
                if not self.ctrl_wdg.rect_obj.deleted[i]:
                    if not os.path.exists(rect_path):
                        os.makedirs(rect_path)
                    occ_temp.append(self.ctrl_wdg.rect_obj.occurence_groups[i])


                    d = np.asarray(rect_)
                    np.savetxt(os.path.join(rect_path, 'rect_'+str(i)+'.csv'), d, delimiter=',')

            if len(occ_temp) > 0:
                np.save(os.path.join(rect_path, 'occ.npy'), np.vstack(occ_temp))

            ##### PLY Data for Quads

            quad_pts = self.ctrl_wdg.quad_obj.all_pts
            occ_temp = []
            quad_path = os.path.join(out_dir, 'quads')
            for i, quad_ in enumerate(quad_pts):
                if not self.ctrl_wdg.quad_obj.deleted[i]:
                    if not os.path.exists(quad_path):
                        os.makedirs(quad_path)
                    occ_temp.append(self.ctrl_wdg.quad_obj.occurence_groups[i])

                    d = np.asarray(quad_)
                    np.savetxt(os.path.join(quad_path, 'quad_' + str(i) + '.csv'), d, delimiter=',')

            if len(occ_temp) > 0:
                np.save(os.path.join(quad_path, 'occ.npy'), np.vstack(occ_temp))


            ##### PLY Data for Cylinders

            num_cyl = 0
            occ_temp = []
            new_base_centers = []
            new_base_vertices = []
            new_top_centers = []
            new_top_vertices = []
            for i, center in enumerate(self.ctrl_wdg.gl_viewer.obj.cylinder_obj.centers):
                if -1 not in center:
                    num_cyl += 1
                    occ_temp.append(self.ctrl_wdg.gl_viewer.obj.cylinder_obj.occurrence_groups[i])
                    new_base_centers.append(center)
                    new_base_vertices.append(self.ctrl_wdg.gl_viewer.obj.cylinder_obj.vertices_cylinder[i])
                    new_top_centers.append(self.ctrl_wdg.gl_viewer.obj.cylinder_obj.top_centers[i])
                    new_top_vertices.append(self.ctrl_wdg.gl_viewer.obj.cylinder_obj.top_vertices[i])

            if len(new_base_centers) > 0:
                center_cylinder_data = np.vstack(new_base_centers)
                base_cylinder_data = np.vstack(new_base_vertices)
                top_center_data = np.vstack(new_top_centers)
                top_cylinder_data = np.vstack(new_top_vertices)

                cyl_path = os.path.join(out_dir, 'cylinders')
                if not os.path.exists(cyl_path):
                    os.mkdir(cyl_path)

                np.savetxt(os.path.join(cyl_path, 'base_centers.csv'), center_cylinder_data, delimiter=',')
                np.savetxt(os.path.join(cyl_path, 'base_vertices.csv'), base_cylinder_data, delimiter=',')
                np.savetxt(os.path.join(cyl_path, 'top_centers.csv'), top_center_data, delimiter=',')
                np.savetxt(os.path.join(cyl_path, 'top_vertices.csv'), top_cylinder_data, delimiter=',')

                mat_occ = np.vstack(occ_temp)
                np.save(os.path.join(cyl_path, 'occ.npy'), mat_occ)


            ##### PLY Data for curved cylinder

            curve_data_list = []
            
            if len(self.ctrl_wdg.gl_viewer.obj.curve_obj.final_cylinder_bases) > 0:
                ccyl_path = os.path.join(out_dir, 'curved_cylinder')
                if not os.path.exists(ccyl_path):
                    os.makedirs(ccyl_path)
                
                for i, cylinder_bases in enumerate(self.ctrl_wdg.gl_viewer.obj.curve_obj.final_cylinder_bases):
                    print("Data for cylinder # "+str(i+1))
                    general_bases = []
                    base_centers = np.vstack(self.ctrl_wdg.gl_viewer.obj.curve_obj.final_base_centers[i])
                    for j, bases in enumerate(cylinder_bases):
                        general_bases.append(np.vstack(bases))
                        if j == len(cylinder_bases) - 1:
                            tops = np.vstack(self.ctrl_wdg.gl_viewer.obj.curve_obj.final_cylinder_tops[i][-1])
                            top_center = self.ctrl_wdg.gl_viewer.obj.curve_obj.final_top_centers[i][-1].reshape((1,3))
                            
                    num_bases = base_centers.shape[0]
                    print("Number of bases : "+str(num_bases))
                    general_cylinder = np.concatenate((base_centers, np.vstack(general_bases), tops, top_center))
                    print(general_cylinder.shape)
                    np.savetxt(os.path.join(ccyl_path, 'curved_cyl_'+str(i)+'.csv'), general_cylinder, delimiter=',')

            
            
            
    
        
    def save_directory(self, name_project):
        out_dir = os.path.join(name_project.split('.')[0], 'extracted_frames')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
            
            
        for i, p in enumerate(self.ctrl_wdg.mv_panel.movie_paths):
            aa = split_path(p)
            video_folder = aa.split('.')[0]
            video_folder_path = os.path.join(out_dir, video_folder)
            
            if len(self.ctrl_wdg.mv_panel.movie_caps[i].key_frames_regular) > 0:
                path_regular = os.path.join(video_folder_path , 'Regular')
                if not os.path.exists(path_regular):
                    os.makedirs(path_regular)
                    
                for j, img in enumerate(self.ctrl_wdg.mv_panel.movie_caps[i].key_frames_regular):
                    # img_path = os.path.join(path_regular, self.ctrl_wdg.mv_panel.movie_caps[i].key_frame_indices_regular[j] +'.png')
                    img_path = os.path.join(path_regular, str(j).zfill(6)+'.jpg')
                    cv2.imwrite(img_path, img)
                    
            if len(self.ctrl_wdg.mv_panel.movie_caps[i].key_frames_network) > 0:
                path_network = os.path.join(video_folder_path , 'Network')
                if not os.path.exists(path_network):
                    os.makedirs(path_network)
                for j, img in enumerate(self.ctrl_wdg.mv_panel.movie_caps[i].key_frames_network):
                    # img_path = os.path.join(path_network, self.ctrl_wdg.mv_panel.movie_caps[i].key_frame_indices_network[j] +'.png')
                    img_path = os.path.join(path_network, str(j).zfill(6)+'.jpg')
                    cv2.imwrite(img_path, img)
                    
                    
    def load_data(self, project_path):
        with open (project_path) as myfile:
            data=json.load(myfile)
            
        mv_paths = data["movies"]
        # print(mv_paths)
        op = data["platform"]
        mv_paths = adjust_op(mv_paths, op)
        h1_past = data["h1"]
        w1_past = data["w1"]
            
        feature_data_list = data["feature_dict"]
        
        a = os.path.join(project_path.split('.')[0], 'extracted_frames')
        movie_dirs = os.listdir(a)
        count = 0
        # self.ctrl_wdg.selected_thumbnail_index = -1
        
        for i,p in enumerate(mv_paths):
            self.ctrl_wdg.selected_thumbnail_index = -1
            movie_name = split_path(p)
            # print(self.ctrl_wdg.grid_layout)
            self.ctrl_wdg.mv_panel.add_movie(p)

            self.ctrl_wdg.mv_panel.selected_movie_idx = i
            v = self.ctrl_wdg.mv_panel.movie_caps[i]
            
                        
            for j,mv in enumerate(movie_dirs):
                if movie_name.split('.')[0] == mv:
                    movie_dirr = os.path.join(a, mv)
                    img_names_regular = sorted(glob.glob(movie_dirr+'/Regular/*'))
                    v.key_frames_regular = [cv2.imread(x) for x in img_names_regular]
                    v.init_features_regular(len(v.key_frames_regular))
                    
                    img_names_network = sorted(glob.glob(movie_dirr+'/Network/*'))
                    v.key_frames_network = [cv2.imread(x) for x in img_names_network]
                    v.init_features_network(len(v.key_frames_network))
           
            video_data = feature_data_list[i]
            self.ctrl_wdg.ui.cross_hair = True
           
            if len(v.key_frames_regular) > 0:
                self.ctrl_wdg.gl_viewer.util_.setPhoto(v.key_frames_regular[0])
                hide_regular = video_data["hide_regular"]
                x_locs = video_data["x_locs"]
                y_locs = video_data["y_locs"]
                # print(self.ctrl_wdg.gl_viewer.util_.w1, self.ctrl_wdg.gl_viewer.util_.h1)
                
                if int(data["selected_thumbnail"]) == -1:
                    w, h, diff_h, diff_w = 1, 1, 0, 0
                else:
                    w = self.ctrl_wdg.gl_viewer.util_.w2 - self.ctrl_wdg.gl_viewer.util_.w1
                    h = self.ctrl_wdg.gl_viewer.util_.h2 - self.ctrl_wdg.gl_viewer.util_.h1
                    diff_h = 0.75 * (self.ctrl_wdg.gl_viewer.util_.h1 - h1_past)
                    diff_w = 0.75 * (self.ctrl_wdg.gl_viewer.util_.w1 - w1_past)

                # print(diff_h)
                self.ctrl_wdg.kf_method = "Regular"
                for j, hr_list in enumerate(hide_regular):
                    if len(hr_list) > 0:
                        self.ctrl_wdg.selected_thumbnail_index = j
                        for k, hide in enumerate(hr_list):
                            if not hide:
                                self.ctrl_wdg.gl_viewer.obj.add_feature(int(diff_w + w*float(x_locs[j][k])), int(diff_h + h*float(y_locs[j][k])))
                                # self.ctrl_wdg.gl_viewer.obj.add_feature(int(x_locs[j][k]), int(y_locs[j][k]))
                            else:
                                self.ctrl_wdg.gl_viewer.obj.add_feature(int(diff_w + w*float(x_locs[j][k])), int(diff_h + h*float(y_locs[j][k])))
                                # self.ctrl_wdg.gl_viewer.obj.add_feature(int(x_locs[j][k]), int(y_locs[j][k]))
                                self.ctrl_wdg.gl_viewer.obj.feature_panel.selected_feature_idx = k
                                self.ctrl_wdg.gl_viewer.obj.delete_feature()                        




            if len(v.key_frames_network) > 0:
                self.ctrl_wdg.gl_viewer.util_.setPhoto(v.key_frames_network[0])
                hide_network = video_data["hide_network"]
                x_locs = video_data["x_locs_network"]
                y_locs = video_data["y_locs_network"]
                # print(self.ctrl_wdg.gl_viewer.util_.w1, self.ctrl_wdg.gl_viewer.util_.h1)
                
                if int(data["selected_thumbnail"]) == -1:
                    w, h, diff_h, diff_w = 1, 1, 0, 0
                else:
                    w = self.ctrl_wdg.gl_viewer.util_.w2 - self.ctrl_wdg.gl_viewer.util_.w1
                    h = self.ctrl_wdg.gl_viewer.util_.h2 - self.ctrl_wdg.gl_viewer.util_.h1
                    diff_h = 0.75 * (self.ctrl_wdg.gl_viewer.util_.h1 - h1_past)
                    diff_w = 0.75 * (self.ctrl_wdg.gl_viewer.util_.w1 - w1_past)
    
                # print(diff_h)
                self.ctrl_wdg.kf_method = "Network"
                for j, hr_list in enumerate(hide_network):
                    if len(hr_list) > 0:
                        self.ctrl_wdg.selected_thumbnail_index = j
                        for k, hide in enumerate(hr_list):
                            if not hide:
                                self.ctrl_wdg.gl_viewer.obj.add_feature(int(diff_w + w*float(x_locs[j][k])), int(diff_h + h*float(y_locs[j][k])))
                                # self.ctrl_wdg.gl_viewer.obj.add_feature(int(x_locs[j][k]), int(y_locs[j][k]))
                            else:
                                self.ctrl_wdg.gl_viewer.obj.add_feature(int(diff_w + w*float(x_locs[j][k])), int(diff_h + h*float(y_locs[j][k])))
                                # self.ctrl_wdg.gl_viewer.obj.add_feature(int(x_locs[j][k]), int(y_locs[j][k]))
                                self.ctrl_wdg.gl_viewer.obj.feature_panel.selected_feature_idx = k
                                self.ctrl_wdg.gl_viewer.obj.delete_feature()                        
                        
            self.ctrl_wdg.ui.cross_hair = False

                    
        self.ctrl_wdg.main_file.create_layout()

        self.ctrl_wdg.mv_panel.selected_movie_idx = int(data["selected_movie"])
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        self.ctrl_wdg.kf_method = data["selected_kf_method"]
        
        if data["bool_3D"]:
            
            ############### Load 3D data points ###############

            self.ctrl_wdg.gl_viewer.obj.img_indices = [int(x) for x in data["img_indices"]]
            
            # print(self.ctrl_wdg.gl_viewer.obj.img_indices)

            a = os.path.join(project_path.split('.')[0], '3D_data')
            ply_all = np.loadtxt(os.path.join(a, 'ply_all.csv'), delimiter=',').astype(float)
            ply = np.loadtxt(os.path.join(a, 'ply.csv'), delimiter=',').astype(float)
            cam_poses = np.loadtxt(os.path.join(a, 'cam_poses.csv'), delimiter=',').astype(float)
            
            self.ctrl_wdg.gl_viewer.obj.K = estimateKMatrix(v.width, v.height, 30, 23.7, 15.6)


            # self.ctrl_wdg.gl_viewer.obj.initialize_mats()
            self.ctrl_wdg.gl_viewer.obj.ply_pts.append(ply)
            self.ctrl_wdg.gl_viewer.obj.all_ply_pts.append(ply_all)
            self.ctrl_wdg.gl_viewer.obj.camera_poses.append(cam_poses)
            
            b = os.path.join(a, 'camera_parameters')
            ext_paths = sorted(glob.glob(b+'/*.csv'))
            # print(ext_paths)
            
            if len(ext_paths) > 0:
                for i, path in enumerate(ext_paths):
                    # print(path)
                    p = split_path(path)
                    idx = int(p.split('.')[0].split('_')[-1])
                    self.ctrl_wdg.gl_viewer.obj.img_indices.append(idx)
    
                    self.ctrl_wdg.gl_viewer.obj.camera_projection_mat.append((idx, np.loadtxt(path, delimiter=',').astype(float)))


            ############### Load Rectangles ###############
            if data["bool_rect"]:
                c = os.path.join(a, 'rectangles')
                ext_p = sorted(glob.glob(c+'/*.csv'))
                
                if len(ext_p) > 0:
                    occ_mat = np.load(os.path.join(c, 'occ.npy'))
                    # print(occ_mat)
                    
                    assert occ_mat.shape[0] == len(ext_p)

                    # Painting for Rectangle Tool
                    
                    for i, path in enumerate(ext_p):
                        occ_list = occ_mat[i, :]             
                        if (len(v.rect_groups_regular) > 0 or len(v.rect_groups_network) > 0) :
                            if self.ctrl_wdg.kf_method == "Regular":
                                for img_ind, fc_group in enumerate(v.rect_groups_regular):
                                    if img_ind in self.ctrl_wdg.gl_viewer.obj.img_indices:
                                        for j, fc in enumerate(v.rect_groups_regular[img_ind]):
                                            if j in occ_list:
                                                v.rect_groups_regular[img_ind][j] = self.ctrl_wdg.rect_obj.group_num

                            else:
                                for img_ind, fc_group in enumerate(v.rect_groups_network):
                                    if img_ind in self.ctrl_wdg.gl_viewer.obj.img_indices:
                                        for j, fc in enumerate(v.rect_groups_network[img_ind]):
                                            if j in occ_list:
                                                v.rect_groups_network[img_ind][j] = self.ctrl_wdg.rect_obj.group_num



                        q_arr = np.loadtxt(path, delimiter=',').astype(float)
                        self.ctrl_wdg.rect_obj.order.append(occ_mat[i,0])
                        self.ctrl_wdg.rect_obj.order.append(occ_mat[i,1])
                        self.ctrl_wdg.rect_obj.order.append(occ_mat[i,2])
                        self.ctrl_wdg.rect_obj.order.append(occ_mat[i,3])
                        self.ctrl_wdg.rect_obj.data_val.append(q_arr[0,:])
                        self.ctrl_wdg.rect_obj.data_val.append(q_arr[1,:])
                        self.ctrl_wdg.rect_obj.data_val.append(q_arr[2,:])
                        self.ctrl_wdg.rect_obj.data_val.append(q_arr[3,:])
                        self.ctrl_wdg.rect_obj.add_rectangle()

            ############### Paint Quadrilaterals ###############

            if data["bool_quad"]:
                c = os.path.join(a, 'quads')
                ext_p = sorted(glob.glob(c + '/*.csv'))

                if len(ext_p) > 0:
                    occ_mat = np.load(os.path.join(c, 'occ.npy'))
                    print(occ_mat.shape)
                    print(occ_mat)

                    assert occ_mat.shape[0] == len(ext_p)

                    for i, path in enumerate(ext_p):
                        occ_list = occ_mat[i, :]

                        if (len(v.quad_groups_regular) > 0 or len(v.quad_groups_network) > 0) :
                            if self.ctrl_wdg.kf_method == "Regular":
                                for img_ind, fc_group in enumerate(v.quad_groups_regular):
                                    if img_ind in self.ctrl_wdg.gl_viewer.obj.img_indices:
                                        for j, fc in enumerate(v.quad_groups_regular[img_ind]):
                                            if j in occ_list:
                                                v.quad_groups_regular[img_ind][j] = self.ctrl_wdg.quad_obj.group_num

                            else:
                                for img_ind, fc_group in enumerate(v.quad_groups_network):
                                    if img_ind in self.ctrl_wdg.gl_viewer.obj.img_indices:
                                        for j, fc in enumerate(v.quad_groups_network[img_ind]):
                                            if j in occ_list:
                                                v.quad_groups_network[img_ind][j] = self.ctrl_wdg.quad_obj.group_num

                        q_arr = np.loadtxt(path, delimiter=',').astype(float)
                        self.ctrl_wdg.quad_obj.order.append(occ_mat[i,0])
                        self.ctrl_wdg.quad_obj.order.append(occ_mat[i,1])
                        self.ctrl_wdg.quad_obj.order.append(occ_mat[i,2])
                        self.ctrl_wdg.quad_obj.order.append(occ_mat[i,3])
                        self.ctrl_wdg.quad_obj.data_val.append(q_arr[0,:])
                        self.ctrl_wdg.quad_obj.data_val.append(q_arr[1,:])
                        self.ctrl_wdg.quad_obj.data_val.append(q_arr[2,:])
                        self.ctrl_wdg.quad_obj.data_val.append(q_arr[3,:])
                        self.ctrl_wdg.quad_obj.add_quad()





            ############### Load Cylinders ###############

            sectorCount = self.ctrl_wdg.gl_viewer.obj.cylinder_obj.sectorCount


            if data["bool_cyl"]:
                c = os.path.join(a, 'cylinders')
                n_cyl = int(data["n_cyl"])

                occ_mat = np.load(os.path.join(c, 'occ.npy'))
                print(type(occ_mat))
                print(occ_mat.shape)
                print(occ_mat)

                base_center_data = np.loadtxt(os.path.join(c, 'base_centers.csv'), delimiter=',')
                base_vertices_data = np.loadtxt(os.path.join(c, 'base_vertices.csv'), delimiter=',')
                top_center_data = np.loadtxt(os.path.join(c, 'top_centers.csv'), delimiter=',')
                top_vertices_data = np.loadtxt(os.path.join(c, 'top_vertices.csv'), delimiter=',')

                if n_cyl == 1:
                    base_center_data = base_center_data.reshape((1, 3))
                    top_center_data = top_center_data.reshape((1, 3))

                assert n_cyl == base_center_data.shape[0]


                for i in range(n_cyl):

                    occ_list = occ_mat[i, :]
                    if (len(v.cylinder_groups_regular) > 0 or len(v.cylinder_groups_network) > 0):
                        if self.ctrl_wdg.kf_method == "Regular":
                            for img_ind, fc_group in enumerate(v.cylinder_groups_regular):
                                if img_ind in self.ctrl_wdg.gl_viewer.obj.img_indices:
                                    for j, fc in enumerate(v.cylinder_groups_regular[img_ind]):
                                        if j in occ_list:
                                            v.cylinder_groups_regular[img_ind][j] = self.ctrl_wdg.gl_viewer.obj.cylinder_obj.group_num

                        else:
                            for img_ind, fc_group in enumerate(v.cylinder_groups_network):
                                if img_ind in self.ctrl_wdg.gl_viewer.obj.img_indices:
                                    for j, fc in enumerate(v.cylinder_groups_network[img_ind]):
                                        if j in occ_list:
                                            v.cylinder_groups_network[img_ind][j] = self.ctrl_wdg.gl_viewer.obj.cylinder_obj.group_num


                    center = base_center_data[i, :]
                    bases = base_vertices_data[i*(sectorCount + 1) : i*(sectorCount + 1) + (sectorCount + 1), :]
                    top_c = top_center_data[i, :]
                    tops = top_vertices_data[i*(sectorCount + 1) : i*(sectorCount + 1) + (sectorCount + 1), :]

                    self.ctrl_wdg.gl_viewer.obj.cylinder_obj.order.append(occ_mat[i, 0])
                    self.ctrl_wdg.gl_viewer.obj.cylinder_obj.order.append(occ_mat[i, 1])
                    self.ctrl_wdg.gl_viewer.obj.cylinder_obj.order.append(occ_mat[i, 2])
                    self.ctrl_wdg.gl_viewer.obj.cylinder_obj.order.append(occ_mat[i, 3])

                    self.ctrl_wdg.gl_viewer.obj.cylinder_obj.refresh_cylinder_data(bases, tops, center, top_c)







            ############### Load Curved Cylinder ###############
            if data["bool_curved_cyl"]:
                c = os.path.join(a, 'curved_cylinder')
                ext_p = sorted(glob.glob(c+'/*.csv'))
                if len(ext_p) > 0:
                    n_cyl = data["n_curved"]
                    # print(n_cyl)

                    for i, path in enumerate(ext_p):
                        # print("Data for cylinder # "+str(i))
                        general_cyl = np.loadtxt(path, delimiter=',').astype(float)
                        base_centers = general_cyl[0:n_cyl, :]
                        bases = general_cyl[n_cyl : n_cyl + n_cyl*(sectorCount+1), :]
                        tops = general_cyl[ n_cyl + n_cyl*(sectorCount+1) :  n_cyl + n_cyl*(sectorCount+1) + sectorCount+1, :]
                        
                        top_center = general_cyl[general_cyl.shape[0] - 1, :]
                        # print(top_center)
                        
                        # print(tops.shape)
                        BC = []
                        for j in range(n_cyl):
                            # print(base_centers[j, :])
                            BC.append(base_centers[j, :])
                        self.ctrl_wdg.gl_viewer.obj.curve_obj.final_base_centers.append(BC)
                        
                        BC_all = []
                        for j in range(n_cyl):
                            bases_arr = bases[j*(sectorCount+1) : (j+1)*(sectorCount+1), :]
                            # print(bases_arr.shape)
                            BC = []
                            for k in range(bases_arr.shape[0]):
                                # print(bases_arr[k, :])
                                BC.append(bases_arr[k, :])
                            BC_all.append(BC)
                        self.ctrl_wdg.gl_viewer.obj.curve_obj.final_cylinder_bases.append(BC_all)
                        
                        TP = []
                        for k in range(tops.shape[0]):
                            TP.append(tops[k, :])
                            
                        self.ctrl_wdg.gl_viewer.obj.curve_obj.final_cylinder_tops.append([TP])
                        
                        self.ctrl_wdg.gl_viewer.obj.curve_obj.final_top_centers.append([top_center])


        self.ctrl_wdg.selected_thumbnail_index = int(data["selected_thumbnail"])
        self.ctrl_wdg.mv_panel.select_movie(self.ctrl_wdg.selected_thumbnail_index )
        self.ctrl_wdg.ui.implement_move_tool()
        self.ctrl_wdg.main_file.bLoad = True
        
        
        
            
