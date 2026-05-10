import os.path
import sys

import euclid
import pygame
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QFont, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMenu, QPushButton, QVBoxLayout, QDockWidget, \
    QHBoxLayout, QWidgetAction, QCheckBox, QLabel, QDialog, QGridLayout, QFrame, QDoubleSpinBox, \
    QScrollArea, QStackedLayout, QSizePolicy, QSlider, QTabWidget, QDial, QColorDialog, QProgressDialog, QLineEdit, QFileDialog

from PyGameWidget import PyGameWidget
from WelcomeWindow import WelcomeWindow
from WidgetInteractive import DragNDrop, StatsDock

import json
from datetime import datetime
from functools import partial


class VectorEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, euclid.Vector2):
            return {"__Vector2__": True, 'x': obj.x, 'y': obj.y}
        return super().default(obj)


class MainWindowFrame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_window = None
        self.save_simwindow_layout = None
        self.save_simwindow = None
        self.orbit_timer = None
        self.get_orbitinfo_ondisplay = None
        self.scroller_widget_layout = None
        self.orbitinfo_window_layout1 = None
        self.orbitinfo_window = None
        self.timescope_label = None
        self.time_slider = None
        self.scale_slider_label = None
        self.main_label_layout = None
        self.main_panel_layout = None
        self.s_eccentricity_toggler = None
        self.b_eccentricity_toggler = None
        self.s_semimajor_toggler = None
        self.b_semimajor_toggler = None
        self.s_posorbit_toggler = None
        self.b_posorbit_toggler = None
        self.color_button = None
        self.scale_scope = None
        self.scale_slider = None
        self.stat_dock = None
        self.firstdotcoo = None
        self.seconddotcoo = None
        self.distance = None
        self.angle = None
        self.measuring_window = None
        self.firstdotcoo = None
        self.seconddotcoo = None

        self.timer_state = False
        self.scale_state = False
        self.statdock_state = False
        self.dragndrop_state = False

        self.timer_scope = None
        self.statdock_scope = None
        self.dragndrop_scope = None
        self.main_statsdock_link = StatsDock()
        self.dragndrop = DragNDrop()

        self.saveinfo = []

        self.setWindowTitle('Astro Balls')
        self.setWindowIcon(QIcon('images/app_icon/Astro Balls Icon.png'))
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.game_widget = PyGameWidget(self.main_statsdock_link, ww.wwsc_simulation)
        self.game_widget.measuring_updater_signal.connect(self.update_measuringtape)

        layout = QVBoxLayout(central_widget)
        self.game_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.game_widget)
        self.resize(1200, 600)

        menu = self.menuBar()
        app_menu = QMenu('&Application')
        savenew_action = QAction('&New Save', parent=self)
        savenew_action.setIcon(QIcon('images/menubar symbol/plus.png'))
        savenew_action.triggered.connect(self.new_save)
        savenew_action.setShortcut('Ctrl+N')
        app_menu.addAction(savenew_action)
        save_action = QAction('&Save', parent=self)
        save_action.setIcon(QIcon('images/menubar symbol/diskette.png'))
        save_action.triggered.connect(self.save_sim)
        save_action.setShortcut('Ctrl+S')
        app_menu.addAction(save_action)
        open_action = QAction('&Open', parent=self)
        open_action.setIcon(QIcon('images/menubar symbol/open-folder.png'))
        open_action.triggered.connect(self.load_sim_window)
        open_action.setShortcut('Ctrl+O')
        app_menu.addAction(open_action)
        app_menu.addSeparator()
        settings_action = QAction('&Settings', parent=self)
        settings_action.setIcon(QIcon('images/menubar symbol/cog.png'))
        settings_action.triggered.connect(self.settings)
        settings_action.setShortcut('Alt+S')
        app_menu.addAction(settings_action)
        app_menu.addSeparator()
        new_sim_action = QAction('&Reload', parent=self)
        new_sim_action.setIcon(QIcon('images/menubar symbol/loading-arrow.png'))
        new_sim_action.triggered.connect(self.reload_ww)
        new_sim_action.setShortcut('Ctrl+R')
        app_menu.addAction(new_sim_action)
        quit_action = QAction('&Quitter', parent=self)
        quit_action.setIcon(QIcon('images/menubar symbol/cross.png'))
        quit_action.triggered.connect(self.closeapp)
        quit_action.setShortcut('Alt+F4')
        app_menu.addAction(quit_action)
        menu.addMenu(app_menu)

        view_menu = QMenu('&Vue')
        self.statdock_action = QWidgetAction(view_menu)
        if not self.statdock_state:
            self.statdock_view, self.statdock_state = self.customcheckbox(func_name='StatDock', method=self.display_statdock, is_checked=True)
            self.statdock_action.setDefaultWidget(self.statdock_view)
        view_menu.addAction(self.statdock_action)

        self.dragndrop_action = QWidgetAction(view_menu)
        if not self.dragndrop_state:
            self.dragndrop_view, self.dragndrop_state = self.customcheckbox(func_name='Drag&Drop', method=self.display_dragndrop, is_checked=True)
            self.dragndrop_action.setDefaultWidget(self.dragndrop_view)
        view_menu.addAction(self.dragndrop_action)

        self.scale_action = QWidgetAction(view_menu)
        if not self.scale_state:
            self.scale_view, self.scale_state = self.customcheckbox(func_name='Échelle', method=self.scaleslider, is_checked=False)
            self.scale_action.setDefaultWidget(self.scale_view)
        view_menu.addAction(self.scale_action)
        self.timer_action = QWidgetAction(view_menu)
        if not self.timer_state:
            self.timer_view, self.timer_state = self.customcheckbox(func_name='Timer', method=self.timerscope, is_checked=False)
            self.timer_action.setDefaultWidget(self.timer_view)
        view_menu.addAction(self.timer_action)
        view_menu.addSeparator()
        self.orbits_action = QWidgetAction(view_menu)
        if not self.game_widget.is_showingorbits:
            self.orbits_view, self.orbits_state = self.customcheckbox(func_name='Orbites', method=self.showorbits, is_checked=True)
            self.orbits_action.setDefaultWidget(self.orbits_view)
        view_menu.addAction(self.orbits_action)
        self.trace_action = QWidgetAction(view_menu)
        if not self.game_widget.is_showingtrace:
            self.trace_view, self.trace_state = self.customcheckbox(func_name='Trace', method=self.showtrace,
                                                                    is_checked=False)
            self.trace_action.setDefaultWidget(self.trace_view)
        view_menu.addAction(self.trace_action)
        vector_menu = view_menu.addMenu('Vecteurs')
        self.orbitalvector_action = QWidgetAction(vector_menu)

        if not self.game_widget.is_showingorbitalvector:
            self.orbitalvector_view, self.orbitalvector_state = self.customcheckbox(func_name="Vecteur d'acceleration",
                                                                                    method=self.show_orbitalvector,
                                                                                    is_checked=False)
            self.orbitalvector_action.setDefaultWidget(self.orbitalvector_view)
        vector_menu.addAction(self.orbitalvector_action)

        self.forcevector_action = QWidgetAction(vector_menu)
        if not self.game_widget.is_showingforcevector:
            self.forcevector_view, self.forcevector_state = self.customcheckbox(func_name='Vecteur de Force',
                                                                                method=self.show_forcevector,
                                                                                is_checked=False)
            self.forcevector_action.setDefaultWidget(self.forcevector_view)
        vector_menu.addAction(self.forcevector_action)

        self.velocityvector_action = QWidgetAction(vector_menu)
        if not self.game_widget.is_showingvelocityvector:
            self.velocityvector_view, self.velocityvector_state = self.customcheckbox(func_name='Vecteur de Vitesse',
                                                                                      method=self.show_velocityvector,
                                                                                      is_checked=False)
            self.velocityvector_action.setDefaultWidget(self.velocityvector_view)
        vector_menu.addAction(self.velocityvector_action)
        menu.addMenu(view_menu)

        tool_menu = QMenu('&Outils')
        menu.addMenu(tool_menu)
        mt = QAction('&Mesuring Tape', parent=self)
        mt.setIcon(QIcon('images/menubar symbol/ruler.png'))
        mt.triggered.connect(self.measuringtape)
        mt.setShortcut('M')
        tool_menu.addAction(mt)
        of = QAction('&Info Orbites', parent=self)
        of.setIcon(QIcon('images/menubar symbol/orbit.png'))
        of.triggered.connect(self.showorbitinfo)
        of.setShortcut('I')
        tool_menu.addAction(of)

        help_menu = QMenu('&Aide')
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
        apropos_action = QAction('À propos', parent=self)
        apropos_action.setIcon(QIcon('images/menubar symbol/question-mark.png'))
        apropos_action.triggered.connect(self.apropos)
        apropos_action.setShortcut('Alt+H')
        help_menu.addAction(apropos_action)
        menu.addMenu(help_menu)

        QTimer.singleShot(0, self.guide)

    def reload_ww(self):
        self.reload = QDialog(self)
        self.reload.setWindowTitle('Reload')
        self.reload.setFixedSize(700, 400)

        ww_opensim1 = QPushButton('Système Orbitale\n à 3 Corps', parent=self.reload)
        ww_opensim1.setFixedSize(175, 400)
        ww_opensim1.move(0, 0)
        ww_opensim1.setStyleSheet("""QPushButton {background-color: #000000; border: 1px solid #1A1A1A;} 
               QPushButton:hover {background-color: #090C29;}""")
        ww_opensim1.clicked.connect(lambda: self.exec_reload(sim_id=1))
        ww_opensim2 = QPushButton('Système à 2 corps', parent=self.reload)
        ww_opensim2.setFixedSize(175, 400)
        ww_opensim2.move(175, 0)
        ww_opensim2.setStyleSheet("""QPushButton {background-color: #000000; border: 1px solid #1A1A1A;} 
               QPushButton:hover {background-color: #1D0721;}""")
        ww_opensim2.clicked.connect(lambda: self.exec_reload(sim_id=2))
        ww_opensim3 = QPushButton('Système à n corps', parent=self.reload)
        ww_opensim3.setFixedSize(175, 400)
        ww_opensim3.move(175*2, 0)
        ww_opensim3.setStyleSheet("""QPushButton {background-color: #000000; border: 1px solid #1A1A1A;} 
               QPushButton:hover {background-color: #0E1F13;}""")
        ww_opensim3.clicked.connect(lambda: self.exec_reload(sim_id=3))
        ww_sandbox = QPushButton('Système Solaire', parent=self.reload)
        ww_sandbox.setFixedSize(175, 400)
        ww_sandbox.move(175*3, 0)
        ww_sandbox.setStyleSheet("""QPushButton {background-color: #000000; border: 1px solid #1A1A1A;} 
               QPushButton:hover {background-color: #072021;}""")
        ww_sandbox.clicked.connect(lambda: self.exec_reload(sim_id=4))

        self.reload.show()

    def exec_reload(self, sim_id):
        self.reload.close()
        self.close()
        ww.wwsc_simulation = sim_id
        self.mw = MainWindowFrame()
        self.mw.show()

    @staticmethod
    def vector_decoder(dct):
        if '__Vector2__' in dct:
            return euclid.Vector2(dct['x'], dct['y'])
        return dct

    def save_sim(self):
        self.save_simwindow = QDialog(parent=self)
        self.save_simwindow.setWindowTitle('Saving...')
        self.save_simwindow.resize(300, 100)
        self.save_simwindow_layout = QGridLayout(self.save_simwindow)
        s_label = QLabel("Entrez un nom: ")
        s_label.setFixedWidth(int(self.save_simwindow.width()/2))
        self.save_simwindow_layout.addWidget(s_label, 0, 0)
        self.save_name = QLineEdit()
        self.save_name.setPlaceholderText('not a big fan of the government')
        self.save_name.setFixedWidth(int(self.save_simwindow.width()/2))
        self.save_name.textChanged.connect(self.save_sim_update_text)
        self.save_simwindow_layout.addWidget(self.save_name, 0, 1)
        self.save_button = QPushButton(f'Save')
        self.save_button.clicked.connect(self.saving)
        self.save_button.clicked.connect(self.save_simwindow.close)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.save_simwindow.close)
        self.save_simwindow_layout.addWidget(cancel_button, 1, 0)
        self.save_simwindow_layout.addWidget(self.save_button, 1, 1)
        self.save_simwindow.exec()

    def save_sim_update_text(self, text):
        if text.strip == "":
            self.save_button.setText('Save')
        else:
            self.save_button.setText(f'Save {text}')

    def saving(self):
        saving_bar = QProgressDialog()
        saving_bar.setWindowTitle('Saving...')
        saving_bar.setMinimum(0)
        saving_bar.setMaximum(0)
        saving_bar.setWindowModality(Qt.WindowModal)
        saving_bar.setValue(0)
        saving_bar.show()

        name = self.save_name.text().strip()
        get_path = os.path.join('saved_files', 'saved_sims')
        path = os.path.join(get_path, f'{name}.json')
        saved_data = {'planets': self.game_widget.planetes, 'scale': self.game_widget.scale}
        with open(path, 'w') as file:
            json.dump(saved_data, file, indent=4, cls=VectorEncoder)

    def loadsim(self):
        get_path = os.path.join('saved_files', 'saved_sims')
        file, _ = QFileDialog.getOpenFileName(self, 'Json', get_path, 'JSON Files (*.json)')
        if file:
            self.loader(file)

    def load_sim_window(self):
        self.load_window = QDialog()
        self.load_window.setWindowTitle('Load Save')
        self.load_window.resize(350, 250)
        self.load_window_layout = QGridLayout(self.load_window)
        self.load_window_layout.setSpacing(1)

        scroller = QScrollArea()
        scroller.setFrameShape(QFrame.Shape.NoFrame)
        scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroller.setWidgetResizable(True)
        self.load_window_layout.addWidget(scroller, 0, 0, 1, 2)
        self.load_window_layout.setSpacing(1)

        scroller_widget = QWidget()
        self.swll = QVBoxLayout(scroller_widget)
        self.swll.setSpacing(4)
        scroller.setWidget(scroller_widget)

        close_button = QPushButton('Fermer')
        close_button.clicked.connect(self.load_window.close)
        self.load_window_layout.addWidget(close_button, 1, 1)

        ofe_button = QPushButton('Ouvrir File Explorer')
        ofe_button.clicked.connect(self.loadsim)
        self.load_window_layout.addWidget(ofe_button, 1, 0)

        self.save_timer = QTimer(self)
        self.save_timer.timeout.connect(self.update_loadwindow)
        self.save_timer.start(50)

        self.load_window.exec()

    def update_loadwindow(self):
        if self.load_window and hasattr(self, 'swll'):
            while self.swll.count():
                item = self.swll.takeAt(0)
                panel_widget = item.widget()
                if panel_widget is not None:
                    panel_widget.deleteLater()
            self.saveinfo = []
            paths = os.path.join('saved_files', 'saved_sims')
            if not os.path.exists(paths):
                return
            getter = os.listdir(paths)
            files = [f for f in getter if os.path.isfile(os.path.join(paths, f))]
            path_dict = []
            for j, k in enumerate(files):
                panel = QFrame()
                panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
                panel_layout = QGridLayout()
                panel.setLayout(panel_layout)
                panel_layout.setSpacing(1)
                name_label = QLabel(k)
                name_label_font = QFont()
                name_label_font.setBold(True)
                name_label.setFont(name_label_font)
                name_label.setFixedWidth(130)
                name_label.setWordWrap(True)
                panel_layout.addWidget(name_label, 0, 0)
                get_paths = os.path.abspath(os.path.join(paths, k))
                path_dict.append(get_paths)
                load_button = QPushButton('Load')
                load_button.setStyleSheet("""QPushButton 
                                        {border: 1px solid #8a8a8a; padding: 2px; background-color: #444444} 
                                        QPushButton::hover { background-color: #4d4d4d}""")
                load_button.pressed.connect(partial(self.loader, path_dict[j]))
                panel_layout.addWidget(load_button, 0, 1)
                delete_file_button = QPushButton('Delete')
                delete_file_button.setStyleSheet("""QPushButton 
                                        {border: 1px solid #FF8A8A; padding: 2px; background-color: #A30000} 
                                        QPushButton::hover { background-color: #FF0000}""")
                delete_file_button.pressed.connect(partial(self.deleter_prevention, path_dict[j]))
                panel_layout.addWidget(delete_file_button, 0, 2)
                self.swll.addWidget(panel)
                self.saveinfo.append(name_label)

    def deleter_prevention(self, path):
        get_path = path
        preventer = QDialog(parent=self)
        preventer.setWindowTitle('delete file?')
        preventer_layout = QGridLayout(preventer)
        preventer.setFixedWidth(240)
        q_label = QLabel("Êtes-vous sûr de vouloir supprimer ce fichier ? Il ne pourra plus être récupéré.")
        q_label.setWordWrap(True)
        preventer_layout.addWidget(q_label, 0, 0, 1, 2)
        yes_button = QPushButton('Oui')
        yes_button.clicked.connect(partial(self.deleter, get_path))
        preventer_layout.addWidget(yes_button, 1, 0)
        no_button = QPushButton('Non')
        no_button.clicked.connect(preventer.close)
        preventer_layout.addWidget(no_button, 1, 1)
        preventer.exec()

    def deleter(self, path):
        if os.path.exists(path):
            os.remove(path)
            self.update_loadwindow()

    def loader(self, path):
        with open(path, 'r') as file:
            file_unloader = json.load(file, object_hook=self.vector_decoder)
            self.game_widget.planetes.clear()
            self.game_widget.scale = file_unloader['scale']
            self.game_widget.planetes = file_unloader['planets']

    def new_save(self):
        preventer = QDialog(parent=self)
        preventer.setWindowTitle('new save?')
        preventer_layout = QGridLayout(preventer)
        preventer.setFixedWidth(240)
        q_label = QLabel("Voulez-vous créer un nouveau fichier? Toutes les modifications non enregistrées seront perdues.")
        q_label.setWordWrap(True)
        preventer_layout.addWidget(q_label, 0, 0, 1, 2)
        yes_button = QPushButton('Oui')
        yes_button.clicked.connect(self.load_newsave)
        yes_button.clicked.connect(preventer.close)
        preventer_layout.addWidget(yes_button, 1, 0)
        no_button = QPushButton('Non')
        no_button.clicked.connect(preventer.close)
        preventer_layout.addWidget(no_button, 1, 1)
        preventer.exec()

    def load_newsave(self):
        self.game_widget.planetes.clear()
        self.game_widget.update()

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

    def display_statdock(self):
        if getattr(self, 'statdock_scope', None) is not None:
            self.statdock_scope.setVisible(self.statdock_state.isChecked())
            return
        self.statdock_scope = self.main_statsdock_link
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.main_statsdock_link)
        self.statdock_scope.visibilityChanged.connect(self.statdock_close)
        self.statdock_scope.show()

    def statdock_close(self, active):
        if hasattr(self, 'statdock_state'):
            #self.statdock_state.blockSignals(True)
            self.statdock_state.setChecked(active)
            #self.statdock_state.blockSignals(False)

    def display_dragndrop(self):
        if getattr(self, 'dragndrop_scope', None) is not None:
            self.dragndrop_scope.setVisible(self.dragndrop_state.isChecked())
            return
        self.dragndrop_scope = self.dragndrop
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.dragndrop)
        self.dragndrop_scope.visibilityChanged.connect(self.dragndrop_closed)
        self.dragndrop_scope.show()

    def dragndrop_closed(self, active):
        if hasattr(self, 'dragndrop_state'):
            self.dragndrop_state.setChecked(active)

    def timerscope(self):
        if getattr(self, 'timer_scope', None) is not None:
            self.timer_scope.setVisible(self.timer_state.isChecked())
            return
        self.timer_scope = QDockWidget(parent=self)
        timerscope_container = QWidget()
        timerscope_widget = QGridLayout(timerscope_container)
        self.timer_scope.setWidget(timerscope_container)
        self.timer_scope.setWindowTitle('Vitesse Simulation')

        self.time_slider = QSlider(Qt.Orientation.Horizontal, parent=timerscope_container)
        self.configure_slider(self.time_slider, 0, 100, 1)
        timerscope_widget.addWidget(self.time_slider, 0, 0, 1, 2)
        self.time_slider.valueChanged.connect(self.update_timerscope)
        self.time_slider.valueChanged.connect(self.game_widget.speed_interactive)
        self.timescope_label = QLabel('', timerscope_container)

        backward_button = QPushButton('Arrière')
        backward_button.clicked.connect(self.backward_timescope)
        timerscope_widget.addWidget(backward_button, 1, 0)

        forward_button = QPushButton('Avant')
        forward_button.clicked.connect(self.forward_timescope)
        timerscope_widget.addWidget(forward_button, 1, 1)

        self.timer_scope.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.timer_scope.setFixedHeight(120)
        self.splitDockWidget(self.main_statsdock_link, self.timer_scope, Qt.Orientation.Vertical)

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

    @staticmethod
    def configure_slider(slider: QSlider, minimum: int, maximum: int, value: int, tick_interval: int = 5,
                         single_step: int = 5):
        slider.setRange(minimum, maximum)
        slider.setValue(value)
        slider.setTickInterval(tick_interval)
        slider.setSingleStep(single_step)
        slider.setTickPosition(QSlider.TickPosition.TicksAbove)

    def timerscope_close(self, active):
        if hasattr(self, 'timer_state'):
            self.timer_state.blockSignals(True)
            self.timer_state.setChecked(active)
            self.timer_state.blockSignals(False)

    def backward_timescope(self):
        self.time_slider.setValue(self.time_slider.value() - 1)

    def forward_timescope(self):
        self.time_slider.setValue(self.time_slider.value() + 1)

    def scaleslider(self):
        if getattr(self, 'scale_slider', None) is not None:
            self.scale_scope.setVisible(self.scale_state.isChecked())
            return
        self.scale_scope = QDockWidget(parent=self)
        scale_scope_container = QWidget()
        scale_scope_widget = QGridLayout(scale_scope_container)
        self.scale_scope.setWidget(scale_scope_container)
        self.scale_scope.setWindowTitle('Échelle de rendu')

        self.scale_slider = QSlider(Qt.Orientation.Horizontal, parent=scale_scope_container)
        self.configure_slider(self.scale_slider, 1, 100, 20)
        scale_scope_widget.addWidget(self.scale_slider, 0, 0, 1, 2)
        self.scale_slider.valueChanged.connect(self.update_scale_slider)
        self.scale_slider.valueChanged.connect(self.game_widget.scale_interactive)
        self.scale_slider.sliderPressed.connect(self.game_widget.on_slider_pressed)
        self.scale_slider.sliderReleased.connect(self.game_widget.on_slider_released)
        self.game_widget.scale_updater.connect(self.view_update)

        self.scale_slider_label = QLabel('', scale_scope_container)

        backward_button = QPushButton('Arrière')
        backward_button.clicked.connect(self.backward_scale_slider)
        scale_scope_widget.addWidget(backward_button, 1, 0)

        forward_button = QPushButton('Avant')
        forward_button.clicked.connect(self.forward_scale_slider)
        scale_scope_widget.addWidget(forward_button, 1, 1)

        self.scale_scope.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.scale_scope.setFixedHeight(120)
        self.splitDockWidget(self.main_statsdock_link, self.scale_scope, Qt.Orientation.Vertical)

        self.scale_scope.visibilityChanged.connect(self.scale_scope_close)
        self.scale_scope.show()

    def scale_scope_close(self, active):
        if hasattr(self, 'timer_state'):
            self.scale_state.blockSignals(True)
            self.scale_state.setChecked(active)
            self.scale_state.blockSignals(False)

    def update_scale_slider(self):
        self.scale_slider_label.setText(f'X{self.scale_slider.value()}')
        self.scale_slider_label.adjustSize()
        ratio = (self.scale_slider.value() - self.scale_slider.minimum()) / (
                self.scale_slider.maximum() - self.scale_slider.minimum())
        x_pos = 16 / 2 + ratio * (self.scale_slider.width())+85
        x_pos_parent = self.scale_slider.x() + x_pos - (self.scale_slider.width() // 2)
        y_pos = self.scale_slider.y() - 15
        self.scale_slider_label.move(int(x_pos_parent), int(y_pos))

    def view_update(self, val):
        self.scale_slider.blockSignals(True)
        self.scale_slider.setValue(int(val))
        self.scale_slider.blockSignals(False)
        self.update_scale_slider()

    def backward_scale_slider(self):
        self.scale_slider.setValue(self.scale_slider.value() - 1)
        self.game_widget.val = self.scale_slider.value() -1

    def forward_scale_slider(self):
        self.scale_slider.setValue(self.scale_slider.value() + 1)
        self.game_widget.val = self.scale_slider.value() + 1

    @staticmethod
    def customcheckbox(func_name, method, is_checked:bool):
        view_widget = QWidget()
        view_layout = QHBoxLayout(view_widget)
        checkbox = QCheckBox(func_name)
        checkbox.toggled.connect(method)
        if is_checked is True:
            checkbox.setChecked(True)
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

        close_button_settings = QPushButton('Close')
        close_button_settings.clicked.connect(settings_window.close)
        settings_layout.addWidget(close_button_settings, 4, 4)

        settings_window.exec()

    def graphicstab(self):
        self.main_panel_layout.setCurrentIndex(0)

    def audiotab(self):
        self.main_panel_layout.setCurrentIndex(1)

    def aspectratiotab(self):
        self.main_panel_layout.setCurrentIndex(2)

    def keybindstab(self):
        self.main_panel_layout.setCurrentIndex(3)

#DEMO
    def mimir(self):
        info_window = QDialog(parent=self)
        info_window.setFixedSize(650, 500)
        info_window.setWindowTitle('Infd')
        info_layout = QHBoxLayout()
        info_tabs = QTabWidget()

        newton1tab = QWidget()
        newton1tab_layout = QGridLayout()
        b_n1_label = QLabel(parent=newton1tab)
        b_n1_label.setFixedSize(500, 40)
        b_n1_label.setText("NEWTON'S FIRST LAW")
        b_n1_label_font = QFont()
        b_n1_label_font.setPointSize(30)
        b_n1_label.setFont(b_n1_label_font)
        b_n1_label.move(20, 20)
        pixmap_newton1 = QPixmap('images/mimir_usedimages/GodfreyKneller-IsaacNewton-1689.jpg').scaled(200, 280,
                                                                            Qt.AspectRatioMode.KeepAspectRatio,
                                                                            Qt.TransformationMode.SmoothTransformation)
        l_pixmap_newton1 = QLabel(parent=newton1tab)
        l_pixmap_newton1.setFrameStyle(QFrame.Shape.Panel)
        l_pixmap_newton1.setFixedSize(200, 280)
        l_pixmap_newton1.setPixmap(pixmap_newton1)
        l_pixmap_newton1.move(420, 95)
        with open('mimir_files/info_text/newton1.txt', 'r', encoding='utf-8') as newton1_txtfile:
            i_n1_label = QLabel(str(newton1_txtfile.read()), parent=newton1tab)
        fixed_sizedw = info_window.width()*(3/5)
        i_n1_label.setFixedWidth(int(fixed_sizedw))
        i_n1_label.setWordWrap(True)
        i_n1_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        i_n1_label.adjustSize()
        i_n1_label.move(20, 100)
        im_n1_label = QLabel("Sir Isaac Newton\nBy Godfrey Kneller\n1689", parent=newton1tab)
        im_n1_label.setFixedSize(100, 100)
        im_n1_label.move(470, 350)
        newton1tab.setLayout(newton1tab_layout)
        info_tabs.addTab(newton1tab, "Newton's First Law")

        newton2tab = QWidget()
        b_n2_label = QLabel(parent=newton2tab)
        b_n2_label.setFixedSize(500, 40)
        b_n2_label.setText("NEWTON'S SECOND LAW")
        b_n2_label_font = QFont()
        b_n2_label_font.setPointSize(30)
        b_n2_label.setFont(b_n2_label_font)
        b_n2_label.move(20, 20)
        with open('mimir_files/info_text/newton2.txt', 'r', encoding='utf-8') as newton2_txtfile:
            i_n2_label = QLabel(str(newton2_txtfile.read()), parent=newton2tab)
        i_n2_label.setFixedWidth(int(fixed_sizedw))
        i_n2_label.setWordWrap(True)
        i_n2_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        i_n2_label.adjustSize()
        i_n2_label.move(20, 100)
        e_n2_label = QLabel("<span style='font-family: Cambria Math; font-style: italic; font-size: 20px;'>"
                            "F = m \u00b7 a</span>", parent=newton2tab)
        e_n2_label.move(100, 250)
        newton2tab_layout = QGridLayout()
        newton2tab.setLayout(newton2tab_layout)
        info_tabs.addTab(newton2tab, "Newton's Second Law")

        newton3tab = QWidget()
        b_n3_label = QLabel(parent=newton3tab)
        b_n3_label.setFixedSize(500, 40)
        b_n3_label.setText("NEWTON'S THIRD LAW")
        b_n3_label_font = QFont()
        b_n3_label_font.setPointSize(30)
        b_n3_label.setFont(b_n3_label_font)
        b_n3_label.move(20, 20)
        with open('mimir_files/info_text/newton3.txt', 'r', encoding='utf-8') as newton3_txtfile:
            i_n3_label = QLabel(str(newton3_txtfile.read()), parent=newton3tab)
        i_n3_label.setFixedWidth(int(fixed_sizedw))
        i_n3_label.setWordWrap(True)
        i_n3_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        i_n3_label.adjustSize()
        i_n3_label.move(20, 100)
        e_n3_label = QLabel("<span style='font-family: Cambria Math; font-style: italic; font-size: 20px;'>"
                            "F<sub>AB</sub> = -F<sub>BA</sub>", parent=newton3tab)
        e_n3_label.move(100, 250)
        newton3tab_layout = QGridLayout()
        newton3tab.setLayout(newton3tab_layout)
        info_tabs.addTab(newton3tab, "Newton's Third Law")

        kflopmtab = QWidget()
        b_k_label = QLabel(parent=kflopmtab)
        b_k_label.setFixedSize(500, 100)
        b_k_label.setText("KEPLER'S FIRST LAW OF \nPLANETARY MOTION")
        b_k_label.setFixedWidth(info_window.width())
        b_k_label_font = QFont()
        b_k_label_font.setPointSize(30)
        b_k_label.setFont(b_n3_label_font)
        b_k_label.move(20, 20)
        with open('mimir_files/info_text/kflopm.txt', 'r', encoding='utf-8') as kflopm_txtfile:
            i_k_label = QLabel(str(kflopm_txtfile.read()), parent=kflopmtab)
        i_k_label.setFixedWidth(int(fixed_sizedw))
        i_k_label.setWordWrap(True)
        i_k_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        i_k_label.adjustSize()
        i_k_label.move(20, 150)
        pixmap_kflopm = QPixmap('images/mimir_usedimages/Johannes_Kepler_1610-746x1024.jpg').scaled(200, 280,
                                                                                Qt.AspectRatioMode.KeepAspectRatio,
                                                                           Qt.TransformationMode.SmoothTransformation)
        l_pixmap_kflopm = QLabel(parent=kflopmtab)
        l_pixmap_kflopm.setFrameStyle(QFrame.Shape.Panel)
        l_pixmap_kflopm.setFixedSize(200, 280)
        l_pixmap_kflopm.setPixmap(pixmap_kflopm)
        l_pixmap_kflopm.move(420, 95)
        e_k_label = QLabel(parent=kflopmtab)
        e_k_txt = """
        <table style='color: white; font-family: "Cambria Math", serif; font-size: 15px; border-collapse: collapse;'>
          <tr>
            <td style='vertical-align: middle; padding-right: 10px; font-style: italic;'>
              r(&theta;) <span style='font-style: normal;'>=</span>
            </td>
        
            <td style='vertical-align: middle;'>
              <table style='border-collapse: collapse; display: inline-table;'>
                <tr>
                  <td style='border-bottom: 2px solid white; text-align: center; padding: 2px 10px; font-style: italic;'>
                    a(1 &minus; e<sup>2</sup>)
                  </td>
                </tr>
                <tr>
                  <td style='text-align: center; padding: 2px 10px; font-style: italic;'>
                    1 + e <span style='font-style: normal;'>cos</span>(&theta;)
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
        """
        e_k_label.setTextFormat(Qt.TextFormat.RichText)
        e_k_label.setText(e_k_txt)
        e_k_label.setFixedSize(500, 70)
        e_k_label.move(110, 238)
        ei_k_label = QLabel("Ou:\nr(θ) = La distance radiale"
                            "\na = L'axe semi-majeur"
                            "\nε = Excentricité"
                            "\nθ = L'angle depuis le perihelion", parent=kflopmtab)
        ei_k_label.setFixedSize(150, 60)
        ei_k_label.move(284, 235)
        kflopmtab_layout = QGridLayout()
        kflopmtab.setLayout(kflopmtab_layout)
        info_tabs.addTab(kflopmtab, "Kepler's First Law of Planetary Motion")

        metrictab = QWidget()
        metrictab_layout = QGridLayout()
        metrictab.setLayout(metrictab_layout)
        info_tabs.addTab(metrictab, "Metric System")

        imperialtab = QWidget()
        imperialtab_layout = QGridLayout()
        imperialtab.setLayout(imperialtab_layout)
        info_tabs.addTab(imperialtab, "Imperial System")

        info_layout.addWidget(info_tabs)
        info_window.setLayout(info_layout)

        info_window.exec()

    def apropos(self):
        apropos_window = QDialog(parent=self)
        apropos_window.resize(560, 360)
        apropos_window.setWindowTitle('À propos de nous')
        apropos_layout = QGridLayout()
        apropos_layout.setContentsMargins(12, 12, 12, 12)
        apropos_layout.setHorizontalSpacing(10)
        apropos_layout.setVerticalSpacing(10)
        apropos_window.setLayout(apropos_layout)

        about_icon = QPixmap('images/app_icon/Astro Balls Icon.png').scaled(170, 170, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        icon_label = QLabel()
        icon_label.setPixmap(about_icon)
        apropos_layout.addWidget(icon_label, 0, 0, 2, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        info_label = QLabel(parent=apropos_window)
        info_label.setText(
            "<b>Astro Balls</b><br>Version: v0.1.11<br><br>Astro Balls est une simulation de mouvements planétaires et "
            "de corps célestes. Amusez vous à ajouter toutes sortes de choses en orbite et à les faire interagir entre "
            "elles. Vous pouvez également visualiser les orbites, mesurer des distances et expérimenter avec la vitesse "
            "et l'échelle de la simulation."
        )
        info_label.setWordWrap(True)
        info_font = QFont()
        info_font.setPointSize(10)
        info_label.setFont(info_font)
        apropos_layout.addWidget(info_label, 0, 1, 1, 2)

        credits_label = QLabel(parent=apropos_window)
        credits_label.setText(
            "Développé par: \n"
            "Maxime Bélanger-Lamarche\n"
            "Samuel Gagné\n"
            "Antoine St-Gelais\n"
        )
        credits_label.setWordWrap(True)
        apropos_layout.addWidget(credits_label, 1, 1, 1, 2)

        bouton_fermer = QPushButton('Fermer')
        bouton_fermer.clicked.connect(apropos_window.close)
        apropos_layout.addWidget(bouton_fermer, 2, 2, Qt.AlignmentFlag.AlignRight)

        apropos_window.exec()

    def guide(self):
        guide_window = QDialog(parent=self)
        guide_window.resize(700, 500)
        guide_window.setWindowTitle('Guide d\'utilisation')
        guide_layout = QGridLayout()
        guide_layout.setContentsMargins(12, 12, 12, 12)
        guide_layout.setHorizontalSpacing(10)
        guide_layout.setVerticalSpacing(10)
        guide_window.setLayout(guide_layout)

        slides = [
            {
                "titre": "Bienvenue dans Astro Balls !",
                "contenu": "Astro Balls est un simulateur de physique gravitationnelle qui vous permet de créer "
                          "et d'observer des systèmes planétaires.\n\n"
                          "Utilisez les boutons ci-dessous pour naviguer dans ce guide et découvrir toutes "
                          "les fonctionnalités de l'application."
            },
            {
                "titre": "Ajouter des corps célestes",
                "contenu": "Pour ajouter un corps céleste :\n\n"
                          "1. Faites glisser un objet depuis le panneau du bas\n"
                          "2. Déposez-le sur la zone de simulation\n"
                          "3. L'objet apparaîtra à l'endroit où vous l'avez déposé\n\n"
                          "Vous pouvez ajouter des planètes, des étoiles, des lunes, et même des trous noirs !"
            },
            {
                "titre": "Contrôles de la caméra",
                "contenu": "Navigation dans la simulation :\n\n"
                          "• Touche F : Changer le mode de caméra (libre / suivi / milieu)\n"
                          "• Touches WASD : Déplacer la caméra en mode libre\n"
                          "• Shift : Accélérer le déplacement de la caméra\n\n"
                          "Cliquez sur une planète pour la suivre automatiquement."
            },
            {
                "titre": "Contrôles de zoom et vitesse",
                "contenu": "Ajuster la vue et la simulation :\n\n"
                          "• Échelle : Contrôle le niveau de zoom\n"
                          "  - Valeurs basses : Vue d'ensemble\n"
                          "  - Valeurs élevées : Zoom rapproché\n\n"
                          "• Vitesse Sim. : Contrôle la vitesse de la simulation\n"
                          "  - Ralentir ou accélérer le temps"
            },
            {
                "titre": "Outils de mesure et orbites",
                "contenu": "Outils avancés :\n\n"
                          "• Si un planète est sélectionné, la distance affiché dans le coin de l'écran "
                           "est la distance entre la souris et l'objet sélectionné"
                          "• Désactiver orbites : Désactive l'affichage des trajectoires orbitales\n"
                          "• Éditeur d'orbites : Modifiez la position des objets sur leur orbite\n\n"
                          "Ces outils vous aident à comprendre la physique du système."
            },
            {
                "titre": "Informations et Modifications",
                "contenu": "Obtenir des informations :\n\n"
                          "• Cliquez sur un corps céleste pour voir ses propriétés\n"
                          "• Le premier panneau latéral affiche les informations de l'objet\n"
                          "• Dans le deuxième panneau vous pourrez modifier la masse et le rayon des objets \n"
                          "  - La masses est en notation scientifique\n"
                          "  - Le rayon est en entier\n"
                          "• Le dernier panneau permet de modifier le facteur elliptique des orbites\n"
                          "  - Entre 0.3 et 1.0\n\n"
                          "Explorez et apprenez !"
            }
        ]

        current_slide = [0]

        titre_label = QLabel(parent=guide_window)
        titre_font = QFont()
        titre_font.setPointSize(14)
        titre_font.setBold(True)
        titre_label.setFont(titre_font)
        titre_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        guide_layout.addWidget(titre_label, 0, 0, 1, 3)

        info_label = QLabel(parent=guide_window)
        info_label.setWordWrap(True)
        info_font = QFont()
        info_font.setPointSize(10)
        info_label.setFont(info_font)
        info_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        guide_layout.addWidget(info_label, 1, 0, 1, 3)

        page_label = QLabel(parent=guide_window)
        page_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        guide_layout.addWidget(page_label, 2, 0, 1, 3)

        def update_slide():
            slide = slides[current_slide[0]]
            titre_label.setText(slide["titre"])
            info_label.setText(slide["contenu"])
            page_label.setText(f"Page {current_slide[0] + 1} / {len(slides)}")

            bouton_precedent.setEnabled(current_slide[0] > 0)
            bouton_suivant.setEnabled(current_slide[0] < len(slides) - 1)

        def slide_precedent():
            if current_slide[0] > 0:
                current_slide[0] -= 1
                update_slide()

        def slide_suivant():
            if current_slide[0] < len(slides) - 1:
                current_slide[0] += 1
                update_slide()

        bouton_precedent = QPushButton('Précédent')
        bouton_precedent.clicked.connect(slide_precedent)
        guide_layout.addWidget(bouton_precedent, 3, 0, Qt.AlignmentFlag.AlignLeft)

        bouton_fermer = QPushButton('Fermer')
        bouton_fermer.clicked.connect(guide_window.close)
        guide_layout.addWidget(bouton_fermer, 3, 1, Qt.AlignmentFlag.AlignCenter)

        bouton_suivant = QPushButton('Suivant')
        bouton_suivant.clicked.connect(slide_suivant)
        guide_layout.addWidget(bouton_suivant, 3, 2, Qt.AlignmentFlag.AlignRight)

        update_slide()

        guide_window.exec()

    def closeapp(self):
        pygame.quit()
        self.close()
        sys.exit()

    def applysetting(self):
        pass

    def showorbits(self, checked):
        self.game_widget.is_showingorbits = checked

    def showorbitinfo(self):
        if self.orbitinfo_window is None:
            self.orbitinfo_window = QDialog(parent=self)
            self.orbitinfo_window.setWindowTitle('Orbites')
            self.orbitinfo_window.setFixedSize(400, 280)
            self.orbitinfo_window_layout1 = QGridLayout(self.orbitinfo_window)
            self.orbitinfo_window_layout1.setContentsMargins(2, 2, 2, 2)

            scroller = QScrollArea()
            scroller.setFrameShape(QFrame.Shape.NoFrame)
            scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroller.setWidgetResizable(True)
            self.orbitinfo_window_layout1.addWidget(scroller, 0, 1)

            scroller_widget = QWidget()
            self.scroller_widget_layout = QVBoxLayout(scroller_widget)
            self.scroller_widget_layout.setSpacing(4)
            scroller.setWidget(scroller_widget)

            orbit_helper = QPushButton('Aide')
            orbit_helper.setCheckable(True)
            orbit_helper.setToolTip('Pré-configure la vitesse suffisante pour maintenir une orbite circulaire')
            orbit_helper.clicked.connect(self.game_widget.kepler_orbit_helper)
            self.orbitinfo_window_layout1.addWidget(orbit_helper, 1, 0)

            close_button = QPushButton('Fermer')
            close_button.clicked.connect(self.orbitinfo_window.close)
            close_button.clicked.connect(self.when_showorbit_closed)
            self.orbitinfo_window_layout1.addWidget(close_button, 1, 1)

            panel = QFrame()
            panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
            panel_layout = QGridLayout()
            panel.setLayout(panel_layout)
            panel_layout.setSpacing(3)
            self.orbitinfo_window_layout1.addWidget(panel, 0, 0)

            l_eccentricity_toggler = QLabel('Excentricité: ')
            panel_layout.addWidget(l_eccentricity_toggler, 0, 0)
            self.s_eccentricity_toggler = QSlider(Qt.Orientation.Horizontal, parent=self)
            self.s_eccentricity_toggler.setMinimum(0)
            self.s_eccentricity_toggler.setMaximum(100)
            self.s_eccentricity_toggler.setSingleStep(1)
            self.s_eccentricity_toggler.setTickPosition(QSlider.TickPosition.TicksAbove)
            self.s_eccentricity_toggler.valueChanged.connect(self.game_widget.orbital_eccentricity_editor)
            panel_layout.addWidget(self.s_eccentricity_toggler, 2, 0, 1, 2)
            self.b_eccentricity_toggler = QDoubleSpinBox()
            self.b_eccentricity_toggler.setDecimals(4)
            self.b_eccentricity_toggler.lineEdit().setMaximumWidth(50)
            self.b_eccentricity_toggler.setMaximumWidth(90)
            panel_layout.addWidget(self.b_eccentricity_toggler, 0, 1)

            l_semimajor_toggler = QLabel('Vitesse: ')
            panel_layout.addWidget(l_semimajor_toggler, 3, 0)
            self.s_semimajor_toggler = QSlider(Qt.Orientation.Horizontal, parent=self)
            self.s_semimajor_toggler.setMinimum(0)
            self.s_semimajor_toggler.setMaximum(100)
            self.s_semimajor_toggler.setSingleStep(1)
            self.s_semimajor_toggler.setTickPosition(QSlider.TickPosition.TicksAbove)
            self.s_semimajor_toggler.valueChanged.connect(self.game_widget.orbital_velocity_editor)
            panel_layout.addWidget(self.s_semimajor_toggler, 4, 0, 1, 2)
            self.b_semimajor_toggler = QDoubleSpinBox()
            self.b_semimajor_toggler.lineEdit().setMaximumWidth(50)
            self.b_semimajor_toggler.setMaximumWidth(90)
            panel_layout.addWidget(self.b_semimajor_toggler, 3, 1)

            l_posorbit_toggler = QLabel('Position Orbitale: ', parent=panel)
            l_posorbit_toggler.move(10, 107)
            self.s_posorbit_toggler = QDial(parent=panel)
            self.s_posorbit_toggler.setMinimum(0)
            self.s_posorbit_toggler.setMaximum(360)
            self.s_semimajor_toggler.setValue(0)
            self.s_posorbit_toggler.setMaximumWidth(90)
            self.s_posorbit_toggler.setSingleStep(1)
            self.s_posorbit_toggler.setWrapping(True)
            self.s_posorbit_toggler.valueChanged.connect(getattr(self.game_widget, 'orbital_position_editor'))
            self.s_posorbit_toggler.setInvertedAppearance(True)
            panel_layout.addWidget(self.s_posorbit_toggler, 5, 1)
            self.b_posorbit_toggler = QDoubleSpinBox(parent=panel)
            self.b_posorbit_toggler.lineEdit().setMaximumWidth(50)
            self.b_posorbit_toggler.setMaximumWidth(60)
            self.b_posorbit_toggler.setRange(0, 360)
            self.b_posorbit_toggler.setStyleSheet("""QDoubleSpinBox {padding-right:1px} 
            QDoubleSpinBox::up-button{subcontrol-position: top right; width: 16px} 
            QDoubleSpinBox::down-button{subcontrol-position: bottom right; width: 16px}""")
            self.b_posorbit_toggler.move(8, 146)

            l_orbitcolor_toggler = QLabel('Couleur: ')
            panel_layout.addWidget(l_orbitcolor_toggler, 6, 0)
            self.color_button = QPushButton('Palette')
            self.color_button.setStyleSheet("""QPushButton 
            {border: 1px solid #8a8a8a; padding: 2px; background-color: #444444} 
            QPushButton::hover { background-color: #4d4d4d}""")
            self.color_button.clicked.connect(self.orbiteditor_color)
            panel_layout.addWidget(self.color_button, 6, 1)

            self.get_orbitinfo_ondisplay = []
            self.orbit_timer = QTimer(self)
            self.orbit_timer.timeout.connect(self.update_showorbitinfo)
            self.orbit_timer.start(50)

            self.orbitinfo_window.finished.connect(lambda: setattr(self, 'orbitinfo_window', None))
            self.orbitinfo_window.show()

        # TODO: try update QDial along planet orbit (for later)

    def update_showorbitinfo(self):
        self.b_eccentricity_toggler.setValue(self.s_eccentricity_toggler.value() / 100)
        self.b_semimajor_toggler.setValue(self.s_semimajor_toggler.value())
        self.b_posorbit_toggler.setValue(self.s_posorbit_toggler.value())
        # self.b_posorbit_toggler.setValue(self.game_widget.uopt_editor())
        # (i need to enable both way value editing without fucking up the orbits... but not rn twin it 1:43am)
        if self.orbitinfo_window and hasattr(self, 'scroller_widget_layout'):
            if len(self.game_widget.kepler()) is not len(self.get_orbitinfo_ondisplay):
                for i in range(self.scroller_widget_layout.count()):
                    panel = self.scroller_widget_layout.itemAt(i).widget()
                    if panel:
                        panel.deleteLater()
                self.get_orbitinfo_ondisplay = []
                for k, j in enumerate(self.game_widget.kepler()):
                    panel = QFrame()
                    panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
                    panel_layout = QVBoxLayout()
                    panel.setLayout(panel_layout)
                    panel_layout.setSpacing(1)

                    planet_label = QLabel()
                    planet_label_font = QFont()
                    planet_label_font.setBold(True)
                    planet_label.setFont(planet_label_font)
                    panel_layout.addWidget(planet_label)
                    epstein_label = QLabel()
                    panel_layout.addWidget(epstein_label)
                    semimajoraxis_label = QLabel()
                    panel_layout.addWidget(semimajoraxis_label)
                    velocity_label = QLabel()
                    panel_layout.addWidget(velocity_label)
                    separator = QFrame()
                    separator.setFrameStyle(QFrame.Shape.HLine)
                    panel_layout.addWidget(separator)
                    configure_orbit_button = QPushButton('Configure Orbit')
                    configure_orbit_button.setStyleSheet("""QPushButton 
                     {border: 1px solid #8a8a8a; padding: 2px; background-color: #444444} 
                     QPushButton::hover { background-color: #4d4d4d}""")
                    configure_orbit_button.setProperty('planet_name', j['planet']['nom'])
                    configure_orbit_button.clicked.connect(getattr(self.game_widget, 'orbit_editor'))
                    panel_layout.addWidget(configure_orbit_button)
                    ondisplay_structure = {'Name': planet_label, 'epstein': epstein_label,
                                           'semimajor': semimajoraxis_label, 'velocity': velocity_label}
                    self.scroller_widget_layout.addWidget(panel)
                    self.get_orbitinfo_ondisplay.append(ondisplay_structure)

            for k, l in enumerate(self.game_widget.kepler()):
                ondisplay = self.get_orbitinfo_ondisplay[k]
                self.get_orbitinfo_ondisplay[k]['Name'].setText(l['planet']['nom'])
                ondisplay['epstein'].setText(f'ε: {round(l['epsilon'], 5)}')
                ondisplay['semimajor'].setText(f'Semi-majeur(a): {round(l['a'], 3)}')
                ondisplay['velocity'].setText(f'Vitesse: {round(l['vel'].magnitude(), 1)}m/s')

    def when_showorbit_closed(self):
        self.orbit_timer.stop()
        self.orbitinfo_window = None

    def orbiteditor_color(self):
        color_window = QColorDialog.getColor()
        if color_window.isValid():
            color = color_window.name()
            self.game_widget.orbital_velocity_color(color)
            self.color_button.setStyleSheet(f"""QPushButton {{border: 1px solid #8a8a8a; padding: 2px; 
                                                background-color: {color};}}""")

    def show_orbitalvector(self, checked):
        self.game_widget.is_showingorbitalvector = checked

    def show_forcevector(self, checked):
        self.game_widget.is_showingforcevector = checked

    def show_velocityvector(self, checked):
        self.game_widget.is_showingvelocityvector = checked

    def showtrace(self, checked):
        self.game_widget.is_showingtrace = checked

    def keybinds(self):
        self.settings()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ww = WelcomeWindow()
    ww.show()
    app.exec()

    if ww.wwsc_simulation is not None:
        mw = MainWindowFrame()
        mw.show()
        sys.exit(app.exec())
