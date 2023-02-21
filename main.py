from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from central_widget import Widget
import sys, os, json
from util.util import *


class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)    # call the init for the parent class
        self.setWindowTitle('MoReLab')
        self.showMaximized()
        self.widget = Widget(self)
        self.create_statusbar()
        self.widget.ui.create_menu()
        self.create_toolbar()
        self.bLoad = False
        
        
        
        
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

        
        
        
    def implement_new_project(self):
        b = confirm_new()
        if b:
            last_wdg = self.widget
            self.widget = Widget(self)
            self.setCentralWidget(QWidget())
            self.create_statusbar()
            self.removeToolBar(self.toolbar2)
            self.removeToolBar(self.toolbar)
            if (not self.bLoad) and len(last_wdg.mv_panel.movie_paths) > 0:
                self.widget.ui.create_menu()
            self.create_toolbar()
            
        
    
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
            movie_path = os.path.relpath(response[0], os.getcwd())
            if movie_path in self.widget.mv_panel.movie_paths:
                movie_dialogue()
            else:
                movie_name = split_path(movie_path)
                display_msg = "Opened "+movie_name
                self.statusBar.showMessage(display_msg, 2000)
                self.widget.mv_panel.add_movie(movie_path)
                
                if len(self.widget.mv_panel.movie_paths) == 1:
                    self.create_layout()
                    

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


    def implement_save(self, p):
        name_project = os.path.relpath(p, os.getcwd())
        disp_name_project = split_path(name_project)
        display_msg = "Saving "+disp_name_project
        self.statusBar.showMessage(display_msg, 2000)
        self.widget.doc.save_directory(name_project)


        data = self.widget.doc.get_data()
        # print(data)
        json_object = json.dumps(data, indent=4)
        if name_project.split('.')[-1] != 'json':
            name_project = name_project+'.json'
        with open(name_project, "w") as outfile:
            outfile.write(json_object)
            
            
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
            # self.create_layout()
        
    def implement_exit_project(self):
        if confirm_exit():
            self.close()


    def create_toolbar(self):
        self.toolbar = QToolBar("&ToolBar", self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)


        self.toolbar.addWidget(self.widget.ui.np_tool)
        self.toolbar.addWidget(self.widget.ui.op_tool)
        self.toolbar.addWidget(self.widget.ui.om_tool)
        self.toolbar.addWidget(self.widget.ui.sp_tool)
        self.toolbar.addWidget(self.widget.ui.sp_as_tool)
        self.toolbar.addWidget(self.widget.ui.ep_tool)
        self.toolbar.addWidget(self.widget.ui.mv_tool)
        self.toolbar.addWidget(self.widget.ui.ft_tool)
        self.toolbar.addWidget(self.widget.ui.quad_tool)
        self.toolbar.addWidget(self.widget.ui.cyl_tool)
        self.toolbar.addWidget(self.widget.ui.new_cyl_tool)
        self.toolbar.addWidget(self.widget.ui.bz_tool)
        self.toolbar.addWidget(self.widget.ui.measure_tool)
        self.toolbar.addWidget(self.widget.ui.pick_tool)
        self.toolbar.addWidget(self.widget.ui.dot_connecting_tool)


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
        if len(self.widget.gl_viewer.obj.ply_pts) > 0:
            bundle_adjustment_ply_data = self.widget.gl_viewer.obj.ply_pts[-1]
            cam_data = self.widget.gl_viewer.obj.camera_poses[-1]
    
            quad_pts = self.widget.quad_obj.new_points
            quad_data_list = []
            for i, quad_ in enumerate(quad_pts):
                if not self.widget.quad_obj.deleted[i]:
                    quad_data_list.append(quad_)
            if len(quad_data_list) > 0:
                quad_data = np.vstack(quad_data_list)
                
                
            connects_data_list = []
            for i, quad_ in enumerate(self.widget.connect_obj.all_pts):
                if not self.widget.connect_obj.deleted[i]:
                    connects_data_list.append(quad_)


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
            if len(quad_data_list) > 0 and len(new_base_centers) > 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, quad_data, cylinder_data))
            elif len(quad_data_list) == 0 and len(new_base_centers) > 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, cylinder_data))
            elif len(quad_data_list) > 0 and len(new_base_centers) == 0:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data, quad_data))
            else:
                ply_data_all = np.concatenate((bundle_adjustment_ply_data, cam_data))
            
            # Write vertex data
            write_vertices_ply('vertex_data.ply', ply_data_all)
            
            # Face data for quads
            face_data = np.zeros(shape=(2*len(quad_data_list), 3), dtype=int)
            for i in range(0,face_data.shape[0], 2):
                face_data[i,0] = bundle_adjustment_ply_data.shape[0] + cam_data.shape[0] + 2*i
                # print(face_data[i,0])
                face_data[i,1] = face_data[i,0] + 3
                face_data[i,2] = face_data[i,0] + 1
                
                face_data[i+1,0] = face_data[i,0] + 2
                face_data[i+1,1] = face_data[i,0] + 1
                face_data[i+1,2] = face_data[i,0] + 3

            
            # Face data for cylinders
            start = bundle_adjustment_ply_data.shape[0] + cam_data.shape[0] + 4*len(quad_data_list)
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

            # Face data for Point connectors
            face_data_connects = np.zeros(shape=(2*len(connects_data_list), 3), dtype=int)
            for i in range(len(connects_data_list)):
                idx_list = self.widget.connect_obj.occurence_groups[i]
                print(idx_list)
                face_data_connects[2*i,0] = idx_list[0]
                # print(face_data[i,0])
                face_data_connects[2*i,1] = idx_list[3]
                face_data_connects[2*i,2] = idx_list[1]
                
                face_data_connects[2*i+1,0] = idx_list[2]
                face_data_connects[2*i+1,1] = idx_list[1]
                face_data_connects[2*i+1,2] = idx_list[3]

            # print(face_data)
                        
            all_faces = np.concatenate((face_data, face_data_cyl, face_data_connects))
            
            if all_faces.shape[0] > 0:
                write_faces_ply('face_data.ply', ply_data_all, all_faces )
        else:
            exportPLY_dialogue()

        
    def create_statusbar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
