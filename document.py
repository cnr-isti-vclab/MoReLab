import os, cv2, platform, json, glob
import numpy as np
from util.util import split_path, adjust_op
from PyQt5.QtWidgets import *
from features import FeatureCrosshair





class Document(QWidget):
    def __init__(self, ctrl_wdg):
        super().__init__(ctrl_wdg)
        self.ctrl_wdg = ctrl_wdg
        
    def get_data(self):
        data_movies = []
        for  i,v in enumerate(self.ctrl_wdg.mv_panel.movie_caps):
            x_locs = []
            y_locs = []
            x_locs_n = []
            y_locs_n = []
            for fc_list in v.features_regular:
                a = []
                b = []
                for fc in fc_list:
                    a.append(str(fc.x_loc))
                    b.append(str(fc.y_loc))
                    
                x_locs.append(a)
                y_locs.append(b)
                
            
            for fc_list in v.features_network:
                a = []
                b = []
                for fc in fc_list:
                    a.append(str(fc.x_loc))
                    b.append(str(fc.y_loc))
                    
                x_locs_n.append(a)
                y_locs_n.append(b)
                
            movie_feature_data = {"hide_regular": v.hide_regular,
                                  "hide_network": v.hide_network,
                                  "x_locs" : x_locs,
                                  "y_locs" : y_locs,
                                  "x_locs_network" : x_locs_n,
                                  "y_locs_network" : y_locs_n
                                  }
            data_movies.append(movie_feature_data)
        
        # #### --------------------- Save 3D data --------------------------
            
        # ply_data_all = self.ctrl_wdg.gl_viewer.obj.all_ply_pts[-1]
        # ply_data = self.ctrl_wdg.gl_viewer.obj.ply_pts[-1]
        # camera_pose = self.ctrl_wdg.gl_viewer.obj.camera_poses[-1]
        # projections = self.ctrl_wdg.gl_viewer.obj.camera_projection_mat
        
        # str_ply_all = []
        # for i in range(ply_data_all.shape[0]):
        #     str_ply_all.append(str(round(ply_data_all[i,0], 5)))
        #     str_ply_all.append(str(round(ply_data_all[i,1], 5)))
        #     str_ply_all.append(str(round(ply_data_all[i,2], 5)))
            
        # str_ply = []
        # for i in range(ply_data.shape[0]):
        #     str_ply.append(str(round(ply_data[i,0], 5)))
        #     str_ply.append(str(round(ply_data[i,1], 5)))
        #     str_ply.append(str(round(ply_data[i,2], 5)))
        
        # str_cam = []
        # for i in range(camera_pose.shape[0]):
        #     str_cam.append(str(round(camera_pose[i,0], 5)))
        #     str_cam.append(str(round(camera_pose[i,1], 5)))
        #     str_cam.append(str(round(camera_pose[i,2], 5)))        
        
        # img_indices = []
        # cam_exts = []
        # for i in range(camera_pose.shape[0]):
        #     img_indices.append(str(projections[i][0]))
        #     mat = projections[i][1]
        #     print(mat.shape)
        #     cols = []
        #     for j in range(mat.shape[0]):
        #         cols.append(str(round(mat[j,0], 5)))
        #         cols.append(str(round(mat[j,1], 5)))
        #         cols.append(str(round(mat[j,2], 5)))
        #         cols.append(str(round(mat[j,3], 5)))
        #     cam_exts.append(cols)
            
        
            
        data = {
            "movies" : self.ctrl_wdg.mv_panel.movie_paths,
            "selected_movie" : self.ctrl_wdg.mv_panel.selected_movie_idx,
            "platform" : platform.system(),
            "selected_kf_method" : self.ctrl_wdg.kf_method,
            "selected_thumbnail": self.ctrl_wdg.selected_thumbnail_index,
            "feature_dict" : data_movies,
            # "all_ply" : str_ply_all,
            # "ply" : str_ply,
            # "cam_pose" : str_cam,
            # "projection_imgs" : img_indices,
            # "projection_mats" : cam_exts,
            }
        
        return data
        
        
        
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
                    img_path = os.path.join(path_regular, str(j).zfill(6)+'.jpeg')
                    cv2.imwrite(img_path, img)
                    
            if len(self.ctrl_wdg.mv_panel.movie_caps[i].key_frames_network) > 0:
                path_network = os.path.join(video_folder_path , 'Network')
                if not os.path.exists(path_network):
                    os.makedirs(path_network)
                for j, img in enumerate(self.ctrl_wdg.mv_panel.movie_caps[i].key_frames_network):
                    # img_path = os.path.join(path_network, self.ctrl_wdg.mv_panel.movie_caps[i].key_frame_indices_network[j] +'.png')
                    img_path = os.path.join(path_network, str(j).zfill(6)+'.jpeg')
                    cv2.imwrite(img_path, img)
                    
                    
    def load_data(self, project_path):
        with open (project_path) as myfile:
            data=json.load(myfile)
            
        mv_paths = data["movies"]
        # print(mv_paths)
        op = data["platform"]
        mv_paths = adjust_op(mv_paths, op)
            
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
    
                self.ctrl_wdg.kf_method = "Regular"
                for j, hr_list in enumerate(hide_regular):
                    if len(hr_list) > 0:
                        self.ctrl_wdg.selected_thumbnail_index = j
                        for k, hide in enumerate(hr_list):
                            if not hide:
                                # print(x_locs[j][k], y_locs[j][k])
                                self.ctrl_wdg.gl_viewer.obj.add_feature(int(x_locs[j][k]), int(y_locs[j][k]))
                            else:
                                self.ctrl_wdg.gl_viewer.obj.add_feature(int(x_locs[j][k]), int(y_locs[j][k]))
                                self.ctrl_wdg.gl_viewer.obj.feature_panel.selected_feature_idx = k
                                self.ctrl_wdg.gl_viewer.obj.delete_feature()                        

            
            hide_network = video_data["hide_network"]
            x_locs_network = video_data["x_locs_network"]
            y_locs_network = video_data["y_locs_network"]
 
            self.ctrl_wdg.kf_method = "Network"
            for j, hr_list in enumerate(hide_network):
                if len(hr_list) > 0:
                    self.ctrl_wdg.selected_thumbnail_index = j
                    for k, hide in enumerate(hr_list):
                        if not hide:
                            # print(x_locs[j][k], y_locs[j][k])
                            self.ctrl_wdg.gl_viewer.obj.add_feature(int(x_locs_network[j][k]), int(y_locs_network[j][k]))
                        else:
                            self.ctrl_wdg.gl_viewer.obj.add_feature(int(x_locs_network[j][k]), int(y_locs_network[j][k]))
                            self.ctrl_wdg.gl_viewer.obj.feature_panel.selected_feature_idx = k
                            self.ctrl_wdg.gl_viewer.obj.delete_feature()
                        
            self.ctrl_wdg.ui.cross_hair = False

                    
        self.ctrl_wdg.main_file.create_layout()

        self.ctrl_wdg.mv_panel.selected_movie_idx = int(data["selected_movie"])
        v = self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx]
        self.ctrl_wdg.kf_method = data["selected_kf_method"]
        self.ctrl_wdg.selected_thumbnail_index = int(data["selected_thumbnail"])
        self.ctrl_wdg.mv_panel.select_movie()
        self.ctrl_wdg.ui.implement_move_tool()
        self.ctrl_wdg.main_file.bLoad = True
        
        
        # # # # ===========================  Load 3D data  ===============================
        # all_ply = data["all_ply"]
        # ply = data["ply"]
        # cam_pos = data["cam_pose"]
        # proj_img = data["projection_imgs"]
        # proj_mat = data["projection_mats"]

        # all_ply_mat = []
        # ply_mat = []
        # cam_ = []
        # for i in range(0,len(all_ply),3):
        #     all_ply_mat.append([np.float(all_ply[i]), np.float(all_ply[i+1]), np.float(all_ply[i+2])])
            
        # for i in range(0,len(ply),3):
        #     ply_mat.append([np.float(ply[i]), np.float(ply[i+1]), np.float(ply[i+2])])
            
        # for i in range(0, len(cam_pos), 3):
        #     cam_.append([np.float(cam_pos[i]), np.float(cam_pos[i+1]), np.float(cam_pos[i+2])])

        # all_ply_mat = np.asarray(all_ply_mat).astype(float)
        # ply_mat = np.asarray(ply_mat).astype(float)
        # cam_ = np.asarray(cam_).astype(float)

        # self.ctrl_wdg.gl_viewer.obj.all_ply_pts.append(all_ply_mat)
        # self.ctrl_wdg.gl_viewer.obj.ply_pts.append(ply_mat)
        # self.ctrl_wdg.gl_viewer.obj.camera_poses.append(cam_)
        
        # for i, img_ind in enumerate(proj_img):
        #     mat = proj_mat[i]
        #     cam_ext = np.array([[np.float(mat[0]), np.float(mat[1]), np.float(mat[2]), np.float(mat[3])],
        #                         [np.float(mat[4]), np.float(mat[5]), np.float(mat[6]), np.float(mat[7])],
        #                         [np.float(mat[8]), np.float(mat[9]), np.float(mat[10]), np.float(mat[11])],
        #                         [np.float(mat[12]), np.float(mat[13]), np.float(mat[14]), np.float(mat[15])]]).astype(float)
        #     self.ctrl_wdg.gl_viewer.obj.camera_projection_mat.append((int(img_ind), cam_ext))



            
