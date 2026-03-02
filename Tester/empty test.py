import random
import sys
import os
import math
import pygame
import euclid
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QLabel, QToolBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QDrag
from PySide6.QtCore import QMimeData



class QtPlanetLabel(QLabel):
    def __init__(self, name):
        super().__init__(name)
        self.planet_name = name
        self.setStyleSheet('padding: 6px; background-color: gray;')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            dragging = QDrag(self)
            mime = QMimeData()
            mime.setText(self.planet_name)
            dragging.setMimeData(mime)
            dragging.exec(Qt.CopyAction)


class Pygame(QWidget):
    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)
        #self.clock = pygame.time.Clock()
        self.clock = QTimer()
        self.clock.timeout.connect(self.game_loop)
        self.clock.start(16)
        self.planets = []
        self.active_planet = None

        self.fps_simulation = 120
        self.G = 100
        self.scale = 10**-5.2
        facteur_ellipse = 0.1  # <1 pour une ellipse
        self.dtime = 1 / self.fps_simulation

        self.pygame_windowhandler()

    def pygame_windowhandler(self):
        os.environ["SDL_WINDOWID"] = str(int(self.winId()))
        os.environ["SDL_VIDEODRIVER"] = "windows"
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 700))
        self.timer = pygame.time.Clock()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        name = event.mimeData().text()
        pos = event.pos()
        self.spawn_planets(name, pos.x(), pos.y(), 0, 0)

    def spawn_planets(self, name, x, y, velx, vely):
        presets = {
            "Earth": {"mass": 50, "radius": 12, "color": (0, 100, 255)},
            "Mars": {"mass": 30, "radius": 10, "color": (255, 100, 100)},
            "Jupiter": {"mass": 190000, "radius": 20, "color": (200, 150, 50)}
        }

        data = presets.get(name, presets["Earth"])

        planet = {
            "pos": pygame.Vector2(x, y),
            "vel": pygame.Vector2(velx, vely),
            "mass": data["mass"],
            "radius": data["radius"],
            "color": data["color"]
        }

        self.planets.append(planet)

    def mouvement(self, objets):  # objet[0] = objet, objet[1] = acc_objet
        list_objets_update = []

        for objet in objets:
            objet[0]["vitesse"] += objet[1] * self.dtime
            objet[0]["position"] += objet[0]["vitesse"] * self.dtime
            list_objets_update.append(objet)

        return list_objets_update

    def gravity(self):
        for i, j in enumerate(self.planets):
            if j['mass'] > 28000:
                total_dmomentum = pygame.Vector2(0, 0)
            else:
                total_dmomentum = pygame.Vector2(70, 10)
            for k, l in enumerate(self.planets):
                if i == k:
                    continue
                direction = l['pos'] - j['pos']
                length = direction.length()
                if length < 10:
                    continue
                direction = direction.normalize() # check here
                dmomentum = self.G * l['mass'] / (length**2)
                total_dmomentum += direction * dmomentum
            j['vel'] += total_dmomentum * self.dtime

    def update_positions(self):
        for planet in self.planets:
            planet["pos"] += planet["vel"] * self.dtime

    def game_loop(self):
        self.gravity()
        self.update_positions()
        self.screen.fill((30, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.Vector2(event.pos)
                    for n, m in enumerate(self.planets):
                        mouse_to_object_distance = mouse_pos.distance_to(m['pos'])
                        if mouse_to_object_distance <= m['radius']:
                            self.active_planet = n
                            break
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.active_planet = None
            elif event.type == pygame.MOUSEMOTION:
                if self.active_planet is not None:
                    self.planets[self.active_planet]['pos'] += event.rel

        for p in self.planets:
            pygame.draw.circle(self.screen, p["color"], (int(p["pos"].x), int(p["pos"].y)), p["radius"])

        pygame.display.flip()
        #pygame.quit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('TEST')
        self.resize(1000, 700)
        toolbar = QToolBar('planets')
        self.addToolBar(toolbar)

        for i in ['Earth', 'Mars', 'Jupiter']:
            toolbar.addWidget(QtPlanetLabel(i))

        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)
        self.pygamewidget = Pygame()
        layout.addWidget(self.pygamewidget)
        self.setCentralWidget(container)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()








