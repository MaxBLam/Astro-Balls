from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QLabel, QGridLayout


class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Astro Balls')
        self.setWindowIcon(QIcon('./images/Astro Balls Icon.png'))
        self.wwsc_simulation = None
        self.setFixedSize(700, 500)
        ww_widget = QWidget()
        self.setCentralWidget(ww_widget)
        ww_layout = QGridLayout()
        ww_widget.setLayout(ww_layout)
        ww_widget.setStyleSheet('background-color: #010101;')
        ww_layout.setContentsMargins(0, 0, 0, 0)
        ww_layout.setSpacing(0)
        ww_pixmap = QPixmap('images/ww_images/The_Earth_seen_from_Apollo_17.jpg').scaled(250, 500, Qt.AspectRatioMode.KeepAspectRatio,
                                                                                         Qt.TransformationMode.SmoothTransformation)
        ww_pixmap_label = QLabel()
        ww_pixmap_label.setPixmap(ww_pixmap)
        ww_layout.addWidget(ww_pixmap_label, 0, 1, Qt.AlignmentFlag.AlignRight)
        ww_label = QLabel(self)
        ww_label.setFixedSize(500, 60)
        ww_label.setText('A s t r o  B a l l s')
        ww_label_font = QFont()
        ww_label_font.setPointSize(40)
        ww_label.setFont(ww_label_font)
        ww_label.move(50, 50)

        ww_opensim1 = QPushButton('Système Orbitale\n à 3 Corps', self)
        ww_opensim1.setFixedSize(175, 100)
        ww_opensim1.move(50, 150)
        ww_opensim1.setStyleSheet("""QPushButton {background-color: #000000; border: 1px solid #1A1A1A;} 
        QPushButton:hover {background-color: #090C29;}""")
        ww_opensim1.clicked.connect(lambda: self.wwsc(1))
        ww_opensim2 = QPushButton('Système à 2 corps', self)
        ww_opensim2.setFixedSize(175, 100)
        ww_opensim2.move(50, 250)
        ww_opensim2.setStyleSheet("""QPushButton {background-color: #000000; border: 1px solid #1A1A1A;} 
        QPushButton:hover {background-color: #1D0721;}""")
        ww_opensim2.clicked.connect(lambda: self.wwsc(2))
        ww_opensim3 = QPushButton('Système à n corps', self)
        ww_opensim3.setFixedSize(175, 200)
        ww_opensim3.move(225, 150)
        ww_opensim3.setStyleSheet("""QPushButton {background-color: #000000; border: 1px solid #1A1A1A;} 
        QPushButton:hover {background-color: #0E1F13;}""")
        ww_opensim3.clicked.connect(lambda: self.wwsc(3))
        ww_sandbox = QPushButton('SandBox', self)
        ww_sandbox.setFixedSize(350, 100)
        ww_sandbox.move(50, 350)
        ww_sandbox.setStyleSheet("""QPushButton {background-color: #000000; border: 1px solid #1A1A1A;} 
        QPushButton:hover {background-color: #072021;}""")
        ww_sandbox.clicked.connect(lambda: self.wwsc(4))

    def wwsc(self, sim_id):
        self.wwsc_simulation = sim_id
        self.close()
