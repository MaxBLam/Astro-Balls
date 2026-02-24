import sys
import os
import pygame
from PySide6.QtGui import QAction, Qt, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMenu, QPushButton, QVBoxLayout, QDockWidget, \
    QHBoxLayout, QWidgetAction, QCheckBox, QLabel, QDialog, QGridLayout, QFrame, QComboBox, QSpinBox, QDoubleSpinBox, \
    QScrollArea, QScrollBar
from PySide6.QtCore import QTimer
import euclid
import math


class Objets:

    @staticmethod
    def terre():
        terre = {
            "masse" : 10,
            "rayon" : 10,
            "couleur" : (0,0,255),
            "position" : euclid.Vector2(800, 100),
            "vitesse" : euclid.Vector2(0,0)
        }
        return terre

    @staticmethod
    def lune():
        lune = {
            "masse" : 1,
            "rayon" : 2,
            "couleur" : (200,200,200),
            "position" : euclid.Vector2(815, 85),
            "vitesse" : euclid.Vector2(0,0)
        }
        return lune

    @staticmethod
    def soleil():
        soleil = {
            "masse" : 500,
            "rayon" : 50,
            "couleur" : (255,222,0),
            "position" : euclid.Vector2(600, 300),
            "vitesse" : euclid.Vector2(0,0)
            }
        return soleil


class Display:
    def __init__(self, position, couleur, rayon, vitesse=euclid.Vector2(0,0)):
        self.position = position
        self.vitesse = vitesse
        self.couleur = couleur
        self.rayon = rayon

    def mouvement(self, acceleration, dtime):
        self.vitesse += acceleration * dtime
        self.position += self.vitesse * dtime

    def display(self, surface):
        rx, ry = int(self.position.x), int(self.position.y)
        pygame.draw.circle(surface, self.couleur, (rx,ry), self.rayon)


class PyGameWidget(QWidget):
    def __init__(self):
        super().__init__()

        os.environ['SDL_WINDOWID'] = str(int(self.winId()))
        os.environ['SDL_VIDEODRIVER'] = 'windows'
        pygame.init()
        self.setMinimumSize(1200, 600)
        self.playscreen = pygame.display.set_mode((1200, 600))
        self.clock = pygame.time.Clock()

        self.G = 1000
        self.vitesse_simulation = 1
        self.terre = Objets.terre()
        self.soleil = Objets.soleil()
        self.lune = Objets.lune()

        self.terre["vitesse"] = self.vitesse_gravitationnelle(self.soleil, self.terre)
        self.lune["vitesse"] = self.vitesse_gravitationnelle(self.terre, self.lune) + self.terre["vitesse"]
        self.display_terre = Display(self.terre['position'], self.terre['couleur'], self.terre['rayon'], self.terre['vitesse'])
        self.display_lune = Display(self.lune['position'], self.lune['couleur'], self.lune['rayon'], self.lune['vitesse'])
        self.display_sun = Display(self.soleil['position'], self.soleil['couleur'], self.soleil['rayon'], self.soleil['vitesse'])

        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(16)

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

    def game_loop(self):
        dtime = (1/60)*self.vitesse_simulation
        fps_limit = 120
        acc_terre = self.force_gravitationnelle(self.terre, self.soleil)
        acc_lune = (self.force_gravitationnelle(self.lune, self.terre)+self.force_gravitationnelle(self.lune, self.soleil))

        self.display_terre.mouvement(acc_terre, dtime)
        self.display_lune.mouvement(acc_lune, dtime)
        self.terre['position'] = self.display_terre.position
        self.lune['position'] = self.display_lune.position
        self.terre['vitesse'] = self.display_terre.vitesse
        self.lune['vitesse'] = self.display_lune.vitesse

        self.playscreen.fill((0, 0, 0))
        self.display_sun.display(self.playscreen)
        self.display_lune.display(self.playscreen)
        self.display_terre.display(self.playscreen)
        pygame.display.update()
        self.clock.tick(60)


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

        config_label = QLabel()
        config_label.setText("CONFIGURATION")
        config_label_txt = QFont()
        config_label_txt.setPointSize(10)
        config_label_txt.setBold(True)
        config_label_txt.setItalic(True)
        config_label.setFont(config_label_txt)
        upper_panel_layout.addWidget(config_label, 0, 0, 1, 3)

        mass_label = QLabel('Mass')
        upper_panel_layout.addWidget(mass_label, 1, 0)
        mass_spin = QDoubleSpinBox()
        mass_spin.setRange(0.0, 1000.0)
        mass_spin.lineEdit().setMaximumWidth(50)
        upper_panel_layout.addWidget(mass_spin, 2, 0,)
        mass_unit = QComboBox()
        pg, ng, mcg, mg, g, kg, t, mt, gt = 'pg', 'ng', 'µg', 'mg', 'g', 'kg', 't', 'Mt', 'Gt'
        unit_lst = [gt, mt, t, kg, g, mg, mcg, ng, pg]
        mass_unit.addItems(unit_lst)
        mass_unit.view().setFixedWidth(40)
        upper_panel_layout.addWidget(mass_unit, 2, 1)

        size_label = QLabel('Radius')
        upper_panel_layout.addWidget(size_label, 4, 0)
        mass_spin = QDoubleSpinBox()
        mass_spin.setRange(0.0, 1000.0)
        mass_spin.lineEdit().setMaximumWidth(50)
        upper_panel_layout.addWidget(mass_spin, 5, 0,)
        size_unit = QComboBox()
        km, m, cm, mm, mcm, nm = 'km', 'm', 'cm', ' mm', 'µm', 'nm'
        size_lst = [km, m, cm, mm, mcm, nm]
        size_unit.addItems(size_lst)
        size_unit.view().setFixedWidth(40)
        upper_panel_layout.addWidget(size_unit, 5, 1)

        density_label = QLabel('Density')
        upper_panel_layout.addWidget(density_label, 6, 0)
        density_spin = QDoubleSpinBox()
        density_spin.lineEdit().setMaximumWidth(50)
        upper_panel_layout.addWidget(density_spin, 7, 0)
        density_unit = QComboBox()
        kgm, gcm = 'kg/m³', 'g/cm³'
        density_lst = [kgm, gcm]
        density_unit.addItems(density_lst)
        size_unit.view().setFixedWidth(40)
        upper_panel_layout.addWidget(density_unit, 7, 1)

        temp_label = QLabel('Temperature')
        upper_panel_layout.addWidget(temp_label, 8, 0)
        temp_spin = QDoubleSpinBox()
        temp_spin.lineEdit().setMaximumWidth(50)
        upper_panel_layout.addWidget(temp_spin, 9, 0)
        temp_unit = QComboBox()
        k, c, f = 'K', '℃', '℉'
        temp_lst = [k, c, f]
        temp_unit.addItems(temp_lst)
        temp_unit.view().setFixedWidth(40)
        upper_panel_layout.addWidget(temp_unit, 9, 1)

        kms, ms, cms, kmh, mh, cmh, mls, yards, fts, inchs, mlh, yardh, fth, inchh = 'km/s', 'm/s', 'cm/s', 'km/h', 'm/h', 'cm/h', 'ml/s', 'yd/s', 'ft/s', 'inch/s', 'ml/h', 'yd/h', 'ft/h', 'inch/h'
        momentum_lst = [kms, ms, cms, kmh, mh, cmh, mls, yards, fts, inchs, mlh, yardh, fth, inchh]

        rotation_label = QLabel('Rotational Momentum')
        upper_panel_layout.addWidget(rotation_label, 10, 0, 1, 2)
        rotation_spin = QDoubleSpinBox()
        rotation_spin.lineEdit().setMaximumWidth(50)
        upper_panel_layout.addWidget(rotation_spin, 11, 0)
        rmomentum_unit = QComboBox()
        rmomentum_unit.addItems(momentum_lst)
        rmomentum_unit.view().setFixedWidth(65)
        upper_panel_layout.addWidget(rmomentum_unit, 11, 1)

        orbital_label = QLabel('Orbital Momentum')
        upper_panel_layout.addWidget(orbital_label, 12, 0, 1, 2)
        orbital_spin = QDoubleSpinBox()
        orbital_spin.lineEdit().setMaximumWidth(50)
        upper_panel_layout.addWidget(orbital_spin, 13, 0)
        omomentum_unit = QComboBox()
        omomentum_unit.addItems(momentum_lst)
        omomentum_unit.view().setFixedWidth(65)
        upper_panel_layout.addWidget(omomentum_unit, 13, 1)

        gravity_label = QLabel('Surface Gravity')
        upper_panel_layout.addWidget(gravity_label, 14, 0, 1, 2)
        gravity_spin = QDoubleSpinBox()
        gravity_spin.lineEdit().setMaximumWidth(50)
        upper_panel_layout.addWidget(gravity_spin, 15, 0)
        gravity_lst = [i+'²' for i in momentum_lst]
        gravity_unit = QComboBox()
        gravity_unit.addItems(gravity_lst)
        gravity_unit.view().setFixedWidth(70)
        upper_panel_layout.addWidget(gravity_unit, 15, 1)

        mid_panel = QFrame()
        mid_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        mid_panel_layout = QGridLayout()
        mid_panel.setLayout(mid_panel_layout)
        mid_panel_layout.setSpacing(10)
        layout.addWidget(mid_panel)
        mid_panel.setFixedSize(200, 450)

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
        self.resize(1200, 600)
        self.setWindowTitle('Astro Balls')
        self.setCentralWidget(PyGameWidget())

        menu = self.menuBar()
        app_menu = QMenu('&Application')
        savenew_action = QAction('&New Save', parent=self)
        savenew_action.triggered.connect(self.savenewfile)
        savenew_action.setShortcut('Ctrl+N')
        app_menu.addAction(savenew_action)
        save_action = QAction('&Save', parent=self)
        save_action.triggered.connect(self.savefile)
        save_action.setShortcut('Ctrl+S')
        app_menu.addAction(save_action)
        open_action = QAction('&Open', parent=self)
        open_action.triggered.connect(self.openfile)
        open_action.setShortcut('Ctrl+O')
        app_menu.addAction(open_action)
        app_menu.addSeparator()
        settings_action = QAction('&Settings', parent=self)
        settings_action.triggered.connect(self.settings)
        settings_action.setShortcut('Alt+S')
        app_menu.addAction(settings_action)
        app_menu.addSeparator()
        quit_action = QAction('&Quit', parent=self)
        quit_action.triggered.connect(self.closeapp)
        quit_action.setShortcut('Alt+F4')
        app_menu.addAction(quit_action)
        menu.addMenu(app_menu)

        view_menu = QMenu('&View')
        orbits_action = QWidgetAction(view_menu)
        orbits_view = self.customcheckbox(func_name='Orbits', method=self.showorbits)
        orbits_action.setDefaultWidget(orbits_view)
        view_menu.addAction(orbits_action)
        orbitsinfo_action = QWidgetAction(view_menu)
        orbitsinfo_view = self.customcheckbox(func_name='Orbits Info', method=self.showorbitinfo)
        orbitsinfo_action.setDefaultWidget(orbitsinfo_view)
        view_menu.addAction(orbitsinfo_action)
        scale_action = QWidgetAction(view_menu)
        scale_view = self.customcheckbox(func_name='Scale Slider', method=self.scaleslider)
        scale_action.setDefaultWidget(scale_view)
        view_menu.addAction(scale_action)
        menu.addMenu(view_menu)

        tool_menu = QMenu('&Tools')
        menu.addMenu(tool_menu)

        help_menu = QMenu('&Help')
        keybinds_action = QAction('&Keybinds', parent=self)
        keybinds_action.triggered.connect(self.keybinds)
        keybinds_action.setShortcut('Alt+K')
        help_menu.addAction(keybinds_action)

        guider_action = QAction('&Mímisbrunnr', parent=self)
        guider_action.triggered.connect(self.mimir)
        guider_action.setShortcut('Alt+M')
        help_menu.addAction(guider_action)

        info_action = QAction('&Guide', parent=self)
        info_action.triggered.connect(self.guide)
        info_action.setShortcut('Alt+G')
        help_menu.addAction(info_action)

        help_menu.addSeparator()
        htui_action = QAction('&About Astro Balls', parent=self)
        htui_action.triggered.connect(self.htui)
        htui_action.setShortcut('Alt+H')
        help_menu.addAction(htui_action)
        menu.addMenu(help_menu)

        self.dragndrop = DragNDrop()
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dragndrop)
        self.statsdock = StatsDock()
        self.addDockWidget(Qt.RightDockWidgetArea, self.statsdock)

    @staticmethod
    def customcheckbox(func_name, method):
        view_widget = QWidget()
        view_layout = QHBoxLayout(view_widget)
        checkbox = QCheckBox(func_name)
        checkbox.toggled.connect(method)
        view_layout.addWidget(checkbox)
        view_widget.setLayout(view_layout)
        return view_widget

    def settings(self):
        settings_window = QDialog(parent=self)
        settings_window.resize(500, 400)
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
        graphics.clicked.connect(self.graphics_setting)
        side_panel_layout.addWidget(graphics)
        audio = QPushButton('Audio')
        audio.setStyleSheet('text-align: left; padding-left: 2px')
        audio.clicked.connect(self.audio_setting)
        side_panel_layout.addWidget(audio)
        aspectratio = QPushButton('Window Aspect Ratio')
        aspectratio.setStyleSheet('text-align: left; padding-left: 2px')
        aspectratio.clicked.connect(self.aspectratio_setting)
        side_panel_layout.addWidget(aspectratio)
        keybinds = QPushButton('Keybinds')
        keybinds.setStyleSheet('text-align: left; padding-left: 2px')
        keybinds.clicked.connect(self.keybinds_setting)
        side_panel_layout.addWidget(keybinds)

        main_panel = QFrame()
        main_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        main_panel_layout = QGridLayout()
        main_panel.setLayout(main_panel_layout)
        settings_layout.addWidget(main_panel, 0, 1, 4, 4)

        apply_button = QPushButton('Apply')
        apply_button.clicked.connect(self.applysetting)
        settings_layout.addWidget(apply_button, 4, 3)

        apply_button = QPushButton('Close')
        apply_button.clicked.connect(settings_window.close)
        settings_layout.addWidget(apply_button, 4, 4)

        settings_window.exec()

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
        newton3.clicked.connect(self.aspectratio_setting)
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

    def savenewfile(self):
        pass

    def closeapp(self):
        pygame.quit()
        self.close()
        sys.exit()

    def applysetting(self):
        pass

    def graphics_setting(self):
        pass

    def audio_setting(self):
        pass

    def aspectratio_setting(self):
        pass

    def keybinds_setting(self):
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


app = QApplication(sys.argv)
mw = MainWindowFrame()
mw.show()
app.exec()
