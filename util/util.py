from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import platform
import numpy as np
import matplotlib.pyplot as plt



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
    

def split_path(complete_path):
    op_sys = platform.system()
    if op_sys == "Windows":
        p = complete_path.split('\\')[-1]
    else:
        p = complete_path.split('/')[-1]

    return p


def numFeature_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("Atleast two frames must have atleast 8 features.")
    msgBox.setWindowTitle("Number of Features")
    msgBox.setStandardButtons(QMessageBox.Ok)                 
    returnValue = msgBox.exec()
    
    
def getFocalLengthPixels(focal_length_mm, sensor_size_mm, sensor_size_px):
    return (focal_length_mm * sensor_size_px) / sensor_size_mm;


def estimateKMatrix(width_in_pixel, height_in_pixel, focal_length_in_mm = 35, sensor_width_in_mm = 4.8, sensor_height_in_mm = 3.6):
    K = np.zeros((3,3))
        
    K[0,0] = getFocalLengthPixels(focal_length_in_mm, sensor_width_in_mm, width_in_pixel)
    K[1,1] = getFocalLengthPixels(focal_length_in_mm, sensor_height_in_mm, height_in_pixel)
    K[2,2] = 1.0
    
    K[0,2] = width_in_pixel // 2
    K[1,2] = height_in_pixel // 2
    return K

def normalize(pts):
    n = pts.shape[0]
    pts_mean = np.mean(pts, axis=0)
    acc = 0
    for i in range(n):
        acc = acc + np.sqrt(np.square(pts[i,0]-pts_mean[0]) + np.square(pts[i,1]-pts_mean[1]))
    s = acc/(n*np.sqrt(2))
    normalized = np.zeros(shape=(n,2), dtype=int)
    for i in range(n):
        normalized[i,0] = int((pts[i,0] - pts_mean[0])/s)
        normalized[i,1] = int((pts[i,1] - pts_mean[1])/s)
        
    return normalized




def distance_F(line, pt):
    numer = abs(np.sum(np.multiply(line, pt)))
    denom = np.sqrt(np.square(line[0]) + np.square(line[1]))
    res = np.square(numer/denom)
    return res


def visualize(pts1, pts2, pts3d, labels, display_bool = True):
    if display_bool:
        fig1, ax1 = plt.subplots()
        ax1.scatter(pts1[:, 0], -1*pts1[:, 1], color='b', marker='+')
        ax1.scatter(pts2[:, 0], -1*pts2[:, 1], color='r', marker='o')
        for i in range(pts1.shape[0]):
            ax1.annotate(str(labels[i]+1), (pts1[i,0], -1*pts1[i,1]))
            ax1.annotate(str(labels[i]+1), (pts2[i,0], -1*pts2[i,1]))
            
        # plt
        plt.title('Observed points')
        plt.show()
        
        fig2 = plt.figure()
        ax = fig2.add_subplot(111, projection='3d')
        ax.scatter(pts3d[:, 0], pts3d[:, 1], pts3d[:, 2])
        for i in range(pts3d.shape[0]):
            ax.text(pts3d[i, 0], pts3d[i, 1], pts3d[i, 2], str(labels[i]+1))
        plt.title('Projected 3d Points')
        plt.show()
        



