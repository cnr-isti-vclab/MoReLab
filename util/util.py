"""
Created on Wed Mar 30 17:55:40 2022
@author: arslan
"""

# Sample and save every tenth frame

import cv2, os




class Video:
    def __init__(self, video_path):
        self.video_path = video_path
        self.output_imgs_dir = 'extracted_images'
        self.cap = []
        self.images = []

    def extract_frames_regularly(self):
        if not os.path.exists(self.output_imgs_dir):
            os.makedirs(self.output_imgs_dir)
        self.cap = cv2.VideoCapture(self.video_path)
        count = 0
        success = True
        while success:
            if count % 10 == 0:
                success, frame_cv = self.cap.read()
                if not success:
                    break
                self.images.append(frame_cv)
                # out_img_path = os.path.join(self.output_imgs_dir, str(count).zfill(5)+'.png')
                # cv2.imwrite(out_img_path, frame_cv)
            count = count + 1
        return self.images
        
        
    
