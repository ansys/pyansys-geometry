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
"""Provides the abstract implementation of plotter widgets."""

from abc import ABC, abstractmethod

from pyvista import Plotter


class PlotterWidget(ABC):
    """
    Provides an abstract class for plotter widgets.

    Parameters
    ----------
    plotter : ~pyvista.Plotter
        Plotter instance to add the widget to.

    Notes
    -----
    These widgets are intended to be used with PyVista plotter objects.
    More specifically, the way in which this abstraction has been built
    ensures that these widgets are easily integrable with PyAnsys Geometry's
    own ``Plotter`` class.
    """

    def __init__(self, plotter: Plotter):
        """Initialize the ``PlotterWidget`` class."""
        self._plotter: Plotter = plotter

    @property
    def plotter(self) -> Plotter:
        """Plotter object the widget is assigned to."""
        return self._plotter

    @abstractmethod
    def callback(self, state) -> None:
        """General callback function for ``PlotterWidget`` objects."""
        pass

    @abstractmethod
    def update(self) -> None:
        """General update function for ``PlotterWidget`` objects."""
        pass
