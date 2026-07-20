from __future__ import absolute_import


from PySide6 import QtCore
from PySide6 import QtWidgets

from viewline import constants

from parameters import StyleSettings
from parameters import FilterSettings
from parameters import DisplaySettings


from viewline.widgets.buttons import TextButton
from viewline.widgets.buttons import ColorButton
from viewline.widgets.buttons import ResetButton

from viewline.widgets.labels import RightLabel

from viewline.widgets.sliders import NormalSlider

from viewline.widgets.pixmaps import NamePixmapIcon

from viewline.widgets.layouts import GridLayout
from viewline.widgets.layouts import VerticalSpacer
from viewline.widgets.layouts import VerticalLayout
from viewline.widgets.layouts import HorizontalLayout
from viewline.widgets.layouts import HorizontalSpacer


class ColorFilterWidget(QtWidgets.QWidget):

    def __init__(self, parent, *args, **kwargs):

        # Initialize QWidget
        super(ColorFilterWidget, self).__init__(parent)

        self.setupUi()

        self.setupIcons()

    def setupUi(self):
        """
        Build and initialize the main user interface.
        """

        # Configure main window size and title
        self.resize(410, 400)

        # Set the window title.
        self.setWindowTitle("Color Filter")

        self.verticallayout = VerticalLayout(self, space=10, margins=(10, 10, 10, 10))

        self.tabWidget = QtWidgets.QTabWidget(self)
        self.verticallayout.addWidget(self.tabWidget)

        self.displayWidget = DisplayWidget(self.tabWidget)
        self.tabWidget.addTab(self.displayWidget, "Display")

        self.stylesWidget = StylesWidget(self)
        self.tabWidget.addTab(self.stylesWidget, "Styles")

        self.filterWidget = FilterWidget(self)
        self.tabWidget.addTab(self.filterWidget, "Filter")

        self.horizontallayout = HorizontalLayout(None, space=10, margins=(5, 5, 5, 5))
        self.verticallayout.addLayout(self.horizontallayout)

        self.horizontalspacer1 = HorizontalSpacer()
        self.horizontallayout.addItem(self.horizontalspacer1)

        self.closeButton = TextButton(None, label="Close", tooltip="Close the Color Filter")
        self.horizontallayout.addWidget(self.closeButton)

        self.tabWidget.setCurrentIndex(0)

        self.closeButton.clicked.connect(self.close)

    def setupIcons(self):
        """
        Setup the main window icon.
        """

        pixmap = NamePixmapIcon(constants.VL_COLOR_FILTER_TOOL_ICON)
        self.setWindowIcon(pixmap)
    
    def reset(self):
        self.stylesWidget.reset_all()



class DisplayWidget(QtWidgets.QWidget):

    display_changed = QtCore.Signal(object)

    def __init__(self, parent, *args, **kwargs):
        super(DisplayWidget, self).__init__(parent)

        self.displaySettings = DisplaySettings()

        self.setupUi()

    def setupUi(self):
        """
        Build and initialize the main user interface.
        """

        self.verticallayout = VerticalLayout(self, space=10, margins=(10, 10, 10, 10))

        self.gridlayout = GridLayout(None, space=(10, 20), margins=(20, 20, 20, 20))
        self.verticallayout.addLayout(self.gridlayout)

        self.verticalSpacer = VerticalSpacer()
        self.verticallayout.addItem(self.verticalSpacer)

        parameters = self.displaySettings.parameters()

        for index, parameter in enumerate(parameters):
            if parameter.name == "overlay":
                widget = ColorButton(None, label=parameter.label, locked=False)

                widget.color_changed.connect(
                    lambda clicked, inputs=(widget, parameter): self.color_changed(*inputs)
                )
            else:
                widget = RightLabel(self, parameter.label)

            self.gridlayout.addWidget(widget, index, 0, 1, 1)

            minimum, maximum = parameter.slider_range()
            value = parameter.slider_value()

            slider = NormalSlider(self, minimum=minimum, maximum=maximum, value=value)
            slider.valueChanged.connect(
                lambda xvalue, param=parameter: self.value_changed(param, xvalue)
            )
            self.gridlayout.addWidget(slider, index, 1, 1, 1)

            resetButton = ResetButton(self, width=18, height=18)
            resetButton.clicked.connect(
                lambda clicked, x=(slider, widget), param=parameter: self.reset(x, param)
            )
            self.gridlayout.addWidget(resetButton, index, 2, 1, 1)

    def color_changed(self, widget, parameter):
        parameter.set_color(widget.normalized_color)
        self.display_changed.emit(parameter)

    def value_changed(self, parameter, value):
        value = parameter.value_from_slider(value)
        parameter.value = value
        self.display_changed.emit(parameter)

    def reset(self, widgets, parameter):
        parameter.reset()
        value = parameter.slider_value()
        widgets[0].setValue(value)

        if isinstance(widgets[1], ColorButton):
            widgets[1].setColor((255, 0, 0))


class StylesWidget(QtWidgets.QWidget):

    style_changed = QtCore.Signal(object)

    def __init__(self, parent, *args, **kwargs):
        super(StylesWidget, self).__init__(parent)

        self.styleSettings = StyleSettings()

        self.setupUi()

    def setupUi(self):
        """
        Build and initialize the main user interface.
        """

        self.verticallayout = VerticalLayout(self, space=10, margins=(10, 10, 10, 10))

        self.gridlayout = GridLayout(None, space=(10, 20), margins=(20, 20, 20, 20))
        self.verticallayout.addLayout(self.gridlayout)

        self.verticalSpacer = VerticalSpacer()
        self.verticallayout.addItem(self.verticalSpacer)

        self.parameters = self.styleSettings.parameters()

        for index, parameter in enumerate(self.parameters):
            widget = RightLabel(self, parameter.label)
            self.gridlayout.addWidget(widget, index, 0, 1, 1)

            minimum, maximum = parameter.slider_range()
            value = parameter.slider_value()

            slider = NormalSlider(self, minimum=minimum, maximum=maximum, value=value)
            slider.valueChanged.connect(
                lambda xvalue, param=parameter: self.value_changed(param, xvalue)
            )
            self.gridlayout.addWidget(slider, index, 1, 1, 1)

            resetButton = ResetButton(self, width=18, height=18)
            resetButton.clicked.connect(
                lambda clicked, x=slider, param=parameter: self.reset(x, param)
            )
            self.gridlayout.addWidget(resetButton, index, 2, 1, 1)

    def value_changed(self, parameter, value):
        value = parameter.value_from_slider(value)
        parameter.value = value
        self.style_changed.emit(parameter)

    def reset(self, slider, parameter):
        parameter.reset()
        value = parameter.slider_value()
        slider.setValue(value)


class FilterWidget(QtWidgets.QWidget):

    filter_changed = QtCore.Signal(object)

    def __init__(self, parent, *args, **kwargs):
        super(FilterWidget, self).__init__(parent)

        self.filterSettings = FilterSettings()

        self.setupUi()

    def setupUi(self):
        """
        Build and initialize the main user interface.
        """

        self.verticallayout = VerticalLayout(self, space=10, margins=(10, 10, 10, 10))

        self.gridlayout = GridLayout(None, space=(10, 20), margins=(20, 20, 20, 20))
        self.verticallayout.addLayout(self.gridlayout)

        self.verticalSpacer = VerticalSpacer()
        self.verticallayout.addItem(self.verticalSpacer)

        parameters = self.filterSettings.parameters()

        for index, parameter in enumerate(parameters):
            widget = RightLabel(self, parameter.label)
            self.gridlayout.addWidget(widget, index, 0, 1, 1)

            minimum, maximum = parameter.slider_range()
            value = parameter.slider_value()

            slider = NormalSlider(self, minimum=minimum, maximum=maximum, value=value)
            slider.valueChanged.connect(
                lambda xvalue, param=parameter: self.value_changed(param, xvalue)
            )
            self.gridlayout.addWidget(slider, index, 1, 1, 1)

            resetButton = ResetButton(self, width=18, height=18)
            resetButton.clicked.connect(
                lambda clicked, x=(slider, widget), param=parameter: self.reset(x, param)
            )
            self.gridlayout.addWidget(resetButton, index, 2, 1, 1)

    def value_changed(self, parameter, value):
        value = parameter.value_from_slider(value)
        parameter.value = value
        self.filter_changed.emit(parameter)

    def reset(self, widgets, parameter):
        parameter.reset()
        value = parameter.slider_value()
        widgets[0].setValue(value)

        if isinstance(widgets[1], ColorButton):
            widgets[1].setColor((255, 0, 0))


if __name__ == "__main__":
    pass
