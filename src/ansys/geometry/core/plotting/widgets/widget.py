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
