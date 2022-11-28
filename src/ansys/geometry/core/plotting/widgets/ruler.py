"""Module containing the Ruler widget."""

import os

from pyvista import Plotter, _vtk

from ansys.geometry.core.plotting.widgets.widget import PlotterWidget


class Ruler(PlotterWidget):
    def __init__(self, plotter: Plotter) -> None:
        # Call PlotterWidget ctor
        super().__init__(plotter)

        # Initialize variables
        self._is_visible: bool = False
        self._actor = None
        self._button: _vtk.vtkButtonWidget = self._plotter.add_checkbox_button_widget(
            self.callback, position=(10, 500), size=30, border_size=3
        )

    def callback(self) -> None:
        if self._is_visible and self._actor is not None:
            self._plotter.remove_actor(self._actor)
            self._is_visible = False
        else:
            self._actor = self._plotter.show_bounds(
                grid="front",
                location="outer",
                all_edges=False,
                show_xaxis=True,
                show_yaxis=True,
                show_zaxis=True,
            )
            self._is_visible = True

    def update(self) -> None:

        show_ruler_vr = self._button.GetRepresentation()
        show_ruler_icon_file = os.path.join(os.path.dirname(__file__), "_images", "show_ruler.png")
        show_ruler_r = _vtk.vtkPNGReader()
        show_ruler_r.SetFileName(show_ruler_icon_file)
        show_ruler_r.Update()
        image = show_ruler_r.GetOutput()
        show_ruler_vr.SetButtonTexture(0, image)
        show_ruler_vr.SetButtonTexture(1, image)
