from PySide6.QtCore import QMimeData, Qt, QRegularExpression
from PySide6.QtGui import QFont, QDrag, QRegularExpressionValidator
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDockWidget, QHBoxLayout, QLabel, QGridLayout, QFrame,
                               QComboBox, QDoubleSpinBox, QScrollArea, QToolBar, QTabWidget, QLineEdit, QPushButton,
                               QSpinBox, QSizePolicy)


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
        tabs.addTab(planet_tab, 'Planets')

        ns_tabs = QWidget()
        ns_layout = QHBoxLayout()
        for j in ['Lune', 'Europe', 'Io', 'Callisto', 'Ganymede', 'Titan', 'Triton', 'Comète 10km', 'Comète 50km', 'Comète 200km']:
            ns_layout.addWidget(QtPlanetLabel(j))
        ns_tabs.setLayout(ns_layout)
        tabs.addTab(ns_tabs, 'Satellites Naturels')

        star_tabs = QWidget()
        star_layout = QHBoxLayout()
        for k in ['Soleil', 'Arcturus', 'Bételgeuse', 'Sirius B', 'Rigel']:
            star_layout.addWidget(QtPlanetLabel(k))
        star_tabs.setLayout(star_layout)
        tabs.addTab(star_tabs, 'Étoiles')

        autres_tabs = QWidget()
        autres_layout = QHBoxLayout()
        for l in ['TON 618', 'Phoenix A', 'Hubble', 'Your Mom']:
            autres_layout.addWidget(QtPlanetLabel(l))
        autres_tabs.setLayout(autres_layout)
        tabs.addTab(autres_tabs, 'Autres')

        self.addWidget(tabs)
        self.setFixedHeight(100)


class StatsDock(QDockWidget):
    def __init__(self):
        super().__init__("Statistics")
        self.body_label = None

        widget = QWidget()
        layout = QVBoxLayout()
#TODO LE SPACING DU TEXTE EST CHIANT
        upper_panel = QFrame()
        upper_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        upper_panel_layout = QGridLayout()
        upper_panel.setLayout(upper_panel_layout)
        layout.addWidget(upper_panel)

        self.body_label = QLabel()
        self.body_label.setText("None")
        body_label_txt = QFont()
        body_label_txt.setPointSize(20)
        body_label_txt.setBold(True)
        body_label_txt.setItalic(True)
        self.body_label.setFont(body_label_txt)
        upper_panel_layout.addWidget(self.body_label, 0, 0, 1, 3)

        self.body_type = QLabel()
        self.body_type.setText(f"Type: ")
        upper_panel_layout.addWidget(self.body_type, 1, 0, 1, 2)

        self.surface_label = QLabel()
        self.surface_label.setText(f"Composition Surface: ")
        self.surface_label.setWordWrap(True)
        upper_panel_layout.addWidget(self.surface_label, 2, 0, 1, 2)

        self.age_label = QLabel()
        self.age_label.setText(f"Âge: ")
        self.age_label.setWordWrap(True)
        upper_panel_layout.addWidget(self.age_label, 3, 0, 1, 2)

        self.rotation_label = QLabel()
        self.rotation_label.setText(f"Température: ")
        self.rotation_label.setWordWrap(True)
        upper_panel_layout.addWidget(self.rotation_label, 4, 0, 1, 2)

        mid_panel = QFrame()
        mid_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        mid_panel_layout = QVBoxLayout()
        mid_panel.setLayout(mid_panel_layout)
        layout.addWidget(mid_panel)

        config_label = QLabel()
        config_label.setText("CONFIGURATION")
        config_label_txt = QFont()
        config_label_txt.setPointSize(10)
        config_label_txt.setBold(True)
        config_label_txt.setItalic(True)
        config_label.setFont(config_label_txt)
        mid_panel_layout.addWidget(config_label)


        h_layout1 = QHBoxLayout()
        self.mass_label = QLabel('Masse: ')
        mid_panel_layout.addWidget(self.mass_label)
        self.mass_edit = QLineEdit()
        regex = QRegularExpression(r"[0-9]+(\.[0-9]+)?e[+-]?[0-9]+")
        validator = QRegularExpressionValidator(regex)
        self.mass_edit.setValidator(validator)
        self.mass_edit.setStyleSheet(""" QLineEdit {border: 1px solid grey;}""")
        self.apply_button_mass = QPushButton('Appliquer')
        self.apply_button_mass.setStyleSheet(""" QPushButton {border: 1px solid grey;}""")
        h_layout1.addWidget(self.mass_edit)
        h_layout1.addWidget(self.apply_button_mass)
        mid_panel_layout.addLayout(h_layout1)

        h_layout2 = QHBoxLayout()
        self.rayon_label = QLabel('Rayon: ')
        mid_panel_layout.addWidget(self.rayon_label)
        self.rayon_edit = QLineEdit()
        regex = QRegularExpression(r"[0-9]+")
        validator = QRegularExpressionValidator(regex)
        self.rayon_edit.setValidator(validator)
        self.rayon_edit.setStyleSheet(""" QLineEdit {border: 1px solid grey;}""")
        self.apply_button_rayon = QPushButton('Appliquer')
        self.apply_button_rayon.setStyleSheet(""" QPushButton {border: 1px solid grey;}""")
        h_layout2.addWidget(self.rayon_edit)
        h_layout2.addWidget(self.apply_button_rayon)
        mid_panel_layout.addLayout(h_layout2)

        low_panel = QFrame()
        low_panel.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
        low_panel.setStyleSheet('background-color: #2c2c2c; border-radius: 5px; overflow: hidden')
        low_panel_layout = QVBoxLayout()
        low_panel.setLayout(low_panel_layout)
        layout.addWidget(low_panel)

        h_layout3 = QHBoxLayout()
        self.ellipse_label = QLabel('Facteur Ellipse: ', parent=self)
        low_panel_layout.addWidget(self.ellipse_label)
        #TODO DOUBLE SPIN BOX EST BUGGÉ
        self.ellipse_edit = QDoubleSpinBox()
        self.ellipse_edit.lineEdit().setMaximumWidth(50)
        self.ellipse_edit.setRange(0, 1)
        self.ellipse_edit.setDecimals(1)
        self.ellipse_edit.setValue(1.0)
        self.ellipse_edit.setSingleStep(0.1)
        self.ellipse_edit.setStyleSheet(""" QDoubleSpinBox {border: 1px solid grey;}""")
        self.apply_button_ellipse = QPushButton('Appliquer')
        self.apply_button_ellipse.setStyleSheet(""" QPushButton {border: 1px solid grey;}""")
        h_layout3.addWidget(self.ellipse_edit)
        h_layout3.addWidget(self.apply_button_ellipse)
        low_panel_layout.addLayout(h_layout3)

        widget.setLayout(layout)
        scroller = QScrollArea()
        scroller.setFrameShape(QFrame.Shape.NoFrame)
        scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroller.setWidgetResizable(True)
        scroller.setWidget(widget)
        scroller.setFixedWidth(217)
        self.setWidget(scroller)
