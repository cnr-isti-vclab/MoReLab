import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from central_widget import Widget
import sys, os, json
from util.util import *
import pymeshlab

# # LOGGING
# import logging


class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)    # call the init for the parent class
        self.setWindowTitle('MoReLab')
        self.showMaximized()

        # self.log_filename = "info.log"
        # logging.basicConfig(level=logging.DEBUG, filemode='w', filename=self.log_filename, format = '%(asctime)s %(levelname)-8s %(message)s')
        # self.logfile = logging.getLogger("tool-logger")
        # self.logfile.info("MoReLab started ....")

        self.widget = Widget(self)
        self.create_statusbar()
        self.create_menu()
        self.create_toolbar()
        

        
    def create_layout(self):
        self.vboxLayout1 = QVBoxLayout()
        self.vboxLayout1.addWidget(self.widget.mv_panel, 3)
        self.vboxLayout1.addWidget(self.widget.ui.radiobutton1)
        self.vboxLayout1.addWidget(self.widget.ui.radiobutton2)
        self.vboxLayout1.addWidget(self.widget.ui.btn_kf)

        self.vboxLayout2 = QVBoxLayout()
        self.vboxLayout2.addWidget(self.widget.ui.scroll_area, 1)
        self.vboxLayout2.addWidget(self.widget.gl_viewer, 5)
        # self.vboxLayout2.addWidget(self.widget.gl_viewer.color_label, 1)

        self.vboxLayout3 = QVBoxLayout()
        self.vboxLayout3.addWidget(self.widget.gl_viewer.obj.feature_panel)
        self.vboxLayout3.addWidget(self.widget.gl_viewer.util_.dist_label)
        self.vboxLayout3.addWidget(self.widget.gl_viewer.obj.btn_sfm)

        self.hboxLayout = QHBoxLayout()

        self.hboxLayout.addLayout(self.vboxLayout1, 1)
        self.hboxLayout.addLayout(self.vboxLayout2, 2)
        self.hboxLayout.addLayout(self.vboxLayout3, 1)

        self.widget.setLayout(self.hboxLayout)
        self.setCentralWidget(self.widget)
        
        # self.logfile.info("Graphic Layout created ....")
        
        
        
    def implement_new_project(self):
        b = confirm_new()
        if b:
            self.setCentralWidget(QWidget())
            self.create_statusbar()
            self.removeToolBar(self.toolbar2)
            self.removeToolBar(self.toolbar)
            self.create_toolbar()
            # self.logfile.info("New Project created ....")
            
            
        
    
    def implement_open_movie(self):
        # file_types = "Video files (*.asf *.mp4 *.mov)"
        file_types = "Supported Video files (*.asf *.mp4 *.mov *.MP4 *.MOV *.ASF);; MP4 (*.mp4);; ASF (*.asf);; MOV(*.mov)"
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select movie file.',
            directory=os.getcwd(),
            filter=file_types
        )
        if response[0] != '':
            # movie_path = os.path.relpath(response[0], os.getcwd())
            movie_path = response[0]
            if movie_path in self.widget.mv_panel.movie_paths:
                movie_dialogue()
            else:
                movie_name = split_path(movie_path)
                display_msg = "Opened "+movie_name
                self.statusBar.showMessage(display_msg, 2000)
                v = self.widget.mv_panel.add_movie(movie_path)
                # self.bLoad = True
                # self.logfile.info("Opened a video named "+movie_name+" ....")
                if len(self.widget.mv_panel.movie_paths) == 1:
                    self.create_layout()
        # else:
        #     self.logfile.info("Video not opened ....")
                        
                                     

    def save_as_project(self):
        file_types = "json (*.json)"
        save_as_response = QFileDialog.getSaveFileName(
            parent=self,
            caption='Save as.',
            directory=os.getcwd(),
            filter=file_types
        )
        if save_as_response[0] != '':
            self.implement_save(save_as_response[0])  
        # else:
        #     self.logfile.info("Project not saved as ....")


    def save_project(self):
        if self.project_name_label.text() == 'untitled.json':
            file_types = "json (*.json)"
            self.save_response = QFileDialog.getSaveFileName(
                parent=self,
                caption='Save project.',
                directory=os.getcwd(),
                filter=file_types
            )
        if self.save_response[0] != '':
            # name_project = os.path.relpath(self.save_response[0], os.getcwd())
            name_project = self.save_response[0]
            disp_name_project = name_project.split('/')[-1]
            self.project_name_label.setText(disp_name_project)
            self.implement_save(self.save_response[0])
        # else:
        #     self.logfile.info("Project not saved ....")


    def implement_save(self, p):
        # self.logfile.info("Saving the project ....")
        w = Dialog()
        w.show()
        
        # name_project = os.path.relpath(p, os.getcwd())
        name_project = p
        disp_name_project = name_project.split('/')[-1]

        display_msg = "Saving "+disp_name_project
        self.statusBar.showMessage(display_msg, 2000)
        self.widget.doc.save_directory(name_project)
        self.widget.doc.save_3D(name_project)


        data = self.widget.doc.get_data()
        # print(data)
        json_object = json.dumps(data, indent=4)
        if name_project.split('.')[-1] != 'json':
            name_project = name_project+'.json'
        with open(name_project, "w") as outfile:
            outfile.write(json_object)
            
            
        w.done(0)
        # self.logfile.info("project named "+name_project+" has been saved ....")
        
        save_dialogue()
        
        
    def implement_open_folder(self):
        # self.logfile.info("Opening the folder ....")
        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        supported_image_types = ('.png', 'jpg', 'jpeg', '.PNG', '.JPG', '.JPEG')

        if folderpath != '':
            file_paths = []
            for f in os.listdir(folderpath):
                if f.endswith(supported_image_types):
                    if os.path.isfile(folderpath + '/' + f):
                        file_paths.append(folderpath + '/' + f)

            if len(file_paths) > 0:
                num_frames = len(file_paths)
                img_0 = cv2.imread(file_paths[0])
                (h, w, c) = img_0.shape
                v = self.widget.mv_panel.add_movie(folderpath, fps=30, n_frames=num_frames, duration=num_frames/30, width=w, height=h)

                v.key_frames_regular = [cv2.imread(x) for x in file_paths]
                v.init_features_regular(len(v.key_frames_regular))
                v.init_3D_regular(len(v.key_frames_regular))
                self.widget.kf_method = "Regular"
                # self.logfile.info("Opened a folder named "+folderpath+" containing "+str(len(file_paths))+" images ....")

                if len(self.widget.mv_panel.movie_paths) == 1:
                    self.create_layout()
                    
                self.widget.populate_scrollbar()
                

    def create_menu(self):
        # menuBar = self.ctrl_wdg.main_file.menuBar()
        menuBar = QMenuBar(self)
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        # menuBar.addMenu("&File")

        # self.logfile.info("Creating menu bar ....")
        self.new_pr = QAction(QIcon("./icons/new_project.png"), "&New", self)
        fileMenu.addAction(self.new_pr)
        self.new_pr.triggered.connect(self.implement_new_project)
        self.new_pr.setShortcut("ctrl+n")


        self.open_pr = QAction(QIcon("./icons/open_project.png"), "&Open", self)
        fileMenu.addAction(self.open_pr)
        self.open_pr.triggered.connect(self.open_project)
        self.open_pr.setShortcut("ctrl+o")
        
        
        self.open_mov = QAction(QIcon("./icons/open_movie.png"), "&Import Movie", self)
        fileMenu.addAction(self.open_mov)
        self.open_mov.triggered.connect(self.implement_open_movie)
        self.open_mov.setShortcut("ctrl+shift+o")
        

        self.open_fold = QAction(QIcon("./icons/open-folder.png"), "&Import Folder", self)
        fileMenu.addAction(self.open_fold)
        self.open_fold.triggered.connect(self.implement_open_folder)
        self.open_fold.setShortcut("ctrl+f")

        
        self.save_pr = QAction(QIcon("./icons/save_project.png"), "&Save", self)
        fileMenu.addAction(self.save_pr)
        self.save_pr.triggered.connect(self.save_project)
        self.save_pr.setShortcut("ctrl+s")

        
        self.save_as = QAction(QIcon("./icons/save_as.png"), "&Save as", self)
        fileMenu.addAction(self.save_as)
        self.save_as.triggered.connect(self.save_as_project)
        self.save_as.setShortcut("ctrl+shift+s")
        
        
        self.exp_ply = QAction(QIcon("./icons/3d_printer.png"), "&Export 3D data", self)
        fileMenu.addAction(self.exp_ply)
        self.exp_ply.triggered.connect(self.export_ply_data)
        self.exp_ply.setShortcut("ctrl+e")
        
        
        self.exit_pr = QAction(QIcon("./icons/exit_project.png"), "&Exit", self)
        fileMenu.addAction(self.exit_pr)
        self.exit_pr.triggered.connect(self.implement_exit_project)
        self.exit_pr.setShortcut("ctrl+q")
        
        self.setMenuBar(menuBar)
            
            
    def open_project(self):
        file_types = "json (*.json)"
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select project.',
            directory=os.getcwd(),
            filter=file_types
        )
        if response[0] != '':
            
            w = Dialog()
            w.show()
            # self.logfile.info("Opening a project named "+response[0]+" ....")
            self.save_response = response
            self.widget = Widget(self)
            self.setCentralWidget(QWidget())
            self.create_statusbar()
            self.removeToolBar(self.toolbar2)
            self.removeToolBar(self.toolbar)
            self.create_toolbar()
            

            project_path = response[0]

            name_project = os.path.relpath(project_path, os.getcwd())
            disp_name_project = split_path(name_project)
            self.project_name_label.setText(disp_name_project)

            self.widget.doc.load_data(project_path)
            
            # self.logfile.info("Project has been loaded successfully ....")
            w.done(0)
            
        
    def implement_exit_project(self):
        if confirm_exit():
            # self.logfile.info("Project has been terminated ....")
            self.close()


    def create_toolbar(self):
        # self.logfile.info("Creating toolbar ....")
        self.toolbar = QToolBar("&ToolBar", self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.toolbar.addWidget(self.widget.ui.np_tool)
        self.toolbar.addWidget(self.widget.ui.op_tool)
        self.toolbar.addWidget(self.widget.ui.om_tool)
        self.toolbar.addWidget(self.widget.ui.of_tool)
        self.toolbar.addWidget(self.widget.ui.sp_tool)
        self.toolbar.addWidget(self.widget.ui.sp_as_tool)
        self.toolbar.addWidget(self.widget.ui.ep_tool)
        self.toolbar.addWidget(self.widget.ui.mv_tool)
        self.toolbar.addWidget(self.widget.ui.ft_tool)
        self.toolbar.addWidget(self.widget.ui.ft_plus_tool)
        self.toolbar.addWidget(self.widget.ui.selection_tool)
        self.toolbar.addWidget(self.widget.ui.rect_tool)
        self.toolbar.addWidget(self.widget.ui.quad_tool)
        self.toolbar.addWidget(self.widget.ui.cyl_tool)
        self.toolbar.addWidget(self.widget.ui.new_cyl_tool)
        self.toolbar.addWidget(self.widget.ui.bz_tool)
        self.toolbar.addWidget(self.widget.ui.pick_tool)
        self.toolbar.addWidget(self.widget.ui.measure_tool)
        self.toolbar.addWidget(self.widget.ui.anchor_tool)
        self.toolbar.addWidget(self.widget.ui.epipolar_tool)
        self.addToolBarBreak(Qt.TopToolBarArea)

        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        right_spacer = QWidget()
        right_spacer.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        # self.project_name_label = QLabel(os.path.join(os.getcwd(), "Untitled.json"))
        self.project_name_label = QLabel("untitled.json")

        self.toolbar2 = QToolBar()
        self.addToolBar(Qt.TopToolBarArea, self.toolbar2)
        self.toolbar2.addWidget(left_spacer)
        self.toolbar2.addWidget(self.project_name_label)
        self.toolbar2.addWidget(right_spacer)


    def export_ply_data(self):
        if len(self.widget.gl_viewer.obj.all_ply_pts) > 0:
            
            bundle_adjustment_ply_data = self.widget.gl_viewer.obj.all_ply_pts[-1]
            col_bundle = np.zeros(bundle_adjustment_ply_data.shape).astype(np.uint8)
            col_bundle[:, 1] = 255

            cam_data = self.widget.gl_viewer.obj.camera_poses[-1]
            col_cam = np.ones(cam_data.shape).astype(np.uint8)*255

            write_vertices_ply('vertex_data.ply', np.concatenate((bundle_adjustment_ply_data, cam_data), axis=0), np.concatenate((col_bundle, col_cam), axis=0))
            # self.logfile.info("------------------ Exported vertex data ---------------------  ....")
            ###### PLY Date for General curved cylinder
            curve_data_list = []
            num_bases_list = []
            sectorCount = self.widget.gl_viewer.obj.cylinder_obj.sectorCount
            
            if len(self.widget.gl_viewer.obj.curve_obj.final_cylinder_bases) > 0:
                for i, cylinder_bases in enumerate(self.widget.gl_viewer.obj.curve_obj.final_cylinder_bases):
                    if not self.widget.gl_viewer.obj.curve_obj.deleted[i]:
                        general_bases = []
                        base_centers = np.vstack(self.widget.gl_viewer.obj.curve_obj.final_base_centers[i])
                        for j, bases in enumerate(cylinder_bases):
                            general_bases.append(np.vstack(bases))

                        tops = np.vstack(self.widget.gl_viewer.obj.curve_obj.final_cylinder_tops[i][-1])
                        top_center = self.widget.gl_viewer.obj.curve_obj.final_top_centers[i][-1].reshape((1,3))

                        num_bases_list.append(base_centers.shape[0])
                        general_cylinder = np.concatenate((base_centers, np.vstack(general_bases), tops, top_center))
                        curve_data_list.append(general_cylinder)

            # print(num_bases_list)
            if len(curve_data_list) > 0:
                curve_data = np.vstack(curve_data_list)


            ##### PLY Date for rect
    
            rect_pts = self.widget.rect_obj.new_points
            rect_data_list = []
            for i, rect_ in enumerate(rect_pts):
                if not self.widget.rect_obj.deleted[i]:
                    rect_data_list.append(rect_)
            if len(rect_data_list) > 0:
                rect_data = np.vstack(rect_data_list)

            ##### PLY Date for Quadrilaterals

            quad_data_list = []
            quad_idx_list = []
            for i, quad_ in enumerate(self.widget.quad_obj.all_pts):
                if not self.widget.quad_obj.deleted[i]:
                    quad_idx_list.append(i)
                    quad_data_list.append(quad_)

            ##### PLY Date for Cylinders
            num_cyl = 0
            face_verts = []
            new_base_centers = []
            new_base_vertices = []
            new_top_centers = []
            new_top_vertices = []
            for i, center in enumerate(self.widget.gl_viewer.obj.cylinder_obj.centers):
                if -1 not in center:
                    num_cyl += 1
                    new_base_centers.append(center)
                    new_base_vertices.append(self.widget.gl_viewer.obj.cylinder_obj.vertices_cylinder[i])
                    new_top_centers.append(self.widget.gl_viewer.obj.cylinder_obj.top_centers[i])
                    new_top_vertices.append(self.widget.gl_viewer.obj.cylinder_obj.top_vertices[i])

            
            if len(new_base_centers) > 0:
                center_cylinder_data = np.vstack(new_base_centers)
                base_cylinder_data = np.vstack(new_base_vertices)
                top_center_data = np.vstack(new_top_centers)
                top_cylinder_data = np.vstack(new_top_vertices)
                cylinder_data = np.concatenate((center_cylinder_data, base_cylinder_data, top_center_data, top_cylinder_data))
                
                
            
                
            if len(rect_data_list) > 0 and len(new_base_centers) > 0 and len(curve_data_list) > 0 and len(quad_data_list) > 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, rect_data, cylinder_data, np.vstack(quad_data_list), curve_data))
            elif len(rect_data_list) == 0 and len(new_base_centers) > 0 and len(curve_data_list) > 0 and len(quad_data_list) > 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, cylinder_data, np.vstack(quad_data_list), curve_data))
            elif len(rect_data_list) > 0 and len(new_base_centers) == 0 and len(curve_data_list) > 0 and len(quad_data_list) > 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, rect_data, np.vstack(quad_data_list), curve_data))
            elif len(rect_data_list) == 0 and len(new_base_centers) == 0 and len(curve_data_list) > 0 and len(quad_data_list) > 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, np.vstack(quad_data_list), curve_data))
            elif len(rect_data_list) > 0 and len(new_base_centers) > 0 and len(curve_data_list) == 0 and len(quad_data_list) > 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, rect_data, cylinder_data, np.vstack(quad_data_list)))
            elif len(rect_data_list) == 0 and len(new_base_centers) > 0 and len(curve_data_list) == 0 and len(quad_data_list) > 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, cylinder_data, np.vstack(quad_data_list)))
            elif len(rect_data_list) > 0 and len(new_base_centers) == 0 and len(curve_data_list) == 0 and len(quad_data_list) > 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, rect_data, np.vstack(quad_data_list)))
            elif len(rect_data_list) == 0 and len(new_base_centers) == 0 and len(curve_data_list) == 0 and len(quad_data_list) > 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, np.vstack(quad_data_list)))
            elif len(rect_data_list) > 0 and len(new_base_centers) > 0 and len(curve_data_list) > 0 and len(quad_data_list) == 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, rect_data, cylinder_data, curve_data))
            elif len(rect_data_list) == 0 and len(new_base_centers) > 0 and len(curve_data_list) > 0 and len(quad_data_list) == 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, cylinder_data, curve_data))
            elif len(rect_data_list) > 0 and len(new_base_centers) == 0 and len(curve_data_list) > 0 and len(quad_data_list) == 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, rect_data, curve_data))
            elif len(rect_data_list) == 0 and len(new_base_centers) == 0 and len(curve_data_list) > 0 and len(quad_data_list) == 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, curve_data))
            elif len(rect_data_list) > 0 and len(new_base_centers) > 0 and len(curve_data_list) == 0 and len(quad_data_list) == 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, rect_data, cylinder_data))
            elif len(rect_data_list) == 0 and len(new_base_centers) > 0 and len(curve_data_list) == 0 and len(quad_data_list) == 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, cylinder_data))
            elif len(rect_data_list) > 0 and len(new_base_centers) == 0 and len(curve_data_list) == 0 and len(quad_data_list) == 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, rect_data))
            else:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data))
            
            ##### print(ply_data_all.shape)
            # write_vertices_ply('vertex_data.ply', ply_data_all) 
            
            # Face data for rects
            face_data = np.zeros(shape=(2*len(rect_data_list), 3), dtype=int)
            for i in range(0,face_data.shape[0], 2):
                face_data[i,0] = bundle_adjustment_ply_data.shape[0] + cam_data.shape[0] + 2*i
                # print(face_data[i,0])
                face_data[i,1] = face_data[i,0] + 3
                face_data[i,2] = face_data[i,0] + 1
                
                face_data[i+1,0] = face_data[i,0] + 2
                face_data[i+1,1] = face_data[i,0] + 1
                face_data[i+1,2] = face_data[i,0] + 3

            
            # Face data for cylinders
            start = bundle_adjustment_ply_data.shape[0] + cam_data.shape[0] + 4*len(rect_data_list)
            # print("Start : "+str(start))
            sectorCount = self.widget.gl_viewer.obj.cylinder_obj.sectorCount
            face_data_cyl = np.zeros(shape=(4*sectorCount*num_cyl, 3), dtype=int)
            for i in range(num_cyl): # Loop through cylinders
                # Base
                for j in range(sectorCount):
                    face_data_cyl[sectorCount*4*i+j, 0] = start + i
                    face_data_cyl[sectorCount*4*i+j, 1] = start + i + num_cyl + j + sectorCount*i
                    face_data_cyl[sectorCount*4*i+j, 2] = start + i + num_cyl + j + sectorCount*i + 1
                    
                # Top    
                for j in range(sectorCount):
                    face_data_cyl[sectorCount*4*i+sectorCount+j, 0] = start + i + num_cyl + (sectorCount + 1)*num_cyl
                    face_data_cyl[sectorCount*4*i+sectorCount+j, 1] = start + i + num_cyl + (sectorCount + 1)*num_cyl + num_cyl + j + sectorCount*i + 1 
                    face_data_cyl[sectorCount*4*i+sectorCount+j, 2] = start + i + num_cyl + (sectorCount + 1)*num_cyl + num_cyl + j + sectorCount*i 
                
                # Strips
                for j in range(sectorCount):
                    face_data_cyl[sectorCount*4*i+2*sectorCount+j, 0] = start + num_cyl + (sectorCount + 1)*i + j
                    face_data_cyl[sectorCount*4*i+2*sectorCount+j, 1] = start + 2*num_cyl + (sectorCount + 1)*num_cyl + (sectorCount+1)*i + j 
                    
                    face_data_cyl[sectorCount*4*i+2*sectorCount+j, 2] = start + num_cyl + (sectorCount + 1)*i + j + 1
                    
                for j in range(sectorCount):
                    face_data_cyl[sectorCount*4*i+3*sectorCount+j, 0] = start + (sectorCount+1)*i + num_cyl + j + 1
                    face_data_cyl[sectorCount*4*i+3*sectorCount+j, 1] = start + i + 2*num_cyl + (sectorCount + 1)*num_cyl + (sectorCount)*i + j 
                    face_data_cyl[sectorCount*4*i+3*sectorCount+j, 2] = start + i + 2*num_cyl + (sectorCount + 1)*num_cyl + (sectorCount)*i + j + 1


            # Face data for Point quadors
            face_data_quad = np.zeros(shape=(2*len(quad_data_list), 3), dtype=int)
            for i, idd in enumerate(quad_idx_list):
                idx_list = self.widget.quad_obj.occurence_groups[idd]
                # print(idx_list)
                face_data_quad[2*i,0] = idx_list[0]
                # print(face_data[i,0])
                face_data_quad[2*i,1] = idx_list[3]
                face_data_quad[2*i,2] = idx_list[1]
                
                face_data_quad[2*i+1,0] = idx_list[2]
                face_data_quad[2*i+1,1] = idx_list[1]
                face_data_quad[2*i+1,2] = idx_list[3]


            ###### Face data for curved cylinder
            total_curve_size = 0
            for num in num_bases_list:
                total_curve_size = total_curve_size + 2*sectorCount*(num+1)
            face_data_general = np.zeros(shape=(total_curve_size , 3), dtype=int)

            if len(curve_data_list) > 0:
                start = bundle_adjustment_ply_data.shape[0] + cam_data.shape[0] + 4*len(rect_data_list) + len(new_base_centers) * (2*(sectorCount+1) + 2) + 4*len(quad_data_list)
                # print("Start : "+str(start))
                if len(curve_data_list) > 0:
                    start_next_idx = 0
                    for k in range(len(curve_data_list)):
                        num_cyl = num_bases_list[k]

                        ###### Bases
                        for j in range(sectorCount):
                            face_data_general[j + start_next_idx, 0] = start
                            face_data_general[j + start_next_idx, 1] = start + num_cyl + j
                            face_data_general[j + start_next_idx, 2] = start + num_cyl + j + 1

                        for i in range(num_cyl - 1):
                            ####### Strips
                            for j in range(sectorCount):
                                if j < 0.75*sectorCount - 1:
                                    face_data_general[sectorCount*2*i + sectorCount+j + start_next_idx, 0] = start + num_cyl + j + (sectorCount+1)*i
                                    face_data_general[sectorCount*2*i + sectorCount+j + start_next_idx, 1] = start + num_cyl + sectorCount + j + 0.25*sectorCount + 2 + (sectorCount+1)*i
                                    face_data_general[sectorCount*2*i + sectorCount+j + start_next_idx, 2] = start + num_cyl + j + 1 + (sectorCount+1)*i
                                else:
                                    face_data_general[sectorCount*2*i + sectorCount+j + start_next_idx, 0] = start + num_cyl + j + (sectorCount+1)*i
                                    face_data_general[sectorCount*2*i + sectorCount+j + start_next_idx, 1] = start + num_cyl + sectorCount + 1 + j - (0.75*sectorCount -1) + (sectorCount+1)*i
                                    face_data_general[sectorCount*2*i + sectorCount+j + start_next_idx, 2] = start + num_cyl + j + 1 + (sectorCount+1)*i
                                
                            for j in range(sectorCount):
                                if j < 0.75*sectorCount - 1:
                                    face_data_general[sectorCount*2*i + 2*sectorCount+j + start_next_idx, 0] = start + num_cyl + j + (sectorCount+1)*i + 1
                                    face_data_general[sectorCount*2*i + 2*sectorCount+j + start_next_idx, 2] = start + num_cyl + sectorCount + j + 0.25*sectorCount + 3 + (sectorCount+1)*i
                                    face_data_general[sectorCount*2*i + 2*sectorCount+j + start_next_idx, 1] = start + num_cyl + sectorCount + j + 0.25*sectorCount + 2 + (sectorCount+1)*i
                                else:
                                    face_data_general[sectorCount*2*i + 2*sectorCount+j + start_next_idx, 0] = start + num_cyl + j + 1 + (sectorCount+1)*i
                                    face_data_general[sectorCount*2*i + 2*sectorCount+j + start_next_idx, 2] = start + num_cyl + sectorCount + 1 + j - ( 0.75*sectorCount - 2) + (sectorCount+1)*i
                                    face_data_general[sectorCount*2*i + 2*sectorCount+j + start_next_idx, 1] = start + num_cyl + sectorCount + 1 + j -  0.75*sectorCount + 1 + (sectorCount+1)*i

                        ###### Last two strips and Top
                        i = num_cyl - 1
                        start_idx = 2*sectorCount*(num_cyl-1) + sectorCount
                        ###### Strips
                        for j in range(sectorCount):
                            face_data_general[start_idx + j + start_next_idx, 0] = start + num_cyl + j + (sectorCount+1)*i
                            face_data_general[start_idx + j + start_next_idx, 1] = start + num_cyl + sectorCount + j + 1 + (sectorCount+1)*i
                            face_data_general[start_idx + j + start_next_idx, 2] = start + num_cyl + j + 1 + (sectorCount+1)*i

                        for j in range(sectorCount):
                            face_data_general[start_idx + sectorCount + j + start_next_idx, 0] = start + num_cyl + j + (sectorCount+1)*i + 1
                            face_data_general[start_idx + sectorCount + j + start_next_idx, 1] = start + num_cyl + sectorCount + j + 1 + (sectorCount+1)*i
                            face_data_general[start_idx + sectorCount + j + start_next_idx, 2] = start + num_cyl + sectorCount + j + 1 + (sectorCount+1)*i + 1


                        ##### Final Top
                        for j in range(sectorCount):
                            face_data_general[start_idx + 2*sectorCount + j + start_next_idx, 0] = start + curve_data_list[k].shape[0] - 1
                            face_data_general[start_idx + 2*sectorCount + j + start_next_idx, 1] = start + num_cyl*(sectorCount + 1 + 1) + j + 1
                            face_data_general[start_idx + 2*sectorCount + j + start_next_idx, 2] = start + num_cyl*(sectorCount + 1 + 1) + j
                
                        start = start + curve_data_list[k].shape[0]
                        start_next_idx = start_next_idx + 2*sectorCount*(num_cyl + 1)
         
            all_faces = np.concatenate((face_data, face_data_cyl, face_data_quad, face_data_general))

            # for i in range(all_faces.shape[0]):
            #     print(all_faces[i, :])
            
            if all_faces.shape[0] > 0:
                # write_faces_ply('face_data.ply', ply_data_all, all_faces)
                                # create a new Mesh with the two arrays
                m = pymeshlab.Mesh(ply_data_all, all_faces)

                # create a new MeshSet
                ms = pymeshlab.MeshSet()
                
                # add the mesh to the MeshSet
                ms.add_mesh(m, "cube_mesh")
                
                # save the current mesh
                ms.save_current_mesh("mesh.ply")
                # self.logfile.info("Exported mesh data  ....")
                export_ply_dialogue()
            else:
                export_ply_dialogue()

        else:
            exportPLY_dialogue()

        
    def create_statusbar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)       


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
