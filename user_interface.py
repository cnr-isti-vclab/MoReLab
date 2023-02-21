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
        self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
        self.set_flags(True, False, False, False, False, False, False, False, False)

        
        
    def create_menu(self):
        menuBar = self.ctrl_wdg.main_file.menuBar()
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)


        self.new_pr = QAction(QIcon("./icons/new_project.png"), "&New", self)
        fileMenu.addAction(self.new_pr)
        self.new_pr.triggered.connect(self.ctrl_wdg.main_file.implement_new_project)
        self.new_pr.setShortcut("ctrl+n")


        self.open_pr = QAction(QIcon("./icons/open_project.png"), "&Open", self)
        fileMenu.addAction(self.open_pr)
        self.open_pr.triggered.connect(self.ctrl_wdg.main_file.open_project)
        self.open_pr.setShortcut("ctrl+o")
        
        
        self.open_mov = QAction(QIcon("./icons/open_movie.png"), "&Import Movie", self)
        fileMenu.addAction(self.open_mov)
        self.open_mov.triggered.connect(self.ctrl_wdg.main_file.implement_open_movie)
        self.open_mov.setShortcut("ctrl+shift+o")

        
        self.save_pr = QAction(QIcon("./icons/save_project.png"), "&Save", self)
        fileMenu.addAction(self.save_pr)
        self.save_pr.triggered.connect(self.ctrl_wdg.main_file.save_project)
        self.save_pr.setShortcut("ctrl+s")

        
        self.save_as = QAction(QIcon("./icons/save_as.png"), "&Save as", self)
        fileMenu.addAction(self.save_as)
        self.save_as.triggered.connect(self.ctrl_wdg.main_file.save_as_project)
        self.save_as.setShortcut("ctrl+shift+s")
        
        
        self.exp_ply = QAction(QIcon("./icons/3d_printer.png"), "&Export PLY", self)
        fileMenu.addAction(self.exp_ply)
        self.exp_ply.triggered.connect(self.ctrl_wdg.main_file.export_ply_data)
        self.exp_ply.setShortcut("ctrl+e")
        
        
        self.exit_pr = QAction(QIcon("./icons/exit_project.png"), "&Exit", self)
        fileMenu.addAction(self.exit_pr)
        self.exit_pr.triggered.connect(self.ctrl_wdg.main_file.implement_exit_project)
        self.exit_pr.setShortcut("ctrl+q")
        

        
        

    def create_scroll_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumSize(self.ctrl_wdg.monitor_width*0.56, self.ctrl_wdg.monitor_height*0.13)

    def create_wdg1(self):
        self.btn_kf = QPushButton("Extract Key-frames")
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
        self.ctrl_wdg.populate_scrollbar()
        
        
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
        self.np_tool.setToolTip("New Project")
        self.np_tool.clicked.connect(self.ctrl_wdg.main_file.implement_new_project)

        self.op_tool = QPushButton()
        self.op_tool.setIcon(QIcon("./icons/open_project.png"))
        self.op_tool.setIconSize(QSize(icon_size, icon_size))
        self.op_tool.setStyleSheet(self.tool_btn_style)
        self.op_tool.setToolTip("Open Project")
        self.op_tool.clicked.connect(self.ctrl_wdg.main_file.open_project)
        
        self.om_tool = QPushButton()
        self.om_tool.setIcon(QIcon("./icons/open_movie.png"))
        self.om_tool.setIconSize(QSize(icon_size, icon_size))
        self.om_tool.setStyleSheet(self.tool_btn_style)
        self.om_tool.setToolTip("Open Movie")
        self.om_tool.clicked.connect(self.ctrl_wdg.main_file.implement_open_movie)
        
        self.sp_tool = QPushButton()
        self.sp_tool.setIcon(QIcon("./icons/save_project.png"))
        self.sp_tool.setIconSize(QSize(icon_size, icon_size))
        self.sp_tool.setStyleSheet(self.tool_btn_style)
        self.sp_tool.setToolTip("Save Project")
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
        self.ep_tool.setToolTip("Exit Project")
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
        self.ft_tool.setToolTip("Feature Tool")
        self.ft_tool.clicked.connect(self.implement_feature_tool)
        
        self.quad_tool = QPushButton()
        self.quad_tool.setIcon(QIcon("./icons/square.png"))
        self.quad_tool.setIconSize(QSize(icon_size, icon_size))
        self.quad_tool.setStyleSheet(self.tool_btn_style)
        self.quad_tool.setToolTip("Quad Tool")
        self.quad_tool.clicked.connect(self.implement_quad_tool)

        self.cyl_tool = QPushButton()
        self.cyl_tool.setIcon(QIcon("./icons/cylinder.png"))
        self.cyl_tool.setIconSize(QSize(icon_size, icon_size))
        self.cyl_tool.setStyleSheet(self.tool_btn_style)
        self.cyl_tool.setToolTip("Cylinder Tool")
        self.cyl_tool.clicked.connect(self.implement_cylinder_tool)
        
        self.new_cyl_tool = QPushButton()
        self.new_cyl_tool.setIcon(QIcon("./icons/new_cylinder.png"))
        self.new_cyl_tool.setIconSize(QSize(icon_size, icon_size))
        self.new_cyl_tool.setStyleSheet(self.tool_btn_style)
        self.new_cyl_tool.setToolTip("New Cylinder Tool")
        self.new_cyl_tool.clicked.connect(self.implement_new_cylinder_tool)
        
        self.bz_tool = QPushButton()
        self.bz_tool.setIcon(QIcon("./icons/bezier.png"))
        self.bz_tool.setIconSize(QSize(icon_size, icon_size))
        self.bz_tool.setStyleSheet(self.tool_btn_style)
        self.bz_tool.setToolTip("Bezier Tool")
        self.bz_tool.clicked.connect(self.implement_bezier_tool)
        
        self.measure_tool = QPushButton()
        self.measure_tool.setIcon(QIcon("./icons/tape_measure.png"))
        self.measure_tool.setIconSize(QSize(icon_size, icon_size))
        self.measure_tool.setStyleSheet(self.tool_btn_style)
        self.measure_tool.setToolTip("Measure Tool")
        self.measure_tool.clicked.connect(self.implement_measure_tool)
        
        self.pick_tool = QPushButton()
        self.pick_tool.setIcon(QIcon("./icons/picking.png"))
        self.pick_tool.setIconSize(QSize(icon_size, icon_size))
        self.pick_tool.setStyleSheet(self.tool_btn_style)
        self.pick_tool.setToolTip("Picking Tool")
        self.pick_tool.clicked.connect(self.implement_picking_tool)
        
        self.dot_connecting_tool = QPushButton()
        self.dot_connecting_tool.setIcon(QIcon("./icons/path_point.png"))
        self.dot_connecting_tool.setIconSize(QSize(icon_size, icon_size))
        self.dot_connecting_tool.setStyleSheet(self.tool_btn_style)
        self.dot_connecting_tool.setToolTip("Dots Connecting Tool")
        self.dot_connecting_tool.clicked.connect(self.implement_connect_tool)
        


    def implement_move_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            self.set_styles(self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(True, False, False, False, False, False, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.ArrowCursor))
            
            
    def implement_feature_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            self.set_styles(self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, True, False, False, False, False, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.CrossCursor))
            
            
    def implement_quad_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, False, True, False, False, False, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.PointingHandCursor))
            
            
    def implement_cylinder_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, False, False, True, False, False, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.PointingHandCursor))
            
    def implement_new_cylinder_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, False, False, False, True, False, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.PointingHandCursor))
                     
    def implement_bezier_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, False, False, False, False, True, False, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.PointingHandCursor))
            
    def implement_measure_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style, self.tool_btn_style)
            self.set_flags(False, False, False, False, False, False, True, False, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.PointingHandCursor))            
            
    def implement_picking_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style, self.tool_btn_style)
            self.set_flags(False, False, False, False, False, False, False, True, False)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.ArrowCursor))
            
    def implement_connect_tool(self):
        if len(self.ctrl_wdg.mv_panel.movie_paths) > 0:
            self.set_styles(self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.tool_btn_style, self.selected_btn_style)
            self.set_flags(False, False, False, False, False, False, False, False, True)
            self.ctrl_wdg.gl_viewer.setCursor(QCursor(Qt.PointingHandCursor))

        
        
    def set_styles(self, mv, ft, quad, cyl, new_cyl, bz, measure, pick, connect_dots):
        self.mv_tool.setStyleSheet(mv)
        self.ft_tool.setStyleSheet(ft)
        self.quad_tool.setStyleSheet(quad)
        self.cyl_tool.setStyleSheet(cyl)
        self.new_cyl_tool.setStyleSheet(new_cyl)
        self.bz_tool.setStyleSheet(bz)
        self.measure_tool.setStyleSheet(measure)
        self.pick_tool.setStyleSheet(pick)
        self.dot_connecting_tool.setStyleSheet(connect_dots)


    def set_flags(self, move_bool, cross_hair, bQuad, bCylinder, bnCylinder, bBezier, bMeasure, bPick, bConnect):
        self.move_bool = move_bool
        self.cross_hair = cross_hair
        self.bQuad = bQuad
        self.bCylinder = bCylinder
        self.bnCylinder = bnCylinder
        self.bBezier = bBezier
        self.bMeasure = bMeasure
        self.bPick = bPick
        self.bConnect = bConnect
        


    
    