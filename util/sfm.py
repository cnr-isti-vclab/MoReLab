import numpy as np
import matplotlib.pyplot as plt
from numpy import *
from scipy import linalg
import cv2
  
  
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


def skew(a):
    """ Skew matrix A such that a x v = Av for any v. """
    return array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])


def compute_P_from_essential(E):
    """    Computes the second camera matrix (assuming P1 = [I 0]) 
        from an essential matrix. Output is a list of four 
        possible camera matrices. """
    
    # make sure E is rank 2
    U,S,V = linalg.svd(E)
    m = S[:2].mean()
    if linalg.det(dot(U,V))<0:
        V = -V
    E = dot(U,dot(diag([m,m,0]),V))    
    
    # create matrices (Hartley p 258)
    Z = skew([0,0,-1])
    W = array([[0,-1,0],[1,0,0],[0,0,1]])
    
    # return all four solutions
    P2 = [vstack((dot(U,dot(W,V)).T,U[:,2])).T,
             vstack((dot(U,dot(W,V)).T,-U[:,2])).T,
            vstack((dot(U,dot(W.T,V)).T,U[:,2])).T,
            vstack((dot(U,dot(W.T,V)).T,-U[:,2])).T]

    return P2



def triangulate(P1, pts1, P2, pts2):
    Pw = []

    for i in range(pts1.shape[0]):
        A = np.array([   pts1[i,0]*P1[2,:] - P1[0,:] ,
                          pts1[i,1]*P1[2,:] - P1[1,:] ,
                          pts2[i,0]*P2[2,:] - P2[0,:] ,
                          pts2[i,1]*P2[2,:] - P2[1,:]   ])

        u, s, vh = np.linalg.svd(A)
        v = vh.T
        X = v[:,-1]
        X = X/X[-1]
        Pw.append(X)

    return np.asarray(Pw)
    

def project_2d(Pw, P1, P2):
    pts1_out = np.matmul(P1, Pw.T )
    pts2_out = np.matmul(P2, Pw.T )
    pts1_out = pts1_out.T
    pts2_out = pts2_out.T

    return pts1_out, pts2_out


def count_positives(pts1_out, pts2_out):
    count = 0
    for i in range(pts1_out.shape[0]):
        if (pts1_out[i, 2] >= 0 and pts2_out[i, 2] >=0):
            count = count + 1
            
    return count


def convert_homogeneity(Pw, pts1_out, pts2_out):
    # NON - HOMOGENIZING
    for i in range(pts1_out.shape[0]):
        pts1_out[i,:] = pts1_out[i,:]/pts1_out[i,2]
        pts2_out[i,:] = pts2_out[i,:]/pts2_out[i,2]
    pts1_out = pts1_out[:, :-1]
    pts2_out = pts2_out[:, :-1]
    # NON-HOMOGENIZING 3d points
    Pw = Pw[:, :-1]
    return Pw, pts1_out, pts2_out

def calc_reprojection_error(pts1, pts1_out, pts2, pts2_out):
    # CALCULATING REPROJECTION ERROR
    reprojection_err = 0
    for i in range(pts1_out.shape[0]):
        reprojection_err = reprojection_err  + np.linalg.norm( pts1[i,:] - pts1_out[i,:] )**2 + np.linalg.norm( pts2[i,:] - pts2_out[i,:] )**2
    return reprojection_err


def visualize2d(img1, img2, pts1, projected_pts1, pts2, projected_pts2, display_bool = True):
    if display_bool:
        for i in range(pts1.shape[0]):
            cv2.circle(img1, (int(pts1[i,0]+10), int(pts1[i,1]+10)), 5, (255, 0, 0), -1)
            cv2.circle(img1, (int(projected_pts1[i,0]+10), int(projected_pts1[i,1]+10)), 5, (0, 0, 255), -1)
            cv2.circle(img2, (int(pts2[i,0]+10), int(pts2[i,1]+10)), 5, (255, 0, 0), -1)
            cv2.circle(img2, (int(projected_pts2[i,0]+10), int(projected_pts2[i,1]+10)), 5, (0, 0, 255), -1)
        cv2.imshow("Image1", img1)
        cv2.imshow("Image2", img2)
        cv2.imwrite("01.png", img1)
        cv2.imwrite("02.png", img2)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def visualize3d(pts3d, labels):        
    fig2 = plt.figure()
    ax = fig2.add_subplot(111, projection='3d')
    ax.scatter(pts3d[:, 0], pts3d[:, 1], pts3d[:, 2])
    for i in range(pts3d.shape[0]):
        ax.text(pts3d[i, 0], pts3d[i, 1], pts3d[i, 2], str(labels[i]+1))
    plt.title('Projected 3d Points')
    plt.show()
    
    
def visualize(pts1, pts2, labels, display_bool = True):
    if display_bool:
        fig1, ax1 = plt.subplots()
        ax1.scatter(pts1[:, 0], pts1[:, 1], color='b', marker='o')
        for i in range(pts1.shape[0]):
            ax1.annotate(str(labels[i]+1), (pts1[i,0], pts1[i,1]))
            
        plt.title('1st image projected points')
        plt.show()
        
        fig2, ax2 = plt.subplots()
        ax2.scatter(pts2[:, 0], pts2[:, 1], color='b', marker='o')
        for i in range(pts2.shape[0]):
            ax2.annotate(str(labels[i]+1), (pts2[i,0], pts2[i,1]))
            
        plt.title('2nd image projected points')
        plt.show()
        
def normalize(pts1, pts2):
    pts1_norm = (pts1 - np.min(pts1))/(np.max(pts1)-np.min(pts1))
    pts2_norm = (pts2 - np.min(pts2))/(np.max(pts2)-np.min(pts2))
    
    return pts1_norm, pts2_norm
    
