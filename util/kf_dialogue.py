from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class KF_dialogue(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Key-frame extraction panel")
        self.kf_met = "Regular"

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.e1 = QLineEdit("10")
        self.e1.setValidator(QIntValidator())
        self.e1.setMaxLength(6)
        self.e1.setFont(QFont("Arial",20))
        
        self.label = QLabel("Enter sampling rate : ")
        self.h = QHBoxLayout()
        self.h.addWidget(self.label)
        self.h.addWidget(self.e1)
        
        self.cb = QComboBox()
        self.kf_methods = ["Regular", "Network"]
        self.cb.addItems(self.kf_methods)
        self.cb.currentIndexChanged.connect(self.selectionchange)
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.cb)
        self.layout.addLayout(self.h)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        
        
    def deleteItemsOfLayout(self, layout):
     if layout is not None:
         while layout.count():
             item = layout.takeAt(0)
             widget = item.widget()
             if widget is not None:
                 widget.setParent(None)
             else:
                 deleteItemsOfLayout(item.layout())
        
        
        
    def selectionchange(self):
        self.kf_met = self.cb.currentText()
        if self.kf_met == "Network":
            self.deleteItemsOfLayout(self.h)
            self.layout.removeItem(self.h)
        elif self.kf_met == "Regular":
            if self.layout.count() == 2:
                self.buttonBox.setParent(None)
                self.layout.removeWidget(self.buttonBox)
                self.h.addWidget(self.label)
                self.h.addWidget(self.e1)
                self.layout.addLayout(self.h)
                self.layout.addWidget(self.buttonBox)
                # self.layout.addLayout(self.h)
                # self.layout.addWidget(self.buttonBox)