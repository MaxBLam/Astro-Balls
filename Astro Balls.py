import sys
import pygame
from PySide6.QtGui import QAction, Qt, QFont, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMenu, QPushButton, QVBoxLayout, QDockWidget, \
    QHBoxLayout, QWidgetAction, QCheckBox, QLabel, QDialog, QGridLayout, QFrame, QComboBox, QSpinBox, QDoubleSpinBox, \
    QScrollArea, QScrollBar, QStackedLayout, QSizePolicy, QSlider, QTabWidget

from PyGameWidget import PyGameWidget
from WelcomeWindow import WelcomeWindow
from WidgetInteractive import DragNDrop, StatsDock


class MainWindowFrame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer_state = False
        self.timescope_label = None
        self.setWindowTitle('Astro Balls')
        self.setWindowIcon(QIcon('./images/Astro Balls Icon.png'))
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.game_widget = PyGameWidget()
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
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.dragndrop)
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
        self.time_slider.setRange(1, 100)
        self.time_slider.setValue(25)
        self.time_slider.setTickInterval(25)
        self.time_slider.setSingleStep(25)
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
        self.time_slider.setValue(self.time_slider.value() - 25)

    def forward_timescope(self):
        self.time_slider.setValue(self.time_slider.value() + 25)

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
    ww = WelcomeWindow()
    ww.show()
    app.exec()

    if ww.wwsc_simulation is not None:
        mw = MainWindowFrame()
        mw.show()
        sys.exit(app.exec())
