from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import platform, struct
import numpy as np
from scipy.spatial import distance
from plyfile import PlyData, PlyElement





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


def movie_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("This movie has already been loaded.")
    msgBox.setWindowTitle("Open movie")
    msgBox.setStandardButtons(QMessageBox.Ok)                 
    returnValue = msgBox.exec()
    
def after_BA_dialogue(filename):
    msgBox = QMessageBox()
    msgBox.setText("3D structure has been computed and saved as "+str(filename))
    msgBox.setWindowTitle("3D structure")
    msgBox.setStandardButtons(QMessageBox.Ok)
    returnValue = msgBox.exec()    

    

def numFeature_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Atleast two frames must have atleast 8 features.")
    msgBox.setWindowTitle("Number of Features")
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


def write_pointcloud(filename,vert_arr, face_arr, rgb_points=None):

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