from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os
import sip
import json
import glob
import cv2
from central_widget import Widget
from util.util import movie_dialogue, split_path, empty_gui, adjust_op, confirm_exit, write_faces_ply, write_vertices_ply
from GL_widget_viewer import GL_Widget

from util.video import Video
from tools import Tools
import numpy as np


class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)    # call the init for the parent class
        # super(QMainWindow, self).__init__()
        self.setWindowTitle('MoReLab')
        self.showMaximized()
        self.widget = Widget()

        self.save_response = ''

        self.create_menu()
        self.create_statusbar()
        self.create_toolbar()

    def create_layout(self):
        self.vboxLayout3 = QVBoxLayout()
        self.vboxLayout3.addWidget(self.widget.mv_panel, 3)
        # self.vboxLayout3.addWidget(self.widget.scale_up_btn)
        # self.vboxLayout3.addWidget(self.widget.scale_down_btn)
        # self.vboxLayout3.addWidget(self.widget.scale_up_binormal_btn)
        # self.vboxLayout3.addWidget(self.widget.scale_down_binormal_btn)
        self.vboxLayout3.addWidget(self.widget.btn_kf)

        self.vboxLayout2 = QVBoxLayout()
        self.vboxLayout2.addWidget(self.widget.scroll_area, 1)
        self.vboxLayout2.addWidget(self.widget.gl_viewer, 5)
        # self.vboxLayout2.addWidget(self.widget.gl_viewer.color_label, 1)

        self.vert1 = QVBoxLayout()
        self.vert1.addWidget(self.widget.gl_viewer.obj.wdg_tree)
        self.vert1.addWidget(self.widget.gl_viewer.obj.cam_btn)

        self.hboxLayout = QHBoxLayout()

        self.hboxLayout.addLayout(self.vboxLayout3, 1)
        self.hboxLayout.addLayout(self.vboxLayout2, 2)
        self.hboxLayout.addLayout(self.vert1, 1)

        self.widget.setLayout(self.hboxLayout)
        self.setCentralWidget(self.widget)

    def create_toolbar(self):
        self.toolbar = QToolBar("&ToolBar", self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        self.widget.gl_viewer.obj.np_tool.clicked.connect(self.new_project)
        self.widget.gl_viewer.obj.op_tool.clicked.connect(self.open_project)
        self.widget.gl_viewer.obj.om_tool.clicked.connect(self.open_movie)
        self.widget.gl_viewer.obj.sp_tool.clicked.connect(self.save_project)
        self.widget.gl_viewer.obj.sp_as_tool.clicked.connect(self.save_as_project)
        self.widget.gl_viewer.obj.ep_tool.clicked.connect(self.exit_project)

        self.toolbar.addWidget(self.widget.gl_viewer.obj.np_tool)
        self.toolbar.addWidget(self.widget.gl_viewer.obj.op_tool)
        self.toolbar.addWidget(self.widget.gl_viewer.obj.om_tool)
        self.toolbar.addWidget(self.widget.gl_viewer.obj.sp_tool)
        self.toolbar.addWidget(self.widget.gl_viewer.obj.sp_as_tool)
        self.toolbar.addWidget(self.widget.gl_viewer.obj.ep_tool)
        self.toolbar.addWidget(self.widget.gl_viewer.obj.mv_tool)
        self.toolbar.addWidget(self.widget.gl_viewer.obj.ft_tool)
        self.toolbar.addWidget(self.widget.gl_viewer.obj.qd_tool)
        self.toolbar.addWidget(self.widget.gl_viewer.obj.meas_tool)
        self.toolbar.addWidget(self.widget.gl_viewer.obj.cylinder_tool)
        self.toolbar.addWidget(self.widget.gl_viewer.obj.picking_tool)
        self.toolbar.addWidget(self.widget.gl_viewer.obj.new_cyl_tool)
        self.toolbar.addWidget(self.widget.gl_viewer.obj.bezier_tool)

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

    def create_menu(self):
        menuBar = self.menuBar()
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)

        self.new_pr = QAction(QIcon("./icons/new_project.png"), "&New", self)
        fileMenu.addAction(self.new_pr)
        self.new_pr.triggered.connect(self.new_project)
        self.new_pr.setShortcut("ctrl+n")

        self.open_pr = QAction(
            QIcon("./icons/open_project.png"), "&Open", self)
        fileMenu.addAction(self.open_pr)
        self.open_pr.triggered.connect(self.open_project)
        self.open_pr.setShortcut("ctrl+o")

        self.save_pr = QAction(
            QIcon("./icons/save_project.png"), "&Save", self)
        fileMenu.addAction(self.save_pr)
        self.save_pr.triggered.connect(self.save_project)
        self.save_pr.setShortcut("ctrl+s")

        self.save_as = QAction(QIcon("./icons/save_as.png"), "&Save as", self)
        fileMenu.addAction(self.save_as)
        self.save_as.triggered.connect(self.save_as_project)
        self.save_as.setShortcut("ctrl+shift+s")

        self.open_mov = QAction(
            QIcon("./icons/open_movie.png"), "&Import Movie", self)
        fileMenu.addAction(self.open_mov)
        self.open_mov.triggered.connect(self.open_movie)
        self.open_mov.setShortcut("ctrl+shift+o")

        self.exp_ply = QAction(
            QIcon("./icons/3d_printer.png"), "&Export PLY", self)
        fileMenu.addAction(self.exp_ply)
        self.exp_ply.triggered.connect(self.export_ply_data)
        self.exp_ply.setShortcut("ctrl+e")

        self.exit_pr = QAction(
            QIcon("./icons/exit_project.png"), "&Exit", self)
        fileMenu.addAction(self.exit_pr)
        self.exit_pr.triggered.connect(self.exit_project)
        self.exit_pr.setShortcut("Esc")

    def export_ply_data(self):
        if len(self.widget.gl_viewer.obj.ply_pts) > 0:
            bundle_adjustment_ply_data = self.widget.gl_viewer.obj.ply_pts[-1]
            cam_pos = self.widget.gl_viewer.obj.camera_poses[-1]
    
            quad_pts = self.widget.quad_obj.new_points
            quad_data_list = []
            for i, quad_ in enumerate(quad_pts):
                if not self.widget.quad_obj.deleted[i]:
                    quad_data_list.append(quad_)
            if len(quad_data_list) > 0:
                quad_data = np.vstack(quad_data_list)

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
                # print(cylinder_data.shape)
            if len(quad_data_list) > 0 and len(new_base_centers) > 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_pos, quad_data, cylinder_data))
            elif len(quad_data_list) == 0 and len(new_base_centers) > 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_pos, cylinder_data))
            elif len(quad_data_list) > 0 and len(new_base_centers) == 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_pos, quad_data))
            else:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_pos))
            
            # Write vertex data
            write_vertices_ply('vertex_data.ply', ply_data_all)
            
            # Face data for quads
            face_data = np.zeros(shape=(2*len(quad_data_list), 3), dtype=int)
            for i in range(0,face_data.shape[0], 2):
                face_data[i,0] = bundle_adjustment_ply_data.shape[0] + 2*i
                # print(face_data[i,0])
                face_data[i,1] = face_data[i,0] + 3
                face_data[i,2] = face_data[i,0] + 1
                
                face_data[i+1,0] = face_data[i,0] + 2
                face_data[i+1,1] = face_data[i,0] + 1
                face_data[i+1,2] = face_data[i,0] + 3

            
            # Face data for cylinders
            start = bundle_adjustment_ply_data.shape[0] + 4*len(quad_data_list)
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
                    face_data_cyl[sectorCount*4*i+2*sectorCount+j, 1] = start + num_cyl + (sectorCount + 1)*i + j + 1
                    face_data_cyl[sectorCount*4*i+2*sectorCount+j, 2] = start + 2*num_cyl + (sectorCount + 1)*num_cyl + (sectorCount+1)*i + j 
                    
                for j in range(sectorCount):
                    face_data_cyl[sectorCount*4*i+3*sectorCount+j, 0] = start + (sectorCount+1)*i + num_cyl + j + 1
                    face_data_cyl[sectorCount*4*i+3*sectorCount+j, 1] = start + i + 2*num_cyl + (sectorCount + 1)*num_cyl + (sectorCount)*i + j + 1
                    face_data_cyl[sectorCount*4*i+3*sectorCount+j, 2] = start + i + 2*num_cyl + (sectorCount + 1)*num_cyl + (sectorCount)*i + j
                    
            all_faces = np.concatenate((face_data, face_data_cyl))
            
            if all_faces.shape[0] > 0:
                write_faces_ply('face_data.ply', ply_data_all, all_faces )
        else:
            print("Please compute 3D data points")

    def ask_save_dialogue(self):
        msgBox = QMessageBox()
        msgBox.setText("Do you want to save your current project ?")
        msgBox.setWindowTitle("Save project")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            self.save_project()

    def new_project(self):
        self.ask_save_dialogue()
        self.widget = Widget()
        self.setCentralWidget(QWidget())
        self.project_name_label.setText("untitled.json")
        self.removeToolBar(self.toolbar2)
        self.removeToolBar(self.toolbar)
        # self.create_statusbar()
        self.create_toolbar()

    def exit_project(self):
        if confirm_exit():
            self.close()

    def open_project(self):
        file_types = "json (*.json)"
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select project.',
            directory=os.getcwd(),
            filter=file_types
        )
        if response[0] != '':
            self.save_response = response
            project_path = response[0]

            name_project = os.path.relpath(project_path, os.getcwd())
            disp_name_project = split_path(name_project)
            self.project_name_label.setText(disp_name_project)

            self.widget.doc.load_data(project_path)
            self.create_layout()
            v = self.widget.mv_panel.movie_caps[self.widget.mv_panel.selected_movie_idx]
            if self.widget.selected_thumbnail_index != -1:
                self.widget.displayThumbnail(self.widget.selected_thumbnail_index)

            if self.widget.gl_viewer.obj.cross_hair:
                self.widget.gl_viewer.obj.feature_tool()
            else:
                self.widget.gl_viewer.obj.move_tool()

            display_msg = "Opened "+split_path(project_path)
            self.statusBar.showMessage(display_msg, 2000)



    def implement_save(self, p):
        name_project = os.path.relpath(p, os.getcwd())

        disp_name_project = split_path(name_project)

        display_msg = "Saving "+disp_name_project
        self.statusBar.showMessage(display_msg, 2000)

        self.widget.doc.save_directory(name_project)

        data = self.widget.doc.get_data()
        json_object = json.dumps(data, indent=4)
        if name_project.split('.')[-1] != 'json':
            name_project = name_project+'.json'
        with open(name_project, "w") as outfile:
            outfile.write(json_object)



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
            name_project = os.path.relpath(self.save_response[0], os.getcwd())
            disp_name_project = split_path(name_project)
            self.project_name_label.setText(disp_name_project)
            self.implement_save(self.save_response[0])



    def save_as_project(self):
        if self.project_name_label.text() == 'untitled.json':
            self.save_project()
        else:
            file_types = "json (*.json)"
            save_as_response = QFileDialog.getSaveFileName(
                parent=self,
                caption='Save as.',
                directory=os.getcwd(),
                filter=file_types
            )
            if save_as_response[0] != '':
                self.implement_save(save_as_response[0])



    def open_movie(self):
        # file_types = "Video files (*.asf *.mp4 *.mov)"
        file_types = "Supported Video files (*.asf *.mp4 *.mov *.MP4 *.MOV *.ASF);; MP4 (*.mp4);; ASF (*.asf);; MOV(*.mov)"
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select movie file.',
            directory=os.getcwd(),
            filter=file_types
        )
        if response[0] != '':
            movie_path = os.path.relpath(response[0], os.getcwd())
            if movie_path in self.widget.mv_panel.movie_paths:
                movie_dialogue()
            else:
                movie_name = split_path(movie_path)
                display_msg = "Opened "+movie_name
                self.statusBar.showMessage(display_msg, 2000)
                self.widget.selected_thumbnail_index = -1
                self.widget.mv_panel.add_movie(movie_path)

                if len(self.widget.mv_panel.movie_paths) == 1:
                    self.create_layout()



    def create_statusbar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
