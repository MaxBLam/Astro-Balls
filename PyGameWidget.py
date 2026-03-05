import os
import pygame
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QWidget
import euclid
import math


class PyGameWidget(QWidget):
    measuring_updater_signal = Signal()

    def __init__(self, statsdock):
        super().__init__()

        self.statsdock = statsdock
        self.y = None
        self.x = None
        self.is_showingorbits = False
        self.setAcceptDrops(True)
        self.planetes = []
        self.planetes_pos = []
        self.active_planet = None
        self.vitesse_state = False
        self.playscreen = None
        self.point = []
        self.measuringtape_state = False
        self.keys_pressed = set()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        self.pygame_windowhandler()

        self.fps_simulation = 120
        self.timer = QTimer()
        self.timer.start(8)

        self.font = pygame.font.SysFont(None, 20)

        self.simulation = 1
        self.G = 6.6743*10**-15
        self.scale = 2**4 / 100**4
        self.facteur_ellipse = 0.5 # <1 pour une ellipse
        self.dtime = 1 / self.fps_simulation

        self.f_pressed_handled = False
        self.camera_pos = euclid.Vector2(0, 0)
        self.camera_milieu_pos = euclid.Vector2(0, 0)
        self.camera_mode = "free"  # "free", "follow", "milieu"

        self.timer.timeout.connect(self.game_loop)

    def pygame_windowhandler(self):
        os.environ["SDL_WINDOWID"] = str(int(self.winId()))
        os.environ["SDL_VIDEODRIVER"] = "windows"
        pygame.init()
        pygame.font.init()
        self.playscreen = pygame.display.set_mode(size=(0, 0))
        self.x, self.y = self.playscreen.get_size()

    def update_size(self):
        pygame.display.update()
        self.x, self.y = pygame.display.get_window_size()

    def keyPressEvent(self, event):
        self.keys_pressed.add(event.key())
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())
        super().keyReleaseEvent(event)

    def speed_interactive(self, value : int):
        self.dtime = 1 / self.fps_simulation * (0.3*value)**3

    def scale_interactive(self, value : int):
        self.scale = float(value**4 / 100**4)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        name = event.mimeData().text()
        pos = event.pos()
        print(pos)
        world_x = (pos.x() + self.x / 2 - self.camera_pos.x) / self.scale
        world_y = (pos.y() + self.y / 2 - self.camera_pos.y) / self.scale
        self.corps(name, world_x, world_y)

        if self.simulation == 1 and len(self.planetes) == 3 and not self.vitesse_state:
            self.vitesse_simulation1()

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

        self.camera_milieu_pos = self.scale * (self.planetes[1]["position"] + self.planetes[0]["position"]) / 2
        self.display(list_objets_update)

    def simulation_2corps(self, objet_orbite1, objet_orbite2):
        acc_objet_orbite1 = self.force_gravitationnelle(objet_orbite1, objet_orbite2)
        acc_objet_orbite2 = self.force_gravitationnelle(objet_orbite2, objet_orbite1)

        list_objets = [(objet_orbite1, acc_objet_orbite1), (objet_orbite2, acc_objet_orbite2)]
        list_objets_update = self.mouvement(list_objets)

        # utiliser les variables locales passées en paramètre (évite référence à des attributs inexistants)
        self.camera_milieu_pos = self.scale * (objet_orbite1["position"] + objet_orbite2["position"]) / 2
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

    def kepler(self):
        centrum = None
        gravitational_parameter = None
        color_dimmer = None
        # max_force = 0 (for later)
        # dominant = self.dmomentum (for later)
        path = []
        for i in self.planetes:
            if i['type'] == 'Étoile' or i['masse'] >= 9999:
                centrum = i
                gravitational_parameter = self.G * centrum['masse']
                break
        if not centrum:
            return []
        for i in self.planetes:
            if i == centrum:
                continue
            current_velocity = i['vitesse']
            current_position_vector = i['position'] - centrum['position']
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
                r = (semimajor_axis * (1 - epsilon ** 2)) / (1 + epsilon * math.cos(theta)) + (1 * 10 ** -10)
                x = (centrum['position'].x + r * math.cos(theta + omega))
                y = (centrum['position'].y + r * math.sin(theta + omega))
                orbit_x, orbit_y = self.pos_objet_orbite(pygame.Vector2(x, y))
                orb_dots.append((orbit_x, orbit_y))
                color_dimmer = pygame.Color(i['couleur']).lerp((0, 0, 0), 0.7)
            path.append({'dots': orb_dots, 'color': color_dimmer, 'epsilon': epsilon, 'a': semimajor_axis, 'planet': i})
        return path

    def mouvement(self, objets):  # objet[0] = objet, objet[1] = acc_objet
        list_objets_update = []
        for objet in objets:
            objet[0]["vitesse"] += objet[1] * self.dtime
            objet[0]["position"] += objet[0]["vitesse"] * self.dtime
            list_objets_update.append(objet)

            #if self.camera_mode == "follow" and objet[0]["nom"] == self.camera_target["nom"]:
                #self.camera_pos = objet[0]["position"] * self.scale
        #print (list_objets_update)
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
            rayon = objet[0]["rayon"] * self.scale

            if rayon < 1:
                text = self.font.render(f"{objet[0]['nom']}", True, (255, 255, 255))
                self.playscreen.blit(text, (int(rx), int(ry)))
            else:
                pygame.draw.circle(self.playscreen, objet[0]["couleur"], (int(rx), int(ry)), rayon)

        for j in self.point:
            pygame.draw.circle(self.playscreen, (255, 255, 255), j, 3)
        if len(self.point) == 2:
            pygame.draw.line(self.playscreen, (255, 255, 255), start_pos=self.point[0], end_pos=self.point[1], width=3)

        pygame.display.flip()

    def corps(self, nom, x, y):
        corps = {
    "Mercure": {'nom': 'Mercure', 'type': 'Planète', 'composition_surface': 'Métallique (70%)', 'âge': '4,503 milliards d’années', 'rotation': '1 408 h', 'révolution': '88 jours', "masse": (3.285*10**23), "rayon": 2439.7, "couleur": (245, 245, 220)},
    "Venus": {'nom': 'Vénus', 'type': 'Planète', 'composition_surface': 'Basalte', 'âge': '4,503 milliards d’années', 'rotation': '5 832 h', 'révolution': '225 jours', "masse": (4.867*10**24), "rayon": 6051.8, "couleur": (255, 215, 0)},
    "Terre": {'nom': 'Terre', 'type': 'Planète', 'composition_surface': 'Granite', 'âge': '4,543 milliards d’années', 'rotation': '24 h', 'révolution': '365 jours', "masse": (5.972*10**24), "rayon": 6371.0, "couleur": (0, 100, 255)},
    "Mars": {'nom': 'Mars', 'type': 'Planète', 'composition_surface': 'Fer oxydé', 'âge': '4,603 milliards d’années', 'rotation': '25 h', 'révolution': '687 jours', "masse": (6.416993*10**23), "rayon": 3389.5, "couleur": (255, 100, 100)},
    "Jupiter": {'nom': 'Jupiter', 'type': 'Géante gazeuse', 'composition_surface': 'Hydrogène (90%)', 'âge': '4,603 milliards d’années', 'rotation': '10 h', 'révolution': '4 333 jours', "masse": (1.899*10**27), "rayon": 69911, "couleur": (200, 150, 50)},
    "Saturn": {'nom': 'Saturne', 'type': 'Géante gazeuse', 'composition_surface': 'Hydrogène (94%)', 'âge': '4,503 milliards d’années', 'rotation': '11 h', 'révolution': '10 757 jours', "masse": (5.683*10**26), "rayon": 58232, "couleur": (195, 146, 79)},
    "Uranus": {'nom': 'Uranus', 'type': 'Géante gazeuse', 'composition_surface': 'Hydrogène (90%)', 'âge': '4,503 milliards d’années', 'rotation': '17 h', 'révolution': '30 687 jours', "masse": (6.681*10**25), "rayon": 25362, "couleur": (172, 229, 238)},
    "Neptune": {'nom': 'Neptune', 'type': 'Géante gazeuse', 'composition_surface': 'Hydrogène (90%)', 'âge': '4,503 milliards d’années', 'rotation': '16 h', 'révolution': '60 197 jours', "masse": (1.024*10**26), "rayon": 24622, "couleur": (124, 183, 187)},
    "Soleil": {'nom': 'Soleil', 'type': 'Étoile', 'composition_surface': 'Hydrogène (74%)', 'âge': '4,603 milliards d’années', 'rotation': '600 h', 'révolution': 'Aucune', "masse": (1.989*10**30), "rayon": 696340, "couleur": (255, 0, 0)},
    "Lune": {'nom': 'Lune', 'type': 'Satellite naturel', 'composition_surface': 'Régolithe lunaire', 'âge': '4,46 milliards d’années', 'rotation': '655 h', 'révolution': '27 jours', "masse": (7.347*10**22), "rayon": 1737.4, "couleur": (200, 200, 200)},
    "Europe": {'nom': 'Europe', 'type': 'Satellite naturel', 'composition_surface': 'Glace', 'âge': '4,5 milliards d’années', 'rotation': '85,2 h', 'révolution': '3,55 jours', "masse": (4.799*10**22), "rayon": 1560.8, "couleur": (191, 207, 217)},
    "Io": {'nom': 'Io', 'type': 'Satellite naturel', 'composition_surface': 'Dioxyde de soufre', 'âge': '4,57 milliards d’années', 'rotation': '42,5 h', 'révolution': '42 h', "masse": (8.931*10**22), "rayon": 1821.6, "couleur": (200, 180, 100)}
        }

        data = corps.get(nom, corps["Mercure"])

        planete = {"nom": data["nom"], "position": pygame.Vector2(x, y), "vitesse": pygame.Vector2(0,0), "masse": data["masse"],
              "rayon": data["rayon"], "couleur": data["couleur"], 'type': data['type'], 'composition_surface': data['composition_surface'],
              'âge': data['âge'], 'rotation': data['rotation'], 'révolution': data['révolution']}

        self.planetes.append(planete)

    def game_loop(self):
        if self.measuringtape_state:
            self.measuringtape()

        self.update_size()

        if self.simulation == 1:
            if len(self.planetes) > 2:
                objet_central, objet_orbite1, objet_orbite2 = self.planetes[0], self.planetes[1], self.planetes[2]
                self.simulation_objet_central_3corps(objet_central, objet_orbite1, objet_orbite2)
            else:
                if self.is_showingorbits:
                    for w in self.kepler():
                        if len(w['dots']):
                            pygame.draw.lines(self.playscreen, w['color'], False, w['dots'], 1)

                for planete in self.planetes:
                    rx, ry = self.pos_objet_orbite(planete['position'])
                    pygame.draw.circle(self.playscreen, planete["couleur"], (int(rx), int(ry)), planete["rayon"] * self.scale)

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
                self.camera_pos.x -= speed
            if Qt.Key.Key_D in self.keys_pressed:
                self.camera_pos.x += speed
            if Qt.Key.Key_W in self.keys_pressed:
                self.camera_pos.y -= speed
            if Qt.Key.Key_S in self.keys_pressed:
                self.camera_pos.y += speed
        elif self.camera_mode == "milieu":
            self.camera_pos = self.camera_milieu_pos

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    souris_pos = pygame.Vector2(event.pos)
                    for n, p in enumerate(self.planetes):
                        sx, sy = self.pos_objet_orbite(p['position'])
                        if souris_pos.distance_to((sx, sy)) <= p['rayon']:
                            self.active_planet = n
                            break
                if event.button == 1:
                    m_pos = pygame.Vector2(event.pos)
                    for n, p in enumerate(self.planetes):
                        sx, sy = self.pos_objet_orbite(p['position'])
                        if m_pos.distance_to((sx, sy)) <= p['rayon']:
                            self.active_planet = n
                            self.statsdock.body_label.setText(f'{p['nom']}')
                            self.statsdock.body_label.repaint()
                            self.statsdock.body_type.setText(f'Type: {p['type']}')
                            self.statsdock.body_type.repaint()
                            self.statsdock.surface_label.setText(f'Surface Composition: {p['composition_surface']}')
                            self.statsdock.body_type.repaint()
                            self.statsdock.age_label.setText(f'Age: {p['âge']}')
                            self.statsdock.age_label.repaint()
                            self.statsdock.rotation_label.setText(f'Length of Rotation: {p['rotation']}')
                            self.statsdock.rotation_label.repaint()
                            self.statsdock.revolution_label.setText(f'Length of Revolution: {p['révolution']}')
                            self.statsdock.revolution_label.repaint()
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                self.active_planet = None
            elif event.type == pygame.MOUSEMOTION:
                if self.active_planet is not None:
                    self.planetes[self.active_planet]['position'] += pygame.Vector2(event.rel) / self.scale
