from PySide6.QtGui import Qt, QFont, QPixmap
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QLabel, QGridLayout


class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.wwsc_simulation = None
        self.setFixedSize(700, 500)
        ww_widget = QWidget()
        self.setCentralWidget(ww_widget)
        ww_layout = QGridLayout()
        ww_widget.setLayout(ww_layout)
        ww_widget.setStyleSheet('background-color: black')
        ww_layout.setContentsMargins(0, 0, 0, 0)
        ww_layout.setSpacing(0)
        ww_pixmap = QPixmap('images/ww_images/The_Earth_seen_from_Apollo_17.jpg').scaled(250, 500, Qt.KeepAspectRatio,
                                                                                         Qt.SmoothTransformation)
        ww_pixmap_label = QLabel()
        ww_pixmap_label.setPixmap(ww_pixmap)
        ww_layout.addWidget(ww_pixmap_label, 0, 1, Qt.AlignmentFlag.AlignRight)
        ww_label = QLabel(self)
        ww_label.setFixedSize(500, 60)
        ww_label.setText('C E L E S T I A')
        ww_label_font = QFont()
        ww_label_font.setPointSize(40)
        ww_label.setFont(ww_label_font)
        ww_label.move(70, 50)
        ww_opensim1 = QPushButton('Simulation #1', self)
        ww_opensim1.setFixedSize(350, 150)
        ww_opensim1.move(50, 150)
        ww_opensim1.setStyleSheet('background-color: black')
        ww_opensim1.clicked.connect(lambda: self.wwsc(1))
        ww_opensim2 = QPushButton('Simulation #2', self)
        ww_opensim2.setFixedSize(350, 150)
        ww_opensim2.move(50, 300)
        ww_opensim2.setStyleSheet('background-color: black')
        ww_opensim2.clicked.connect(lambda: self.wwsc(1))

    def wwsc(self, sim_id):
        self.wwsc_simulation = sim_id
        self.close()
