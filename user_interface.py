from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class UserInterface(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.ctrl_wdg = parent
        self.tool_btn_style =  """
                QPushButton:hover   { background-color: rgb(180,180,180); border: 1px solid darkgray;         }
                QPushButton {border:none; padding: 10px;}
                QToolTip { background-color: white; color: black); }
                """
        self.selected_btn_style = """
                QPushButton {background-color: rgb(180,180,180); border: 1px solid darkgray; }
                QToolTip { background-color: white; color: black); }
        """

        self.create_wdg1()
        self.create_scroll_area()
        self.add_tool_icons()
        self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
        self.set_flags(True, False, False, False, False, False, False, False, False, False, False, False)
        self.bEpipolar = False
        self.epipolar_tool.setStyleSheet(self.tool_btn_style)
        
        

    def create_scroll_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumSize(self.ctrl_wdg.monitor_width*0.56, self.ctrl_wdg.monitor_height*0.13)

    def create_wdg1(self):
        self.btn_kf = QPushButton("Extract Frames")
        self.btn_kf.setStyleSheet("""
                                  QPushButton:hover   { background-color: rgb(145,224,255)}
                                  QPushButton {background-color: rgb(230,230,230); border-radius: 20px; padding: 15px; border: 1px solid black; color:black; font-size: 15px;}
                                  """)
        self.btn_kf.clicked.connect(self.ctrl_wdg.extract)
        
        self.radiobutton1 = QRadioButton("Regular")
        self.radiobutton1.setChecked(True)
        self.radiobutton1.toggled.connect(self.onClicked)
        self.radiobutton2 = QRadioButton("Network")
        self.radiobutton2.toggled.connect(self.onClicked)

        
    def onClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            self.ctrl_wdg.kf_method = radioButton.text()
            self.ctrl_wdg.selected_thumbnail_index = -1
            self.ctrl_wdg.populate_scrollbar()
            # self.ctrl_wdg.gl_viewer.obj.compute_sfm()
        
        
    def setClick(self):
        if self.ctrl_wdg.kf_method == "Network":
            self.radiobutton2.setChecked(True)
        else:
            self.radiobutton1.setChecked(True)
        
    def add_tool_icons(self):
        icon_size = 30
        
        self.np_tool = QPushButton()
        self.np_tool.setIcon(QIcon("./icons/new_project.png"))
        self.np_tool.setIconSize(QSize(icon_size, icon_size))
        self.np_tool.setStyleSheet(self.tool_btn_style)
        self.np_tool.setToolTip("New")
        self.np_tool.clicked.connect(self.ctrl_wdg.main_file.implement_new_project)

        self.op_tool = QPushButton()
        self.op_tool.setIcon(QIcon("./icons/open_project.png"))
        self.op_tool.setIconSize(QSize(icon_size, icon_size))
        self.op_tool.setStyleSheet(self.tool_btn_style)
        self.op_tool.setToolTip("Open")
        self.op_tool.clicked.connect(self.ctrl_wdg.main_file.open_project)
        
        self.om_tool = QPushButton()
        self.om_tool.setIcon(QIcon("./icons/open_movie.png"))
        self.om_tool.setIconSize(QSize(icon_size, icon_size))
        self.om_tool.setStyleSheet(self.tool_btn_style)
        self.om_tool.setToolTip("Import Movie")
        self.om_tool.clicked.connect(self.ctrl_wdg.main_file.implement_open_movie)

        self.of_tool = QPushButton()
        self.of_tool.setIcon(QIcon("./icons/open-folder.png"))
        self.of_tool.setIconSize(QSize(icon_size, icon_size))
        self.of_tool.setStyleSheet(self.tool_btn_style)
        self.of_tool.setToolTip("Import Folder")
        self.of_tool.clicked.connect(self.ctrl_wdg.main_file.implement_open_folder)
        
        self.sp_tool = QPushButton()
        self.sp_tool.setIcon(QIcon("./icons/save_project.png"))
        self.sp_tool.setIconSize(QSize(icon_size, icon_size))
        self.sp_tool.setStyleSheet(self.tool_btn_style)
        self.sp_tool.setToolTip("Save")
        self.sp_tool.clicked.connect(self.ctrl_wdg.main_file.save_project)
        
        self.sp_as_tool = QPushButton()
        self.sp_as_tool.setIcon(QIcon("./icons/save_as.png"))
        self.sp_as_tool.setIconSize(QSize(icon_size, icon_size))
        self.sp_as_tool.setStyleSheet(self.tool_btn_style)
        self.sp_as_tool.setToolTip("Save as")
        self.sp_as_tool.clicked.connect(self.ctrl_wdg.main_file.save_as_project)
        
        self.ep_tool = QPushButton()
        self.ep_tool.setIcon(QIcon("./icons/exit_project.png"))
        self.ep_tool.setIconSize(QSize(icon_size, icon_size))
        self.ep_tool.setStyleSheet(self.tool_btn_style)
        self.ep_tool.setToolTip("Exit")
        self.ep_tool.clicked.connect(self.ctrl_wdg.main_file.implement_exit_project)
        
        self.mv_tool = QPushButton()
        self.mv_tool.setIcon(QIcon("./icons/cursor.png"))
        self.mv_tool.setIconSize(QSize(icon_size, icon_size))
        self.mv_tool.setStyleSheet(self.tool_btn_style)
        self.mv_tool.setToolTip("Move Tool")
        self.mv_tool.clicked.connect(self.implement_move_tool)
        
        self.ft_tool = QPushButton()
        self.ft_tool.setIcon(QIcon("./icons/crosshair.png"))
        self.ft_tool.setIconSize(QSize(icon_size, icon_size))
        self.ft_tool.setStyleSheet(self.tool_btn_style)
        self.ft_tool.setToolTip("New Feature Tool")
        self.ft_tool.clicked.connect(self.implement_feature_tool)
        
        
        self.ft_plus_tool = QPushButton()
        self.ft_plus_tool.setIcon(QIcon("./icons/focus.png"))
        self.ft_plus_tool.setIconSize(QSize(icon_size, icon_size))
        self.ft_plus_tool.setStyleSheet(self.tool_btn_style)
        self.ft_plus_tool.setToolTip("Latest Feature Tool")
        self.ft_plus_tool.clicked.connect(self.implement_feature_plus_tool)
        
        
        self.rect_tool = QPushButton()
        self.rect_tool.setIcon(QIcon("./icons/square.png"))
        self.rect_tool.setIconSize(QSize(icon_size, icon_size))
        self.rect_tool.setStyleSheet(self.tool_btn_style)
        self.rect_tool.setToolTip("Rectangle Tool")
        self.rect_tool.clicked.connect(self.implement_rect_tool)

        self.quad_tool = QPushButton()
        self.quad_tool.setIcon(QIcon("./icons/path_point.png"))
        self.quad_tool.setIconSize(QSize(icon_size, icon_size))
        self.quad_tool.setStyleSheet(self.tool_btn_style)
        self.quad_tool.setToolTip("Quadrilateral Tool")
        self.quad_tool.clicked.connect(self.implement_quad_tool)


        self.cyl_tool = QPushButton()
        self.cyl_tool.setIcon(QIcon("./icons/cylinder.png"))
        self.cyl_tool.setIconSize(QSize(icon_size, icon_size))
        self.cyl_tool.setStyleSheet(self.tool_btn_style)
        self.cyl_tool.setToolTip("Center Cylinder Tool")
        self.cyl_tool.clicked.connect(self.implement_cylinder_tool)
        
        self.new_cyl_tool = QPushButton()
        self.new_cyl_tool.setIcon(QIcon("./icons/new_cylinder.png"))
        self.new_cyl_tool.setIconSize(QSize(icon_size, icon_size))
        self.new_cyl_tool.setStyleSheet(self.tool_btn_style)
        self.new_cyl_tool.setToolTip("Base Cylinder Tool")
        self.new_cyl_tool.clicked.connect(self.implement_new_cylinder_tool)
        
        self.bz_tool = QPushButton()
        self.bz_tool.setIcon(QIcon("./icons/bezier.png"))
        self.bz_tool.setIconSize(QSize(icon_size, icon_size))
        self.bz_tool.setStyleSheet(self.tool_btn_style)
        self.bz_tool.setToolTip("Curved Cylinder Tool")
        self.bz_tool.clicked.connect(self.implement_bezier_tool)
        
        self.pick_tool = QPushButton()
        self.pick_tool.setIcon(QIcon("./icons/picking.png"))
        self.pick_tool.setIconSize(QSize(icon_size, icon_size))
        self.pick_tool.setStyleSheet(self.tool_btn_style)
        self.pick_tool.setToolTip("Picking Tool")
        self.pick_tool.clicked.connect(self.implement_picking_tool)
        
        self.measure_tool = QPushButton()
        self.measure_tool.setIcon(QIcon("./icons/tape_measure.png"))
        self.measure_tool.setIconSize(QSize(icon_size, icon_size))
        self.measure_tool.setStyleSheet(self.tool_btn_style)
        self.measure_tool.setToolTip("Measuring Tool")
        self.measure_tool.clicked.connect(self.implement_measure_tool)
        
        self.anchor_tool = QPushButton()
        self.anchor_tool.setIcon(QIcon("./icons/big-anchor.png"))
        self.anchor_tool.setIconSize(QSize(icon_size, icon_size))
        self.anchor_tool.setStyleSheet(self.tool_btn_style)
        self.anchor_tool.setToolTip("Anchor Tool")
        self.anchor_tool.clicked.connect(self.implement_anchor_tool)
        
        self.selection_tool = QPushButton()
        self.selection_tool.setIcon(QIcon("./icons/select.png"))
        self.selection_tool.setIconSize(QSize(icon_size, icon_size))
        self.selection_tool.setStyleSheet(self.tool_btn_style)
        self.selection_tool.setToolTip("Selection Tool")
        self.selection_tool.clicked.connect(self.implement_selection_tool)


        self.epipolar_tool = QPushButton()
        self.epipolar_tool.setIcon(QIcon("./icons/diagonal-line.png"))
        self.epipolar_tool.setIconSize(QSize(icon_size, icon_size))
        self.epipolar_tool.setStyleSheet(self.tool_btn_style)
        self.epipolar_tool.setToolTip("Epipolar Tool")
        self.epipolar_tool.clicked.connect(self.implement_epipolar_tool)
        

        

    def implement_move_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            # self.ctrl_wdg.main_file.logfile.info("------------------ Selected Move Tool ---------------- ...")
            self.set_styles(self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(True, False, False, False, False, False, False, False, False, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.ArrowCursor))
            
            
    def implement_feature_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            # self.ctrl_wdg.main_file.logfile.info("------------------ Selected New Feature Tool ---------------- ...")
            self.set_styles(self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, True, False, False, False, False, False, False, False, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.CrossCursor))
            
            
    def implement_feature_plus_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            # self.ctrl_wdg.main_file.logfile.info("------------------ Selected Latest Feature Tool ---------------- ...")
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, False, True, False, False, False, False, False, False, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.CrossCursor))

            
    def implement_rect_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            # self.ctrl_wdg.main_file.logfile.info("------------------ Selected Rectangle Tool ---------------- ...")
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, False, False, True, False, False, False, False, False, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.PointingHandCursor))
            
            
    def implement_cylinder_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            # self.ctrl_wdg.main_file.logfile.info("------------------ Selected Center Cylinder Tool ---------------- ...")
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, False, False, False, True, False, False, False, False, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.PointingHandCursor))
            
    def implement_new_cylinder_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            # self.ctrl_wdg.main_file.logfile.info("------------------ Selected Base Cylinder Tool ---------------- ...")
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, False, False, False, False, True, False, False, False, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.PointingHandCursor))
                     
    def implement_bezier_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            # self.ctrl_wdg.main_file.logfile.info("------------------ Selected Bezier Curve Tool ---------------- ...")
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, False, False, False, False, False, True, False, False, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.PointingHandCursor))
            
    def implement_measure_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            # self.ctrl_wdg.main_file.logfile.info("------------------ Selected Measure Tool ---------------- ...")
            self.set_styles(self.tool_btn_style, self.tool_btn_style,self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, False, False, False, False, False, False, True, False, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.PointingHandCursor))            
            
    def implement_picking_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            # self.ctrl_wdg.main_file.logfile.info("------------------ Selected Picking Tool ---------------- ...")
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, False, False, False, False, False, False, False, True, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.ArrowCursor))
            
    def implement_quad_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            # self.ctrl_wdg.main_file.logfile.info("------------------ Selected Quad Tool ---------------- ...")
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, False, False, False, False, False, False, False, False, True, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.PointingHandCursor))
            
    def implement_anchor_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            # self.ctrl_wdg.main_file.logfile.info("------------------ Selected Anchor Tool ---------------- ...")
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style)
            self.set_flags(False, False, False, False, False, False, False, False, False, False, True, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.PointingHandCursor))
            
    def implement_selection_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            # self.ctrl_wdg.main_file.logfile.info("------------------ Selected Selection Tool ---------------- ...")
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style)
            self.set_flags(False, False, False, False, False, False, False, False, False, False, False, True)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.PointingHandCursor))
            
                        

    def implement_epipolar_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            # self.ctrl_wdg.main_file.logfile.info("------------------ Selected Epipolar Line Tool ---------------- ...")
            if self.bEpipolar:
                self.bEpipolar = False
                self.epipolar_tool.setStyleSheet(self.tool_btn_style)
            else:
                self.bEpipolar = True
                self.epipolar_tool.setStyleSheet(self.selected_btn_style)
                self.ctrl_wdg.gl_viewer.obj.compute_fundamental_mat()

        
        
    def set_styles(self, mv_sty, ft_sty, ft_plus_sty, quad_sty, cyl_sty, new_cyl_sty, bz_sty, measure_sty, pick_sty, connect_dots_sty, anchor_sty, sel_sty):
        self.mv_tool.setStyleSheet(mv_sty)
        self.ft_tool.setStyleSheet(ft_sty)
        self.ft_plus_tool.setStyleSheet(ft_plus_sty)
        self.rect_tool.setStyleSheet(quad_sty)
        self.cyl_tool.setStyleSheet(cyl_sty)
        self.new_cyl_tool.setStyleSheet(new_cyl_sty)
        self.bz_tool.setStyleSheet(bz_sty)
        self.measure_tool.setStyleSheet(measure_sty)
        self.pick_tool.setStyleSheet(pick_sty)
        self.quad_tool.setStyleSheet(connect_dots_sty)
        self.anchor_tool.setStyleSheet(anchor_sty)
        self.selection_tool.setStyleSheet(sel_sty)


    def set_flags(self, move_bool, cross_hair, crosshair_plus, bRect, bCylinder, bnCylinder, bBezier, bMeasure, bPick, bQuad, bAnchor, bSelect):
        self.move_bool = move_bool
        self.cross_hair = cross_hair
        self.crosshair_plus = crosshair_plus
        self.bRect = bRect
        self.bCylinder = bCylinder
        self.bnCylinder = bnCylinder
        self.bBezier = bBezier
        self.bMeasure = bMeasure
        self.bPick = bPick
        self.bQuad = bQuad
        self.bAnchor = bAnchor
        self.bSelect = bSelect

    