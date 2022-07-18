from scipy.optimize import least_squares
from util.sfm import estimateKMatrix
import numpy as np
import cv2





def cost_cipolla(X, Fs, case='1'):
    K = np.array([[X[0], X[1], X[2]],
                   [0,   X[3], X[4]],
                   [0,      0,   1]])

    E = []
    
    
    N = Fs.shape[2]
    
    Den = N*(N-1)/2; # For N Images we can find N(N-1)/2 Fundamental Matrix
    
    # Compute the Cost using Mendonca & Cipolla's Equation
    for i in range(N):
        for j in range(i+1,N):
            # print("Index i: "+str(i)+' index j : '+str(j))
            
            # Compute the Essential Matrix 'EM'
            EM = np.dot(np.dot(K.transpose(), Fs[:,:,i,j]),  K)
            # EM = F[:,:,i,j]
            
            # Compute SVD of Essential Matrix
            [_,D,_] = np.linalg.svd(EM);
            
            # Singular Values (3rd value, D(3,3) is 0)
            r = D[0];
            s = D[1];
            
            # Compute Cost
            if case == '1':
                # Use the  Mendonca & Cipolla's Equation-1
                E1 = (1/Den) * ((r - s)/s);
            elif case=='2':
                # Use the  Mendonca & Cipolla's Equation-2
                E1 = (1/Den) * ((r - s)/(r + s));
            
            # Append Computed Cost
            E.append(E1);
    E = np.asarray(E)
    # print("======================")
    # print(E)
    return E


def find_optimized_K(all_pts, K_init, case='2'):
    n_imgs = len(all_pts)
    Fs = np.zeros(shape=(3,3,n_imgs,n_imgs))
    
    for i in range(n_imgs):
        for j in range(n_imgs):
            F, mask = cv2.findFundamentalMat(all_pts[i],all_pts[j], cv2.FM_8POINT)
            Fs[:,:,i,j] = F
    
    print("Initial Intrinsic matrix:")
    print(K_init)
    
    x0 = [K_init[0,0], K_init[0,1], K_init[0,2], K_init[1,1], K_init[1,2]]
    # print(x0)
    result = least_squares(cost_cipolla, x0, verbose=1, args=(Fs, case), method='trf')
    
    x_opt = result['x']
    K = np.array([[x_opt[0], x_opt[1], x_opt[2]],
                  [  0,      x_opt[3], x_opt[4]],
                  [  0,          0,          1]])
    print("Final Intrinsic matrix through "+case+":")
    print(K)
    return K
    