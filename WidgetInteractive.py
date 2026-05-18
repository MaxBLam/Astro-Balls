from PySide6.QtCore import QMimeData, Qt, QRegularExpression
from PySide6.QtGui import QFont, QDrag, QRegularExpressionValidator, QIcon
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDockWidget, QHBoxLayout, QLabel, QFrame, QDoubleSpinBox,
                               QScrollArea, QToolBar, QTabWidget, QLineEdit, QPushButton, QSizePolicy)


class QtPlanetLabel(QLabel):
    def __init__(self, name):
        super().__init__(name)
        self.planet_name = name
        self.setStyleSheet('padding: 6px; background-color: gray;')

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            dragging = QDrag(self)
            mime = QMimeData()
            mime.setText(self.planet_name)
            dragging.setMimeData(mime)
            dragging.exec(Qt.DropAction.CopyAction)


class DragNDrop(QToolBar):
    def __init__(self):
        super().__init__("Drag-and-Drop Menu")

        tabs = QTabWidget()
        tabs.setMovable(False)

        planet_tab = QWidget()
        planet_layout = QHBoxLayout()
        for i in ['Mercure', 'Vénus', 'Terre', 'Mars', 'Jupiter', 'Saturne', 'Uranus', 'Neptune']:
            planet_layout.addWidget(QtPlanetLabel(i))
        planet_tab.setLayout(planet_layout)
        tabs.addTab(planet_tab, QIcon('images/dragndrop_image/venus.png'), 'Planets')

        ns_tabs = QWidget()
        ns_layout = QHBoxLayout()
        for j in ['Lune', 'Europe', 'Io', 'Callisto', 'Ganymede', 'Titan', 'Triton', 'Comète 10km', 'Comète 50km', 'Comète 200km']:
            ns_layout.addWidget(QtPlanetLabel(j))
        ns_tabs.setLayout(ns_layout)
        tabs.addTab(ns_tabs, QIcon('images/dragndrop_image/moon.png'), 'Satellites Naturels')

        star_tabs = QWidget()
        star_layout = QHBoxLayout()
        for k in ['Soleil', 'Arcturus', 'Bételgeuse', 'Sirius B', 'Rigel']:
            star_layout.addWidget(QtPlanetLabel(k))
        star_tabs.setLayout(star_layout)
        tabs.addTab(star_tabs, QIcon('images/dragndrop_image/sun.png'), 'Étoiles')

        autres_tabs = QWidget()
        autres_layout = QHBoxLayout()
        for l in ['TON 618', 'Phoenix A', 'Hubble', 'Your Mom']:
            autres_layout.addWidget(QtPlanetLabel(l))
        autres_tabs.setLayout(autres_layout)
        tabs.addTab(autres_tabs, QIcon('images/dragndrop_image/satellite.png'), 'Autres')

        self.addWidget(tabs)
        self.setFixedHeight(110)


class StatsDock(QDockWidget):
    def __init__(self):
        super().__init__("StatDock")
        self.body_label = None

        widget = QWidget()
        layout = QVBoxLayout()
        upper_panel = QFrame()
        upper_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        upper_panel.setFixedSize(400, 900)
        layout.addWidget(upper_panel)

        self.body_label = QLabel(upper_panel)
        self.body_label.setText("None")
        self.body_label.setFixedWidth(250)
        self.body_label.setFixedHeight(100)
        self.body_label_txt = QFont()
        self.body_label_txt.setPointSize(20)
        self.body_label_txt.setBold(True)
        self.body_label_txt.setItalic(True)
        self.body_label.setFont(self.body_label_txt)
        self.body_label.move(20, 40)

        self.img_label = QLabel(upper_panel)
        self.img_label.setFixedSize(180, 180)
        self.img_label.move(200, 0)

        line_sep = QFrame(upper_panel)
        line_sep.setFrameStyle(QFrame.Shape.HLine)
        line_sep.setStyleSheet('background-color: #444444')
        line_sep.setFixedHeight(1)
        line_sep.setFixedWidth(270)
        line_sep.move(50, 180)

        corp_label = QLabel('CORP', upper_panel)
        corp_label.move(10, 170)

        self.body_type = QLabel(upper_panel)
        self.body_type.setText(f"Type: ")
        type_label_txt = QFont()
        type_label_txt.setPointSize(12)
        self.body_type.setFont(type_label_txt)
        self.body_type.move(20, 200)

        self.body_type_dis = QLabel(upper_panel)
        self.body_type_dis.setText(f"None")
        self.body_type_dis.setFixedWidth(200)
        type_label_txt_dis = QFont()
        type_label_txt_dis.setPointSize(12)
        self.body_type_dis.setFont(type_label_txt)
        self.body_type_dis.move(70, 200)

        self.surface_label = QLabel(upper_panel)
        self.surface_label.setText(f"Composition Surface: ")
        surface_label_txt = QFont()
        surface_label_txt.setPointSize(12)
        self.surface_label.setFont(surface_label_txt)
        self.surface_label.move(20, 230)

        self.surface_label_dis = QLabel(upper_panel)
        self.surface_label_dis.setText(f"None")
        self.surface_label_dis.setFixedWidth(200)
        surface_label_txt_dis = QFont()
        surface_label_txt_dis.setPointSize(12)
        self.surface_label_dis.setFont(type_label_txt)
        self.surface_label_dis.move(180, 230)

        self.age_label = QLabel(upper_panel)
        self.age_label.setText(f"Âge: ")
        age_label_txt = QFont()
        age_label_txt.setPointSize(12)
        self.age_label.setFont(age_label_txt)
        self.age_label.move(20, 260)

        self.age_label_dis = QLabel(upper_panel)
        self.age_label_dis.setText(f"None")
        self.surface_label_dis.setFixedWidth(200)
        age_label_txt_dis = QFont()
        age_label_txt_dis.setPointSize(12)
        self.age_label_dis.setFont(age_label_txt_dis)
        self.age_label_dis.move(60, 260)

        self.rotation_label = QLabel(upper_panel)
        self.rotation_label.setText(f"Température: ")
        rotation_label_txt = QFont()
        rotation_label_txt.setPointSize(12)
        self.rotation_label.setFont(rotation_label_txt)
        self.rotation_label.move(20, 290)

        self.rotation_label_dis = QLabel(upper_panel)
        self.rotation_label_dis.setText(f"None")
        self.surface_label_dis.setFixedWidth(200)
        rotation_label_txt_dis = QFont()
        rotation_label_txt_dis.setPointSize(12)
        self.rotation_label_dis.setFont(rotation_label_txt_dis)
        self.rotation_label_dis.move(120, 290)

        line_sep2 = QFrame(upper_panel)
        line_sep2.setFrameStyle(QFrame.Shape.HLine)
        line_sep2.setStyleSheet('background-color: #444444')
        line_sep2.setFixedHeight(1)
        line_sep2.setFixedWidth(211)
        line_sep2.move(110, 340)

        corp_label = QLabel('CONFIGURATION', upper_panel)
        corp_label.move(10, 330)

        self.mass_label = QLabel(upper_panel)
        self.mass_label.setText(f"Masse: ")
        self.mass_label.setFixedWidth(200)
        mass_label_txt = QFont()
        mass_label_txt.setPointSize(12)
        self.mass_label.setFont(mass_label_txt)
        self.mass_label.move(20, 360)

        self.mass_edit = QLineEdit(upper_panel)
        regex = QRegularExpression(r"[0-9]+(\.[0-9]+)?e[+-]?[0-9]+")
        validator = QRegularExpressionValidator(regex)
        self.mass_edit.setValidator(validator)
        self.mass_edit.setStyleSheet(""" QLineEdit {border: 1px solid grey;}""")
        self.mass_edit.move(80, 361)

        self.apply_button_mass = QPushButton('Appliquer', upper_panel)
        self.apply_button_mass.setFixedSize(90, 20)
        self.apply_button_mass.setStyleSheet(""" QPushButton {border: 1px solid grey;}""")
        self.apply_button_mass.move(200, 361)

        self.rad_label = QLabel(upper_panel)
        self.rad_label.setText(f"Rayon: ")
        self.rad_label.setFixedWidth(320)
        rad_label_txt = QFont()
        rad_label_txt.setPointSize(12)
        self.rad_label.setFont(mass_label_txt)
        self.rad_label.move(20, 390)

        self.rad_edit = QLineEdit(upper_panel)
        regex = QRegularExpression(r"[0-9]+(\.[0-9]+)?e[+-]?[0-9]+")
        validator = QRegularExpressionValidator(regex)
        self.rad_edit.setValidator(validator)
        self.rad_edit.setStyleSheet(""" QLineEdit {border: 1px solid grey;}""")
        self.rad_edit.move(80, 391)

        self.apply_button_rayon = QPushButton('Appliquer', upper_panel)
        self.apply_button_rayon.setFixedSize(90, 20)
        self.apply_button_rayon.setStyleSheet(""" QPushButton {border: 1px solid grey;}""")
        self.apply_button_rayon.move(200, 391)

        self.elp_label = QLabel(upper_panel)
        self.elp_label.setText(f"Ellipse: ")
        self.elp_label.setFixedWidth(200)
        elp_label_txt = QFont()
        elp_label_txt.setPointSize(12)
        self.elp_label.setFont(mass_label_txt)
        self.elp_label.move(20, 420)

        self.ellipse_edit = QDoubleSpinBox(upper_panel)
        self.ellipse_edit.lineEdit().setMaximumWidth(50)
        self.ellipse_edit.setFixedWidth(109)
        self.ellipse_edit.setRange(0, 1)
        self.ellipse_edit.setDecimals(1)
        self.ellipse_edit.setValue(1.0)
        self.ellipse_edit.setSingleStep(0.1)
        self.ellipse_edit.setStyleSheet(""" QDoubleSpinBox {border: 1px solid grey;}""")
        self.ellipse_edit.move(80, 421)

        self.apply_button_ellipse = QPushButton('Appliquer', upper_panel)
        self.apply_button_ellipse.setFixedSize(90, 20)
        self.apply_button_ellipse.setStyleSheet(""" QPushButton {border: 1px solid grey;}""")
        self.apply_button_ellipse.move(200, 421)

        self.mom_label = QLabel(upper_panel)
        self.mom_label.setText(f"Vitesse: ")
        self.mom_label.setFixedWidth(200)
        self.mom_label.setFont(mass_label_txt)
        self.mom_label.move(20, 456)

        self.mom_edit = QDoubleSpinBox(upper_panel)
        self.mom_edit.lineEdit().setMaximumWidth(50)
        self.mom_edit.setFixedWidth(109)
        self.mom_edit.setRange(0, 100)
        self.mom_edit.setDecimals(1)
        self.mom_edit.setValue(1)
        self.mom_edit.setSingleStep(1)
        self.mom_edit.setStyleSheet(""" QDoubleSpinBox {border: 1px solid grey;}""")
        self.mom_edit.move(80, 456)

        self.apply_button_mom = QPushButton('Appliquer', upper_panel)
        self.apply_button_mom.setFixedSize(90, 20)
        self.apply_button_mom.setStyleSheet(""" QPushButton {border: 1px solid grey;}""")
        self.apply_button_mom.move(200, 456)

        widget.setLayout(layout)
        scroller = QScrollArea()
        scroller.setFrameShape(QFrame.Shape.NoFrame)
        scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroller.setWidgetResizable(True)
        scroller.setWidget(widget)
        scroller.setMaximumWidth(350)
        scroller.setMinimumWidth(100)
        scroller.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setWidget(scroller)
