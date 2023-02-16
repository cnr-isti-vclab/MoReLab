import os, cv2, platform, json, glob
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
            
            
        data = {
            "movies" : self.ctrl_wdg.mv_panel.movie_paths,
            "selected_movie" : self.ctrl_wdg.mv_panel.selected_movie_idx,
            "platform" : platform.system(),
            "selected_kf_method" : self.ctrl_wdg.kf_method,
            "selected_thumbnail": self.ctrl_wdg.selected_thumbnail_index,
            "feature_dict" : data_movies,
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
        
        for i,p in enumerate(mv_paths):
            movie_name = split_path(p)
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
        print()
        self.ctrl_wdg.kf_method = data["selected_kf_method"]
        self.ctrl_wdg.mv_panel.select_movie()
        self.ctrl_wdg.ui.implement_move_tool()
        self.ctrl_wdg.main_file.bLoad = True
        self.ctrl_wdg.selected_thumbnail_index = int(data["selected_thumbnail"])
        if self.ctrl_wdg.selected_thumbnail_index != -1:
            self.ctrl_wdg.displayThumbnail(self.ctrl_wdg.selected_thumbnail_index)




            
