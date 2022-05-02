from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class KF_dialogue(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Key-frame extraction panel")
        self.kf_met = ""

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.cb = QComboBox()
        self.kf_methods = ["-- Choose frame extraction technique --", "Network", "Regular"]
        self.cb.addItems(self.kf_methods)
        self.cb.currentIndexChanged.connect(self.selectionchange)
        self.layout.addWidget(self.cb)
        
        self.setLayout(self.layout)
        
    def selectionchange(self):
        self.kf_met = self.cb.currentText()
        if self.kf_met == "Regular":
            self.e1 = QLineEdit()
            self.e1.setValidator(QIntValidator())
            self.e1.setMaxLength(6)
            self.e1.setFont(QFont("Arial",20))
            
            label = QLabel("Enter sampling rate : ")
            h = QHBoxLayout()
            h.addWidget(label)
            h.addWidget(self.e1)
            self.layout.addLayout(h)
            self.layout.addWidget(self.buttonBox)
        else:
            self.layout.addWidget(self.buttonBox)
            
            
            
            
class Feature_Dialogue(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Feature Label")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        label = QLabel("Enter the label of feature point.")
        
        self.e2 = QLineEdit()
        self.e2.setValidator(QIntValidator())
        self.e2.setMaxLength(6)
        self.e2.setFont(QFont("Arial",15))
        
        h_layout.addWidget(label)
        h_layout.addWidget(self.e2)
        
        layout.addLayout(h_layout)
        layout.addWidget(self.buttonBox)
        
        self.setLayout(layout)
        
        
def duplicate_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("This feature label already exists on this frame. Please give another label.")
    msgBox.setWindowTitle("Features with duplicate labels")
    msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    # msgBox.buttonClicked.connect(msgButtonClick)
     
    returnValue = msgBox.exec()
    
    
def increment_dialogue():
    msgBox = QMessageBox()
    msgBox.setText("This feature label is too high. Please use the next increment number for new feature label.")
    msgBox.setWindowTitle("Too high Feature label")
    msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    # msgBox.buttonClicked.connect(msgButtonClick)
     
    returnValue = msgBox.exec()