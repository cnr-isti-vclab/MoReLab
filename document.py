import os, glob, json
import cv2, platform
import numpy as np
from util.video import Video
from util.util import split_path, adjust_op
from feature_crosshair import FeatureCrosshair

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Document():
    def __init__(self, ctrl_wdg):
        super().__init__()
        self.ctrl_wdg = ctrl_wdg
        
    def get_data(self):
        data_movies = []
        for  i,v in enumerate(self.ctrl_wdg.mv_panel.movie_caps):
            movie_feature_data = {"n_obj_regular" : [str(x) for x in v.n_objects_kf_regular],
                                  "n_obj_network" : [str(x) for x in v.n_objects_kf_network],
                                  "hide_regular": v.hide_regular,
                                  "hide_network": v.hide_network
                                  }
            data_movies.append(movie_feature_data)
            
        labels = []
        frames = []
        videos = []
        loccs = []
        for j,f in enumerate(self.ctrl_wdg.gl_viewer.obj.associated_frames):
            labels.append(str(self.ctrl_wdg.gl_viewer.obj.labels[j]))
            frames.append([str(x) for x in f])
            videos.append([str(x) for x in self.ctrl_wdg.gl_viewer.obj.associated_videos[j]])
            ab = []
            for k,e in enumerate(self.ctrl_wdg.gl_viewer.obj.locs[j]):
                a = [str(int(x)) for x in e]
                ab.append(a)
            loccs.append(ab)     
        
        data = {
            "movies" : self.ctrl_wdg.mv_panel.movie_paths,
            "selected_movie" : self.ctrl_wdg.mv_panel.selected_movie_path,
            "platform" : platform.system(),
            "selected_kf_method" : self.ctrl_wdg.kf_method,
            "cross_hair" : self.ctrl_wdg.gl_viewer.obj.cross_hair,
            "displayIndex": self.ctrl_wdg.selected_thumbnail_index,
            "labels" : labels,
            "frames" : frames,
            "videos" : videos,
            "locations" : loccs,
            "feature_dict" : data_movies,
            "selected_feature" : self.ctrl_wdg.gl_viewer.obj.selected_feature_index
            }
        return data



                    
    def load_data(self, project_path):
        with open (project_path) as myfile:
            data=json.load(myfile)
            
        mv_paths = data["movies"]
        # print(mv_paths)
        op = data["platform"]
        mv_paths = adjust_op(mv_paths, op)
        # print(mv_paths)
        self.ctrl_wdg.kf_method = data["selected_kf_method"]
        self.ctrl_wdg.selected_thumbnail_index = data["displayIndex"]
        self.ctrl_wdg.gl_viewer.obj.cross_hair = data["cross_hair"]
        
        for j,f in enumerate(data["frames"]):
            self.ctrl_wdg.gl_viewer.obj.labels.append(int(data["labels"][j]))
            self.ctrl_wdg.gl_viewer.obj.associated_frames.append([int(x) for x in f])
            self.ctrl_wdg.gl_viewer.obj.associated_videos.append([int(x) for x in data["videos"][j]])
            
            ab = []
            for k,e in enumerate(data["locations"][j]):
                a = [int(e[0]), int(e[1])]
                ab.append(a)
            self.ctrl_wdg.gl_viewer.obj.locs.append(ab)
        
        feature_data_list = data["feature_dict"]
        
        a = os.path.join(project_path.split('.')[0], 'extracted_frames')
        movie_dirs = os.listdir(a)
        count = 0
        
        for i,p in enumerate(mv_paths):
            movie_name = split_path(p)
            self.ctrl_wdg.mv_panel.add_movie(p)

            self.ctrl_wdg.mv_panel.selected_movie_idx = i
            v = self.ctrl_wdg.mv_panel.movie_caps[i]
            video_data = feature_data_list[i]            
            v.n_objects_kf_regular = [int(x) for x in video_data["n_obj_regular"]]
            
            v.n_objects_kf_network = [int(x) for x in video_data["n_obj_network"]]            
            
            v.hide_regular = video_data["hide_regular"]
            v.hide_network = video_data["hide_network"]
                
            for j,mv in enumerate(movie_dirs):
                if movie_name.split('.')[0] == mv:
                    movie_dirr = os.path.join(a, mv)
                    img_names_regular = sorted(glob.glob(movie_dirr+'/Regular/*'))
                    # print(len(img_names_regular))
                    v.key_frames_regular = [cv2.imread(x) for x in img_names_regular]
                    
                    img_names_network = sorted(glob.glob(movie_dirr+'/Network/*'))
                    v.key_frames_network = [cv2.imread(x) for x in img_names_network]          

            # print("Number : "+str(len(v.n_objects_kf_regular)))
            for j, val in enumerate(v.n_objects_kf_regular):
                v.features_regular.append([])
                v.quad_groups_regular.append([])
                v.cylinder_groups_regular.append([])
                if val > 0:
                    bool_list = v.hide_regular[j]
                    for k in range(val):
                        if bool_list[k]:
                            fc = FeatureCrosshair(self.ctrl_wdg.gl_viewer.obj.feature_pixmap, 0, 0, k+1, self.ctrl_wdg.gl_viewer.obj)
                            v.features_regular[j].append(fc)
                            v.quad_groups_regular[j].append(-1)
                        else:
                            loccc = self.ctrl_wdg.gl_viewer.obj.locs[k][self.ctrl_wdg.gl_viewer.obj.find_idx(k, j)]
                            fc = FeatureCrosshair(self.ctrl_wdg.gl_viewer.obj.feature_pixmap, loccc[0], loccc[1], k+1, self.ctrl_wdg.gl_viewer.obj)
                            v.features_regular[j].append(fc)
                            v.quad_groups_regular[j].append(-1)
                            v.cylinder_groups_regular[j].append(-1)


            for j, val in enumerate(v.n_objects_kf_network):
                v.features_network.append([])
                v.quad_groups_network.append([])
                v.cylinder_groups_network.append([])
                if val > 0:
                    bool_list = v.hide_network[j]
                    for k in range(val):
                        if bool_list[k]:
                            fc = FeatureCrosshair(self.ctrl_wdg.gl_viewer.obj.feature_pixmap, 0, 0, k+1, self.ctrl_wdg.gl_viewer.obj)
                            v.features_network[j].append(fc)
                        else:
                            loccc = self.ctrl_wdg.gl_viewer.obj.locs[k][self.ctrl_wdg.gl_viewer.obj.find_idx(k, j)]
                            fc = FeatureCrosshair(self.ctrl_wdg.gl_viewer.obj.feature_pixmap, loccc[0], loccc[1], k+1, self.ctrl_wdg.gl_viewer.obj)
                            v.features_network[j].append(fc)
                            v.quad_groups_network[j].append(-1)
                            v.cylinder_groups_network[j].append(-1)
                            
                            
        self.ctrl_wdg.mv_panel.selected_movie_path = adjust_op([data["selected_movie"]], op)[0]
        self.ctrl_wdg.mv_panel.selected_movie_idx = self.ctrl_wdg.mv_panel.movie_paths.index(self.ctrl_wdg.mv_panel.selected_movie_path)
        self.ctrl_wdg.mv_panel.movie_caps[self.ctrl_wdg.mv_panel.selected_movie_idx].selected_thumbnail_index = data["displayIndex"]
        self.ctrl_wdg.mv_panel.select_movie(self.ctrl_wdg.mv_panel.items[self.ctrl_wdg.mv_panel.selected_movie_idx])                                
        self.ctrl_wdg.gl_viewer.obj.selected_feature_index = data["selected_feature"]  





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
            
            
        
    # def adjust_points(self, arr):
        