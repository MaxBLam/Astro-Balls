import pygame
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QImage
from PySide6.QtWidgets import QWidget
import euclid
import math


class PyGameWidget(QWidget):
    measuring_updater_signal = Signal()

    def __init__(self, statsdock):
        super().__init__()

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
        self.font = pygame.font.SysFont(None, 20)

        self.simulation = 1
        self.G = 6.6743*10**-15
        self.scale = 20**6 / 100**6
        self.facteur_ellipse = 1 # <1 pour une ellipse
        self.dtime = 1 / self.fps_simulation

        self.f_pressed_handled = False
        self.target = None
        self.camera_pos = euclid.Vector2(0,0)
        self.camera_mode = "follow"  # "free", "follow", "milieu"

        self.timer.timeout.connect(self.game_loop)

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

    def speed_interactive(self, value : int):
        self.dtime = 1 / self.fps_simulation * (0.3*value)**4

    def scale_interactive(self, value : int):
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
        print(self.target)

    def vitesse_simulation1(self):
        self.planetes[0]["vitesse"] = euclid.Vector2(0, 0)
        self.planetes[1]["vitesse"] = self.vitesse_gravitationnelle(self.planetes[0], self.planetes[1]) * self.facteur_ellipse
        self.planetes[2]["vitesse"] = self.vitesse_gravitationnelle(self.planetes[1], self.planetes[2]) + self.planetes[1]["vitesse"]
        self.vitesse_state = True

    def simulation_objet_central_3corps(self, objet_central, objet_orbite1, objet_orbite2):
        acc_objet_central = euclid.Vector2(0, 0)
        acc_objet_orbite1 = self.force_gravitationnelle(objet_orbite1, objet_central)
        acc_objet_orbite2 = self.force_gravitationnelle(objet_orbite2, objet_orbite1) + self.force_gravitationnelle(objet_orbite2, objet_central)

        list_objets = [(objet_central, acc_objet_central), (objet_orbite1, acc_objet_orbite1), (objet_orbite2, acc_objet_orbite2)]
        list_objets_update = self.mouvement(list_objets)

        if self.camera_mode == "follow":
            pos_x = objet_orbite1["position"].x - (self.width() / self.scale / 2)
            pos_y = objet_orbite1["position"].y - (self.height() / self.scale / 2)
            self.camera_pos = euclid.Vector2(pos_x, pos_y)
        elif self.camera_mode == "milieu":
            pos_x = ((objet_central["position"].x + objet_orbite1["position"].x) / 2) - (self.width() / self.scale / 2)
            pos_y = ((objet_central["position"].y + objet_orbite1["position"].y) / 2) - (self.height() / self.scale / 2)
            self.camera_pos = euclid.Vector2(pos_x, pos_y)
            #self.camera_pos = (objet_central["position"] + objet_orbite1["position"]) / 2

        self.display(list_objets_update)

    def simulation_2corps(self, objet_orbite1, objet_orbite2):
        acc_objet_orbite1 = self.force_gravitationnelle(objet_orbite1, objet_orbite2)
        acc_objet_orbite2 = self.force_gravitationnelle(objet_orbite2, objet_orbite1)

        list_objets = [(objet_orbite1, acc_objet_orbite1), (objet_orbite2, acc_objet_orbite2)]
        list_objets_update = self.mouvement(list_objets)

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

    def kepler(self):
        color_dimmer = None
        path = []
        for i in self.planetes:
            max_centrum = -1
            for j in self.planetes:
                if j == i:
                    continue
                gravitational_force = j['masse'] / (i['position'] - j['position']).magnitude_squared() + (1*10 **-10)
                if gravitational_force > max_centrum:
                    max_centrum = gravitational_force
                    self.centrum = j
                    self.centrum['isCentrum'] = True
            if self.centrum is None:
                continue
            gravitational_parameter = self.G * self.centrum['masse']
            current_velocity = i['vitesse'] - self.centrum['vitesse']
            current_position_vector = i['position'] - self.centrum['position']
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
                r = (semimajor_axis * (1 - epsilon ** 2)) / (1 + epsilon * math.cos(theta)) + (1*10**-10)
                x = (self.centrum['position'].x + r * math.cos(theta + omega))
                y = (self.centrum['position'].y + r * math.sin(theta + omega))
                orbit_x, orbit_y = self.pos_objet_orbite(pygame.Vector2(x, y))
                orb_dots.append((orbit_x, orbit_y))
                color_dimmer = pygame.Color(i['couleur']).lerp((0, 0, 0), 0.7)
            orbital_momentum = math.sqrt((self.G * self.centrum['masse']) / current_position)
            tan_current_position = pygame.Vector2(
                (current_position_vector.y * -1), current_position_vector.x).normalize()
            if self.is_helpingorbits is True:
                i['vel'] = self.centrum['vel'] + (orbital_momentum * tan_current_position)
            path.append({'dots': orb_dots, 'color': color_dimmer, 'epsilon': epsilon, 'a': semimajor_axis, 'planet': i,
                         'vel': i['vel'], 'omega': omega})
        return path

    def orbit_editor(self):
        self.is_editingorbits = True
        receiver_config_button = self.sender()
        self.p_index = receiver_config_button.property('index') + 1
        return self.is_editingorbits

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
                        (self.G * centrum['masse']) / ((semimajor * (1-ecc**2)) + 1*10**-10))
                    urvx = -inner_sqrt * math.sin(theta)
                    urvy = inner_sqrt * (ecc + math.cos(theta))
                    rvx = urvx * math.cos(omega) - urvy * math.sin(omega)
                    rvy = urvx * math.sin(omega) + urvy * math.cos(omega)
                    planet['vitesse'].x = rvx + centrum['vitesse'].x  # type: ignore
                    planet['vitesse'].y = rvy + centrum['vitesse'].y  # type: ignore

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
            list_objets_update.append(objet)

        return list_objets_update

    def changer_vue(self):
        if self.camera_mode == "free":
            self.camera_mode = "milieu"
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

    def display(self, objets: list):# objet[0] = objet, objet[1] = acc_objet
        self.playscreen.fill((0,0,0))

        for objet in objets:
            rx, ry = self.pos_objet_orbite(objet[0]["position"])
            rayon = objet[0]["rayon"] * self.scale

            if rayon < 1:
                text = self.font.render(f"{objet[0]['nom']}", True, (255, 255, 255))
                self.playscreen.blit(text, (int(rx) - 20, int(ry) - 7))
            else:
                pygame.draw.circle(self.playscreen, objet[0]["couleur"], (int(rx), int(ry)), int(rayon))

        self.update()

        for j in self.point:
            pygame.draw.circle(self.playscreen, (255, 255, 255), j, 3)
        if len(self.point) == 2:
            pygame.draw.line(self.playscreen, (255, 255, 255), start_pos=self.point[0], end_pos=self.point[1], width=3)

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
                        "masse": 1.3e41, "rayon": 390000000000, "couleur": (50, 50, 50)},
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

        planete = {"nom": data["nom"], "position": euclid.Vector2(x, y), "vitesse": euclid.Vector2(0,0), "masse": data["masse"],
              "rayon": data["rayon"], "couleur": data["couleur"], 'type': data['type'], 'composition_surface': data['composition_surface'],
              'âge': data['âge'], 'rotation': data['rotation'], 'révolution': data['révolution']}

        self.planetes.append(planete)

    def mousePressEvent(self, event):
        souris_pos = euclid.Vector2(event.pos().x(), event.pos().y())

        if event.button() == Qt.MouseButton.RightButton:
            # clic droit : sélectionner la planète active
            for n, p in enumerate(self.planetes):
                sx, sy = p['position'].x, p['position'].y
                if souris_pos.distance_to((sx, sy)) <= p['rayon']:
                    self.active_planet = n
                    break

        elif event.button() == Qt.MouseButton.LeftButton:
            # clic gauche : sélectionner et mettre à jour statsdock
            for index, planete in enumerate(self.planetes):
                x, y = self.pos_objet_orbite(planete["position"])
                diff = souris_pos - euclid.Vector2(x + 8, y - 5)
                if abs(diff) <= max(planete["rayon"] * self.scale, 15):
                    self.active_planet = planete
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

    def mouseReleaseEvent(self, event):
        self.active_planet = None

    def mouseMoveEvent(self, event):
        if self.active_planet is not None:
            # Déplacer la planète active
            dx = event.position().x() - event.lastPosition().x()
            dy = event.position().y() - event.lastPosition().y()
            self.planetes[self.active_planet["position"]] += euclid.Vector2(dx, dy) / self.scale

    def game_loop(self):
        if self.measuringtape_state:
            self.measuringtape()

        if not self.active:
            self.playscreen.fill((0, 0, 0))
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
                    self.update()
                else:
                    pygame.draw.circle(self.playscreen, planete["couleur"], (rx, ry), rayon)
                    self.update()
        if self.simulation == 1 and len(self.planetes) > 2:
            self.active = True
            if not self.vitesse_state:
                self.vitesse_simulation1()
            objet_central, objet_orbite1, objet_orbite2 = self.planetes[0], self.planetes[1], self.planetes[2]
            self.simulation_objet_central_3corps(objet_central, objet_orbite1, objet_orbite2)

        elif self.simulation == 2:
            pass

        elif self.simulation == 3:
            pass

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



    def paintEvent(self, event):
        painter = QPainter(self)
        # Transforme la surface Pygame en QImage
        raw_data = pygame.image.tostring(self.playscreen, "RGB")
        image = QImage(raw_data, self.playscreen.get_width(), self.playscreen.get_height(), 3 * self.playscreen.get_width(), QImage.Format.Format_RGB888)
        painter.drawImage(self.rect(), image)