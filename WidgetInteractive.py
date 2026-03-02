from PySide6.QtCore import QMimeData
from PySide6.QtGui import Qt, QFont, QDrag
from PySide6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QDockWidget,QHBoxLayout, QLabel, QGridLayout, QFrame,
                               QComboBox, QDoubleSpinBox, QScrollArea, QToolBar, QTabWidget)


class QtPlanetLabel(QLabel):
    def __init__(self, name):
        super().__init__(name)
        self.planet_name = name
        self.setStyleSheet('padding: 6px; background-color: gray;')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            dragging = QDrag(self)
            mime = QMimeData()
            mime.setText(self.planet_name)
            dragging.setMimeData(mime)
            dragging.exec(Qt.CopyAction)


class DragNDrop(QToolBar):
    def __init__(self):
        super().__init__("Drag-and-Drop Menu")

        tabs = QTabWidget()
        tabs.setMovable(False)

        planet_tab = QWidget()
        planet_layout = QHBoxLayout()
        for i in ['Earth', 'Mars', 'Jupiter']:
            planet_layout.addWidget(QtPlanetLabel(i))
        planet_tab.setLayout(planet_layout)
        tabs.addTab(planet_tab, 'Planets')

        ns_tabs = QWidget()
        ns_layout = QHBoxLayout()
        for j in ['Moon']:
            ns_layout.addWidget(QtPlanetLabel(j))
        ns_tabs.setLayout(ns_layout)
        tabs.addTab(ns_tabs, 'Natural Satellites')

        star_tabs = QWidget()
        star_layout = QHBoxLayout()
        for k in ['Sun']:
            star_layout.addWidget(QtPlanetLabel(k))
        star_tabs.setLayout(star_layout)
        tabs.addTab(star_tabs, 'Stars')

        self.addWidget(tabs)
        self.setFixedHeight(100)


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