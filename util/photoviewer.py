from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
from tools import Tools



class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self.photoClicked.connect(self.get_mouse_pos)
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
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(200, 200, 200)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.obj = Tools(parent)

 

    def get_mouse_pos(self, p):
        return p


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
            # self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
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
                
                
    # def toggleDragMode(self):
    #     if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
    #         self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
    #     elif not self._photo.pixmap().isNull():
    #         self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def setNoDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            
            
    def setScrolDragMode(self):    
        if self.dragMode() == QtWidgets.QGraphicsView.NoDrag:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

        
    def convert_cv_qt(self, cv_img, width, height):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(width, height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
    
    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            p = self.mapToScene(event.pos()).toPoint()
            self.photoClicked.emit(p)

        super(PhotoViewer, self).mousePressEvent(event)
    
    
    def mouseDoubleClickEvent(self, event):
        if self._photo.isUnderMouse():
            p = self.mapToScene(event.pos()).toPoint()
            self.photoClicked.emit(p)
            self.obj.add_feature(p)
            
        super(PhotoViewer, self).mouseDoubleClickEvent(event)
        
    def keyPressEvent(self, event):
        super(PhotoViewer, self).keyPressEvent(event)
        if event.key() in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
            self.obj.delete_feature()

        
    # def mouseMoveEvent(self, event):
    #     if self._photo.isUnderMouse():
    #         p = self.mapToScene(event.pos()).toPoint()
    #         self.mouse_pos = p
    #         self.photoClicked.emit(p)

    #     super(PhotoViewer, self).mousePressEvent(event)

        

    
