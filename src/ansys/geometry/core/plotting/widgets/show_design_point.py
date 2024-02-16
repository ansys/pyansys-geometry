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

from vtk import vtkButtonWidget, vtkPNGReader

from ansys.geometry.core.designer.designpoint import DesignPoint
from ansys.geometry.core.plotting.widgets.widget import PlotterWidget


class ShowDesignPoints(PlotterWidget):
    """
    Provides the a button to hide/show DesignPoint objects in the plotter.

    Parameters
    ----------
    plotter_helper : PlotterHelper
        Provides the plotter to add the button to.
    """

    def __init__(self, plotter_helper: "PlotterHelper") -> None:
        """Initialize the ``ShowDesignPoints`` class."""
        # Call PlotterWidget ctor
        super().__init__(plotter_helper._pl.scene)
        self.plotter_helper = plotter_helper

        # Initialize variables
        self._geom_object_actors_map = self.plotter_helper._pl._geom_object_actors_map
        self._button: vtkButtonWidget = self.plotter_helper._pl.scene.add_checkbox_button_widget(
            self.callback, position=(5, 438), size=30, border_size=3
        )

    def callback(self, state: bool) -> None:
        """
        Remove or add the DesignPoint actors upon click.

        Parameters
        ----------
        state : bool
            State of the button, which is inherited from PyVista. The value is ``True``
            if the button is active.
        """
        if not state:
            for actor, object in self._geom_object_actors_map.items():
                if isinstance(object, DesignPoint):
                    self.plotter_helper._pl.scene.add_actor(actor)
        else:
            for actor, object in self._geom_object_actors_map.items():
                if isinstance(object, DesignPoint):
                    self.plotter_helper._pl.scene.remove_actor(actor)

    def update(self) -> None:
        """Define the configuration and representation of the button widget button."""
        show_point_vr = self._button.GetRepresentation()
        show_point_icon_file = os.path.join(os.path.dirname(__file__), "_images", "designpoint.png")
        show_point_r = vtkPNGReader()
        show_point_r.SetFileName(show_point_icon_file)
        show_point_r.Update()
        image = show_point_r.GetOutput()
        show_point_vr.SetButtonTexture(0, image)
        show_point_vr.SetButtonTexture(1, image)
