"""Module containing the Button abstract class."""

from abc import abstractmethod
import os

from pyvista import Plotter
from vtk import vtkButtonWidget, vtkPNGReader

from ansys.geometry.core.plotting.widgets.widget import PlotterWidget


class Button(PlotterWidget):
    """
    Abstract class for implementing buttons in PyGeometry.

    Notes
    -----
    Wraps the function ``add_check_button_widget()`` from ``PyVista``.

    Parameters
    ----------
    plotter : Plotter
        Plotter on which the buttons will be drawn.
    button_config : tuple
        Tuple containing the position and the path to the icon of the button.
    """

    def __init__(self, plotter: Plotter, button_config: tuple):
        """Initialize ``Button`` class."""
        super().__init__(plotter)
        self._arrow_button: vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=button_config.value[2], size=30, border_size=3
        )
        self.button_config = button_config

    @abstractmethod
    def callback(self, state: bool) -> None:
        """
        Functionality of the button, to be implemented by subclasses.

        Parameters
        ----------
        state : bool
            True if the button is active.
        """
        pass

    def update(self) -> None:
        """Assign the image that will represent the button."""
        arrow_button_repr = self._arrow_button.GetRepresentation()
        arrow_button_icon_path = os.path.join(
            os.path.dirname(__file__), "_images", self.button_config.value[1]
        )
        arrow_button_icon = vtkPNGReader()
        arrow_button_icon.SetFileName(arrow_button_icon_path)
        arrow_button_icon.Update()
        image = arrow_button_icon.GetOutput()
        arrow_button_repr.SetButtonTexture(0, image)
        arrow_button_repr.SetButtonTexture(1, image)
