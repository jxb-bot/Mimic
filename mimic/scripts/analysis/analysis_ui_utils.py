#!usr/bin/env python
# -*- coding: utf-8 -*-


import general_utils
import ui_utils

reload(general_utils)
reload(ui_utils)

# Use Qt.py to provide for back-compatibility from PySide2 to PySide
from extern.Qt import QtWidgets
from extern.Qt import QtGui
from extern.Qt import QtCore
from extern.Qt import QtCompat

from extern import pyqtgraph as pg

# create a font
FONT = QtGui.QFont()
FONT.setPointSize(12)
FONT.setBold = True


class Toggle(QtWidgets.QPushButton):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        super(Toggle, self).__init__(*args, **kwargs)

        icon_directory = general_utils.get_mimic_dir()
        self.toggle_off_path = icon_directory + '/icons/toggle_button_off.png'
        self.toggle_on_path = icon_directory + '/icons/toggle_button_on.png'
        
        self.setCheckable(True)
        self.setChecked(False)

        self.setFixedWidth(26)
        self.setFixedHeight(19)
        self.setStyleSheet('QPushButton {background-image: url('
                                       + self.toggle_off_path + '); ' \
                                        'border: none; ' \
                                        'background-repeat: no-repeat;}' 
                         + 'QPushButton:checked {background-image: url(' 
                                       + self.toggle_on_path + '); ' \
                                        'border: none; '\
                                        'background-repeat: no-repeat;}')
        self.setFlat(False)


class DataToggle(Toggle):
    """
    """
    def __init__(self, plot_widget, data_type, *args, **kwargs):
        """
        """
        super(DataToggle, self).__init__(*args, **kwargs)

        self.plot_widget = plot_widget
        self.type = data_type  # 'axis' or 'derivative'
        self.toggled.connect(self.update)

    def update(self):
        """
        """
        self.plot_widget.update(self)
        if self.isChecked():
            print self.accessibleName() + ' is checked'
        else:
            print self.accessibleName() + ' is unchecked'


class IsolateToggle(Toggle):
    """
    """
    def __init__(self, toggle_group, *args, **kwargs):
        """
        """
        super(IsolateToggle, self).__init__(*args, **kwargs)

        self.toggle_group = toggle_group

        self.toggled.connect(self.update)

    def update(self):
        """
        """
        if self.isChecked():
            # If the toggle is turned on, turn off all of the toggles in the 
            # group, set the group to exclusive, then turn on a single toggle
            
            # Turn off group exclusivity as this is the only way to uncheck
            # Every button
            self.toggle_group.setExclusive(False)

            # Get a list of active toggles
            toggles = self.toggle_group.buttons()

            # Break this out into a utility function?
            active_toggles = [toggle for toggle in toggles if toggle.isChecked() == True]

            # Turn off all active toggles
            for toggle in active_toggles:
                toggle.setChecked(False)
            
            # Set the first active toggle back on
            try:
                active_toggles[0].setChecked(True)
            except IndexError:
                # No toggles were active
                pass

            # Set the toggle group back to exclusive
            self.toggle_group.setExclusive(True)
        else:
            # If toggle is turned off, set the toggle group to inexclusive
            self.toggle_group.setExclusive(False)


class LimitsToggle(Toggle):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        super(LimitsToggle, self).__init__(*args, **kwargs)

        self.toggled.connect(self.update)

    def update(self):
        """
        """
        if self.isChecked():
            print self.accessibleName() + ' is checked'
        else:
            print self.accessibleName() + ' is unchecked'


class UtilityButton(QtWidgets.QPushButton):
    """
    """
    def __init__(self, label, data_control_widget, *args, **kwargs):
        """
        """
        super(UtilityButton, self).__init__(label, *args, **kwargs)
        
        self.button_type = label
        self.data_control_widget = data_control_widget
        self.toggles = data_control_widget.toggles
        self.toggle_buttons = data_control_widget.toggle_group.buttons()
        self.toggle_group = data_control_widget.toggle_group

        self.clicked.connect(self.update)
    
    def update(self):
        """
        """
        if self.button_type == 'Show All':
            self.show_all()
        else:
            self.hide_all()

    def show_all(self):
        """
        """

        # Make sure the Isolate toggle is turned off to enable all of the
        # data toggles to be turned on
        self.toggles['Isolate'].setChecked(False)

        # Turn on all of the inactive data toggles
        inactive_toggles = [toggle for toggle in self.toggle_buttons if toggle.isChecked() == False]

        for toggle in inactive_toggles:
            toggle.setChecked(True)

    def hide_all(self):
        """
        """
        # Make a reference for the state of the isolate toggle so we can
        # maintain its state later
        initial_isolate_toggle_state = self.toggles['Isolate'].isChecked()

        # Turn off the Isolate toggle if necessary, which sets the toggle
        # group's state to inexclusive, which allows us to turn off all of
        # the toggles
        self.toggles['Isolate'].setChecked(False)

        # Turn off all of the active data toggles
        active_toggles = [toggle for toggle in self.toggle_buttons if toggle.isChecked() == True]

        for toggle in active_toggles:
            toggle.setChecked(False)

        # Set the state of the isolate toggle back to its initial state
        self.toggles['Isolate'].setChecked(initial_isolate_toggle_state)


class DataControlWidget(QtWidgets.QWidget):
    """
     --------------------------------
    |   --------------------------   |
    |  |   --------------------   |  |
    W  C  |  Label 1 | Toggle  |  |  |
    I  O  G  Label 2 | Toggle  |  |  |
    D  L  R  Label 3 | Toggle  |  |  |
    G  U  I        ...         |  |  |
    E  M  D        ...         |  |  |
    T  N  |  Label n | Toggle  |  |  |
    |  |   --------------------   |  |
    |  |                          |  |
    |  |     Isolate | Toggle     |  |
    |  |                          |  |
    |  |     ---- Button ----     |  |
    |  |    |    Show All    |    |  |
    |  |     ----------------     |  |
    |  |     ---- Button ----     |  |
    |  |    |    Hide All    |    |  |
    |  |     ----------------     |  |
    |   --------------------------   |
     --------------------------------
    """
    def __init__(self, toggle_names, plot_widget, data_type):
        super(DataControlWidget, self).__init__()

        self.main_layout = None
        self.toggle_grid_layout = None

        self.toggle_names = toggle_names
        self.plot_widget = plot_widget
        self.data_type = data_type

        self.toggles = {}
        self.toggle_group = QtWidgets.QButtonGroup()
        self.toggle_group.setExclusive(False)

        self.__build_data_control_widget()

    def __build_data_control_widget(self):
        """
        """        
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Create and add the data control toggles
        toggle_widget = self.__build_toggle_widget()
        main_layout.addWidget(toggle_widget)

        # Add a spacing character
        main_layout.addWidget(QtWidgets.QLabel(unichr(0x2022)), alignment = 4)

        # Create and add "isolate" toggle
        isolate_widget = self.__build_isolate_toggle_widget()
        main_layout.addWidget(isolate_widget)

        # Create and ddd "Show all" and "Hide all" buttons
        show_all_button = UtilityButton(label = 'Show All', data_control_widget = self)
        hide_all_button = UtilityButton(label = 'Hide All', data_control_widget = self)
        main_layout.addWidget(show_all_button) 
        main_layout.addWidget(hide_all_button) 

        # Set layout view preferences
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.setSpacing(3)
        main_layout.setContentsMargins(0, 5, 0, 5)

        self.main_layout = main_layout


    def __build_toggle_widget(self):
        """
        """
        # Create a widget to hold the toggle button and label grid
        toggle_widget = QtWidgets.QWidget()

        # Create grid layout to be filled with toggle buttons and labels
        toggle_grid_layout = QtWidgets.QGridLayout(toggle_widget)

        for i, toggle_name in enumerate(self.toggle_names):
            # Create a toggle button and assign it a name            
            toggle_object = DataToggle(plot_widget = self.plot_widget,
                                       data_type = self.data_type)
            toggle_object.setAccessibleName(toggle_name)

            # Assign the button object to its appropriate dictionary key
            self.toggles[toggle_name] = toggle_object
            
            self.toggle_group.addButton(toggle_object)

            toggle_label = QtWidgets.QLabel(toggle_name)
            toggle_label.setFont(FONT)

            # Add the button and its label to the toggle grid UI
            toggle_grid_layout.addWidget(toggle_label, i, 0)
            toggle_grid_layout.addWidget(toggle_object, i, 1)

        self.toggle_grid_layout = toggle_grid_layout

        return toggle_widget

    def __build_isolate_toggle_widget(self):
        """
        """
        isolate_widget = QtWidgets.QWidget()
        isolate_toggle = IsolateToggle(self.toggle_group)

        isolate_grid_layout = QtWidgets.QGridLayout(isolate_widget)

        label = QtWidgets.QLabel('Isolate')
        label.setFont(FONT)

        isolate_grid_layout.addWidget(label, 0, 0)
        isolate_grid_layout.addWidget(isolate_toggle, 0, 1)

        # Add the isolate toggle button to the toggles dictionary
        self.toggles['Isolate'] = isolate_toggle

        return isolate_widget


class LimitsToggleWidget(QtWidgets.QWidget):
    """
    """
    def __init__(self):
        super(LimitsToggleWidget, self).__init__()
        
        self.toggle = None
        self.limits_toggle_widget = None
        self.__build_limits_toggle_widget()

    def __build_limits_toggle_widget(self):
        """
        """
        limits_toggle_widget = QtWidgets.QWidget()
        limits_toggle = LimitsToggle()

        limits_grid_layout = QtWidgets.QGridLayout(limits_toggle_widget)

        label = QtWidgets.QLabel('Limits')
        label.setFont(FONT)

        limits_grid_layout.addWidget(label, 0, 0)
        limits_grid_layout.addWidget(limits_toggle, 0, 1)

        self.toggle  = limits_toggle
        self.limits_toggle_widget = limits_toggle_widget


class AnalysisPlotWidget(QtWidgets.QWidget):
    """
    """
    def __init__(self, axis_toggles, derivative_toggles):
        super(AnalysisPlotWidget, self).__init__()

        self.plot_window = pg.GraphicsLayoutWidget(show = True,
                                                   title = 'Mimic Analysis')

        self.axis_toggles = axis_toggles
        self.derivative_toggles = derivative_toggles

        self.plot_window.setBackground((78, 78, 78))

        pg.setConfigOptions(antialias = True)

        self.plot = self.plot_window.addPlot()
        self.plot.showGrid(x = True, y = True)

    def update(self, toggle):
        if toggle.isChecked():
            self.update_axis_data(toggle)
        else:
            self.update_derivative_data(toggle)

        print toggle.type

    def update_axis_data(self, toggle):
        """
        """
        print 'hey'

    def update_derivative_data(self, toggle):
        print 'sup'
