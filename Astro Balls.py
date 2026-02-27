import random
import sys
import os
import pygame
from PySide6.QtGui import QAction, Qt, QFont, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMenu, QPushButton, QVBoxLayout, QDockWidget, \
    QHBoxLayout, QWidgetAction, QCheckBox, QLabel, QDialog, QGridLayout, QFrame, QComboBox, QSpinBox, QDoubleSpinBox, \
    QScrollArea, QScrollBar, QStackedLayout, QSizePolicy, QSlider
from PySide6.QtCore import QTimer, Signal
import euclid
import math


class PyGameWidget(QWidget):
    measuring_updater_signal = Signal()
    def __init__(self, planet_id):
        super().__init__()

        self.point = []
        self.measuringtape_state = False
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

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
        self.planet_id = planet_id  # [1,2,3,1,2,3,1,2,1,2,3,1,2,3,1,1,2,3,1,2]
        self.liste_objets = self.initialiser_objets(self.planet_id)

        self.G = 100
        self.simulation = 1
        self.vitesse_simulation = 1
        facteur_ellipse = 0.5  # <1 pour une ellipse
        self.dtime = 1 / self.fps_simulation

        if self.simulation == 1:
            self.objet_central = self.liste_objets[0]
            self.objet_orbite1 = self.liste_objets[1]
            self.objet_orbite2 = self.liste_objets[2]

            self.objet_central["position"] = euclid.Vector2(0, 0)
            self.objet_orbite1["position"] = euclid.Vector2(500, 0)
            self.objet_orbite2["position"] = euclid.Vector2(550, 0)
            self.camera_target_pos = self.objet_central["position"]

            self.objet_orbite1["vitesse"] = self.vitesse_gravitationnelle(self.objet_central,
                                                                          self.objet_orbite1) * facteur_ellipse
            self.objet_orbite2["vitesse"] = self.vitesse_gravitationnelle(self.objet_orbite1, self.objet_orbite2) + \
                                            self.objet_orbite1["vitesse"]

        elif self.simulation == 2:
            self.objet_orbite1 = self.liste_objets[1]
            self.objet_orbite2 = self.liste_objets[2]

            self.objet_orbite1["position"] = euclid.Vector2(random.randint(-200, 0), random.randint(-200, 0))
            self.objet_orbite2["position"] = euclid.Vector2(random.randint(0, 200), random.randint(0, 200))

            self.camera_target_pos = self.objet_orbite1["position"]

            self.objet_orbite1["vitesse"] = self.vitesse_gravitationnelle(self.objet_orbite2,
                                                                          self.objet_orbite1) * facteur_ellipse
            self.objet_orbite2["vitesse"] = self.vitesse_gravitationnelle(self.objet_orbite1, self.objet_orbite2)

        self.f_pressed_handled = False
        self.camera_pos = euclid.Vector2(0, 0)
        self.camera_milieu_pos = euclid.Vector2(0, 0)
        self.camera_mode = "milieu"  # "free", "follow", "milieu"

        """FIN INITIALIZATION DE LA SIMULATION """

        self.timer.timeout.connect(self.game_loop)

    def speed_interactive(self, value : int):
        self.vitesse_simulation = value
        self.dtime = 1 / self.fps_simulation * self.vitesse_simulation

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
        acc_objet_orbite2 = self.force_gravitationnelle(objet_orbite2, objet_orbite1) + self.force_gravitationnelle(
            objet_orbite2, objet_central)

        list_objets = [(objet_central, acc_objet_central), (objet_orbite1, acc_objet_orbite1),
                       (objet_orbite2, acc_objet_orbite2)]
        list_objets_update = self.mouvement(list_objets)

        self.camera_milieu_pos = (self.objet_orbite1["position"] + self.objet_central["position"]) / 2
        self.display(list_objets_update)

    def simulation_2corps(self, objet_orbite1, objet_orbite2):
        acc_objet_orbite1 = self.force_gravitationnelle(objet_orbite1, objet_orbite2)
        acc_objet_orbite2 = self.force_gravitationnelle(objet_orbite2, objet_orbite1)

        list_objets = [(objet_orbite1, acc_objet_orbite1), (objet_orbite2, acc_objet_orbite2)]
        list_objets_update = self.mouvement(list_objets)

        self.camera_milieu_pos = (self.objet_orbite1["position"] + self.objet_orbite2["position"]) / 2
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

    def mouvement(self, objets):  # objet[0] = objet, objet[1] = acc_objet
        list_objets_update = []

        for objet in objets:
            objet[0]["vitesse"] += objet[1] * self.dtime
            objet[0]["position"] += objet[0]["vitesse"] * self.dtime
            list_objets_update.append(objet)

        return list_objets_update

    def pos_objet_orbite(self, pos):
        relative = pos - self.camera_pos

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
        #pygame.draw.rect(self.playscreen, border_color, pygame.Rect(0, 0, self.x, self.y), border_thickness)

        pygame.display.update()

    @staticmethod
    def terre_objet():
        terre = {
            "nom objet": "terre",
            "masse": 10,
            "rayon": 10,
            "couleur": (0, 0, 255),
            "vitesse": euclid.Vector2(0, 0)
        }
        return terre

    @staticmethod
    def soleil_objet():
        soleil = {
            "nom objet": "soleil",
            "masse": 500,
            "rayon": 50,
            "couleur": (255, 222, 0),
            "vitesse": euclid.Vector2(0, 0)
        }
        return soleil

    @staticmethod
    def lune_objet():
        lune = {
            "nom objet": "lune",
            "masse": 1,
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
        elif self.camera_mode == "follow":
            self.camera_pos = self.camera_target_pos + euclid.Vector2(1, 1)
        elif self.camera_mode == "milieu":
            self.camera_pos = self.camera_milieu_pos

        self.update_size()
        if self.simulation == 1:
            self.simulation_objet_central_3corps(self.objet_central, self.objet_orbite1, self.objet_orbite2)

            if self.measuringtape_state:
                self.measuringtape()

        elif self.simulation == 2:
            self.simulation_2corps(self.objet_orbite1, self.objet_orbite2)

        elif self.simulation == 3:
            pass
        elif self.simulation == 4:
            pass
        else:
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

        widget.setFixedHeight(100)

        widget.setLayout(layout)
        self.setWidget(widget)


class StatsDock(QDockWidget):
    def __init__(self):
        super().__init__("Statistics")

        widget = QWidget()
        layout = QVBoxLayout()

        upper_panel = QFrame()
        upper_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        upper_panel_layout = QGridLayout()
        upper_panel.setLayout(upper_panel_layout)
        upper_panel_layout.setSpacing(10)
        layout.addWidget(upper_panel)
        upper_panel.setFixedSize(200, 450)

        body_label = QLabel()
        body_label.setText("[SELECTED BODY'S NAME]")
        body_label_txt = QFont()
        body_label_txt.setPointSize(10)
        body_label_txt.setBold(True)
        body_label_txt.setItalic(True)
        body_label.setFont(body_label_txt)
        upper_panel_layout.addWidget(body_label, 0, 0, 1, 3)

        body_type = QLabel()
        body_type.setText(f"Type: [body's type]")
        upper_panel_layout.addWidget(body_type, 1, 0, 1, 2)

        surface_label = QLabel()
        surface_label.setText(f"Surface Composition")
        surface_label.setWordWrap(True)
        upper_panel_layout.addWidget(surface_label, 2, 0, 1, 2)

        age_label = QLabel()
        age_label.setText(f"Age: [body's age]")
        upper_panel_layout.addWidget(age_label, 3, 0, 1, 2)

        rotation_label = QLabel()
        rotation_label.setText(f"Length of Rotation: [body's rotation time]")
        rotation_label.setWordWrap(True)
        upper_panel_layout.addWidget(rotation_label, 4, 0, 1, 2)

        revolution_label = QLabel()
        revolution_label.setText(f"Length of Revolution: [body's revolution time]")
        revolution_label.setWordWrap(True)
        upper_panel_layout.addWidget(revolution_label, 5, 0, 1, 2)

        mid_panel = QFrame()
        mid_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        mid_panel_layout = QGridLayout()
        mid_panel.setLayout(mid_panel_layout)
        mid_panel_layout.setSpacing(10)
        layout.addWidget(mid_panel)
        mid_panel.setFixedSize(200, 450)

        config_label = QLabel()
        config_label.setText("CONFIGURATION")
        config_label_txt = QFont()
        config_label_txt.setPointSize(10)
        config_label_txt.setBold(True)
        config_label_txt.setItalic(True)
        config_label.setFont(config_label_txt)
        mid_panel_layout.addWidget(config_label, 0, 0, 1, 3)

        mass_label = QLabel('Mass')
        mid_panel_layout.addWidget(mass_label, 1, 0)
        mass_spin = QDoubleSpinBox()
        mass_spin.setRange(0.0, 1000.0)
        mass_spin.lineEdit().setMaximumWidth(50)
        mid_panel_layout.addWidget(mass_spin, 2, 0,)
        mass_unit = QComboBox()
        pg, ng, mcg, mg, g, kg, t, mt, gt = 'pg', 'ng', 'µg', 'mg', 'g', 'kg', 't', 'Mt', 'Gt'
        unit_lst = [gt, mt, t, kg, g, mg, mcg, ng, pg]
        mass_unit.addItems(unit_lst)
        mass_unit.view().setFixedWidth(40)
        mid_panel_layout.addWidget(mass_unit, 2, 1)

        size_label = QLabel('Radius')
        mid_panel_layout.addWidget(size_label, 4, 0)
        mass_spin = QDoubleSpinBox()
        mass_spin.setRange(0.0, 1000.0)
        mass_spin.lineEdit().setMaximumWidth(50)
        mid_panel_layout.addWidget(mass_spin, 5, 0,)
        size_unit = QComboBox()
        km, m, cm, mm, mcm, nm = 'km', 'm', 'cm', ' mm', 'µm', 'nm'
        size_lst = [km, m, cm, mm, mcm, nm]
        size_unit.addItems(size_lst)
        size_unit.view().setFixedWidth(40)
        mid_panel_layout.addWidget(size_unit, 5, 1)

        density_label = QLabel('Density')
        mid_panel_layout.addWidget(density_label, 6, 0)
        density_spin = QDoubleSpinBox()
        density_spin.lineEdit().setMaximumWidth(50)
        mid_panel_layout.addWidget(density_spin, 7, 0)
        density_unit = QComboBox()
        kgm, gcm = 'kg/m³', 'g/cm³'
        density_lst = [kgm, gcm]
        density_unit.addItems(density_lst)
        size_unit.view().setFixedWidth(40)
        mid_panel_layout.addWidget(density_unit, 7, 1)

        temp_label = QLabel('Temperature')
        mid_panel_layout.addWidget(temp_label, 8, 0)
        temp_spin = QDoubleSpinBox()
        temp_spin.lineEdit().setMaximumWidth(50)
        mid_panel_layout.addWidget(temp_spin, 9, 0)
        temp_unit = QComboBox()
        k, c, f = 'K', '℃', '℉'
        temp_lst = [k, c, f]
        temp_unit.addItems(temp_lst)
        temp_unit.view().setFixedWidth(40)
        mid_panel_layout.addWidget(temp_unit, 9, 1)

        momentum_lst = ['km/s', 'm/s', 'cm/s', 'km/h', 'm/h', 'cm/h', 'ml/s', 'yd/s', 'ft/s', 'inch/s', 'ml/h', 'yd/h', 'ft/h', 'inch/h']

        rotation_label = QLabel('Rotational Momentum')
        mid_panel_layout.addWidget(rotation_label, 10, 0, 1, 2)
        rotation_spin = QDoubleSpinBox()
        rotation_spin.lineEdit().setMaximumWidth(50)
        mid_panel_layout.addWidget(rotation_spin, 11, 0)
        rmomentum_unit = QComboBox()
        rmomentum_unit.addItems(momentum_lst)
        rmomentum_unit.view().setFixedWidth(65)
        mid_panel_layout.addWidget(rmomentum_unit, 11, 1)

        orbital_label = QLabel('Orbital Momentum')
        mid_panel_layout.addWidget(orbital_label, 12, 0, 1, 2)
        orbital_spin = QDoubleSpinBox()
        orbital_spin.lineEdit().setMaximumWidth(50)
        mid_panel_layout.addWidget(orbital_spin, 13, 0)
        omomentum_unit = QComboBox()
        omomentum_unit.addItems(momentum_lst)
        omomentum_unit.view().setFixedWidth(65)
        mid_panel_layout.addWidget(omomentum_unit, 13, 1)

        gravity_label = QLabel('Surface Gravity')
        mid_panel_layout.addWidget(gravity_label, 14, 0, 1, 2)
        gravity_spin = QDoubleSpinBox()
        gravity_spin.lineEdit().setMaximumWidth(50)
        mid_panel_layout.addWidget(gravity_spin, 15, 0)
        gravity_lst = [i+'²' for i in momentum_lst]
        gravity_unit = QComboBox()
        gravity_unit.addItems(gravity_lst)
        gravity_unit.view().setFixedWidth(70)
        mid_panel_layout.addWidget(gravity_unit, 15, 1)

        bottom_panel = QFrame()
        bottom_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        bottom_panel_layout = QGridLayout()
        bottom_panel.setLayout(bottom_panel_layout)
        bottom_panel_layout.setSpacing(10)
        layout.addWidget(bottom_panel)
        bottom_panel.setFixedSize(200, 450)

        widget.setLayout(layout)
        scroller = QScrollArea()
        scroller.setFrameShape(QFrame.NoFrame)
        scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroller.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroller.setWidgetResizable(True)
        scroller.setWidget(widget)
        scroller.setFixedWidth(217)
        self.setWidget(scroller)


class MainWindowFrame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer_state = False
        self.timescope_label = None
        self.setWindowTitle('Astro Balls')
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.game_widget = PyGameWidget([1, 2, 3])
        self.firstdotcoo = None
        self.seconddotcoo = None
        self.measuring_window = None
        self.distance = None
        self.angle = None
        self.timer_scope = None
        self.game_widget.measuring_updater_signal.connect(self.update_measuringtape)

        layout = QVBoxLayout(central_widget)
        self.game_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.game_widget)
        self.resize(1200, 600)

        menu = self.menuBar()
        app_menu = QMenu('&Application')
        savenew_action = QAction('&New Save', parent=self)
        savenew_action.setIcon(QIcon('images/menubar symbol/plus.png'))
        savenew_action.triggered.connect(self.newsavefile)
        savenew_action.setShortcut('Ctrl+N')
        app_menu.addAction(savenew_action)
        save_action = QAction('&Save', parent=self)
        save_action.setIcon(QIcon('images/menubar symbol/diskette.png'))
        save_action.triggered.connect(self.savefile)
        save_action.setShortcut('Ctrl+S')
        app_menu.addAction(save_action)
        open_action = QAction('&Open', parent=self)
        open_action.setIcon(QIcon('images/menubar symbol/open-folder.png'))
        open_action.triggered.connect(self.openfile)
        open_action.setShortcut('Ctrl+O')
        app_menu.addAction(open_action)
        app_menu.addSeparator()
        settings_action = QAction('&Settings', parent=self)
        settings_action.setIcon(QIcon('images/menubar symbol/cog.png'))
        settings_action.triggered.connect(self.settings)
        settings_action.setShortcut('Alt+S')
        app_menu.addAction(settings_action)
        app_menu.addSeparator()
        quit_action = QAction('&Quit', parent=self)
        quit_action.setIcon(QIcon('images/menubar symbol/cross.png'))
        quit_action.triggered.connect(self.closeapp)
        quit_action.setShortcut('Alt+F4')
        app_menu.addAction(quit_action)
        menu.addMenu(app_menu)

        view_menu = QMenu('&View')
        orbits_action = QWidgetAction(view_menu)
        orbits_view = self.customcheckbox(func_name='Orbits', method=self.showorbits)[0]
        orbits_action.setDefaultWidget(orbits_view)
        view_menu.addAction(orbits_action)
        orbitsinfo_action = QWidgetAction(view_menu)
        orbitsinfo_view = self.customcheckbox(func_name='Orbits Info', method=self.showorbitinfo)[0]
        orbitsinfo_action.setDefaultWidget(orbitsinfo_view)
        view_menu.addAction(orbitsinfo_action)
        scale_action = QWidgetAction(view_menu)
        scale_view = self.customcheckbox(func_name='Scale Slider', method=self.scaleslider)[0]
        scale_action.setDefaultWidget(scale_view)
        view_menu.addAction(scale_action)
        menu.addMenu(view_menu)
        self.timer_action = QWidgetAction(view_menu)
        if self.timer_state is False:
            print('false')
            self.timer_view, self.timer_state = self.customcheckbox(func_name='Time', method=self.timerscope)
            self.timer_action.setDefaultWidget(self.timer_view)
        view_menu.addAction(self.timer_action)
        menu.addMenu(view_menu)
        vector_menu = view_menu.addMenu('Vectors')
        orbits_vector = QWidgetAction(vector_menu)
        orbits_vector_view = self.customcheckbox(func_name='Orbital Vectors', method=self.showorbitvector)[0]
        orbits_vector.setDefaultWidget(orbits_vector_view)
        vector_menu.addAction(orbits_vector)
        force_vector = QWidgetAction(vector_menu)
        force_vector_view = self.customcheckbox(func_name='Force Vectors', method=self.showforcevector)[0]
        force_vector.setDefaultWidget(force_vector_view)
        vector_menu.addAction(force_vector)
        rotational_vector = QWidgetAction(vector_menu)
        rotational_vector_view = self.customcheckbox(func_name='Rotational Vectors', method=self.showrotationalvector)[0]
        rotational_vector.setDefaultWidget(rotational_vector_view)
        vector_menu.addAction(rotational_vector)

        tool_menu = QMenu('&Tools')
        menu.addMenu(tool_menu)
        mt = QAction('&Mesuring Tape', parent=self)
        mt.setIcon(QIcon('images/menubar symbol/ruler.png'))
        mt.triggered.connect(self.measuringtape)
        tool_menu.addAction(mt)

        help_menu = QMenu('&Help')
        keybinds_action = QAction('&Keybinds', parent=self)
        keybinds_action.setIcon(QIcon('images/menubar symbol/space.png'))
        keybinds_action.triggered.connect(self.keybinds)
        keybinds_action.setShortcut('Alt+K')
        help_menu.addAction(keybinds_action)
        info_action = QAction('&Mímisbrunnr', parent=self)
        info_action.setIcon(QIcon('images/menubar symbol/book.png'))
        info_action.triggered.connect(self.mimir)
        info_action.setShortcut('Alt+M')
        help_menu.addAction(info_action)
        guider_action = QAction('&Guide', parent=self)
        guider_action.setIcon(QIcon('images/menubar symbol/up-arrow.png'))
        guider_action.triggered.connect(self.guide)
        guider_action.setShortcut('Alt+G')
        help_menu.addAction(guider_action)
        help_menu.addSeparator()
        htui_action = QAction('&About Astro Balls', parent=self)
        htui_action.setIcon(QIcon('images/menubar symbol/question-mark.png'))
        htui_action.triggered.connect(self.htui)
        htui_action.setShortcut('Alt+H')
        help_menu.addAction(htui_action)
        menu.addMenu(help_menu)

        self.dragndrop = DragNDrop()
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dragndrop)
        self.statsdock = StatsDock()
        self.addDockWidget(Qt.RightDockWidgetArea, self.statsdock)

    def measuringtape(self):
        self.game_widget.toggle_measuringtape(True)

        if self.measuring_window is None:
            self.measuring_window = QDialog(parent=self)
            self.measuring_window.setWindowTitle('Measuring Tool')
            self.measuring_window.resize(180, 70)
            measuring_window_layout = QGridLayout(self.measuring_window)
            measuring_window_layout.setSpacing(10)

            self.firstdotcoo = QLabel(f'Dot #1: ')
            self.seconddotcoo = QLabel(f'Dot #2: ')
            measuring_window_layout.addWidget(self.firstdotcoo, 0, 0)
            measuring_window_layout.addWidget(self.seconddotcoo, 0, 1)
            line_sep = QFrame()
            line_sep.setFrameStyle(QFrame.Shape.HLine)
            line_sep.setStyleSheet('background-color: #444444')
            line_sep.setFixedHeight(1)
            measuring_window_layout.addWidget(line_sep, 1, 0, 1, 2)
            self.distance = QLabel()
            self.distance.setText(f' Distance:\n0U')
            distance_txt_font = QFont()
            distance_txt_font.setBold(True)
            self.distance.setFont(distance_txt_font)
            measuring_window_layout.addWidget(self.distance, 2, 0)
            self.angle = QLabel()
            self.angle.setText(f' Angle:\n0°')
            angle_txt_font = QFont()
            angle_txt_font.setBold(True)
            self.angle.setFont(angle_txt_font)
            measuring_window_layout.addWidget(self.angle, 2, 1)

            cancelbutton = QPushButton('Cancel')
            cancelbutton.clicked.connect(self.game_widget.toggle_measuringtape)
            cancelbutton.clicked.connect(self.measuring_window.close)
            measuring_window_layout.addWidget(cancelbutton, 3, 0, 1, 2)

            self.measuring_window.finished.connect(lambda: setattr(self, 'measuring_window', None))
            self.measuring_window.finished.connect(lambda: self.game_widget.toggle_measuringtape(False))
            self.measuring_window.show()

    def update_measuringtape(self):
        if self.measuring_window is None:
            return
        if len(self.game_widget.point) >= 1:
            self.firstdotcoo.setText(f"Dot #1:\n{self.game_widget.point[0]}")
        else:
            self.firstdotcoo.setText("Dot #1:")
        if len(self.game_widget.point) == 2:
            self.seconddotcoo.setText(f"Dot #2:\n{self.game_widget.point[1]}")
            self.distance.setText(f"Distance:\n{self.game_widget.pythagoras(self.game_widget.point)[0]}U")
            self.angle.setText(f"Angle:\n{self.game_widget.pythagoras(self.game_widget.point)[1]}°")
        else:
            self.seconddotcoo.setText("Dot #2:")

    def timerscope(self):
        if getattr(self, 'timer_scope', None) is not None:
            self.timer_scope.setVisible(self.timer_state.isChecked())
            return
        self.timer_scope = QDockWidget(parent=self)
        timerscope_container = QWidget()
        timerscope_widget = QGridLayout(timerscope_container)
        self.timer_scope.setWidget(timerscope_container)
        self.timer_scope.setWindowTitle('Timer')

        self.time_slider = QSlider(Qt.Orientation.Horizontal, parent=timerscope_container)
        self.time_slider.setRange(0, 100)
        self.time_slider.setValue(1)
        self.time_slider.setTickInterval(5)
        self.time_slider.setSingleStep(5)
        self.time_slider.setTickPosition(QSlider.TicksAbove)
        timerscope_widget.addWidget(self.time_slider, 0, 0, 1, 2)
        self.time_slider.valueChanged.connect(self.update_timerscope)
        self.time_slider.valueChanged.connect(self.game_widget.speed_interactive)
        self.timescope_label = QLabel('', timerscope_container)

        backward_button = QPushButton('Backward')
        backward_button.clicked.connect(self.backward_timescope)
        timerscope_widget.addWidget(backward_button, 1, 0)

        forward_button = QPushButton('Forward')
        forward_button.clicked.connect(self.forward_timescope)
        timerscope_widget.addWidget(forward_button, 1, 1)

        self.timer_scope.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.timer_scope.setFixedHeight(120)
        self.splitDockWidget(self.statsdock, self.timer_scope, Qt.Vertical)

        self.timer_scope.visibilityChanged.connect(self.timerscope_close)
        self.timer_scope.show()

    def update_timerscope(self):
        self.timescope_label.setText(f'X{self.time_slider.value()}')
        self.timescope_label.adjustSize()
        ratio = (self.time_slider.value() - self.time_slider.minimum()) / (
                    self.time_slider.maximum() - self.time_slider.minimum())
        x_pos = 16 / 2 + ratio * (self.time_slider.width() - 16)
        x_pos_parent = self.time_slider.x() + x_pos - (self.timescope_label.width() // 2)
        y_pos = self.time_slider.y() - 15
        self.timescope_label.move(int(x_pos_parent), int(y_pos))

    def timerscope_close(self, active):
        if hasattr(self, 'timer_state'):
            self.timer_state.blockSignals(True)
            self.timer_state.setChecked(active)
            self.timer_state.blockSignals(False)

    def backward_timescope(self):
        self.time_slider.setValue(self.time_slider.value() - 2)

    def forward_timescope(self):
        self.time_slider.setValue(self.time_slider.value() + 2)

    @staticmethod
    def customcheckbox(func_name, method):
        view_widget = QWidget()
        view_layout = QHBoxLayout(view_widget)
        checkbox = QCheckBox(func_name)
        checkbox.toggled.connect(method)
        view_layout.addWidget(checkbox)
        view_widget.setLayout(view_layout)
        return view_widget, checkbox

    def settings(self):
        settings_window = QDialog(parent=self)
        settings_window.resize(650, 500)
        settings_window.setWindowTitle('Settings')
        settings_layout = QGridLayout()
        settings_window.setLayout(settings_layout)

        side_panel = QFrame()
        side_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        side_panel_layout = QVBoxLayout()
        side_panel.setLayout(side_panel_layout)
        side_panel_layout.setSpacing(10)
        settings_layout.addWidget(side_panel, 0, 0, 1, 1)

        graphics = QPushButton('Graphics')
        graphics.setStyleSheet('text-align: left; padding-left: 2px')
        graphics.clicked.connect(self.graphicstab)
        side_panel_layout.addWidget(graphics)
        audio = QPushButton('Audio')
        audio.setStyleSheet('text-align: left; padding-left: 2px')
        audio.clicked.connect(self.audiotab)
        side_panel_layout.addWidget(audio)
        aspectratio = QPushButton('Window Aspect Ratio')
        aspectratio.setStyleSheet('text-align: left; padding-left: 2px')
        aspectratio.clicked.connect(self.aspectratiotab)
        side_panel_layout.addWidget(aspectratio)
        keybinds = QPushButton('Keybinds')
        keybinds.setStyleSheet('text-align: left; padding-left: 2px')
        keybinds.clicked.connect(self.keybindstab)
        side_panel_layout.addWidget(keybinds)

        main_panel = QFrame()
        main_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        self.main_panel_layout = QStackedLayout()
        main_panel.setLayout(self.main_panel_layout)
        settings_layout.addWidget(main_panel, 0, 1, 4, 4)

        graphics_settings_panel = QFrame()
        graphics_settings_panel_layout = QGridLayout()
        graphics_settings_panel.setLayout(graphics_settings_panel_layout)
        self.main_panel_layout.addWidget(graphics_settings_panel)
        graphics_settings_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        graphics_settings_panel_label = QLabel()
        graphics_settings_panel_label.setText("GRAPHICS")
        graphics_settings_panel_label_font = QFont()
        graphics_settings_panel_label_font.setPointSize(20)
        graphics_settings_panel_label_font.setBold(True)
        graphics_settings_panel_label_font.setItalic(True)
        graphics_settings_panel_label.setFont(graphics_settings_panel_label_font)
        graphics_settings_panel_layout.addWidget(graphics_settings_panel_label, 0, 0)

        audio_settings_panel = QFrame()
        audio_settings_panel_layout = QGridLayout()
        audio_settings_panel.setLayout(audio_settings_panel_layout)
        self.main_panel_layout.addWidget(audio_settings_panel)
        audio_settings_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        audio_settings_panel_label = QLabel()
        audio_settings_panel_label.setText("AUDIO")
        audio_settings_panel_label_font = QFont()
        audio_settings_panel_label_font.setPointSize(20)
        audio_settings_panel_label_font.setBold(True)
        audio_settings_panel_label_font.setItalic(True)
        audio_settings_panel_label.setFont(audio_settings_panel_label_font)
        audio_settings_panel_layout.addWidget(audio_settings_panel_label, 0, 0)

        aspectratio_settings_panel = QFrame()
        aspectratio_settings_panel_layout = QGridLayout()
        aspectratio_settings_panel.setLayout(aspectratio_settings_panel_layout)
        self.main_panel_layout.addWidget(aspectratio_settings_panel)
        aspectratio_settings_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        aspectratio_settings_panel_label = QLabel()
        aspectratio_settings_panel_label.setText("ASPECT RATIO")
        aspectratio_settings_panel_label_font = QFont()
        aspectratio_settings_panel_label_font.setPointSize(20)
        aspectratio_settings_panel_label_font.setBold(True)
        aspectratio_settings_panel_label_font.setItalic(True)
        aspectratio_settings_panel_label.setFont(aspectratio_settings_panel_label_font)
        aspectratio_settings_panel_layout.addWidget(aspectratio_settings_panel_label, 0, 0)

        keybinds_settings_panel = QFrame()
        keybinds_settings_panel_layout = QGridLayout()
        keybinds_settings_panel.setLayout(keybinds_settings_panel_layout)
        self.main_panel_layout.addWidget(keybinds_settings_panel)
        keybinds_settings_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        keybinds_settings_panel_label = QLabel()
        keybinds_settings_panel_label.setText("KEYBINDS")
        keybinds_settings_panel_label_font = QFont()
        keybinds_settings_panel_label_font.setPointSize(20)
        keybinds_settings_panel_label_font.setBold(True)
        keybinds_settings_panel_label_font.setItalic(True)
        keybinds_settings_panel_label.setFont(keybinds_settings_panel_label_font)
        keybinds_settings_panel_layout.addWidget(keybinds_settings_panel_label, 0, 0)

        apply_button = QPushButton('Apply')
        apply_button.clicked.connect(self.applysetting)
        settings_layout.addWidget(apply_button, 4, 3)

        apply_button = QPushButton('Close')
        apply_button.clicked.connect(settings_window.close)
        settings_layout.addWidget(apply_button, 4, 4)

        settings_window.exec()

    def graphicstab(self):
        self.main_panel_layout.setCurrentIndex(0)

    def audiotab(self):
        self.main_panel_layout.setCurrentIndex(1)

    def aspectratiotab(self):
        self.main_panel_layout.setCurrentIndex(2)

    def keybindstab(self):
        self.main_panel_layout.setCurrentIndex(3)

    def mimir(self):
        info_window = QDialog(parent=self)
        info_window.resize(650, 500)
        info_window.setWindowTitle('Mímisbrunnr')
        info_layout = QGridLayout()
        info_window.setLayout(info_layout)

        side_panel = QFrame()
        side_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        side_panel_layout = QVBoxLayout()
        side_panel.setLayout(side_panel_layout)
        side_panel_layout.setSpacing(20)
        info_layout.addWidget(side_panel, 0, 0, 1, 1)

        newton1 = QPushButton("Newton's First Law")
        newton1.setStyleSheet('text-align: left; padding-left: 2px')
        newton1.clicked.connect(self.newton1)
        side_panel_layout.addWidget(newton1)
        newton2 = QPushButton("Newton's Second Law")
        newton2.setStyleSheet('text-align: left; padding-left: 2px')
        newton2.clicked.connect(self.newton2)
        side_panel_layout.addWidget(newton2)
        newton3 = QPushButton("Newton's Third Law")
        newton3.setStyleSheet('text-align: left; padding-left: 2px')
        newton3.clicked.connect(self.newton3)
        side_panel_layout.addWidget(newton3)
        kflopm = QPushButton("Kepler's First Law of\nPlanetary Motion")
        kflopm.setStyleSheet('QPushButton {text-align: left; padding-left: 2px; white-space: normal}')
        kflopm.clicked.connect(self.kflopm)
        side_panel_layout.addWidget(kflopm)
        metric = QPushButton("Metric System")
        metric.setStyleSheet('QPushButton {text-align: left; padding-left: 2px; white-space: normal}')
        metric.clicked.connect(self.metric)
        side_panel_layout.addWidget(metric)

        imperial = QPushButton("Imperial System\n(US and UK)")
        imperial.setStyleSheet('QPushButton {text-align: left; padding-left: 2px; white-space: normal}')
        imperial.clicked.connect(self.metric)
        side_panel_layout.addWidget(imperial)

        main_panel = QFrame()
        main_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        main_panel_layout = QGridLayout()
        main_panel.setLayout(main_panel_layout)
        info_layout.addWidget(main_panel, 0, 1, 4, 4)

        apply_button = QPushButton('Close')
        apply_button.clicked.connect(info_window.close)
        info_layout.addWidget(apply_button, 4, 4)

        info_window.exec()

    def htui(self):
        about_window = QDialog(parent=self)
        about_window.resize(500, 400)
        about_window.setWindowTitle('About Astro Balls')
        about_layout = QGridLayout()
        about_window.setLayout(about_layout)

        about_window.exec()

    def guide(self):
        pass

    def savefile(self):
        pass

    def openfile(self):
        pass

    def newsavefile(self):
        pass

    def closeapp(self):
        pygame.quit()
        self.close()
        sys.exit()

    def applysetting(self):
        pass

    def showorbits(self):
        pass

    def showorbitinfo(self):
        pass

    def keybinds(self):
        self.settings()

    def scaleslider(self):
        pass

    def newton1(self):
        pass

    def newton2(self):
        pass

    def newton3(self):
        pass

    def kflopm(self):
        pass

    def showorbitvector(self):
        pass

    def showforcevector(self):
        pass

    def showrotationalvector(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindowFrame()
    mw.show()
    app.exec()
