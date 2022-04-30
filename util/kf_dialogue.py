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
            
            
            
            
class feature_dialogue(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Feature Label")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        label = QLabel("Enter the label of feature point.")
        
        e2 = QLineEdit()
        e2.setValidator(QIntValidator())
        e2.setMaxLength(6)
        e2.setFont(QFont("Arial",10))
        
        layout.addWidget(label)
        layout.addWidget(e2)
        
        self.setLayout(layout)