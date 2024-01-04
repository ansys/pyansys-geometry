# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Provides the ruler widget for the PyAnsys Geometry plotter."""

import os

from vtk import vtkActor, vtkButtonWidget, vtkPNGReader

from ansys.geometry.core.plotting.widgets.widget import PlotterWidget


class MeasureWidget(PlotterWidget):
    """
    Provides the measure widget for the PyAnsys Geometry ``Plotter`` class.

    Parameters
    ----------
    plotter_helper : PlotterHelper
        Provides the plotter to add the measure widget to.
    """

    def __init__(self, plotter_helper: "PlotterHelper") -> None:
        """Initialize the ``Ruler`` class."""
        # Call PlotterWidget ctor
        super().__init__(plotter_helper._pl.scene)

        # Initialize variables
        self._actor: vtkActor = None
        self.plotter_helper = plotter_helper
        self._button: vtkButtonWidget = self.plotter_helper._pl.scene.add_checkbox_button_widget(
            self.callback, position=(10, 60), size=30, border_size=3
        )

    def callback(self, state: bool) -> None:
        """
        Remove or add the measurement widget actor upon click.

        Parameters
        ----------
        state : bool
            State of the button, which is inherited from PyVista. The value is ``True``
            if the button is active.
        """
        # This implementation uses direct calls to VTK due to limitations
        # in PyVista. If there are improvements in the compatibility between
        # the PyVista picker and the measurement widget, this should be reviewed.
        if not state:
            self._widget.Off()
            self.plotter_helper._pl.scene.clear_measure_widgets()
            if self.plotter_helper._allow_picking:
                self.plotter_helper.enable_picking()
        else:
            if self.plotter_helper._allow_picking:
                self.plotter_helper.disable_picking()
            self._widget = self.plotter_helper._pl.scene.add_measurement_widget()

    def update(self) -> None:
        """Define the measurement widget button params."""
        show_measure_vr = self._button.GetRepresentation()
        show_measure_icon_file = os.path.join(
            os.path.dirname(__file__), "_images", "measurement.png"
        )
        show_measure_r = vtkPNGReader()
        show_measure_r.SetFileName(show_measure_icon_file)
        show_measure_r.Update()
        image = show_measure_r.GetOutput()
        show_measure_vr.SetButtonTexture(0, image)
        show_measure_vr.SetButtonTexture(1, image)
