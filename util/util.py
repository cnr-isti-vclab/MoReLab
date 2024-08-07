from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import platform, struct
import numpy as np
from scipy.spatial import distance
import cv2





class Feature_Dialogue(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Feature Label")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        label = QLabel("Enter the label of feature point.")
        
        self.e2 = QLineEdit()
        self.e2.setValidator(QIntValidator())
        self.e2.setMaxLength(6)
        self.e2.setFont(QFont("Arial",15))
        
        h_layout.addWidget(label)
        h_layout.addWidget(self.e2)
        
        layout.addLayout(h_layout)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        
    
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Processing. Please wait !")
        Dialog.resize(321, 220)

        self.label = QLabel(Dialog)
        self.label.setText("Processing ...............")
        # self.label.setGeometry(QRect(10, 10, 113, 21))
        self.label.setObjectName("Label")



        self.retranslateUi(Dialog)
        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Processing. Please wait !", "Processing. Please wait !"))




class Dialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.setupUi(self)
        
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        
                              
        
    
def convert_cv_qt(cv_img, width, height):
    """Convert from an opencv image to QPixmap"""
    rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
    p = convert_to_Qt_format.scaled(width, height, Qt.KeepAspectRatio)
    return QPixmap.fromImage(p)


def duplicate_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("This feature label already exists on this frame. Please give another label.")
    msgBox.setWindowTitle("Features with duplicate labels")
    msgBox.setStandardButtons(QMessageBox.Ok)
    # msgBox.buttonClicked.connect(msgButtonClick)     
    returnValue = msgBox.exec()

    
    
def increment_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("This feature label is too high. Next increment number will be used as new feature label.")
    msgBox.setWindowTitle("Too high Feature label")
    msgBox.setStandardButtons(QMessageBox.Ok)
    # msgBox.buttonClicked.connect(msgButtonClick)
     
    returnValue = msgBox.exec()
    
    
def feature_absent_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("The selected feature is not present on the selected frame. Please select another feature. ")
    msgBox.setWindowTitle("Feature Not Found")
    msgBox.setStandardButtons(QMessageBox.Ok)
    # msgBox.buttonClicked.connect(msgButtonClick)
    returnValue = msgBox.exec()
    
    
def no_keyframe_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Please extract key-frames first")
    msgBox.setWindowTitle("No KeyFrames")
    msgBox.setStandardButtons(QMessageBox.Ok)
    # msgBox.buttonClicked.connect(msgButtonClick)
    returnValue = msgBox.exec()
    
def same_image_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Detection cannot be done for the same image. Please select two different images. ")
    msgBox.setWindowTitle("No KeyFrames")
    msgBox.setStandardButtons(QMessageBox.Ok)
    # msgBox.buttonClicked.connect(msgButtonClick)
    returnValue = msgBox.exec()
    

def resetFrame_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Frame has been initialized. ")
    msgBox.setWindowTitle("Reset frame")
    msgBox.setStandardButtons(QMessageBox.Ok)
    # msgBox.buttonClicked.connect(msgButtonClick)
    returnValue = msgBox.exec()
    
    
def no_feature_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("SuperGlue detection has already been done on both images")
    msgBox.setWindowTitle("No Feature")
    msgBox.setStandardButtons(QMessageBox.Ok)
    # msgBox.buttonClicked.connect(msgButtonClick)
    returnValue = msgBox.exec()
    
def models_folder_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("models folder not found for automatic feature detection. Please download models folder from SuperGlue Github repository and place it in the current working directory.")
    msgBox.setWindowTitle("Pretrained feature detection model missing")
    msgBox.setStandardButtons(QMessageBox.Ok)
    # msgBox.buttonClicked.connect(msgButtonClick)
    returnValue = msgBox.exec()
    
    
def numberOfFrames_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Please enter a number smaller than or equal to total number of frames of the video.")
    msgBox.setWindowTitle("Number of Frames")
    msgBox.setStandardButtons(QMessageBox.Ok)
    # msgBox.buttonClicked.connect(msgButtonClick)
    returnValue = msgBox.exec()
    
    
def exportPLY_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Please compute 3D data points and then export 3D data. ")
    msgBox.setWindowTitle("3D data")
    msgBox.setStandardButtons(QMessageBox.Ok)
    # msgBox.buttonClicked.connect(msgButtonClick)
    returnValue = msgBox.exec()
    
    
def not_extractKF_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("This video does not exist. Hence, frames cannot be extracted.")
    msgBox.setWindowTitle("Extact keyframes")
    msgBox.setStandardButtons(QMessageBox.Ok)
    # msgBox.buttonClicked.connect(msgButtonClick)
    returnValue = msgBox.exec()
    
    
def noImage_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Please click on image thumbnail first and then copy features. ")
    msgBox.setWindowTitle("select Image")
    msgBox.setStandardButtons(QMessageBox.Ok)
    # msgBox.buttonClicked.connect(msgButtonClick)
    returnValue = msgBox.exec()
    
def copy_features_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Please copy features first. ")
    msgBox.setWindowTitle("copy features")
    msgBox.setStandardButtons(QMessageBox.Ok)
    # msgBox.buttonClicked.connect(msgButtonClick)
    returnValue = msgBox.exec()
    
    
def filledImage_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Please select a frame containing no feature. Copied features can only be pasted on a frame with no feature. ")
    msgBox.setWindowTitle("paste features")
    msgBox.setStandardButtons(QMessageBox.Ok)
    # msgBox.buttonClicked.connect(msgButtonClick)
    returnValue = msgBox.exec()
    

def show_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Are you sure you want to extract key-frames again ?")
    msgBox.setWindowTitle("Key-frame extraction")
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    # msgBox.buttonClicked.connect(msgButtonClick) 
    returnValue = msgBox.exec()
    b = False
    if returnValue == QMessageBox.Yes:
       b = True
    return b


def confirm_exit():
    msgBox = QMessageBox()
    msgBox.setText("Are you sure you want to exit ?")
    msgBox.setWindowTitle("Exit Project")
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    returnValue = msgBox.exec()
    b = False
    if returnValue == QMessageBox.Yes:
       b = True
    return b


def confirm_new():
    msgBox = QMessageBox()
    msgBox.setText("Are you sure you want to create new project ?")
    msgBox.setWindowTitle("New Project")
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    returnValue = msgBox.exec()
    b = False
    if returnValue == QMessageBox.Yes:
       b = True
    return b


def movie_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("This movie has already been loaded.")
    msgBox.setWindowTitle("Open movie")
    msgBox.setStandardButtons(QMessageBox.Ok)                 
    returnValue = msgBox.exec()
    
def after_BA_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("3D structure has been computed.")
    msgBox.setWindowTitle("3D structure")
    msgBox.setStandardButtons(QMessageBox.Ok)
    returnValue = msgBox.exec()        

def numFeature_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("SfM cannot be computed because a minimum of two frames must have atleast 8 features each.")
    msgBox.setWindowTitle("Number of Features")
    msgBox.setStandardButtons(QMessageBox.Ok)                 
    returnValue = msgBox.exec()
    

def constraint_labels():
    msgBox = QMessageBox()
    msgBox.setText("Some feature is not present on the image. Please make sure that all features are present on the image.")
    msgBox.setWindowTitle("Constraint features")
    msgBox.setStandardButtons(QMessageBox.Ok)                 
    returnValue = msgBox.exec()
    
def constraint_labels_different():
    msgBox = QMessageBox()
    msgBox.setText("Feature 1 and 2 must be different. Similarly feature 3 and 4 must also be different.")
    msgBox.setWindowTitle("Different constraint features")
    msgBox.setStandardButtons(QMessageBox.Ok)                 
    returnValue = msgBox.exec()
    
    
    
def straight_line_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("The selected features are in a straight line and cannot form circle. Please select another feature.")
    msgBox.setWindowTitle("Features on a straight line")
    msgBox.setStandardButtons(QMessageBox.Ok)                 
    returnValue = msgBox.exec()
    

def copy_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Feature data has been copied")
    msgBox.setWindowTitle("Copy feature data")
    msgBox.setStandardButtons(QMessageBox.Ok)                 
    returnValue = msgBox.exec()
    
def switch_kf_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Extraction method has been switched. Features can be pasted on the frames of same extraction method.")
    msgBox.setWindowTitle("Switch extraction method")
    msgBox.setStandardButtons(QMessageBox.Ok)                 
    returnValue = msgBox.exec()
    
def switch_movie_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("You have changed the movie. Features can be pasted only within the same movie.")
    msgBox.setWindowTitle("Switch movie")
    msgBox.setStandardButtons(QMessageBox.Ok)                 
    returnValue = msgBox.exec()

def export_ply_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("3D data has been exported successfully.")
    msgBox.setWindowTitle("Export PLY")
    msgBox.setStandardButtons(QMessageBox.Ok)
    returnValue = msgBox.exec()
    
def noFrameSelected_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Please click on a thumbnail first and then you can reset the selected image.")
    msgBox.setWindowTitle("Reset frame")
    msgBox.setStandardButtons(QMessageBox.Ok)
    returnValue = msgBox.exec()
    
    
def del_primitive_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("No 3D primitive has been selected. Please click on a 3D primitive with left mouse button.")
    msgBox.setWindowTitle("Selection of 3D primitive")
    msgBox.setStandardButtons(QMessageBox.Ok)
    returnValue = msgBox.exec()
    

def label_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("The label of feature must be an integer greater than 0.")
    msgBox.setWindowTitle("label value")
    msgBox.setStandardButtons(QMessageBox.Ok)
    returnValue = msgBox.exec()
    
def lc_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Please compute SfM first before applying linear constraints optimization.")
    msgBox.setWindowTitle("Linear constraints optimization")
    msgBox.setStandardButtons(QMessageBox.Ok)
    returnValue = msgBox.exec()
    
    
def epipolar_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Guiding lines cannot be computed because selected frame and last feature-marked frame should have a minimum of 8 features each.")
    msgBox.setWindowTitle("Guiding lines computation")
    msgBox.setStandardButtons(QMessageBox.Ok)
    returnValue = msgBox.exec()
    

def lc_add_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Please add linear constraints first")
    msgBox.setWindowTitle("Linear constraints optimization")
    msgBox.setStandardButtons(QMessageBox.Ok)
    returnValue = msgBox.exec()
    
    
def fundamental_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Fundamental matrix has been computed")
    msgBox.setWindowTitle("Fundamental matrix")
    msgBox.setStandardButtons(QMessageBox.Ok)
    returnValue = msgBox.exec()
    
    
def save_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Project has been saved.")
    msgBox.setWindowTitle("Save Project")
    msgBox.setStandardButtons(QMessageBox.Ok)
    returnValue = msgBox.exec()
    
def load_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Project has been loaded.")
    msgBox.setWindowTitle("Load Project")
    msgBox.setStandardButtons(QMessageBox.Ok)
    returnValue = msgBox.exec()
    


def split_path(complete_path):
    op_sys = platform.system()
    if op_sys == "Windows":
        p = complete_path.split('\\')[-1]
    else:
        p = complete_path.split('/')[-1]

    return p


def adjust_op(mv_paths, op):
    op_sys = platform.system()
    new_paths = []
    if op == "Windows" and op_sys != "Windows":
        for mv in mv_paths:
            new_paths.append(mv.replace('\\', '/'))
    elif op != "Windows" and op_sys == "Windows":
        for mv in mv_paths:
            new_paths.append(mv.replace('/', '\\'))
    else:
        new_paths = mv_paths
    return new_paths    


def write_faces_ply(filename,vert_arr, face_arr, rgb_points=None):

    """ creates a .pkl file of the point clouds generated
    """

    assert vert_arr.shape[1] == 3,'Input XYZ points should be Nx3 float array'
    if rgb_points is None:
        rgb_points = np.ones(face_arr.shape).astype(np.uint8)*255
        
    assert face_arr.shape == rgb_points.shape,'Color is for faces and hence should have same shape as faces'
    
    vert_arr = vert_arr.astype('f4')
    face_arr = face_arr.astype('i4')
    
    vertex = np.empty(vert_arr.shape[0], dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
    vertex['x'] = vert_arr[:,0]
    vertex['y'] = vert_arr[:,1]
    vertex['z'] = vert_arr[:,2]
    
    
    
    ply_faces = np.empty(face_arr.shape[0], dtype=[('vertex_indices', 'i4', (3,)), ('red', 'u1'), ('green', 'u1'), ('blue', 'u1')])
    ply_faces['vertex_indices'] = face_arr
    ply_faces['red'] = rgb_points[:,0]
    ply_faces['green'] = rgb_points[:,1]
    ply_faces['blue'] = rgb_points[:,2]
    
    
    data = PlyData(
        [
            PlyElement.describe(vertex, 'vertex'),
            PlyElement.describe(ply_faces, 'face')
        ]
    )
    data.write(filename)


def is_integer_num(n):
    if isinstance(n, int):
        return True
    if isinstance(n, float):
        return n.is_integer()
    return False

    
    
def write_vertices_ply(filename,xyz_points,rgb_points=None):

    """ creates a .pkl file of the point clouds generated
    """
    # Input XYZ points should be Nx3 float array
    assert xyz_points.shape[1] == 3
    if rgb_points is None:
        rgb_points = np.ones(xyz_points.shape).astype(np.uint8)*255

    # Input RGB colors should be Nx3 float array and have same size as input XYZ points
    assert xyz_points.shape == rgb_points.shape

    # Write header of .ply file
    fid = open(filename,'wb')
    fid.write(bytes('ply\n', 'utf-8'))
    fid.write(bytes('format binary_little_endian 1.0\n', 'utf-8'))
    fid.write(bytes('element vertex %d\n'%xyz_points.shape[0], 'utf-8'))
    fid.write(bytes('property float x\n', 'utf-8'))
    fid.write(bytes('property float y\n', 'utf-8'))
    fid.write(bytes('property float z\n', 'utf-8'))
    fid.write(bytes('property uchar red\n', 'utf-8'))
    fid.write(bytes('property uchar green\n', 'utf-8'))
    fid.write(bytes('property uchar blue\n', 'utf-8'))
    fid.write(bytes('end_header\n', 'utf-8'))

    # Write 3D points to .ply file
    for i in range(xyz_points.shape[0]):
        fid.write(bytearray(struct.pack("fffccc",xyz_points[i,0],xyz_points[i,1],xyz_points[i,2],
                                        rgb_points[i,0].tostring(),rgb_points[i,1].tostring(),
                                        rgb_points[i,2].tostring())))
    fid.close()
    
    
    
    
    
def point_line_distance(line, point):
    numer = abs(np.sum(np.multiply(line, point)))
    denom = np.sqrt(np.square(point[0]) + np.square(point[1]))
    return numer/denom


def save_feature_locs(all_pts, visible_labels):
    for i, pts in enumerate(all_pts):
        np.save('test4_features'+str(i)+'.npy', pts)
        np.save('test4_labels'+str(i)+'.npy', visible_labels[i])
        

def deleteItemsOfLayout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                deleteItemsOfLayout(item.layout())
                
def empty_gui(layout):
    for i in range(3):
        item = layout.takeAt(0)
        deleteItemsOfLayout(item)
        layout.removeItem(item)
    
    return layout


def calc_near_far(cm, opt_points):
    dist_list = []
    for i in range(opt_points.shape[0]):
        dist = distance.euclidean(opt_points[i,:], cm)
        dist_list.append(dist)
    
    near = min(dist_list)
    far = max(dist_list)
    return (near, far)