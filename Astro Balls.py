import sys
import pygame

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, Qt, QFont, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMenu, QPushButton, QVBoxLayout, QDockWidget, \
    QHBoxLayout, QWidgetAction, QCheckBox, QLabel, QDialog, QGridLayout, QFrame, QComboBox, QSpinBox, QDoubleSpinBox, \
    QScrollArea, QScrollBar, QStackedLayout, QSizePolicy, QSlider, QTabWidget, QDial, QColorDialog

from PyGameWidget import PyGameWidget
from WelcomeWindow import WelcomeWindow
from WidgetInteractive import DragNDrop, StatsDock


class MainWindowFrame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.orbit_timer = None
        self.get_orbitinfo_ondisplay = None
        self.scroller_widget_layout = None
        self.orbitinfo_window_layout1 = None
        self.orbitinfo_window = None
        self.timer_state = False
        self.timescope_label = None
        self.scale_state = False
        self.scale_scope = None
        self.scale_slider = None
        self.firstdotcoo = None
        self.seconddotcoo = None
        self.measuring_window = None
        self.distance = None
        self.angle = None
        self.timer_scope = None
        self.main_statsdock_link = StatsDock()

        self.setWindowTitle('Astro Balls')
        self.setWindowIcon(QIcon('./images/Astro Balls Icon.png'))
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.game_widget = PyGameWidget(self.main_statsdock_link)
        layout = QVBoxLayout(central_widget)
        self.game_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.game_widget)
        self.resize(1200, 600)

        self.game_widget.measuring_updater_signal.connect(self.update_measuringtape)

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
        self.orbits_action = QWidgetAction(view_menu)
        self.orbits_action = QWidgetAction(view_menu)
        if self.game_widget.is_showingorbits is False:
            self.orbits_view, self.orbits_state = self.customcheckbox(func_name='Orbits', method=self.showorbits)
            self.orbits_action.setDefaultWidget(self.orbits_view)
        view_menu.addAction(self.orbits_action)
        self.scale_action = QWidgetAction(view_menu)
        if self.scale_state is False:
            self.scale_view, self.scale_state = self.customcheckbox(func_name='Scale', method=self.scaleslider)
            self.scale_action.setDefaultWidget(self.scale_view)
        view_menu.addAction(self.scale_action)
        self.timer_action = QWidgetAction(view_menu)
        if self.timer_state is False:
            self.timer_view, self.timer_state = self.customcheckbox(func_name='Time', method=self.timerscope)
            self.timer_action.setDefaultWidget(self.timer_view)
        view_menu.addAction(self.timer_action)
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
        menu.addMenu(view_menu)

        tool_menu = QMenu('&Outils')
        menu.addMenu(tool_menu)
        mt = QAction('&Mesuring Tape', parent=self)
        mt.setIcon(QIcon('images/menubar symbol/ruler.png'))
        mt.triggered.connect(self.measuringtape)
        tool_menu.addAction(mt)
        of = QAction('&Orbit Info', parent=self)
        of.triggered.connect(self.showorbitinfo)
        tool_menu.addAction(of)

        help_menu = QMenu('&Aide')
        keybinds_action = QAction('&Raccourcis clavier', parent=self)
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
        apropos_action = QAction('À propos', parent=self)
        apropos_action.setIcon(QIcon('images/menubar symbol/question-mark.png'))
        apropos_action.triggered.connect(self.apropos)
        apropos_action.setShortcut('Alt+H')
        help_menu.addAction(apropos_action)
        menu.addMenu(help_menu)

        self.dragndrop = DragNDrop()
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.dragndrop)
        self.addDockWidget(Qt.RightDockWidgetArea, self.main_statsdock_link)

    def resizeEvent(self, event):
        self.game_widget.window_resize_event(self.width(), self.height())
        super().resizeEvent(event)

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
        self.splitDockWidget(self.main_statsdock_link, self.timer_scope, Qt.Vertical)

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
        self.scale_scope.setWindowTitle('Scale Slider')

        self.scale_slider = QSlider(Qt.Orientation.Horizontal, parent=scale_scope_container)
        self.scale_slider.setRange(1, 100)
        self.scale_slider.setValue(20)
        self.scale_slider.setTickInterval(5)
        self.scale_slider.setSingleStep(5)
        self.scale_slider.setTickPosition(QSlider.TicksAbove)
        scale_scope_widget.addWidget(self.scale_slider, 0, 0, 1, 2)
        self.scale_slider.valueChanged.connect(self.update_scale_slider)
        self.scale_slider.valueChanged.connect(self.game_widget.scale_interactive)
        self.scale_slider_label = QLabel('', scale_scope_container)

        backward_button = QPushButton('Backward')
        backward_button.clicked.connect(self.backward_scale_slider)
        scale_scope_widget.addWidget(backward_button, 1, 0)

        forward_button = QPushButton('Forward')
        forward_button.clicked.connect(self.forward_scale_slider)
        scale_scope_widget.addWidget(forward_button, 1, 1)

        self.scale_scope.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.scale_scope.setFixedHeight(120)
        self.splitDockWidget(self.main_statsdock_link, self.scale_scope, Qt.Vertical)

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
        x_pos = 16 / 2 + ratio * (self.scale_slider.width() - 16)
        x_pos_parent = self.scale_slider.x() + x_pos - (self.scale_slider.width() // 2)
        y_pos = self.scale_slider.y() - 15
        self.scale_slider.move(int(x_pos_parent), int(y_pos))

    def backward_scale_slider(self):
        self.scale_slider.setValue(self.scale_slider.value() - 1)

    def forward_scale_slider(self):
        self.scale_slider.setValue(self.scale_slider.value() + 1)

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

#DEMO
    def mimir(self):
        info_window = QDialog(parent=self)
        info_window.setFixedSize(650, 500)
        info_window.setWindowTitle('Mímisbrunnr')
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
                                                                            Qt.KeepAspectRatio,Qt.SmoothTransformation)
        l_pixmap_newton1 = QLabel(parent=newton1tab)
        l_pixmap_newton1.setFrameStyle(QFrame.Shape.Panel)
        l_pixmap_newton1.setFixedSize(200, 280)
        l_pixmap_newton1.setPixmap(pixmap_newton1)
        l_pixmap_newton1.move(420, 95)
        i_n1_label = QLabel("Newton's first law states that an object in motion will remain in motion\nindefinitely as "
                            "long as there is no opposing force. Similarly, an object at\nrest will remain at rest "
                            "indefinitely as long as no force is applied to it.", parent=newton1tab)
        i_n1_label.setFixedSize(390, 50)
        i_n1_label.move(20, 100)

        im_n1_label = QLabel("Sir Isaac Newton\nBy Godfrey Kneller\n1689", parent=newton1tab)
        im_n1_label.setFixedSize(100, 100)
        im_n1_label.move(470, 350)
        newton1tab.setLayout(newton1tab_layout)
        info_tabs.addTab(newton1tab, "Newton's First Law")

        newton2tab = QWidget()
        newton2tab_layout = QGridLayout()
        newton2tab.setLayout(newton2tab_layout)
        info_tabs.addTab(newton2tab, "Newton's Second Law")

        newton3tab = QWidget()
        newton3tab_layout = QGridLayout()
        newton3tab.setLayout(newton3tab_layout)
        info_tabs.addTab(newton3tab, "Newton's Third Law")

        kflopmtab = QWidget()
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

        about_icon = QPixmap('./images/Astro Balls Icon.png').scaled(170, 170, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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

    def showorbits(self, checked):
        self.game_widget.is_showingorbits = checked

    def showorbitinfo(self):
        if self.orbitinfo_window is None:
            self.orbitinfo_window = QDialog(parent=self)
            self.orbitinfo_window.setWindowTitle('Orbits')
            self.orbitinfo_window.setFixedSize(380, 280)
            self.orbitinfo_window_layout1 = QGridLayout(self.orbitinfo_window)
            self.orbitinfo_window_layout1.setContentsMargins(2, 2, 2, 2)

            scroller = QScrollArea()
            scroller.setFrameShape(QFrame.NoFrame)
            scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroller.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroller.setWidgetResizable(True)
            self.orbitinfo_window_layout1.addWidget(scroller, 0, 1)

            scroller_widget = QWidget()
            self.scroller_widget_layout = QVBoxLayout(scroller_widget)
            self.scroller_widget_layout.setSpacing(4)
            scroller.setWidget(scroller_widget)

            orbit_helper = QPushButton('Help')
            orbit_helper.setCheckable(True)
            orbit_helper.setToolTip('Pre-configures the sufficient velocity to maintain circular orbit')
            orbit_helper.clicked.connect(self.game_widget.kepler_orbit_helper)
            self.orbitinfo_window_layout1.addWidget(orbit_helper, 1, 0)

            close_button = QPushButton('Close')
            close_button.clicked.connect(self.orbitinfo_window.close)
            close_button.clicked.connect(self.when_showorbit_closed)
            self.orbitinfo_window_layout1.addWidget(close_button, 1, 1)

            panel = QFrame()
            panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
            panel_layout = QGridLayout()
            panel.setLayout(panel_layout)
            panel_layout.setSpacing(3)
            self.orbitinfo_window_layout1.addWidget(panel, 0, 0)

            l_eccentricity_toggler = QLabel('Eccentricity: ')
            panel_layout.addWidget(l_eccentricity_toggler, 0, 0)
            self.s_eccentricity_toggler = QSlider(Qt.Orientation.Horizontal, parent=self)
            self.s_eccentricity_toggler.setMinimum(0)
            self.s_eccentricity_toggler.setMaximum(100)
            self.s_eccentricity_toggler.setSingleStep(1)
            self.s_eccentricity_toggler.setTickPosition(QSlider.TicksAbove)
            panel_layout.addWidget(self.s_eccentricity_toggler, 2, 0, 1, 2)
            self.b_eccentricity_toggler = QDoubleSpinBox()
            self.b_eccentricity_toggler.lineEdit().setMaximumWidth(50)
            self.b_eccentricity_toggler.setMaximumWidth(90)
            panel_layout.addWidget(self.b_eccentricity_toggler, 0, 1)

            l_semimajor_toggler = QLabel('Velocity: ')
            panel_layout.addWidget(l_semimajor_toggler, 3, 0)
            self.s_semimajor_toggler = QSlider(Qt.Orientation.Horizontal, parent=self)
            self.s_semimajor_toggler.setMinimum(0)
            self.s_semimajor_toggler.setMaximum(100)
            self.s_semimajor_toggler.setSingleStep(1)
            self.s_semimajor_toggler.setTickPosition(QSlider.TicksAbove)
            panel_layout.addWidget(self.s_semimajor_toggler, 4, 0, 1, 2)
            self.b_semimajor_toggler = QDoubleSpinBox()
            self.b_semimajor_toggler.lineEdit().setMaximumWidth(50)
            self.b_semimajor_toggler.setMaximumWidth(90)
            panel_layout.addWidget(self.b_semimajor_toggler, 3, 1)

            l_posorbit_toggler = QLabel('Orbital Position: ', parent=panel)
            l_posorbit_toggler.move(10, 107)
            self.s_posorbit_toggler = QDial(parent=panel)
            self.s_posorbit_toggler.setMinimum(0)
            self.s_posorbit_toggler.setMaximum(360)
            self.s_semimajor_toggler.setValue(0)
            self.s_posorbit_toggler.setMaximumWidth(90)
            self.s_posorbit_toggler.setSingleStep(1)
            self.s_posorbit_toggler.setWrapping(True)
            self.s_posorbit_toggler.valueChanged.connect(self.game_widget.orbital_position_editor)
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

            l_orbitcolor_toggler = QLabel('Orbit Color: ')
            panel_layout.addWidget(l_orbitcolor_toggler, 6, 0)
            self.color_button = QPushButton('Color Palette')
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
                    configure_orbit_button.setProperty('index', k)
                    configure_orbit_button.clicked.connect(self.game_widget.orbit_editor)
                    panel_layout.addWidget(configure_orbit_button)
                    ondisplay_structure = {'Name': planet_label, 'epstein': epstein_label,
                                           'semimajor': semimajoraxis_label, 'velocity': velocity_label}
                    self.scroller_widget_layout.addWidget(panel)
                    self.get_orbitinfo_ondisplay.append(ondisplay_structure)

            for k, l in enumerate(self.game_widget.kepler()):
                ondisplay = self.get_orbitinfo_ondisplay[k]
                ondisplay['Name'].setText(l['planet']['Name'])
                ondisplay['epstein'].setText(f'ε: {round(l['epsilon'], 3)}')
                ondisplay['semimajor'].setText(f'Semi-major(a): {round(l['a'], 3)}')
                ondisplay['velocity'].setText(f'Velocity: {round(l['vel'].magnitude(), 1)}')

            for k, l in enumerate(self.game_widget.kepler()):
                ondisplay = self.get_orbitinfo_ondisplay[k]
                self.get_orbitinfo_ondisplay[k]['Name'].setText(l['planet']['nom'])
                ondisplay['epstein'].setText(f'ε: {round(l['epsilon'], 3)}')
                ondisplay['semimajor'].setText(f'Semi-major(a): {round(l['a'], 3)}')

    def when_showorbit_closed(self):
        self.orbit_timer.stop()
        self.orbitinfo_window = None

    def orbiteditor_color(self):
        color_window = QColorDialog.getColor()
        if color_window.isValid():
            color = color_window.name()
            self.color_button.setStyleSheet(
                f"""QPushButton {{border: 1px solid #8a8a8a; padding: 2px; background-color: {color};}}""")

    def keybinds(self):
        self.settings()

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
    ww = WelcomeWindow()
    ww.show()
    app.exec()

    if ww.wwsc_simulation is not None:
        mw = MainWindowFrame()
        mw.show()
        sys.exit(app.exec())