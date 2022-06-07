from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import platform
import numpy as np
import matplotlib.pyplot as plt
from numpy import *
from scipy import linalg



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
    pts = np.float32(pts)
    n = pts.shape[0]
    pts_mean = np.mean(pts, axis=0)
    acc = 0
    for i in range(n):
        acc = acc + np.sqrt(np.square(pts[i,0]-pts_mean[0]) + np.square(pts[i,1]-pts_mean[1]))
    s = acc/(n*np.sqrt(2))
    normalized = np.zeros(shape=(n,2), dtype=float)
    for i in range(n):
        normalized[i,0] = (pts[i,0] - pts_mean[0])/s
        normalized[i,1] = (pts[i,1] - pts_mean[1])/s
        
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
        ax1.scatter(pts2[:, 0], pts2[:, 1], color='r', marker='o')
        for i in range(pts1.shape[0]):
            ax1.annotate(str(labels[i]+1), (pts1[i,0], -1*pts1[i,1]))
            ax1.annotate(str(labels[i]+1), (pts2[i,0], pts2[i,1]))
            
        # plt
        plt.title('Observed points')
        plt.show()
        
        # fig2 = plt.figure()
        # ax = fig2.add_subplot(111, projection='3d')
        # ax.scatter(pts3d[:, 0], pts3d[:, 1], pts3d[:, 2])
        # for i in range(pts3d.shape[0]):
        #     ax.text(pts3d[i, 0], pts3d[i, 1], pts3d[i, 2], str(labels[i]+1))
        # plt.title('Projected 3d Points')
        # plt.show()



def compute_fundamental(x1,x2):
    """    Computes the fundamental matrix from corresponding points 
        (x1,x2 3*n arrays) using the 8 point algorithm.
        Each row in the A matrix below is constructed as
        [x'*x, x'*y, x', y'*x, y'*y, y', x, y, 1] """
    
    n = x1.shape[1]
    if x2.shape[1] != n:
        raise ValueError("Number of points don't match.")
    
    # build matrix for equations
    A = zeros((n,9))
    for i in range(n):
        A[i] = [x1[0,i]*x2[0,i], x1[0,i]*x2[1,i], x1[0,i]*x2[2,i],
                x1[1,i]*x2[0,i], x1[1,i]*x2[1,i], x1[1,i]*x2[2,i],
                x1[2,i]*x2[0,i], x1[2,i]*x2[1,i], x1[2,i]*x2[2,i] ]
            
    # compute linear least square solution
    U,S,V = linalg.svd(A)
    F = V[-1].reshape(3,3)
        
    # constrain F
    # make rank 2 by zeroing out last singular value
    U,S,V = linalg.svd(F)
    S[2] = 0
    F = dot(U,dot(diag(S),V))
    
    return F/F[2,2]

        
        
def compute_fundamental_normalized(x1,x2):
    """    Computes the fundamental matrix from corresponding points 
        (x1,x2 3*n arrays) using the normalized 8 point algorithm. """

    print(x1.shape)
    print(x2.shape)
    
    n = x1.shape[1]
    if x2.shape[1] != n:
        raise ValueError("Number of points don't match.")

    # normalize image coordinates
    x1 = x1 / x1[2]
    mean_1 = mean(x1[:2],axis=1)
    S1 = sqrt(2) / std(x1[:2])
    T1 = array([[S1,0,-S1*mean_1[0]],[0,S1,-S1*mean_1[1]],[0,0,1]])
    x1 = dot(T1,x1)
    
    x2 = x2 / x2[2]
    mean_2 = mean(x2[:2],axis=1)
    S2 = sqrt(2) / std(x2[:2])
    T2 = array([[S2,0,-S2*mean_2[0]],[0,S2,-S2*mean_2[1]],[0,0,1]])
    x2 = dot(T2,x2)

    # compute F with the normalized coordinates
    F = compute_fundamental(x1,x2)

    # reverse normalization
    F = dot(T1.T,dot(F,T2))

    return F/F[2,2]


def skew(a):
    """ Skew matrix A such that a x v = Av for any v. """
    return array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])



def compute_epipole(F):
    """ Computes the (right) epipole from a 
        fundamental matrix F. 
        (Use with F.T for left epipole.) """
    
    # return null space of F (Fx=0)
    U,S,V = linalg.svd(F)
    e = V[-1]
    return e/e[2]



def compute_P_from_fundamental(F):
    """    Computes the second camera matrix (assuming P1 = [I 0]) 
        from a fundamental matrix. """
        
    e = compute_epipole(F.T) # left epipole
    Te = skew(e)
    return vstack((dot(Te,F.T).T,e)).T



def compute_parameters(projection_matrix):
    Q = projection_matrix[:,:3]
    b = projection_matrix[:,-1]
    b = b.reshape(3,1)

    translation = np.dot((LA.inv(-Q)),b)

    Qinv = np.linalg.inv(Q)
    Rt,Kinv = np.linalg.qr(Qinv)

    intrinsic = np.linalg.inv(Kinv)
    intrinsic_n = intrinsic/intrinsic[2,2]
    #intrinsic_n[0,1] = 0
    rotation = np.transpose(Rt)

    return abs(intrinsic_n), rotation, translation


def triangulate_point(x1,x2,P1,P2):
    """ Point pair triangulation from 
        least squares solution. """
        
    M = zeros((6,6))
    M[:3,:4] = P1
    M[3:,:4] = P2
    M[:3,4] = -x1
    M[3:,5] = -x2

    U,S,V = linalg.svd(M)
    X = V[-1,:4]

    return X / X[3]


def triangulate(x1,x2,P1,P2):
    n = x1.shape[1]
    if x2.shape[1] != n:
        raise ValueError("Number of points don't match.")

    X = [ triangulate_point(x1[:,i],x2[:,i],P1,P2) for i in range(n)]
    return array(X)[:,:3]



def compute_parameters(projection_matrix):
    Q = projection_matrix[:,:3]
    b = projection_matrix[:,-1]
    b = b.reshape(3,1)

    translation = np.dot((np.linalg.inv(-Q)),b)

    Qinv = np.linalg.inv(Q)
    Rt,Kinv = np.linalg.qr(Qinv)

    intrinsic = np.linalg.inv(Kinv)
    intrinsic_n = intrinsic/intrinsic[2,2]
    #intrinsic_n[0,1] = 0
    rotation = np.transpose(Rt)

    return abs(intrinsic_n), rotation, translation


def reprojection_error(projection_matrix, rotation, translation, data):
    Q = projection_matrix[:,:3]
    Qinv = np.linalg.inv(Q)
    Rt,Kinv = np.linalg.qr(Qinv)
    intrinsic = np.linalg.inv(Kinv)

    f=np.dot(intrinsic, rotation)
    s = np.dot(-Q,translation)
    pcon = np.hstack((f,s))

    wp = data
    image_points = np.dot(pcon, wp.T).T
    image_points = image_points/image_points[:,2].reshape(-1,1)
    print(image_points.shape)
    print("\nProjected points are:")
    print(image_points)
    return image_points

def compute_P_from_essential(E):
    """    Computes the second camera matrix (assuming P1 = [I 0]) 
        from an essential matrix. Output is a list of four 
        possible camera matrices. """
    
    # make sure E is rank 2
    U,S,V = linalg.svd(E)
    if linalg.det(dot(U,V))<0:
        V = -V
    E = dot(U,dot(diag([1,1,0]),V))    
    
    # create matrices (Hartley p 258)
    Z = skew([0,0,-1])
    W = array([[0,-1,0],[1,0,0],[0,0,1]])
    
    # return all four solutions
    P2 = [vstack((dot(U,dot(W,V)).T,U[:,2])).T,
             vstack((dot(U,dot(W,V)).T,-U[:,2])).T,
            vstack((dot(U,dot(W.T,V)).T,U[:,2])).T,
            vstack((dot(U,dot(W.T,V)).T,-U[:,2])).T]

    return P2

