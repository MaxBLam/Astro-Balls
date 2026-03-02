import random
import os
import pygame
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Signal
import euclid
import math


class PyGameWidget(QWidget):
    measuring_updater_signal = Signal()

    def __init__(self):
        super().__init__()

        self.y = None
        self.x = None
        self.j = None
        self.setAcceptDrops(True)
        self.planets = []
        self.active_planet = None
        self.playscreen = None
        self.point = []
        self.measuringtape_state = False
        self.keys_pressed = set()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self.fps_simulation = 120
        self.G = 1000
        self.scale = 0.1
        facteur_ellipse = 0.1  # <1 pour une ellipse
        self.dtime = 0.1 / self.fps_simulation

        self.camera_mode = 'milieu'
        self.camera_milieu_pos = euclid.Vector2(0, 0)
        self.camera_pos = euclid.Vector2(0, 0)
        self.camera_target_pos = euclid.Vector2(0, 0)
        self.f_pressed_handled = None

        self.pygame_windowhandler()

        self.clock = QTimer()
        self.clock.timeout.connect(self.game_loop)
        self.clock.start(16)

    def pygame_windowhandler(self):
        os.environ["SDL_WINDOWID"] = str(int(self.winId()))
        os.environ["SDL_VIDEODRIVER"] = "windows"
        pygame.init()
        self.playscreen = pygame.display.set_mode(size=(0, 0))
        self.x, self.y = self.playscreen.get_size()
        self.timer = pygame.time.Clock()

    def speed_interactive(self, value: int):
        self.dtime = 0.1 / self.fps_simulation * value

    def keyPressEvent(self, event):
        self.keys_pressed.add(event.key())
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())
        super().keyReleaseEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        name = event.mimeData().text()
        pos = event.pos()

        world_x = (pos.x() - self.x / 2 + self.camera_pos.x) / self.scale
        world_y = (pos.y() - self.y / 2 + self.camera_pos.y) / self.scale

        self.spawn_planets(name, world_x, world_y, 0, 0)

    def update_size(self):
        pygame.display.update()
        self.x, self.y = pygame.display.get_window_size()

    @staticmethod
    def pythagoras(pos):
        max_height, min_height = max([pos[0][1], pos[1][1]]), min([pos[0][1], pos[1][1]])
        max_length, min_length = max([pos[0][0], pos[1][0]]), min([pos[0][0], pos[1][0]])
        height = max_height - min_height
        length = max_length - min_length
        hypotenus = math.sqrt((height ** 2 + length ** 2))
        theta = math.degrees(math.atan2(height, length))
        return round(hypotenus, 2), round(theta, 2)

    def kepler(self):
        pass

    def measuringtape(self):
        for i in pygame.event.get():
            if i.type == pygame.MOUSEBUTTONDOWN:
                if i.button == 1:
                    pos = pygame.mouse.get_pos()
                    pos = pygame.mouse.get_pos()
                    self.point.append(pos)
                    self.point = self.point[-2:]
                    self.measuring_updater_signal.emit()

    def toggle_measuringtape(self, state: bool):
        self.measuringtape_state = state
        if not state:
            self.point.clear()
            self.measuring_updater_signal.emit()

    def changer_vue(self):
        modes = ["free", "follow", "milieu"]
        current_idx = modes.index(self.camera_mode)
        self.camera_mode = modes[(current_idx + 1) % len(modes)]
        print(f"Camera Mode: {self.camera_mode}")

    def spawn_planets(self, name, x, y, velx, vely):
        presets = {
            "Mercury": {"mass": (3.285*10**23)/(1*10**21), "radius": 9, "color": (245, 245, 220)},
            "Venus": {"mass": (4.867*10**24)/(1*10**21), "radius": 11, "color": (255, 215, 0)},
            "Earth": {"mass": (5.972*10**24)/(1*10**21), "radius": 12, "color": (0, 100, 255)},
            "Mars": {"mass": (6.416993*10**23)/(1*10**21), "radius": 10, "color": (255, 100, 100)},
            "Jupiter": {"mass": (1.899*10**27)/(1*10**21), "radius": 50, "color": (200, 150, 50)},
            "Saturn": {"mass": (5.683*10**26)/(1*10**21), "radius": 45, "color": (195, 146, 79)},
            "Uranus": {"mass": (6.681*10**25)/(1*10**21), "radius": 20, "color": (172, 229, 238)},
            "Neptune": {"mass": (1.024*10**26)/(1*10**21), "radius": 21, "color": (124, 183, 187)},
            "Sun": {"mass": (1.989*10**30)/(1*10**21), "radius": 200, "color": (255, 0, 0)},
            "Moon": {"mass": (7.347*10**22)/(1*10**21), "radius": 4, "color": (200, 200, 200)},
            "Europa": {"mass": (4.799*10**22)/(1*10**21), "radius": 2, "color": (191, 207, 217)},
            "Io": {"mass": (8.931*10**22)/(1*10**21), "radius": 3, "color": (200, 180, 100)}
        }

        data = presets.get(name, presets["Earth"])

        planet = {"pos": pygame.Vector2(x, y), "vel": pygame.Vector2(velx, vely), "mass": data["mass"],
                  "radius": data["radius"], "color": data["color"]}

        self.planets.append(planet)

    def gravity(self):
        for i, self.j in enumerate(self.planets):
            if self.j['mass'] > 28000:
                total_dmomentum = pygame.Vector2(0, 0)
            else:
                total_dmomentum = pygame.Vector2(0, 0)  # do not change, will implement acceleration later
            for k, l in enumerate(self.planets):
                if i == k:
                    continue
                direction = l['pos'] - self.j['pos']
                length = direction.length()
                if length < 10:
                    continue
                direction = direction.normalize() # check here
                dmomentum = self.G * l['mass'] / (length**2)
                total_dmomentum += direction * dmomentum
            self.j['vel'] += total_dmomentum * self.dtime

    def update_positions(self):
        for planet in self.planets:
            planet["pos"] += planet["vel"] * self.dtime

    def pos_objet_orbite(self, pos):
        pos_pixel = pos * self.scale
        relative = pos_pixel - self.camera_pos

        new_world_x = self.x / 2 + relative.x
        new_world_y = self.y / 2 + relative.y

        return new_world_x, new_world_y

    def game_loop(self):
        self.gravity()
        self.update_positions()
        self.playscreen.fill((0, 0, 0))
        if self.measuringtape_state:
            self.measuringtape()
            for i in self.point:
                pygame.draw.circle(self.playscreen, (255, 255, 255), i, 3)

            if len(self.point) == 2:
                pygame.draw.line(self.playscreen, (255, 255, 255), self.point[0], self.point[1], 3)

        if Qt.Key_F in self.keys_pressed:
            if not self.f_pressed_handled:
                self.changer_vue()
                self.f_pressed_handled = True
        else:
            self.f_pressed_handled = False

        speed = 3
        if Qt.Key_Shift in self.keys_pressed:
            speed = 10

        if self.camera_mode == "free":
            if Qt.Key_A in self.keys_pressed:
                self.camera_pos.x -= speed
            if Qt.Key_D in self.keys_pressed:
                self.camera_pos.x += speed
            if Qt.Key_W in self.keys_pressed:
                self.camera_pos.y -= speed
            if Qt.Key_S in self.keys_pressed:
                self.camera_pos.y += speed

        elif self.camera_mode == "follow" and self.planets:
            self.camera_pos = self.planets[0]['pos'] * self.scale
        elif self.camera_mode == "milieu":
            self.camera_pos = self.camera_milieu_pos

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    m_pos = pygame.Vector2(event.pos)
                    for n, p in enumerate(self.planets):
                        sx, sy = self.pos_objet_orbite(p['pos'])
                        if m_pos.distance_to((sx, sy)) <= p['radius']:
                            self.active_planet = n
                            break
            elif event.type == pygame.MOUSEBUTTONUP:
                self.active_planet = None
            elif event.type == pygame.MOUSEMOTION:
                if self.active_planet is not None:
                    self.planets[self.active_planet]['pos'] += pygame.Vector2(event.rel) / self.scale

        for p in self.planets:
            screen_x, screen_y = self.pos_objet_orbite(p['pos'])
            pygame.draw.circle(self.playscreen, p["color"], (int(screen_x), int(screen_y)), p["radius"])

        pygame.display.flip()
