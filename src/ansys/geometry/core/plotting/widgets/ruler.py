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

from pyvista import Plotter
from vtk import vtkActor, vtkButtonWidget, vtkPNGReader

from ansys.geometry.core.misc.measurements import DEFAULT_UNITS
from ansys.geometry.core.plotting.widgets.widget import PlotterWidget


class Ruler(PlotterWidget):
    """
    Provides the ruler widget for the PyAnsys Geometry ``Plotter`` class.

    Parameters
    ----------
    plotter : ~pyvista.Plotter
        Provides the plotter to add the ruler widget to.
    """

    def __init__(self, plotter: Plotter) -> None:
        """Initialize the ``Ruler`` class."""
        # Call PlotterWidget ctor
        super().__init__(plotter)

        # Initialize variables
        self._actor: vtkActor = None
        self._button: vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=(10, 100), size=30, border_size=3
        )

    def callback(self, state: bool) -> None:
        """
        Remove or add the ruler widget actor upon click.

        Notes
        -----
        This method provides a callback function for the ruler widet.
        It is called every time the ruler widget is clicked.

        Parameters
        ----------
        state : bool
            State of the button, which is inherited from PyVista. The value is ``True``
            if the button is active.
        """
        if not state and self._actor:
            self.plotter.remove_actor(self._actor)
            self._actor = None
        else:
            self._actor = self.plotter.show_bounds(
                grid="front",
                location="outer",
                all_edges=False,
                show_xaxis=True,
                show_yaxis=True,
                show_zaxis=True,
                color="black",
                xlabel=f"X Axis [{DEFAULT_UNITS.LENGTH:~H}]",
                ylabel=f"Y Axis [{DEFAULT_UNITS.LENGTH:~H}]",
                zlabel=f"Z Axis [{DEFAULT_UNITS.LENGTH:~H}]",
            )

    def update(self) -> None:
        """Define the configuration and representation of the ruler widget button."""
        show_ruler_vr = self._button.GetRepresentation()
        show_ruler_icon_file = os.path.join(os.path.dirname(__file__), "_images", "ruler.png")
        show_ruler_r = vtkPNGReader()
        show_ruler_r.SetFileName(show_ruler_icon_file)
        show_ruler_r.Update()
        image = show_ruler_r.GetOutput()
        show_ruler_vr.SetButtonTexture(0, image)
        show_ruler_vr.SetButtonTexture(1, image)
