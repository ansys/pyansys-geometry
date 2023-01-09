import os

from pyvista import Plotter, _vtk

from ansys.geometry.core.plotting.widgets.widget import PlotterWidget


class DisplaceArrowXUp(PlotterWidget):
    def __init__(self, plotter: Plotter):
        super().__init__(plotter)
        self._button_left: _vtk.vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=(5, 170), size=30, border_size=3
        )

    def callback(self, state) -> None:
        current_pos = self.plotter.camera_position.to_list()
        self.plotter.set_position([current_pos[0][0] + 1, current_pos[0][1], current_pos[0][2]])
        self.plotter.set_focus([current_pos[1][0] + 1, current_pos[1][1], current_pos[1][2]])

    def update(self) -> None:
        """Method defining the configuration and representation of the Ruler widget button."""
        show_ruler_vr = self._button_left.GetRepresentation()
        show_ruler_icon_file = os.path.join(os.path.dirname(__file__), "_images", "upxarrow.png")
        show_ruler_r = _vtk.vtkPNGReader()
        show_ruler_r.SetFileName(show_ruler_icon_file)
        show_ruler_r.Update()
        image = show_ruler_r.GetOutput()
        show_ruler_vr.SetButtonTexture(0, image)
        show_ruler_vr.SetButtonTexture(1, image)


class DisplaceArrowXDown(PlotterWidget):
    def __init__(self, plotter: Plotter):
        super().__init__(plotter)
        self._button_right: _vtk.vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=(5, 130), size=30, border_size=3
        )

    def callback(self, state) -> None:
        # retrieve current camera position, focus and viewup
        current_pos = self.plotter.camera_position.to_list()
        self.plotter.set_position([current_pos[0][0] - 1, current_pos[0][1], current_pos[0][2]])
        self.plotter.set_focus([current_pos[1][0] - 1, current_pos[1][1], current_pos[1][2]])

    def update(self) -> None:
        """Method defining the configuration and representation of the Ruler widget button."""
        show_ruler_vr = self._button_right.GetRepresentation()
        show_ruler_icon_file = os.path.join(os.path.dirname(__file__), "_images", "downarrow.png")
        show_ruler_r = _vtk.vtkPNGReader()
        show_ruler_r.SetFileName(show_ruler_icon_file)
        show_ruler_r.Update()
        image = show_ruler_r.GetOutput()
        show_ruler_vr.SetButtonTexture(0, image)
        show_ruler_vr.SetButtonTexture(1, image)


class DisplaceArrowYUp(PlotterWidget):
    def __init__(self, plotter: Plotter):
        super().__init__(plotter)
        self._button_right: _vtk.vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=(35, 170), size=30, border_size=3
        )

    def callback(self, state) -> None:
        # retrieve current camera position, focus and viewup
        current_pos = self.plotter.camera_position.to_list()
        self.plotter.set_position([current_pos[0][0], current_pos[0][1] + 1, current_pos[0][2]])
        self.plotter.set_focus([current_pos[1][0], current_pos[1][1] + 1, current_pos[1][2]])

    def update(self) -> None:
        """Method defining the configuration and representation of the Ruler widget button."""
        show_ruler_vr = self._button_right.GetRepresentation()
        show_ruler_icon_file = os.path.join(os.path.dirname(__file__), "_images", "upyarrow.png")
        show_ruler_r = _vtk.vtkPNGReader()
        show_ruler_r.SetFileName(show_ruler_icon_file)
        show_ruler_r.Update()
        image = show_ruler_r.GetOutput()
        show_ruler_vr.SetButtonTexture(0, image)
        show_ruler_vr.SetButtonTexture(1, image)


class DisplaceArrowYDown(PlotterWidget):
    def __init__(self, plotter: Plotter):
        super().__init__(plotter)
        self._button_right: _vtk.vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=(35, 130), size=30, border_size=3
        )

    def callback(self, state) -> None:
        # retrieve current camera position, focus and viewup
        current_pos = self.plotter.camera_position.to_list()
        self.plotter.set_position([current_pos[0][0], current_pos[0][1] - 1, current_pos[0][2]])
        self.plotter.set_focus([current_pos[1][0], current_pos[1][1] - 1, current_pos[1][2]])

    def update(self) -> None:
        """Method defining the configuration and representation of the Ruler widget button."""
        show_ruler_vr = self._button_right.GetRepresentation()
        show_ruler_icon_file = os.path.join(os.path.dirname(__file__), "_images", "downarrow.png")
        show_ruler_r = _vtk.vtkPNGReader()
        show_ruler_r.SetFileName(show_ruler_icon_file)
        show_ruler_r.Update()
        image = show_ruler_r.GetOutput()
        show_ruler_vr.SetButtonTexture(0, image)
        show_ruler_vr.SetButtonTexture(1, image)


class DisplaceArrowZUp(PlotterWidget):
    def __init__(self, plotter: Plotter):
        super().__init__(plotter)

        self._actor: _vtk.vtkActor = None
        self._button_up: _vtk.vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=(65, 170), size=30, border_size=3
        )

    def callback(self, state) -> None:
        current_pos = self.plotter.camera_position.to_list()
        self.plotter.set_position([current_pos[0][0], current_pos[0][1], current_pos[0][2] + 1])
        self.plotter.set_focus([current_pos[1][0], current_pos[1][1], current_pos[1][2] + 1])

    def update(self) -> None:
        """Method defining the configuration and representation of the Ruler widget button."""
        show_ruler_vr = self._button_up.GetRepresentation()
        show_ruler_icon_file = os.path.join(os.path.dirname(__file__), "_images", "upzarrow.png")
        show_ruler_r = _vtk.vtkPNGReader()
        show_ruler_r.SetFileName(show_ruler_icon_file)
        show_ruler_r.Update()
        image = show_ruler_r.GetOutput()
        show_ruler_vr.SetButtonTexture(0, image)
        show_ruler_vr.SetButtonTexture(1, image)


class DisplaceArrowZDown(PlotterWidget):
    def __init__(self, plotter: Plotter):
        super().__init__(plotter)
        self._button_down: _vtk.vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=(65, 130), size=30, border_size=3
        )

    def callback(self, state) -> None:
        current_pos = self.plotter.camera_position.to_list()
        self.plotter.set_position([current_pos[0][0], current_pos[0][1], current_pos[0][2] - 1])
        self.plotter.set_focus([current_pos[1][0], current_pos[1][1], current_pos[1][2] - 1])

    def update(self) -> None:
        """Method defining the configuration and representation of the Ruler widget button."""
        show_ruler_vr = self._button_down.GetRepresentation()
        show_ruler_icon_file = os.path.join(os.path.dirname(__file__), "_images", "downarrow.png")
        show_ruler_r = _vtk.vtkPNGReader()
        show_ruler_r.SetFileName(show_ruler_icon_file)
        show_ruler_r.Update()
        image = show_ruler_r.GetOutput()
        show_ruler_vr.SetButtonTexture(0, image)
        show_ruler_vr.SetButtonTexture(1, image)
