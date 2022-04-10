"""
Created on Wed Mar 30 17:55:40 2022
@author: arslan
"""

# Sample and save every tenth frame

import cv2, os
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets



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


class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)

        
        
    
