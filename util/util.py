"""
Created on Wed Mar 30 17:55:40 2022
@author: arslan
"""

# Sample and save every tenth frame

import cv2, os
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt



class Video:
    def __init__(self, video_path):
        self.video_path = video_path
        self.output_imgs_dir = 'extracted_images'
        self.cap = cv2.VideoCapture(self.video_path)
        self.images = []

    def extract_frames_regularly(self):
        if not os.path.exists(self.output_imgs_dir):
            os.makedirs(self.output_imgs_dir)
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
    
    def video_summary(self):
        self.fps = round(self.cap.get(cv2.CAP_PROP_FPS))
        self.n_frames = int(self.cap.get(cv2. CAP_PROP_FRAME_COUNT))
        self.duration = int(self.n_frames/self.fps)
        success, frame_cv = self.cap.read()
        if success:
            self.height, self.width, _ = frame_cv.shape
        txt = "Video Summary: \n\nFPS: "+str(self.fps)+"\nNumber of Frames: "+str(self.n_frames)+ \
            "\nLength: "+str(self.duration) +" sec.\nResolution: "+str(self.width)+" X "+str(self.height)
        return txt
    
    
def convert_cv_qt(cv_img, width, height):
    """Convert from an opencv image to QPixmap"""
    rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    p = convert_to_Qt_format.scaled(width, height, Qt.KeepAspectRatio)
    return QPixmap.fromImage(p)

        
        
    
