import os

import pygame
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QImage
from PySide6.QtWidgets import QWidget
import euclid
import math
import random

class PyGameWidget(QWidget):
    measuring_updater_signal = Signal()

    def __init__(self, statsdock):
        super().__init__()

        self.base_planet_image = None
        self.setMouseTracking(True)
        self.acceleration = None
        self.old_mouse = None
        self.souris_pos = None
        self.souris_pos_vector = euclid.Vector2(0,0)
        self.centrum = None
        self.p_index = None
        self.statsdock = statsdock
        self.window_x = None
        self.window_y = None
        self.drag_and_drop_x = None
        self.drag_and_drop_y = None
        self.statsdock_x = None
        self.statsdock_y = None
        self.setAcceptDrops(True)
        self.planetes = []
        self.planetes_pos = []
        self.active_planet = None
        self.vitesse_state = False
        self.active = False
        self.playscreen = pygame.Surface((self.width(), self.height()))
        self.point = []
        self.measuringtape_state = False
        self.is_editingorbits = False
        self.is_showingorbits = False
        self.is_helpingorbits = False
        self.vitesse_state = False
        self.is_showingorbitalvector = False
        self.is_showingforcevector = False

        self.planetes = []
        self.planetes_pos = []

        self.keys_pressed = set()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        self.fps_simulation = 120
        self.timer = QTimer()
        self.timer.start(8)

        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font("./Font/Orbitron-Regular.ttf", 15)

        self.simulation = 2
        self.G = 6.6743 * 10**-15
        self.scale = 20**6 / 100**6
        self.facteur_ellipse = 1 # <1 pour une ellipse
        self.dtime = 1 / self.fps_simulation

        self.f_pressed_handled = False
        self.target = None
        self.camera_pos = euclid.Vector2(0, 0)
        self.camera_mode = "follow"  # "free", "follow", "milieu"

        self.timer.timeout.connect(self.game_loop)

        self.planet_surfaces_cache = {}

    def window_resize_event(self, width, height):
        self.window_x = width
        self.window_y = height
        self.playscreen = pygame.Surface((self.width(), self.height()))

    def keyPressEvent(self, event):
        self.keys_pressed.add(event.key())
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())
        super().keyReleaseEvent(event)

    def speed_interactive(self, value: int):
        self.dtime = 1 / self.fps_simulation * (0.3 * value)**4

    def scale_interactive(self, value: int):
        if value < 90:
            self.scale = float(value**6 / 100**6)
        else:
            self.scale = 0.1 * (value - 88)**3 + (90**6/100**6 - 0.1 * 2**3)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.playscreen = pygame.Surface((self.width(), self.height()))
        nom = event.mimeData().text()
        pos = event.pos()
        pos_x = (pos.x() + self.camera_pos.x * self.scale) / self.scale
        pos_y = (pos.y() + self.camera_pos.y * self.scale) / self.scale

        self.corps(nom, pos_x, pos_y)

    def update_target(self, planete):
        self.target = planete["position"]

    def vitesse_simulation1(self):
        masse_max_id = 0
        id_list = []
        masse_max = max(self.planetes[0]["masse"], self.planetes[1]["masse"], self.planetes[2]["masse"])
        for planete_id in range (len(self.planetes)):
            if masse_max == self.planetes[planete_id]["masse"]:
                masse_max_id = planete_id
            else:
                id_list.append(planete_id)
        self.planetes[masse_max_id]["vitesse"] = euclid.Vector2(0, 0)
        vitesse_1 = self.vitesse_gravitationnelle(self.planetes[masse_max_id], self.planetes[id_list[0]])
        self.planetes[id_list[0]]["vitesse"] = vitesse_1 * self.facteur_ellipse
        vitesse_2 = self.vitesse_gravitationnelle(self.planetes[id_list[0]], self.planetes[id_list[1]])
        self.planetes[id_list[1]]["vitesse"] = vitesse_2 + self.planetes[id_list[0]]["vitesse"]
        self.vitesse_state = True

    def simulation_objet_central_3corps(self, objet_central, objet_orbite1, objet_orbite2):
        dampener = (max(objet_orbite1["rayon"], objet_orbite2["rayon"], objet_orbite2["rayon"])
                    + min(objet_orbite1["rayon"], objet_orbite2["rayon"], objet_orbite2["rayon"])) / 2
        acc_objet_central = self.force_gravitationnelle(objet_central, objet_orbite1, dampener) + self.force_gravitationnelle(objet_central, objet_orbite2, dampener)
        acc_objet_orbite1 = self.force_gravitationnelle(objet_orbite1, objet_central, dampener) + self.force_gravitationnelle(objet_orbite1, objet_orbite2, dampener)
        acc_objet_orbite2 = self.force_gravitationnelle(objet_orbite2, objet_orbite1, dampener) + self.force_gravitationnelle(objet_orbite2, objet_central, dampener)

        list_objets = [(objet_central, acc_objet_central), (objet_orbite1, acc_objet_orbite1), (objet_orbite2, acc_objet_orbite2)]
        list_objets_update = self.mouvement(list_objets)

        if self.camera_mode == "milieu":
            pos_x = ((objet_central["position"].x + objet_orbite1["position"].x) / 2) - (self.width() / self.scale / 2)
            pos_y = ((objet_central["position"].y + objet_orbite1["position"].y) / 2) - (self.height() / self.scale / 2)
            self.camera_pos = euclid.Vector2(pos_x, pos_y)

        self.display(list_objets_update)

    def vitesse_simulation2(self):
        self.planetes[0]["vitesse"] = self.vitesse_gravitationnelle(self.planetes[1], self.planetes[0]) * random.uniform(0.4,1.0)
        self.planetes[1]["vitesse"] = self.vitesse_gravitationnelle(self.planetes[0], self.planetes[1]) * random.uniform(0.8,1.2)
        self.vitesse_state = True

    def simulation_2corps(self, objet_orbite1, objet_orbite2):
        dampener = (max(objet_orbite1["rayon"], objet_orbite2["rayon"])
                    + min(objet_orbite1["rayon"], objet_orbite2["rayon"])) / 2
        acc_objet_orbite1 = self.force_gravitationnelle(objet_orbite1, objet_orbite2, dampener)
        acc_objet_orbite2 = self.force_gravitationnelle(objet_orbite2, objet_orbite1, dampener)

        list_objets = [(objet_orbite1, acc_objet_orbite1), (objet_orbite2, acc_objet_orbite2)]
        list_objets_update = self.mouvement(list_objets)

        if self.camera_mode == "milieu":
            pos_x = ((objet_orbite1["position"].x + objet_orbite2["position"].x) / 2) - (self.width() / self.scale / 2)
            pos_y = ((objet_orbite1["position"].y + objet_orbite2["position"].y) / 2) - (self.height() / self.scale / 2)
            self.camera_pos = euclid.Vector2(pos_x, pos_y)

        self.display(list_objets_update)

    def vitesse_simulation3(self):
        self.planetes[0]["vitesse"] = self.vitesse_gravitationnelle(self.planetes[1], self.planetes[0]) * random.uniform(0.1,0.3)
        self.planetes[1]["vitesse"] = self.vitesse_gravitationnelle(self.planetes[2], self.planetes[1]) * random.uniform(0.1,0.3)
        self.planetes[2]["vitesse"] = self.vitesse_gravitationnelle(self.planetes[0], self.planetes[2]) * random.uniform(0.1,0.3)
        self.vitesse_state = True

    def simulation_3corps(self, objet_orbite1, objet_orbite2, objet_orbite3):
        dampener = 5 * max(objet_orbite1["rayon"], objet_orbite2["rayon"], objet_orbite2["rayon"])
        acc_objet_orbite1 = self.force_gravitationnelle(objet_orbite1, objet_orbite2, dampener) + self.force_gravitationnelle(objet_orbite1, objet_orbite3, dampener)
        acc_objet_orbite2 = self.force_gravitationnelle(objet_orbite2, objet_orbite1, dampener) + self.force_gravitationnelle(objet_orbite2, objet_orbite3, dampener)
        acc_objet_orbite3 = self.force_gravitationnelle(objet_orbite3, objet_orbite1, dampener) + self.force_gravitationnelle(objet_orbite3, objet_orbite2, dampener)


        list_objets = [(objet_orbite1, acc_objet_orbite1), (objet_orbite2, acc_objet_orbite2), (objet_orbite3, acc_objet_orbite3)]
        list_objets_update = self.mouvement(list_objets)

        if self.camera_mode == "milieu":
            pos_x = (objet_orbite1["position"].x + objet_orbite2["position"].x + objet_orbite3["position"].x) / 3 - (self.width() / self.scale / 2)
            pos_y = (objet_orbite1["position"].y + objet_orbite2["position"].y + objet_orbite3["position"].y) / 3- (self.height() / self.scale / 2)
            self.camera_pos = euclid.Vector2(pos_x, pos_y)

        self.display(list_objets_update)

    def force_gravitationnelle(self, obj1, obj2, dampener):
        d_vecteur = obj2["position"] - obj1["position"]
        distance = d_vecteur.magnitude()
        distance = max(distance, dampener)
        d_vecteur.normalize()
        self.acceleration = d_vecteur * (self.G * obj2["masse"] / (distance ** 2))
        return self.acceleration

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

    @staticmethod
    def vector_arrow(start, end):
        vector = end - start
        if vector.magnitude() > 1:
            rotater = math.radians(135)
            cos_angle = math.cos(rotater)
            sin_angle = math.sin(rotater)

            leftx = vector.x*cos_angle - vector.y*(-sin_angle)
            lefty = vector.x*(-sin_angle) + vector.y*cos_angle
            arrow_left = euclid.Vector2(leftx, lefty)
            arrow_left.normalized()*10

            rightx = vector.x * cos_angle - vector.y * sin_angle
            righty = vector.x * sin_angle + vector.y * cos_angle
            arrow_right = euclid.Vector2(rightx, righty)
            arrow_right.normalized() * 10

            vector_arrow_left = end + arrow_left
            vector_arrow_right = end+arrow_right
            return vector_arrow_left, vector_arrow_right
        return end, end


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

    def kepler_orbit_helper(self, checked):
        self.is_helpingorbits = checked


    def orbit_editor(self):
        self.is_editingorbits = True
        receiver_config_button = self.sender()
        self.p_index = receiver_config_button.property('index') + 1
        return self.is_editingorbits

    # TODO: may delete this later
    def uopt_editor(self):
        orbital_data = None
        if self.p_index is None:
            return 0.0
        planet = self.planetes[self.p_index]
        centrum = self.centrum
        rpx = planet['position'].x - centrum['position'].x  # type: ignore
        rpy = planet['position'].y - centrum['position'].y  # type: ignore
        angle = math.atan2(rpy, rpx)
        for i in self.kepler():
            if i['planet'] == planet:
                orbital_data = i
                break
        if orbital_data is not None:
            theta = angle - orbital_data['omega']
            theta = theta % (2 * math.pi)
            return math.degrees(theta)
        return 0.0

    def mouvement(self, objets):  # objet[0] = objet, objet[1] = acc_objet
        list_objets_update = []
        for objet in objets:
            objet[0]["vitesse"] += objet[1] * self.dtime
            objet[0]["position"] += objet[0]["vitesse"] * self.dtime
            list_objets_update.append(objet[0])

        return list_objets_update

    def changer_vue(self):
        if self.camera_mode == "free":
            if self.active:
                self.camera_mode = "milieu"
            else:
                self.camera_mode = "follow"
        elif self.camera_mode == "milieu":
            self.camera_mode = "follow"
        elif self.camera_mode == "follow":
            self.camera_mode = "free"

    def pos_objet_orbite(self, pos):
        relative = pos - self.camera_pos

        if pos != relative:
            new_world_x = relative.x
            new_world_y = relative.y
        else:
            new_world_x = pos.x
            new_world_y = pos.y

        return new_world_x * self.scale, new_world_y * self.scale

    def get_planet_surface(self, planete):
        rayon = int(planete["rayon"] * self.scale)
        key = (planete["nom"], rayon)

        if key in self.planet_surfaces_cache:
            return self.planet_surfaces_cache[key]

        if self.base_planet_image is None:
            self.base_planet_image = pygame.image.load("./images/Skins/soleil.jpg")

        image = pygame.transform.scale(self.base_planet_image, (rayon*2, rayon*2))
        circle_surface = pygame.Surface((rayon*2, rayon*2), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, (255, 255, 255, 255), (rayon, rayon), rayon)
        circle_surface.blit(image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        self.planet_surfaces_cache[key] = circle_surface
        return circle_surface

    def display(self, planetes: list):
        self.playscreen.fill((0,0,0))
        text_list = []
        shift = 0

        for planete in planetes:
            rx, ry = self.pos_objet_orbite(planete["position"])
            rayon = planete["rayon"] * self.scale

            if rayon < 1:
                text = self.font.render(f"{planete['nom']}", True, (255, 255, 255))
                text_list.append((text, (rx,ry)))
            else:
                if rayon > 800 or not os.path.exists("./images/Skins/soleil.jpg"):
                    if all(c < 50 for c in planete["couleur"]) and rayon < 3000:
                        pygame.draw.circle(self.playscreen, (255, 255, 255), (rx, ry), rayon, int(0.05 * rayon))
                    else:
                        pygame.draw.circle(self.playscreen, planete["couleur"], (rx, ry), rayon)
                else:
                    surface = self.get_planet_surface(planete)
                    self.playscreen.blit(surface, (rx - rayon, ry - rayon))
            for text in text_list:
                self.playscreen.blit(text[0], (text[1][0], text[1][1] + shift))
                shift += 10

        for j in self.point:
            pygame.draw.circle(self.playscreen, (255, 255, 255), j, 3)
        if len(self.point) == 2:
            pygame.draw.line(self.playscreen, (255, 255, 255), start_pos=self.point[0], end_pos=self.point[1], width=3)
        self.update()

    def corps(self, nom, x, y):
        corps = {
            "Mercure": {'nom': 'Mercure', 'type': 'Planète', 'composition_surface': 'Métallique (70%)',
                        'âge': '4,503 milliards d’années', 'rotation': '1 408 h', 'révolution': '88 jours',
                        "masse": 3.285e23, "rayon": 2439.7, "couleur": (245, 245, 220)},
            "Vénus": {'nom': 'Vénus', 'type': 'Planète', 'composition_surface': 'Basalte',
                      'âge': '4,503 milliards d’années', 'rotation': '5 832 h', 'révolution': '225 jours',
                      "masse": 4.867e24, "rayon": 6051.8, "couleur": (255, 215, 0)},
            "Terre": {'nom': 'Terre', 'type': 'Planète', 'composition_surface': 'Granite',
                      'âge': '4,543 milliards d’années', 'rotation': '24 h', 'révolution': '365 jours',
                      "masse": 5.972e24, "rayon": 6371.0, "couleur": (0, 100, 255)},
            "Mars": {'nom': 'Mars', 'type': 'Planète', 'composition_surface': 'Fer oxydé',
                     'âge': '4,603 milliards d’années', 'rotation': '25 h', 'révolution': '687 jours',
                     "masse": 6.416993e23, "rayon": 3389.5, "couleur": (255, 100, 100)},
            "Jupiter": {'nom': 'Jupiter', 'type': 'Géante gazeuse', 'composition_surface': 'Hydrogène (90%)',
                        'âge': '4,603 milliards d’années', 'rotation': '10 h', 'révolution': '4 333 jours',
                        "masse": 1.899e27, "rayon": 69911, "couleur": (200, 150, 50)},
            "Saturn": {'nom': 'Saturne', 'type': 'Géante gazeuse', 'composition_surface': 'Hydrogène (94%)',
                       'âge': '4,503 milliards d’années', 'rotation': '11 h', 'révolution': '10 757 jours',
                       "masse": 5.683e26, "rayon": 58232, "couleur": (195, 146, 79)},
            "Uranus": {'nom': 'Uranus', 'type': 'Géante gazeuse', 'composition_surface': 'Hydrogène (90%)',
                       'âge': '4,503 milliards d’années', 'rotation': '17 h', 'révolution': '30 687 jours',
                       "masse": 6.681e25, "rayon": 25362, "couleur": (172, 229, 238)},
            "Neptune": {'nom': 'Neptune', 'type': 'Géante gazeuse', 'composition_surface': 'Hydrogène (90%)',
                        'âge': '4,503 milliards d’années', 'rotation': '16 h', 'révolution': '60 197 jours',
                        "masse": 1.024e26, "rayon": 24622, "couleur": (124, 183, 187)},
            "Soleil": {'nom': 'Soleil', 'type': 'Étoile', 'composition_surface': 'Hydrogène (74%)',
                       'âge': '4,603 milliards d’années', 'rotation': '600 h', 'révolution': 'Aucune',
                       "masse": 1.989e30, "rayon": 696340, "couleur": (255, 0, 0)},
            "Lune": {'nom': 'Lune', 'type': 'Satellite naturel', 'composition_surface': 'Régolithe lunaire',
                     'âge': '4,46 milliards d’années', 'rotation': '655 h', 'révolution': '27 jours',
                     "masse": 7.347e22, "rayon": 1737.4, "couleur": (200, 200, 200)},
            "Europe": {'nom': 'Europe', 'type': 'Satellite naturel', 'composition_surface': 'Glace',
                       'âge': '4,5 milliards d’années', 'rotation': '85,2 h', 'révolution': '3,55 jours',
                       "masse": 4.799e22, "rayon": 1560.8, "couleur": (191, 207, 217)},
            "Io": {'nom': 'Io', 'type': 'Satellite naturel', 'composition_surface': 'Dioxyde de soufre',
                   'âge': '4,57 milliards d’années', 'rotation': '42,5 h', 'révolution': '42 h',
                   "masse": 8.931e22, "rayon": 1821.6, "couleur": (200, 180, 100)},

            "TON 618": {'nom': 'TON 618', 'type': 'Trou noir supermassif', 'composition_surface': 'Singularité',
                        'âge': '≈ 10 milliards d’années', 'rotation': 'Inconnue', 'révolution': 'Aucune',
                        "masse": 1.3e41, "rayon": 390000000000, "couleur": (15, 15, 15)},
            "Phoenix A": {'nom': 'Phoenix A', 'type': 'Trou noir supermassif', 'composition_surface': 'Singularité',
                          'âge': '≈ 8 milliards d’années', 'rotation': 'Inconnue', 'révolution': 'Aucune',
                          "masse": 2.0e41, "rayon": 590000000000, "couleur": (15, 15, 15)},
            "Hubble": {'nom': 'Télescope Hubble', 'type': 'Satellite artificiel',
                       'composition_surface': 'Métal et instruments', 'âge': '1990', 'rotation': '≈ 95 min',
                       'révolution': '≈ 95 min', "masse": 11110, "rayon": 0.007, "couleur": (180, 180, 180)},
            "Your Mom": {'nom': 'Your Mom', 'type': '???', 'composition_surface': 'Classifié', 'âge': 'Éternel',
                         'rotation': '∞', 'révolution': '∞', "masse": 1000 * 1.989e30, "rayon": 500000000000,
                         "couleur": (255, 105, 180)},

            "Comète 50km": {'nom': 'Comète (50 km)', 'type': 'Comète', 'composition_surface': 'Glace et poussière',
                            'âge': '4,6 milliards d’années', 'rotation': 'Variable', 'révolution': 'Très elliptique',
                            "masse": 1e15, "rayon": 50, "couleur": (200, 200, 255)},
            "Comète 10km": {'nom': 'Comète (10 km)', 'type': 'Comète', 'composition_surface': 'Glace et poussière',
                            'âge': '4,6 milliards d’années', 'rotation': 'Variable', 'révolution': 'Très elliptique',
                            "masse": 1e13, "rayon": 10, "couleur": (220, 220, 255)},
            "Comète 200km": {'nom': 'Comète (200 km)', 'type': 'Comète', 'composition_surface': 'Glace et poussière',
                             'âge': '4,6 milliards d’années', 'rotation': 'Variable', 'révolution': 'Très elliptique',
                             "masse": 1e17, "rayon": 200, "couleur": (180, 180, 255)},

            "Arcturus": {'nom': 'Arcturus', 'type': 'Étoile géante rouge', 'composition_surface': 'Hydrogène et hélium',
                         'âge': '≈ 7 milliards d’années', 'rotation': '≈ 2 ans', 'révolution': 'Aucune',
                         "masse": 2.2 * 1.989e30, "rayon": 17700000, "couleur": (255, 140, 80)},
            "Bételgeuse": {'nom': 'Bételgeuse', 'type': 'Supergéante rouge',
                           'composition_surface': 'Hydrogène et hélium', 'âge': '≈ 10 millions d’années',
                           'rotation': '≈ 36 ans', 'révolution': 'Aucune', "masse": 20 * 1.989e30, "rayon": 617000000,
                           "couleur": (255, 80, 50)},
            "Sirius B": {'nom': 'Sirius B', 'type': 'Naine blanche', 'composition_surface': 'Carbone et oxygène',
                         'âge': '≈ 120 millions d’années', 'rotation': 'Inconnue',
                         'révolution': '50 ans (avec Sirius A)', "masse": 1.02 * 1.989e30, "rayon": 5800,
                         "couleur": (200, 220, 255)},
            "Rigel": {'nom': 'Rigel', 'type': 'Supergéante bleue', 'composition_surface': 'Hydrogène',
                      'âge': '≈ 8 millions d’années', 'rotation': '≈ 25 jours', 'révolution': 'Aucune',
                      "masse": 21 * 1.989e30, "rayon": 78000000, "couleur": (180, 220, 255)}
        }

        data = corps.get(nom, corps["Mercure"])

        planete = {"nom": data["nom"], "position": euclid.Vector2(x, y), "vitesse": euclid.Vector2(0, 0),
                   "masse": data["masse"], "rayon": data["rayon"], "couleur": data["couleur"], 'type': data['type'],
                   'composition_surface': data['composition_surface'], 'âge': data['âge'],
                   'rotation': data['rotation'], 'révolution': data['révolution']}

        self.planetes.append(planete)

    def kepler(self):
        color_dimmer = None
        path = []
        for planete_1 in self.planetes:
            max_centrum = -1
            for planete_2 in self.planetes:
                if planete_2 == planete_1:
                    continue
                gravitational_force = planete_2['masse'] / (planete_1['position'] - planete_2['position']).magnitude_squared() + (1 * 10 ** -10)
                if gravitational_force > max_centrum:
                    max_centrum = gravitational_force
                    self.centrum = planete_2
                    self.centrum['isCentrum'] = True
            if self.centrum is None:
                continue
            gravitational_parameter = self.G * self.centrum['masse']
            current_velocity = planete_1['vitesse'] - self.centrum['vitesse']
            current_position_vector = planete_1['position'] - self.centrum['position']
            current_position = current_position_vector.magnitude()
            vectorial_epsilon = (1 / gravitational_parameter *
                                 ((current_velocity.magnitude_squared() -
                                   (gravitational_parameter / current_position)) * current_position_vector -
                                  (current_position_vector.dot(current_velocity)) * current_velocity))
            epsilon = vectorial_epsilon.magnitude() + (1 * 10 ** -10)
            omega = math.atan2(vectorial_epsilon.y, vectorial_epsilon.x)
            paracond = (2 / current_position) - (current_velocity.magnitude_squared() / gravitational_parameter)
            if paracond <= 0:
                continue
            semimajor_axis = 1 / paracond
            orb_dots = []
            for k in range(301):
                theta = (2 * math.pi * k) / 300
                r = (semimajor_axis * (1 - epsilon ** 2)) / (1 + epsilon * math.cos(theta))
                x = (self.centrum['position'].x + r * math.cos(theta + omega))
                y = (self.centrum['position'].y + r * math.sin(theta + omega))
                orbit_x, orbit_y = self.pos_objet_orbite(pygame.Vector2(x, y))
                orb_dots.append((orbit_x, orbit_y))
                color_dimmer = pygame.Color(planete_1['couleur']).lerp((0, 0, 0), 0.7)
            orbital_momentum = math.sqrt((self.G * self.centrum['masse']) / current_position)
            tan_current_position = pygame.Vector2(
                (current_position_vector.y * -1), current_position_vector.x).normalize()
            if self.is_helpingorbits is True:
                planete_1['vel'] = self.centrum['vel'] + (orbital_momentum * tan_current_position)
            path.append({'dots': orb_dots, 'color': color_dimmer, 'epsilon': epsilon, 'a': semimajor_axis, 'planet': planete_1,
                         'vel': planete_1['vitesse'], 'omega': omega})
        return path

    def newton(self, planet):
        for i in self.kepler():
            if planet == i['planet']:
                direction = self.centrum['position'] - i['planet']['position']
                if direction.magnitude() == 0:
                    vector = euclid.Vector2(0, 0)
                    return vector
                acceleration = direction.normalize()/self.acceleration.magnitude()
                return acceleration
        return euclid.Vector2(0, 0)

    # TODO: needs improvement
    def orbital_position_editor(self, angle_degrees):
        orbital_data = None
        if self.is_editingorbits and self.p_index is not None:
            theta = math.radians(angle_degrees)
            planet = self.planetes[self.p_index]
            if planet:
                for i in self.kepler():
                    if i['planet'] == planet:
                        orbital_data = i
                        break
                if orbital_data:
                    semimajor = orbital_data['a']
                    ecc = orbital_data['epsilon']
                    omega = orbital_data['omega']
                    r = (semimajor * (1 - ecc ** 2)) / (1 + ecc * math.cos(theta))
                    centrum = self.centrum
                    planet['position'].x = centrum['position'].x + r * math.cos(theta + omega)  # type: ignore
                    planet['position'].y = centrum['position'].y + r * math.sin(theta + omega)  # type: ignore

                    inner_sqrt = math.sqrt(
                        (self.G * centrum['masse']) / ((semimajor * (1 - ecc ** 2)) + 1 * 10 ** -10))
                    urvx = -inner_sqrt * math.sin(theta)
                    urvy = inner_sqrt * (ecc + math.cos(theta))
                    rvx = urvx * math.cos(omega) - urvy * math.sin(omega)
                    rvy = urvx * math.sin(omega) + urvy * math.cos(omega)
                    planet['vitesse'].x = rvx + centrum['vitesse'].x  # type: ignore
                    planet['vitesse'].y = rvy + centrum['vitesse'].y  # type: ignore

    def orbital_eccentricity_editor(self, edited_ecc):
        if self.is_editingorbits is not None:
            new_ecc = edited_ecc / 100
            planet = self.planetes[self.p_index]
            if planet:
                for i in self.kepler():
                    if i['planet'] == planet:
                        semimajor = i['a']
                        omega = i['omega']
                        i['epsilon'] = new_ecc
                        relative_pos = planet['position'] - self.centrum['position']
                        theta = math.atan2(relative_pos.y, relative_pos.x) - omega
                        new_r = (semimajor * (1 - new_ecc ** 2)) / (1 + new_ecc * math.cos(theta))
                        gravitational_parameter = self.G * self.centrum['masse']
                        orbit_size = math.sqrt(gravitational_parameter * semimajor * (1 - new_ecc ** 2))
                        velocity = (gravitational_parameter / orbit_size) * new_ecc * math.sin(theta)
                        velocity_tangent = orbit_size / new_r

                        urvx = velocity * math.cos(theta + omega) - velocity_tangent * math.sin(theta + omega)
                        urvy = velocity * math.sin(theta + omega) + velocity_tangent * math.cos(theta + omega)
                        planet['vitesse'].x = urvx + self.centrum['vitesse'].x
                        planet['vitesse'].y = urvy + self.centrum['vitesse'].y

    def orbital_velocity_editor(self, edited_value):
        if self.is_editingorbits is not None:
            planet = self.planetes[self.p_index]
            if planet:
                for i in self.kepler():
                    if i['planet'] == planet:
                        new_velocity_addition = edited_value
                        planet['vitesse'].x += new_velocity_addition + self.centrum['vitesse'].x
                        planet['vitesse'].y += new_velocity_addition + self.centrum['vitesse'].y

    def orbital_velocity_color(self, edited_value):
        if self.is_editingorbits is not None:
            self.planetes[self.p_index]['couleur'] = edited_value

    def orbital_vector(self):
        scope_updater = 0
        vector_data = []
        for i in self.kepler():
            orbital_data = i['dots'][scope_updater:scope_updater + 50]
            vectorial_data = [euclid.Vector2(x + i['planet']['rayon'] / 2, y + i['planet']['rayon'] / 2) for x, y in
                              orbital_data]
            start = vectorial_data[0]
            end = vectorial_data[-1]
            arrow = self.vector_arrow(start=start, end=end)
            arrow_left, arrow_right = arrow

            vectorial_data.append(arrow_left)
            vectorial_data.append(end)
            vectorial_data.append(arrow_right)

            vector_data.extend(vectorial_data)
            scope_updater += 1
        return vector_data

    def force_vector(self):
        force_vec = {}
        for i in self.planetes:
            acc = self.newton(i)
            force = i['masse'] * acc
            force_vec[i['nom']] = force
        return force_vec

    def mousePressEvent(self, event):
        self.souris_pos = euclid.Vector2(event.pos().x(), event.pos().y())
        self.old_mouse = event.position()

        if event.button() == Qt.MouseButton.RightButton:
            # clic droit : sélectionner la planète active
            for n, p in enumerate(self.planetes):
                sx, sy = p['position'].x, p['position'].y
                if self.souris_pos.distance_to((sx, sy)) <= p['rayon']:
                    self.active_planet = n
                    break

        elif event.button() == Qt.MouseButton.LeftButton:
            # clic gauche : sélectionner et mettre à jour statsdock
            for index, planete in enumerate(self.planetes):
                x, y = self.pos_objet_orbite(planete["position"])
                diff = self.souris_pos - euclid.Vector2(x + 8, y - 5)
                if abs(diff) <= max(planete["rayon"] * self.scale, 15):
                    self.active_planet = index
                    self.update_target(planete)
                    # Mettre à jour les infos dans statsdock
                    self.statsdock.body_label.setText(f'{planete["nom"]}')
                    self.statsdock.body_label.repaint()
                    self.statsdock.body_type.setText(f'Type: {planete["type"]}')
                    self.statsdock.body_type.repaint()
                    self.statsdock.surface_label.setText(f'Composition de la surface: {planete["composition_surface"]}')
                    self.statsdock.surface_label.repaint()
                    self.statsdock.age_label.setText(f'Âge: {planete["âge"]}')
                    self.statsdock.age_label.repaint()
                    self.statsdock.rotation_label.setText(f'Durée de la rotation: {planete["rotation"]}')
                    self.statsdock.rotation_label.repaint()
                    self.statsdock.revolution_label.setText(f'Durée de la révolution: {planete["révolution"]}')
                    self.statsdock.revolution_label.repaint()
                    break

    def mouseMoveEvent(self, event):
        pos_x, pos_y = event.pos().x(), event.pos().y()
        self.souris_pos = euclid.Vector2(pos_x, pos_y)

        if self.active_planet is not None and self.souris_pos and self.camera_mode != 'follow':
            dragged_pos = event.position()
            distance = dragged_pos - self.old_mouse
            rel = euclid.Vector2(distance.x(), distance.y())/self.scale
            self.planetes[self.active_planet]['position'] += rel
            self.old_mouse = dragged_pos

    def mouseReleaseEvent(self, event):
        self.active_planet = None

    def game_loop(self):
        self.playscreen.fill((0, 0, 0))
        if self.measuringtape_state:
            self.measuringtape()

        if not self.active and len(self.planetes) > 0:
            if self.target is not None and self.camera_mode == "follow":
                pos_x = self.target.x - (self.width() / self.scale / 2)
                pos_y = self.target.y - (self.height() / self.scale / 2)
                self.camera_pos = euclid.Vector2(pos_x, pos_y)

            for planete in self.planetes:
                rx, ry = self.pos_objet_orbite(planete["position"])
                rayon = planete["rayon"] * self.scale
                if rayon < 1:
                    text = self.font.render(f"{planete['nom']}", True, (255, 255, 255))
                    self.playscreen.blit(text, (rx - 20, ry - 7))
                else:
                    if rayon > 800 or not os.path.exists("./images/Skins/soleil.jpg"):
                        if all(c < 50 for c in planete["couleur"]) and rayon < 3000:
                            pygame.draw.circle(self.playscreen, (255, 255, 255), (rx, ry), rayon, int(0.05 * rayon))
                        else:
                            pygame.draw.circle(self.playscreen, planete["couleur"], (rx, ry), rayon)
                    else:
                        surface = self.get_planet_surface(planete)
                        self.playscreen.blit(surface, (rx - rayon, ry - rayon))

        if self.camera_mode == "follow" and self.target is not None:
            pos_x = self.target.x - (self.width() / self.scale / 2)
            pos_y = self.target.y - (self.height() / self.scale / 2)
            self.camera_pos = euclid.Vector2(pos_x, pos_y)

        if self.simulation == 1 and len(self.planetes) > 2:
            self.active = True
            if not self.vitesse_state:
                self.vitesse_simulation1()
            objet_central, objet_orbite1, objet_orbite2 = self.planetes[0], self.planetes[1], self.planetes[2]
            self.simulation_objet_central_3corps(objet_central, objet_orbite1, objet_orbite2)

        elif self.simulation == 2 and len(self.planetes) > 1:
            self.active = True
            if not self.vitesse_state:
                self.vitesse_simulation2()
            objet_orbite1, objet_orbite2 = self.planetes[0], self.planetes[1]
            self.simulation_2corps(objet_orbite1, objet_orbite2)

        elif self.simulation == 3 and len(self.planetes) > 2:
            self.active = True
            if not self.vitesse_state:
                self.vitesse_simulation3()
            objet_orbite1, objet_orbite2, objet_orbite3 = self.planetes[0], self.planetes[1], self.planetes[2]
            self.simulation_3corps(objet_orbite1, objet_orbite2, objet_orbite3)

        elif self.simulation == 4:
            pass

        else:
            pass

        if Qt.Key.Key_F in self.keys_pressed:
            if not self.f_pressed_handled:
                self.changer_vue()
                self.f_pressed_handled = True
        else:
            self.f_pressed_handled = False

        speed = 3

        if Qt.Key.Key_Shift in self.keys_pressed:
            speed = 10
        if self.camera_mode == "free":
            if Qt.Key.Key_A in self.keys_pressed:
                self.camera_pos.x -= speed / self.scale
            if Qt.Key.Key_D in self.keys_pressed:
                self.camera_pos.x += speed / self.scale
            if Qt.Key.Key_W in self.keys_pressed:
                self.camera_pos.y -= speed / self.scale
            if Qt.Key.Key_S in self.keys_pressed:
                self.camera_pos.y += speed / self.scale

        if  not self.is_showingorbits:
            for w in self.kepler():
                if len(w['dots']):
                    pygame.draw.lines(self.playscreen, w['color'], False, w['dots'], 1)

        if self.target is not None:
            distance_x = self.souris_pos_vector.x + self.scale * (self.camera_pos.x - self.target.x)
            distance_y = self.souris_pos_vector.y + self.scale * (self.camera_pos.y - self.target.y)
            distance = math.sqrt(distance_x ** 2 + distance_y ** 2) / self.scale
            if distance < 1000000000:
                text_distance = self.font.render(f"{int(distance):,} km | {round(distance / 1.496e8, 3)} UA", True,(255, 255, 255))
            else:
                text_distance = self.font.render(f"{distance:.2e} km | {int(distance / 1.496e8)} UA", True,(255, 255, 255))
            self.playscreen.blit(text_distance, (10, 10))

        texte_camera = self.font.render(f"Mode caméra: {self.camera_mode}", True, (255, 255, 255))
        self.playscreen.blit(texte_camera, (10, self.height() - 20))


        if self.is_showingorbitalvector:
            dots = [(i.x, i.y) for i in self.orbital_vector()]
            if len(dots) >= 2:
                print(dots)
                pygame.draw.lines(self.playscreen, (255, 255, 255), False, dots, 2)

        if self.is_showingforcevector:
            force = self.force_vector()
            for pl in self.planetes:
                screenx, screeny = self.pos_objet_orbite(pl['position'])
                for x, y in self.force_vector().items():
                    if x == pl['nom']:
                        vectorial_force = force[x]
                        if vectorial_force.magnitude() > 0:
                            norm_vector = vectorial_force.normalize() * 25
                            end_pos = (int(screenx + norm_vector.x), int(screeny + norm_vector.y))
                            pygame.draw.line(self.playscreen, (255, 255, 255), (screenx, screeny), end_pos, 1)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Transforme la surface Pygame en QImage
        raw_data = pygame.image.tostring(self.playscreen, "RGB")
        image = QImage(raw_data, self.playscreen.get_width(), self.playscreen.get_height(), 3 * self.playscreen.get_width(), QImage.Format.Format_RGB888)
        painter.drawImage(self.rect(), image)
