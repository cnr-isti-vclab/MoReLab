#
#Copyright (C) 2020-2021 ISTI-CNR
#Licensed under the BSD 3-Clause Clear License (see license.txt)
#

"""
Copyright (c) 2020-2021 ISTI-CNR
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

        * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
        * Neither the name of ISTI-CNR nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""



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
        self.measured_pos_regular = []
        self.measured_pos_network = []
        self.measured_distances_regular = []
        self.measured_distances_network = []
        
        
        self.n_objects_kf_regular = []
        self.features_regular = []
        self.hide_regular = []
        self.rect_groups_regular = []
        self.quad_groups_regular = []
        self.cylinder_groups_regular = []
        self.curve_groups_regular = []
        self.curve_pts_regular = []
        self.curve_3d_point_regular = []
        
        self.n_objects_kf_network = []
        self.features_network = []
        self.hide_network = []
        self.rect_groups_network = []
        self.quad_groups_network = []
        self.cylinder_groups_network = []
        self.curve_groups_network = []
        self.curve_pts_network = []
        self.curve_3d_point_network = []
        
        self.summary = ""

    
    def video_summary(self):
        self.fps = round(self.cap.get(cv2.CAP_PROP_FPS))
        self.n_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = round(self.n_frames/self.fps, 2)
        success, frame_cv = self.cap.read()
        if success:
            self.height, self.width, _ = frame_cv.shape


    def extract_frames_regularly(self, sampling_rate):
        self.key_frames_regular = []
        self.key_frame_indices_regular = []
        self.measured_pos_regular = []
        self.measured_distances_regular = []
        self.n_objects_kf_regular = []
        self.features_regular = []
        self.hide_regular = []
        self.rect_groups_regular = []
        self.quad_groups_regular = []
        self.cylinder_groups_regular = []
        self.curve_groups_regular = []
        self.curve_pts_regular = []
        self.curve_3d_point_regular = []
        
        self.cap = cv2.VideoCapture(self.video_path)
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
            self.measured_pos_regular.append([])
            self.measured_distances_regular.append([])
            self.features_regular.append([])
            self.hide_regular.append([])
            self.rect_groups_regular.append([])
            self.quad_groups_regular.append([])
            self.cylinder_groups_regular.append([])
            self.curve_groups_regular.append([])
            self.curve_pts_regular.append([])
            self.curve_3d_point_regular.append([])
    
    
    
    # ========================== Network Implementation =======================
    
    def luma(self, img, bBGR = False):
        r, c, col = img.shape
        if col == 3:
            if bBGR:
                return 0.299 * img[:, :, 2] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 0]
            else:
                return 0.299 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2]
        else:
            return []
        
    def writeCV2(self, img, filename, bBGR = True):
        if bBGR:
            out = np.zeros(img.shape, dtype = np.float32)
            out[:,:,0] = img[:,:,2]
            out[:,:,1] = img[:,:,1]
            out[:,:,2] = img[:,:,0]
            img = out

        cv2.imwrite(filename, self.fromFloatToUint8(img))
        
    def checkLaplaicanBluriness(self, img, thr = 100.0):
        L = self.luma(img)
        value = cv2.Laplacian(L, cv2.CV_32F).var()
        return (value > thr), value
    
    def fromFloatToUint8(self, img):
        formatted = (img * 255).astype('uint8')
        return formatted
    
    
    def checkSimilarity(self, img1, img2, thr = 0.925, bBGR = False):

        if(thr < 0.0):
            thr = 0.925

        ssim_none = ssim(self.luma(img1, bBGR), self.luma(img2, bBGR), data_range=1.0, multichannel = False)
        return (ssim_none >= thr), ssim_none
    
    def checkMTB(self, img1, img2, thr = 4, bBGR = False):
        gray1_u8 = self.fromFloatToUint8(self.luma(img1, bBGR))
        gray2_u8 = self.fromFloatToUint8(self.luma(img2, bBGR))
        mtb = cv2.createAlignMTB()
        shift = mtb.calculateShift(gray1_u8, gray2_u8)
        len = np.sqrt(shift[0] * shift[0] + shift[1] * shift[1])
        return len < thr, len
    
    def setFrame(self, frame):
                    
        if (frame > -1):
            frame = frame % self.n
            
            self.counter = frame
            
            if (self.cap != []):
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
    
    
    def getNextFrame(self, frame = -1, bBGR = True):
        self.setFrame(frame)
        
        counter = self.counter
    
        success, frame_cv = self.cap.read()
        
        if success and bBGR:
            frame = np.zeros(frame_cv.shape, dtype = np.float32)
            frame[:,:,0] = frame_cv[:,:,2]
            frame[:,:,1] = frame_cv[:,:,1]
            frame[:,:,2] = frame_cv[:,:,0]
        else:
            frame = frame_cv
        self.counter = (self.counter + 1) % self.n_frames

        return success, frame, counter, frame_cv

            
    def cleanSequence(self, shift_threshold = 8, bBGR = False, bSave = True, folder_out = 'images', name_base = 'frame'):
        self.cap = cv2.VideoCapture(self.video_path)
        # print("Extracting frames by network")
        n = self.n_frames
        # print("n : "+str(n))
        self.key_frames_network = []
        self.key_frame_indices_network = []
        self.measured_pos_network = []
        self.measured_distances_network = []
        self.n_objects_kf_network = []
        self.features_network = []
        self.hide_network = []
        self.rect_groups_network = []
        self.quad_groups_network = []
        self.cylinder_groups_network = []
        self.curve_pts_network = []
        self.curve_3d_point_network = []



        c = 0
        id_list = []
        lst = []
        self.counter = 0
        
        lap = False
        threshold = 15.0
        while lap == False:
            success, img, j, img_cv = self.getNextFrame()
            if (success == False) or (j >= (n - 1)):
                break
            lap, value = self.checkLaplaicanBluriness(img, threshold)
        self.key_frame_indices_network.append(j)
        self.key_frames_network.append(img_cv)
        
        # if bSave:
        #     writeCV2(img / 255.0, folder_out + '/' + name_base + '_' + format(j,'06d') + '.jpg')
    
        if shift_threshold < 0:
            shape_max = np.max(img.shape)
            shift_threshold = np.max([8, np.round(shape_max / 40.0)])
    
        # print('Threshold: ' + str(shift_threshold))
        
        while(j < (n - 1)):
            
            lap = False
            while (lap == False):
                success, img_n, k, img_n_cv = self.getNextFrame()
                if (success == False) or (k >= (n - 1)):
                    j = n + 1
                    break
                lap, value = self.checkLaplaicanBluriness(img_n, threshold)
    
            if success:
                removed_str = ' removed '
                bTest1, ssim = self.checkSimilarity(img, img_n, 0.925, bBGR)
                tmp = " "
                
                if(bTest1 == False):
            
                    bTest2, shift = self.checkMTB(img, img_n, shift_threshold, bBGR)
                    tmp += "Shift: " + str(shift) + " "
    
                    if(bTest2 == False):
                        img = img_n
                        j = k
                        self.key_frame_indices_network.append(str(j-1).zfill(6))
                        self.key_frames_network.append(img_n_cv)
    
                # print('Ref: ' + str(j) + ' Cur: ' + str(k) + removed_str + " SSIM: " + str(ssim) + tmp)
        
        self.init_features_network(len(self.key_frames_network))
        self.cap.release()
        
    
    
    
    def init_features_network(self, n):        
        for i in range(n):
            self.n_objects_kf_network.append(0)
            self.measured_pos_network.append([])
            self.measured_distances_network.append([])
            self.features_network.append([])
            self.hide_network.append([])
            self.rect_groups_network.append([])
            self.quad_groups_network.append([])
            self.cylinder_groups_network.append([])
            self.curve_groups_network.append([])
            self.curve_pts_network.append([])
            self.curve_3d_point_network.append([])


