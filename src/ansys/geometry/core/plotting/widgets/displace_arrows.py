import os

from pyvista import Plotter, _vtk

from ansys.geometry.core.plotting.widgets.widget import PlotterWidget


class DisplaceArrowUp(PlotterWidget):
    def __init__(self, plotter: Plotter):
        super().__init__(plotter)

        self._actor: _vtk.vtkActor = None
        self._button_up: _vtk.vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=(35, 150), size=30, border_size=3
        )

    def callback(self, state) -> None:
        current_pos = self.plotter.camera_position
        self.plotter.set_position([])

    def update(self) -> None:
        """Method defining the configuration and representation of the Ruler widget button."""
        show_ruler_vr = self._button.GetRepresentation()
        show_ruler_icon_file = os.path.join(os.path.dirname(__file__), "_images", "ruler.png")
        show_ruler_r = _vtk.vtkPNGReader()
        show_ruler_r.SetFileName(show_ruler_icon_file)
        show_ruler_r.Update()
        image = show_ruler_r.GetOutput()
        show_ruler_vr.SetButtonTexture(0, image)
        show_ruler_vr.SetButtonTexture(1, image)


class DisplaceArrowDown(PlotterWidget):
    def __init__(self, plotter: Plotter):
        super().__init__(plotter)
        self._button_down: _vtk.vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=(35, 120), size=30, border_size=3
        )


class DisplaceArrowLeft(PlotterWidget):
    def __init__(self, plotter: Plotter):
        super().__init__(plotter)
        self._button_left: _vtk.vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=(5, 130), size=30, border_size=3
        )


class DisplaceArrowRight(PlotterWidget):
    def __init__(self, plotter: Plotter):
        super().__init__(plotter)
        self._button_right: _vtk.vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=(65, 130), size=30, border_size=3
        )
