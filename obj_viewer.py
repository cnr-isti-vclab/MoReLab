from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *

from OpenGL.GL import *
from OpenGL.GLU import *
import open3d as o3d
import numpy as np
from util.sfm import scale_data



class GT_Widget(QOpenGLWidget):
    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)

        timer = QTimer(self)
        timer.setInterval(10)   # period, in milliseconds
        timer.timeout.connect(self.update)
        timer.start()

        self.setFocusPolicy(Qt.StrongFocus)
        self.showMaximized()
        
        mesh = o3d.io.read_triangle_mesh('gl.obj')
        X = np.array(mesh.vertices)
        self.data = scale_data(50, 250, 50, 250, 0, 100, X)
        
        
        
    def initializeGL(self):
        glClearDepth(1.0)
        glClearColor(0.8, 0.8, 0.8, 1)
        glEnable(GL_DEPTH_TEST)
        
        self.transX = 0.0
        self.transY = 0.0
        self.transZ = 0.0
        self.last_transX = 0.0
        self.last_transY = 0.0
        self.last_transZ = 0.0
        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0
    

    
    def setRotX(self, val):
        self.rotX = val*(np.pi/8)
    
    def setRotY(self, val):
        self.rotY = val*(np.pi/8)
    
    def setRotZ(self, val):
        self.rotZ = val*(np.pi/8)
        
    def setTransX(self, val):
        self.transX = val - self.last_transX
        self.last_transX = val
    
    def setTransY(self, val):
        self.transY = val - self.last_transY
        self.last_transY = val
    
    def setTransZ(self, val):
        self.transZ = val - self.last_transZ
        self.last_transZ = val

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = float(width) / float(height)
        # gluPerspective(45.0, aspect, -1, 1.0)
        glOrtho(0, width, height, 0, -1000, 1000)
        glMatrixMode(GL_MODELVIEW)
        
    def paintGL(self):        
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT | GL_ACCUM_BUFFER_BIT)
        
        


        glRotate(self.rotX, 1.0, 0.0, 0.0)
        glRotate(self.rotY, 0.0, 1.0, 0.0)
        glRotate(self.rotZ, 0.0, 0.0, 1.0)
        
        glTranslate(self.transX, self.transY, self.transZ)
        
        self.rotX, self.rotY, self.rotZ = 0, 0, 0
        self.transX, self.transY, self.transZ = 0, 0, 0

        # glPushMatrix()
        glPointSize(2)
        glBegin(GL_POINTS)
        
        for i in range(self.data.shape[0]):
            glColor3f(0.0, 0.0, 0.0)
            glVertex3f(self.data[i,0], self.data[i,1], self.data[i,2])
        glEnd()
        # glPopMatrix()>
        
        
        
