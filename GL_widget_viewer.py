from PyQt5 import QtCore      # core Qt functionality
from PyQt5 import QtGui       # extends QtCore with GUI functionality
from PyQt5 import QtOpenGL    # provides QGLWidget, a special OpenGL QWidget

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


import OpenGL.GL as gl        # python wrapping of OpenGL
from OpenGL import GLU        # OpenGL Utility Library, extends OpenGL functionality

import sys                    # we'll need this later to run our Qt application

from OpenGL.arrays import vbo
import numpy as np


class GL_Widget(QtOpenGL.QGLWidget):
# class GL_Widget(QWidget):
    def __init__(self):
        # QWidget.__init__(self, parent)
        # self.setStyleSheet('background=None')
        QtOpenGL.QGLWidget.__init__(self)
        # gui_layout = QVBoxLayout()
        # gui_layout.addWidget(self)
        # self.setLayout(gui_layout)
        

    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(200, 200, 200))    # initialize the screen to blue
        gl.glEnable(gl.GL_DEPTH_TEST)                  # enable depth testing

        self.initGeometry()

        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0
         
    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect = width / float(height)

        GLU.gluPerspective(45.0, aspect, 1.0, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glPushMatrix()    # push the current matrix to the current stack

        gl.glTranslate(0.0, 0.0, -50.0)    # third, translate cube to specified depth
        gl.glScale(20.0, 20.0, 20.0)       # second, scale cube
        gl.glRotate(self.rotX, 1.0, 0.0, 0.0)
        gl.glRotate(self.rotY, 0.0, 1.0, 0.0)
        gl.glRotate(self.rotZ, 0.0, 0.0, 1.0)
        gl.glTranslate(-0.5, -0.5, -0.5)   # first, translate cube center to origin

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, self.vertVBO)
        gl.glColorPointer(3, gl.GL_FLOAT, 0, self.colorVBO)

        gl.glDrawElements(gl.GL_QUADS, len(self.cubeIdxArray), gl.GL_UNSIGNED_INT, self.cubeIdxArray)

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)

        gl.glPopMatrix()    # restore the previous modelview matrix
        
    def initGeometry(self):
        self.cubeVtxArray = np.array(
                [[0.0, 0.0, 0.0],
                 [1.0, 0.0, 0.0],
                 [1.0, 1.0, 0.0],
                 [0.0, 1.0, 0.0],
                 [0.0, 0.0, 1.0],
                 [1.0, 0.0, 1.0],
                 [1.0, 1.0, 1.0],
                 [0.0, 1.0, 1.0]])
        self.vertVBO = vbo.VBO(np.reshape(self.cubeVtxArray,
                                          (1, -1)).astype(np.float32))
        self.vertVBO.bind()
        
        self.cubeClrArray = np.array(
                [[0.0, 0.0, 0.0],
                 [1.0, 0.0, 0.0],
                 [1.0, 1.0, 0.0],
                 [0.0, 1.0, 0.0],
                 [0.0, 0.0, 1.0],
                 [1.0, 0.0, 1.0],
                 [1.0, 1.0, 1.0],
                 [0.0, 1.0, 1.0 ]])
        self.colorVBO = vbo.VBO(np.reshape(self.cubeClrArray,
                                           (1, -1)).astype(np.float32))
        self.colorVBO.bind()

        self.cubeIdxArray = np.array(
                [0, 1, 2, 3,
                 3, 2, 6, 7,
                 1, 0, 4, 5,
                 2, 1, 5, 6,
                 0, 3, 7, 4,
                 7, 6, 5, 4 ])

    def setRotX(self, val):
        self.rotX = np.pi * val

    def setRotY(self, val):
        self.rotY = np.pi * val

    def setRotZ(self, val):
        self.rotZ = np.pi * val













































# from pyqtgraph.opengl import GLViewWidget
# import pyqtgraph as pg
# from PyQt5.QtWidgets import *
# from PyQt5 import QtGui
# import OpenGL
# import numpy as np

# from OpenGL.GL import *
# from OpenGL.GLUT import *
# from OpenGL.GLU import *



# import pygame


# width=500
# height=500

# class GL_Widget(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setStyleSheet("background: transparent")
#         # self.image = QtGui.QImage(np.zeros((width,height,3)), width, height, QtGui.QImage.Format_RGB32)
    
    
#     def display(self):
#         pygame.init()
#         surface = pygame.Surface((width, height))
#         surface.fill((0,0,0, 0))
        
#         w=surface.get_width()
#         h=surface.get_height()
    
#         pygame.draw.circle(surface, (255, 0, 0, 200), (150, 150), 20)
#         self.data=surface.get_buffer().raw
#         self.image=QtGui.QImage(self.data,w,h,QtGui.QImage.Format_RGB32)
#         # self.image = QtGui.QImage(img, width, height, QtGui.QImage.Format_RGB32)
    
#     def paintEvent(self,event):
#         qp=QtGui.QPainter()
#         qp.begin(self)
#         qp.drawImage(width / 7, height / 6, self.image)
#         qp.end()
    
    
    
    
    
    
    
    
        
    # def display1(self):
    #     pygame.init()
    #     display = pygame.Surface((width, height))
    #     display.fill((0,0,0, 0))
    #     # display = pygame.display.set_mode((800, 600), pygame.DOUBLEBUF|pygame.OPENGL)
        
    #     clock = pygame.time.Clock()
    #     FPS = 60


    #     VERTEX_SHADER_SOURCE = '''
    #         #version 330 core
    #         layout (location = 0) in vec3 aPos;
            
    #         void main()
    #         {
    #             gl_Position = vec4(aPos, 1.0);
    #         }
    #     '''

    #     FRAGMENT_SHADER_SOURCE = '''
    #         #version 330 core

    #         out vec4 fragColor;
    #         void main()
    #         {
    #             fragColor = vec4(1.0f, 0.0f, 0.0f, 1.0f);
    #         }
    #     '''

    #     #  (x, y, z)
    #     vertices = [
    #         -0.5, -0.5, 0.0,
    #         0.5, -0.5, 0.0,
    #         0.0, 0.5, 0.0,
    #     ]
    #     vertices = (GLfloat * len(vertices))(*vertices)

    #     # we created program object 
    #     program = glCreateProgram()

    #     # we created vertex shader
    #     vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    #     # we passed vertex shader's source to vertex_shader object
    #     glShaderSource(vertex_shader, VERTEX_SHADER_SOURCE)
    #     # and we compile it
    #     glCompileShader(vertex_shader)


    #     # we created fragment shader
    #     fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    #     # we passed fragment shader's source to fragment_shader object
    #     glShaderSource(fragment_shader, FRAGMENT_SHADER_SOURCE)
    #     # and we compile it
    #     glCompileShader(fragment_shader)

    #     # attach these shaders to program
    #     glAttachShader(program, vertex_shader)
    #     glAttachShader(program, fragment_shader)

    #     # link the program
    #     glLinkProgram(program)

    #     # create vbo object
    #     vbo = None
    #     vbo = glGenBuffers(1, vbo)

    #     # enable buffer(VBO)
    #     glBindBuffer(GL_ARRAY_BUFFER, vbo)

    #     # send the data  
    #     glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW)

    #     # create vao object
    #     vao = None
    #     vao = glGenVertexArrays(1, vao)

    #     # enable VAO and then finally binding to VBO object what we created before.
    #     glBindVertexArray(vao)

    #     # we activated to the slot of position in VAO (vertex array object)
    #     glEnableVertexAttribArray(0)

    #     # explaining to the VAO what data will be used for slot 0 (position slot) 
    #     glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), c_void_p(0))
    #     running=True
    #     while running:
    #         for event in pygame.event.get():
    #             if event.type == pygame.QUIT:
    #                 pygame.quit()
    #                 running=False

    #         if running:
    #             glClearColor(1.0, 0.6, 0.0, 1.0)
    #             glClear(GL_COLOR_BUFFER_BIT)
            
    #             glUseProgram(program)
    #             glBindVertexArray(vao)
    #             glDrawArrays(GL_TRIANGLES, 0, 3)
                
    #             pygame.display.flip()
    #             clock.tick(FPS)