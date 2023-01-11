from enum import Enum
import os

from pyvista import Plotter, _vtk

from ansys.geometry.core.plotting.widgets.widget import PlotterWidget


class CameraPanDirection(Enum):
    """Enumerate with the possible movement directions of the camera"""

    XUP = 0, "upxarrow.png", (5, 170)
    XDOWN = 1, "downarrow.png", (5, 130)
    YUP = 2, "upyarrow.png", (35, 170)
    YDOWN = 3, "downarrow.png", (35, 130)
    ZUP = 4, "upzarrow.png", (65, 170)
    ZDOWN = 5, "downarrow.png", (65, 130)


class DisplacementArrow(PlotterWidget):
    """Defines which arrow you will draw and what it will do

    Parameters
    ----------
    plotter : Plotter
        Plotter on which the buttons will be drawn.
    direction : CameraPanDirection
        Direction on which the camera will move.
    """

    def __init__(self, plotter: Plotter, direction: CameraPanDirection):
        """Constructor method for ``DisplacementArrow``."""
        super().__init__(plotter)
        self._arrow_button: _vtk.vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=direction.value[2], size=30, border_size=3
        )
        self.direction = direction

    def callback(self, state: bool) -> None:
        """Move the camera in the direction that the button was defined.

        Parameters
        ----------
        state : bool
            Inherited from PyVista. State of the button, true if active. Unused
            in this case.
        """
        self.current_camera_pos = list(map(list, self.plotter.camera_position.to_list()))

        if self.direction == CameraPanDirection.XUP:
            self.current_camera_pos[0][0] += 1
            self.current_camera_pos[1][0] += 1
        elif self.direction == CameraPanDirection.XDOWN:
            self.current_camera_pos[0][0] -= 1
            self.current_camera_pos[1][0] -= 1
        elif self.direction == CameraPanDirection.YUP:
            self.current_camera_pos[0][1] += 1
            self.current_camera_pos[1][1] += 1
        elif self.direction == CameraPanDirection.YDOWN:
            self.current_camera_pos[0][1] -= 1
            self.current_camera_pos[1][1] -= 1
        elif self.direction == CameraPanDirection.ZUP:
            self.current_camera_pos[0][2] += 1
            self.current_camera_pos[1][2] += 1
        elif self.direction == CameraPanDirection.ZDOWN:
            self.current_camera_pos[0][2] -= 1
            self.current_camera_pos[1][2] -= 1
        else:  # pragma: no cover
            raise NotImplementedError(
                f"CameraPanDirection {self.direction.name} is not implemented as a widget."
            )

        self.plotter.set_position(self.current_camera_pos[0])
        self.plotter.set_focus(self.current_camera_pos[1])

    def update(self) -> None:
        """Assigns the image that will represent the button."""
        arrow_button_repr = self._arrow_button.GetRepresentation()
        arrow_button_icon_path = os.path.join(
            os.path.dirname(__file__), "_images", self.direction.value[1]
        )
        arrow_button_icon = _vtk.vtkPNGReader()
        arrow_button_icon.SetFileName(arrow_button_icon_path)
        arrow_button_icon.Update()
        image = arrow_button_icon.GetOutput()
        arrow_button_repr.SetButtonTexture(0, image)
        arrow_button_repr.SetButtonTexture(1, image)
