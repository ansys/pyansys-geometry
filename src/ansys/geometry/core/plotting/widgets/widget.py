"""Module containing the abstract implementation of Plotter widgets."""

from abc import ABC, abstractmethod

from pyvista import Plotter


class PlotterWidget(ABC):
    """
    Abstract class for Plotter widgets.

    Parameters
    ----------
    plotter : ~pyvista.Plotter
        The Plotter instance to which the widget will be added.

    Notes
    -----
    These widgets are intended to be used with PyVista plotter objects.
    More specifically, the way in which this abstraction has been build
    is such that they are easily integrable with PyGeometry's own Plotter
    class.
    """

    def __init__(self, plotter: Plotter):
        """Initialize ``PlotterWidget`` class."""
        self._plotter: Plotter = plotter

    @property
    def plotter(self) -> Plotter:
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
