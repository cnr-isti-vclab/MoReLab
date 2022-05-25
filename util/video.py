import cv2, os
import numpy as np
from skimage.metrics import structural_similarity as ssim


class Video:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(self.video_path)
        
        self.height = 0
        self.width = 0
        
        self.key_frames_regular = []
        self.key_frame_indices_regular = []
        self.key_frames_network = []
        self.key_frame_indices_network = []
        
        self.n_objects_kf_regular = []
        self.features_regular = []
        self.hide_regular = []
        
        self.n_objects_kf_network = []
        self.features_network = []
        self.hide_network = []
        
        self.summary = ""

    
    def video_summary(self):
        self.fps = round(self.cap.get(cv2.CAP_PROP_FPS))
        self.n_frames = int(self.cap.get(cv2. CAP_PROP_FRAME_COUNT))
        self.duration = round(self.n_frames/self.fps, 2)
        success, frame_cv = self.cap.read()
        if success:
            self.height, self.width, _ = frame_cv.shape


    def extract_frames_regularly(self, sampling_rate):
        # print("Extracting frames regularly")
        count = 0
        while self.cap.isOpened():
            success, frame_cv = self.cap.read()
            if not success:
                break
            if count % sampling_rate == 0:
                self.key_frames_regular.append(frame_cv)
                self.key_frame_indices_regular.append(str(count).zfill(6))
            count = count + 1
   
        self.init_features_regular(len(self.key_frames_regular))
        self.cap.release()

    
    def init_features_regular(self, n):        
        for i in range(n):
            self.n_objects_kf_regular.append(0)
            self.features_regular.append([])
            self.hide_regular.append([])
    
            
    def fromVideoFrameToNP(self, frame):
        frame = frame.astype(dtype = np.float32)
        frame = frame / 255.0
        out = np.zeros(frame.shape, dtype = np.float32)
        out[:,:,0] = frame[:,:,2]
        out[:,:,1] = frame[:,:,1]
        out[:,:,2] = frame[:,:,0]
        return out
    
    def fromFloatToUint8(self, img):
        formatted = (img * 255).astype('uint8')
        return formatted
    
    def checkMTB(self, img1, img2, thr = 4):
        gray1_u8 = self.fromFloatToUint8(self.luminance(img1))
        gray2_u8 = self.fromFloatToUint8(self.luminance(img2))
        mtb = cv2.createAlignMTB()
        shift = mtb.calculateShift(gray1_u8, gray2_u8)
        len = np.sqrt(shift[0] * shift[0] + shift[1] * shift[1])
        # print(len)
        return len < thr, len
    
    def luminance(self, img):
        r, c, col = img.shape
        if col == 3:
            return (img[:, :, 0] + img[:, :, 1] + img[:, :, 2]) / 3.0
        else:
            return []
    
    def checkSimilarity(self, img1, img2, thr = 0.925):
        
        if(thr < 0.0):
            thr = 0.925
    
        ssim_none = ssim(self.luminance(img1), self.luminance(img2), data_range=1.0, multichannel = False)
        # print(ssim_none)
        return (ssim_none >= thr), ssim_none
    
    def checkKeyPointBluriness(self, img, thr = 16):
        gray = self.luminance(img)
        gray_u8 = self.fromFloatToUint8(gray)
        orb = cv2.ORB_create()
        kp = orb.detect(gray_u8, None)
        len_kp = len(kp)
        kp, des = orb.compute(img, kp)
        
        return (len_kp >= thr), len_kp
            
    def cleanSequence(self, shift_threshold = 8):
        # print("Extracting frames by network")
        n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        bLoad = True
        j = 0
        lst_m = []
        lst_s = []
        bFirst = True
        
        while(j < (n - 1)):
            succces, img_cv = self.cap.read()
            
            if not succces:
                break

            bLoad = True
            img = self.fromVideoFrameToNP(img_cv)
            bFlag, nKey = self.checkKeyPointBluriness(img)
                
            j += 1
            bWhile = True
            
            
            while(bWhile and (j < (n - 1))):
                # print(j)
                j_old = j
                success, img_n_cv = self.cap.read()
                
                if not success:
                    j = n
                    break
                img_n = self.fromVideoFrameToNP(img_n_cv)
                
                bTest1, ssim = self.checkSimilarity(img, img_n)
                tmp = " "
                
                if(bTest1):
                    bWhile = True
                    j += 1
                else:
                    bTest2, shift = self.checkMTB(img, img_n, shift_threshold)
                    tmp += "Shift: " + str(shift) + " "
                    if(bTest2):
                        bWhile = True
                        j += 1
                    else:
                        # Key frame found.
                        bWhile = False
                        bLoad = False
                        img = img_n
                        self.key_frame_indices_network.append(str(j-1).zfill(6))
                        self.key_frames_network.append(img_n_cv)
                        # print("Index : "+str(j-1))

                if(bFirst):
                    bFirst = False
                    lst_m.append(j_old)
                    self.key_frame_indices_network.append(str(j-1).zfill(6))
                    self.key_frames_network.append(img_cv)
                    # print("First frame")
                    # print('Frame ' + str(j_old) + ' is kept')
        
        self.init_features_network(len(self.key_frames_network))
        self.cap.release()
        
    
    
    
    def init_features_network(self, n):        
        for i in range(n):
            self.n_objects_kf_network.append(0)
            self.features_network.append([])
            self.hide_network.append([])
    


