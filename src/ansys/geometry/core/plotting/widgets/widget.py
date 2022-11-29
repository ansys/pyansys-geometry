"""Module containing the abstract implementation of Plotter widgets."""

from abc import ABC, abstractmethod

from pyvista import Plotter


class PlotterWidget(ABC):
    """Abstract class for Plotter widgets.

    Notes
    -----
    These widgets are intended to be used with PyVista plotter objects.
    """

    def __init__(self, plotter: Plotter):
        self._plotter: Plotter = plotter

    @property
    def plotter(self):
        """The Plotter object to which the widget is assigned."""
        return self._plotter

    @abstractmethod
    def callback(self, state) -> None:
        """General callback function for PlotterWidget objects."""
        pass

    @abstractmethod
    def update(self) -> None:
        """General update function for PlotterWidget objects."""
        pass
