"""Module containing the Ruler widget."""

import os

from pyvista import Plotter
from vtk import vtkActor, vtkButtonWidget, vtkPNGReader

from ansys.geometry.core.misc import DEFAULT_UNITS
from ansys.geometry.core.plotting.widgets.widget import PlotterWidget


class Ruler(PlotterWidget):
    """
    Ruler widget for the PyGeometry plotter class.

    Parameters
    ----------
    plotter : ~pyvista.Plotter
        The Plotter instance to which the widget will be added.
    """

    def __init__(self, plotter: Plotter) -> None:
        """Initialize ``Ruler`` class."""
        # Call PlotterWidget ctor
        super().__init__(plotter)

        # Initialize variables
        self._actor: vtkActor = None
        self._button: vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=(10, 100), size=30, border_size=3
        )

    def callback(self, state: bool) -> None:
        """
        Remove/Add Ruler widget actor upon click.

        Callback function for the Ruler widget.

        Notes
        -----
        This method is called every time the Ruler widget is clicked.

        Parameters
        ----------
        state : bool
            The value of the button. ``True`` if active.
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
        """Define the configuration and representation of the Ruler widget button."""
        show_ruler_vr = self._button.GetRepresentation()
        show_ruler_icon_file = os.path.join(os.path.dirname(__file__), "_images", "ruler.png")
        show_ruler_r = vtkPNGReader()
        show_ruler_r.SetFileName(show_ruler_icon_file)
        show_ruler_r.Update()
        image = show_ruler_r.GetOutput()
        show_ruler_vr.SetButtonTexture(0, image)
        show_ruler_vr.SetButtonTexture(1, image)
