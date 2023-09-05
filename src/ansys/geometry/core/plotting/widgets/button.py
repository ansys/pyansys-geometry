"""Provides for implementing buttons in PyAnsys Geometry."""

from abc import abstractmethod
import os

from pyvista import Plotter
from vtk import vtkButtonWidget, vtkPNGReader

from ansys.geometry.core.plotting.widgets.widget import PlotterWidget


class Button(PlotterWidget):
    """
    Provides the abstract class for implementing buttons in PyAnsys Geometry.

    Notes
    -----
    This class wraps the PyVista ``add_checkbox_button_widget()`` method.

    Parameters
    ----------
    plotter : Plotter
        Plotter to draw the buttons on.
    button_config : tuple
        Tuple containing the position and the path to the icon of the button.
    """

    def __init__(self, plotter: Plotter, button_config: tuple):
        """Initialize the ``Button`` class."""
        super().__init__(plotter)
        self._arrow_button: vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=button_config.value[2], size=30, border_size=3
        )
        self.button_config = button_config

    @abstractmethod
    def callback(self, state: bool) -> None:
        """
        Get the functionality of the button, which is implemented by subclasses.

        Parameters
        ----------
        state : bool
            Whether the button is active.
        """
        pass

    def update(self) -> None:
        """Assign the image that represents the button."""
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
