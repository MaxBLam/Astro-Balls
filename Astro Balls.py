import sys
import os
import pygame
from PySide6.QtGui import QAction, Qt
import PySide6.QtCore
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMenu, QPushButton, QVBoxLayout, QDockWidget, \
    QHBoxLayout
from PySide6.QtCore import QTimer


class PyGameWidget(QWidget):
    def __init__(self):
        super().__init__()

        os.environ['SDL_WINDOWID'] = str(int(self.winId()))
        os.environ['SDL_VIDEODRIVER'] = 'windows'
        pygame.init()
        self.playscreen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()

        ##########
        #Game here
        ##########

        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(16)

        self.playscreen.fill((30, 30, 30))

        pygame.display.update()
        self.clock.tick(60)

    def game_loop(self):
        pass


class DragNDrop(QDockWidget):
    def __init__(self):
        super().__init__("Drag-and-Drop Menu")

        widget = QWidget()
        layout = QHBoxLayout()

        layout.addWidget(QPushButton("1"))
        layout.addWidget(QPushButton("2"))
        layout.addWidget(QPushButton("3"))
        layout.addWidget(QPushButton("4"))
        layout.addWidget(QPushButton("5"))

        widget.setLayout(layout)
        self.setWidget(widget)


class StatsDock(QDockWidget):
    def __init__(self):
        super().__init__("Statistics")

        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QPushButton("1"))
        layout.addWidget(QPushButton("2"))
        layout.addWidget(QPushButton("3"))
        layout.addWidget(QPushButton("4"))
        layout.addWidget(QPushButton("5"))

        widget.setLayout(layout)
        self.setWidget(widget)


class MainWindowFrame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle('Astro Balls')
        self.setCentralWidget(PyGameWidget())

        menu = self.menuBar()
        settings_menu = QMenu('&Settings')
        settings_action = QAction('&placeholder1')
        settings_menu.addAction(settings_action)
        menu.addMenu(settings_menu)

        self.dragndrop = DragNDrop()
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dragndrop)
        self.statsdock = StatsDock()
        self.addDockWidget(Qt.RightDockWidgetArea, self.statsdock)


app = QApplication(sys.argv)
mw = MainWindowFrame()
mw.show()
app.exec()

