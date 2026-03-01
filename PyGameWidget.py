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

    def __init__(self, planet_id, sim):
        super().__init__()

        self.point = []
        self.measuringtape_state = False
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        self.simulation = sim
        self.setAcceptDrops(True)

        os.environ['SDL_WINDOWID'] = str(int(self.winId()))
        os.environ['SDL_VIDEODRIVER'] = 'windows'
        pygame.init()

        self.keys_pressed = set()

        self.fps_simulation = 120
        self.timer = QTimer()
        self.timer.start(1000 // self.fps_simulation)

        self.playscreen = pygame.display.set_mode(size=(0, 0))
        self.x, self.y = self.playscreen.get_size()

        """ INITIALIZATION DES PARAMÈTRES DE LA SIMULATION """
        self.planet_id = planet_id
        self.liste_objets = self.initialiser_objets(self.planet_id)

        self.G = 6.6743*10**-11
        self.scale = 10**-5.2
        facteur_ellipse = 0.1  # <1 pour une ellipse
        self.dtime = 1 / self.fps_simulation

        if self.simulation == 1:
            self.objet_central = self.liste_objets[0]
            self.objet_orbite1 = self.liste_objets[1]
            self.objet_orbite2 = self.liste_objets[2]

            self.objet_central["position"] = euclid.Vector2(0, 0)
            self.objet_orbite1["position"] = euclid.Vector2(149597870, 0)
            self.objet_orbite2["position"] = euclid.Vector2( 149982270, 0)
            self.camera_target_pos = self.objet_central["position"]

            self.objet_orbite1["vitesse"] = self.vitesse_gravitationnelle(self.objet_central, self.objet_orbite1) * facteur_ellipse
            self.objet_orbite2["vitesse"] = self.vitesse_gravitationnelle(self.objet_orbite1, self.objet_orbite2) + self.objet_orbite1["vitesse"]

        elif self.simulation == 2:
            self.objet_orbite1 = self.liste_objets[1]
            self.objet_orbite2 = self.liste_objets[2]

            self.objet_orbite1["position"] = euclid.Vector2(random.randint(-100000000, 0), random.randint(-5000000, 0))
            self.objet_orbite2["position"] = euclid.Vector2(random.randint(0, 100000000), random.randint(0, 5000000))

            self.camera_target_pos = self.objet_orbite1["position"]

            self.objet_orbite1["vitesse"] = self.vitesse_gravitationnelle(self.objet_orbite2, self.objet_orbite1) * facteur_ellipse
            self.objet_orbite2["vitesse"] = self.vitesse_gravitationnelle(self.objet_orbite1, self.objet_orbite2)

        self.f_pressed_handled = False
        self.camera_pos = euclid.Vector2(0, 0)
        self.camera_milieu_pos = euclid.Vector2(0, 0)
        self.camera_mode = "milieu"  # "free", "follow", "milieu"

        """FIN INITIALIZATION DE LA SIMULATION """

        self.timer.timeout.connect(self.game_loop)

    def remote_changesim1(self):
        return self.simulation == 0

    def remote_changesin2(self):
        return self.simulation == 1

    def speed_interactive(self, value: int):
        self.dtime = 1 / self.fps_simulation * value

    def initialiser_objets(self, planet_id):

        dict_planete = {
            1: self.terre_objet(),
            2: self.soleil_objet(),
            3: self.lune_objet()
        }
        compteurs = {"terre": 0, "soleil": 0, "lune": 0}

        objets = []

        for id in planet_id:
            if id not in dict_planete:
                continue
            nom_base = dict_planete[id]["nom objet"]  # copier le nom original
            compteurs[nom_base] += 1
            # créer un nouvel objet avec le nom modifié
            objet = dict_planete[id].copy()
            objet["nom objet"] = f"{nom_base}{compteurs[nom_base]}"

            objets.append(objet)
        return objets

    def keyPressEvent(self, event):
        self.keys_pressed.add(event.key())
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())
        super().keyReleaseEvent(event)

    def update_size(self):
        pygame.display.update()
        self.x, self.y = pygame.display.get_window_size()

    def simulation_objet_central_3corps(self, objet_central, objet_orbite1, objet_orbite2):
        acc_objet_central = euclid.Vector2(0, 0)
        acc_objet_orbite1 = self.force_gravitationnelle(objet_orbite1, objet_central)
        acc_objet_orbite2 = self.force_gravitationnelle(objet_orbite2, objet_orbite1) + self.force_gravitationnelle(objet_orbite2, objet_central)

        list_objets = [(objet_central, acc_objet_central), (objet_orbite1, acc_objet_orbite1), (objet_orbite2, acc_objet_orbite2)]
        list_objets_update = self.mouvement(list_objets)

        self.camera_milieu_pos = self.scale * (self.objet_orbite1["position"] + self.objet_central["position"]) / 2
        self.display(list_objets_update)

    def simulation_2corps(self, objet_orbite1, objet_orbite2):
        acc_objet_orbite1 = self.force_gravitationnelle(objet_orbite1, objet_orbite2)
        acc_objet_orbite2 = self.force_gravitationnelle(objet_orbite2, objet_orbite1)

        list_objets = [(objet_orbite1, acc_objet_orbite1), (objet_orbite2, acc_objet_orbite2)]
        list_objets_update = self.mouvement(list_objets)

        self.camera_milieu_pos = self.scale * (self.objet_orbite1["position"] + self.objet_orbite2["position"]) / 2
        self.display(list_objets_update)

    def force_gravitationnelle(self, obj1, obj2):
        d_vecteur = obj2["position"] - obj1["position"]
        distance = d_vecteur.magnitude()
        distance = max(distance, 1)
        d_vecteur.normalize()
        acceleration = d_vecteur * (self.G * obj2["masse"] / distance ** 2)
        return acceleration

    def vitesse_gravitationnelle(self, obj1, obj2):
        d_vecteur = obj2["position"] - obj1["position"]
        distance = d_vecteur.magnitude()
        d_vecteur.normalize()
        tangente = euclid.Vector2(-d_vecteur.y, d_vecteur.x)
        v_orbitale = math.sqrt(self.G * obj1["masse"] / distance)
        v_orbitale = v_orbitale * tangente
        return v_orbitale

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
        position = self.objet_central['position']

    def measuringtape(self):
        for i in pygame.event.get():
            if i.type == pygame.MOUSEBUTTONDOWN:
                if i.button == 1:
                    pos = pygame.mouse.get_pos()
                    self.point.append(pos)
                    self.point = self.point[-2:]
                    self.measuring_updater_signal.emit()

    def toggle_measuringtape(self, state: bool):
        self.measuringtape_state = state
        if not state:
            self.point.clear()
            self.measuring_updater_signal.emit()

    def mouvement(self, objets):  # objet[0] = objet, objet[1] = acc_objet
        list_objets_update = []

        for objet in objets:
            objet[0]["vitesse"] += objet[1] * self.dtime
            objet[0]["position"] += objet[0]["vitesse"] * self.dtime
            list_objets_update.append(objet)

        return list_objets_update

    def pos_objet_orbite(self, pos):
        pos_pixel = pos * self.scale
        relative = pos_pixel - self.camera_pos

        new_world_x = self.x / 2 + relative.x
        new_world_y = self.y / 2 + relative.y

        return new_world_x, new_world_y

    def changer_vue(self):
        if self.camera_mode == "free":
            self.camera_mode = "follow"
        elif self.camera_mode == "follow":
            self.camera_mode = "milieu"
        elif self.camera_mode == "milieu":
            self.camera_mode = "free"

    def display(self, objets: list):  # objet[0] = objet, objet[1] = acc_objet
        self.playscreen.fill((0, 0, 0))

        for objet in objets:
            rx, ry = self.pos_objet_orbite(objet[0]["position"])
            pygame.draw.circle(self.playscreen, objet[0]["couleur"], (rx, ry), objet[0]["rayon"])

        for j in self.point:
            pygame.draw.circle(self.playscreen, (255, 255, 255), j, 3)
        if len(self.point) == 2:
            pygame.draw.line(self.playscreen, (255, 255, 255), start_pos=self.point[0], end_pos=self.point[1], width=3)

        border_color = (255, 0, 0)  # red border
        border_thickness = 2  # pixels
        pygame.draw.rect(
            self.playscreen,
            border_color,
            pygame.Rect(0, 0, self.x, self.y),
            border_thickness
        )

        pygame.display.update()

    @staticmethod
    def terre_objet():
        terre = {
            "nom objet": "terre",
            "masse": 5.972*10**24,
            "rayon": 10,
            "couleur": (0, 0, 255),
            "vitesse": euclid.Vector2(0, 0)
        }
        return terre

    @staticmethod
    def soleil_objet():
        soleil = {
            "nom objet": "soleil",
            "masse": 1.989*10**30,
            "rayon": 50,
            "couleur": (255, 222, 0),
            "vitesse": euclid.Vector2(0, 0)
        }
        return soleil

    @staticmethod
    def lune_objet():
        lune = {
            "nom objet": "lune",
            "masse": 7.347*10**22,
            "rayon": 2,
            "couleur": (200, 200, 200),
            "vitesse": euclid.Vector2(0, 0)
        }
        return lune

    def game_loop(self):
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

        # CAMÉRA ICI
        elif self.camera_mode == "follow":
            self.camera_pos = self.camera_target_pos * self.scale + euclid.Vector2(1, 1)
        elif self.camera_mode == "milieu":
            self.camera_pos = self.camera_milieu_pos

        if self.measuringtape_state:
            self.measuringtape()

        self.update_size()
        if self.simulation == 1:
            self.simulation_objet_central_3corps(self.objet_central, self.objet_orbite1, self.objet_orbite2)

        elif self.simulation == 2:
            self.simulation_2corps(self.objet_orbite1, self.objet_orbite2)

        elif self.simulation == 3:
            pass
        elif self.simulation == 4:
            pass
        else:
            pass