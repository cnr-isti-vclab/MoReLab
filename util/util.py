from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import platform, pymeshlab, struct
import open3d as o3d
import numpy as np





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


def movie_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("This movie has already been loaded.")
    msgBox.setWindowTitle("Open movie")
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


def write_pointcloud(filename,xyz_points,rgb_points=None):

    """ creates a .pkl file of the point clouds generated
    """

    assert xyz_points.shape[1] == 3,'Input XYZ points should be Nx3 float array'
    if rgb_points is None:
        rgb_points = np.ones(xyz_points.shape).astype(np.uint8)*255
    assert xyz_points.shape == rgb_points.shape,'Input RGB colors should be Nx3 float array and have same size as input XYZ points'

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
    