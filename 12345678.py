class PyGameWidget(QWidget):
    measuring_updater_signal = Signal()

    def __init__(self, statsdock):
        super().__init__()
        self.statsdock = statsdock

        self.y = None
        self.x = None
        self.j = None
        self.setAcceptDrops(True)
        self.planets = []
        self.active_planet = None
        self.pygame_windowhandler()

    def pygame_windowhandler(self):
        os.environ["SDL_WINDOWID"] = str(int(self.winId()))
        os.environ["SDL_VIDEODRIVER"] = "windows"
        pygame.init()
        self.playscreen = pygame.display.set_mode(size=(0, 0))
        self.x, self.y = self.playscreen.get_size()
        self.timer = pygame.time.Clock()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        name = event.mimeData().text()
        pos = event.pos()

        world_x = (pos.x() - self.x / 2 + self.camera_pos.x) / self.scale
        world_y = (pos.y() - self.y / 2 + self.camera_pos.y) / self.scale

        self.spawn_planets(name, world_x, world_y, 0, 0)

    def spawn_planets(self, name, x, y, velx, vely):
        presets = {
            "Mercury": {'name': 'Mercury', 'type': 'Planet', 'sufcomp': 'Metallic (70%)',
                        'age': '4.503 billion Earth-Years', 'rotation': '1,408h', 'revolution': '88 days',
                        "mass": (3.285 * 10 ** 23) / (1 * 10 ** 21), "radius": 9, "color": (245, 245, 220)},
            "Venus": {'name': 'Venus', 'type': 'Planet', 'sufcomp': 'Basalt', 'age': '4.503 billion Earth-Years',
                      'rotation': '5,832h', 'revolution': '225 days', "mass": (4.867 * 10 ** 24) / (1 * 10 ** 21),
                      "radius": 11, "color": (255, 215, 0)},
            "Earth": {'name': 'Earth', 'type': 'Planet', 'sufcomp': 'Granite', 'age': '4.543 billion Earth-Years',
                      'rotation': '24h', 'revolution': '365 days', "mass": (5.972 * 10 ** 24) / (1 * 10 ** 21),
                      "radius": 12, "color": (0, 100, 255)},
            "Mars": {'name': 'Mars', 'type': 'Planet', 'sufcomp': 'Oxidized Iron', 'age': '4.603 billion Earth-Years',
                     'rotation': '25h', 'revolution': '687 days', "mass": (6.416993 * 10 ** 23) / (1 * 10 ** 21),
                     "radius": 10, "color": (255, 100, 100)},
            "Jupiter": {'name': 'Jupiter', 'type': 'Gas Giant', 'sufcomp': 'Hydrogen (90%)',
                        'age': '4.603 billion Earth-Years', 'rotation': '10h', 'revolution': '4,333 days',
                        "mass": (1.899 * 10 ** 27) / (1 * 10 ** 21), "radius": 50, "color": (200, 150, 50)},
            "Saturn": {'name': 'Saturn', 'type': 'Gas Giant', 'sufcomp': 'Hydrogen (94%)',
                       'age': '4.503 billion Earth-Years', 'rotation': '11h', 'revolution': '10,757 days',
                       "mass": (5.683 * 10 ** 26) / (1 * 10 ** 21), "radius": 45, "color": (195, 146, 79)},
            "Uranus": {'name': 'Uranus', 'type': 'Gas Giant', 'sufcomp': 'Hydrogen (90%)',
                       'age': '4.503 billion Earth-Years', 'rotation': '17h', 'revolution': '30,687 days',
                       "mass": (6.681 * 10 ** 25) / (1 * 10 ** 21), "radius": 20, "color": (172, 229, 238)},
            "Neptune": {'name': 'Neptune', 'type': 'Gas Giant', 'sufcomp': 'Hydrogen (90%)',
                        'age': '4.503 billion Earth-Years', 'rotation': '16h', 'revolution': '60,197 days',
                        "mass": (1.024 * 10 ** 26) / (1 * 10 ** 21), "radius": 21, "color": (124, 183, 187)},
            "Sun": {'name': 'Sun', 'type': 'Star', 'sufcomp': 'Hydrogen (74%)', 'age': '4.603 billion Earth-Years',
                    'rotation': '600h', 'revolution': 'None', "mass": (1.989 * 10 ** 30) / (1 * 10 ** 21),
                    "radius": 200, "color": (255, 0, 0)},
            "Moon": {'name': 'Moon', 'type': 'Natural Satellite', 'sufcomp': 'Lunar Regolith',
                     'age': '4.46 billion Earth-Years', 'rotation': '655h', 'revolution': '27 days',
                     "mass": (7.347 * 10 ** 22) / (1 * 10 ** 21), "radius": 4, "color": (200, 200, 200)},
            "Europa": {'name': 'Europa', 'type': 'Natural Satellite', 'sufcomp': 'Ice',
                       'age': '4.5 billion Earth-Years', 'rotation': '85.2h', 'revolution': '3.55 days',
                       "mass": (4.799 * 10 ** 22) / (1 * 10 ** 21), "radius": 2, "color": (191, 207, 217)},
            "Io": {'name': 'Io', 'type': 'Natural Satellite', 'sufcomp': 'Sulfur Dioxide',
                   'age': '4.57 billion Earth-Years', 'rotation': '42.5h', 'revolution': '42h',
                   "mass": (8.931 * 10 ** 22) / (1 * 10 ** 21), "radius": 3, "color": (200, 180, 100)}
        }

        data = presets.get(name, presets["Mercury"])

        planet = {"Name": name, "pos": pygame.Vector2(x, y), "vel": pygame.Vector2(velx, vely), "mass": data["mass"],
                  "radius": data["radius"], "color": data["color"], 'type': data['type'], 'sufcomp': data['sufcomp'],
                  'age': data['age'], 'rotation': data['rotation'], 'revolution': data['revolution']}

        self.planets.append(planet)

    def update_positions(self):
        for planet in self.planets:
            planet["pos"] += planet["vel"] * self.dtime

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
                if event.button == 1:
                    m_pos = pygame.Vector2(event.pos)
                    for n, p in enumerate(self.planets):
                        sx, sy = self.pos_objet_orbite(p['pos'])
                        if m_pos.distance_to((sx, sy)) <= p['radius']:
                            self.active_planet = n
                            self.statsdock.body_label.setText(f'{p['Name']}')
                            self.statsdock.body_label.repaint()
                            self.statsdock.body_type.setText(f'Type: {p['type']}')
                            self.statsdock.body_type.repaint()
                            self.statsdock.surface_label.setText(f'Surface Composition: {p['sufcomp']}')
                            self.statsdock.body_type.repaint()
                            self.statsdock.age_label.setText(f'Age: {p['age']}')
                            self.statsdock.age_label.repaint()
                            self.statsdock.rotation_label.setText(f'Length of Rotation: {p['rotation']}')
                            self.statsdock.rotation_label.repaint()
                            self.statsdock.revolution_label.setText(f'Length of Revolution: {p['revolution']}')
                            self.statsdock.revolution_label.repaint()
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

