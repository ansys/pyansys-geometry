from enum import Enum
import os

from pyvista import Plotter, _vtk

from ansys.geometry.core.plotting.widgets.widget import PlotterWidget


class CameraPanDirection(Enum):
    """Enumerate with the possible movement directions of the camera"""

    XUP = 0
    XDOWN = 1
    YUP = 2
    YDOWN = 3
    ZUP = 4
    ZDOWN = 5


class DisplacementArrow(PlotterWidget):
    def __init__(
        self, plotter: Plotter, position: tuple, button_image: str, direction: CameraPanDirection
    ):
        """Defines which arrow you will draw and what it will do

        Parameters
        ----------
        plotter : Plotter
            Plotter on which the buttons will be drawn.
        position : tuple
            (x, y) tuple with the position of the button in the screen.
        button_image : str
            Path to the image of the button
        direction : CameraPanDirection
            Direction on which the camera will move.
        """
        super().__init__(plotter)
        self._arrow_button: _vtk.vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=position, size=30, border_size=3
        )
        self.icon_dict = {
            CameraPanDirection.XUP: "upxarrow.png",
            CameraPanDirection.YUP: "upyarrow.png",
            CameraPanDirection.ZUP: "upzarrow.png",
            CameraPanDirection.XDOWN: "downarrow.png",
            CameraPanDirection.YDOWN: "downarrow.png",
            CameraPanDirection.ZDOWN: "downarrow.png",
        }
        self.button_image = button_image
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
            raise NotImplementedError

        self.plotter.set_position(self.current_camera_pos[0])
        self.plotter.set_focus(self.current_camera_pos[1])

    def update(self) -> None:
        """Assigns the image that will represent the button."""
        arrow_button_repr = self._arrow_button.GetRepresentation()
        arrow_button_icon_path = os.path.join(
            os.path.dirname(__file__), "_images", self.icon_dict[self.direction]
        )
        arrow_button_icon = _vtk.vtkPNGReader()
        arrow_button_icon.SetFileName(arrow_button_icon_path)
        arrow_button_icon.Update()
        image = arrow_button_icon.GetOutput()
        arrow_button_repr.SetButtonTexture(0, image)
        arrow_button_repr.SetButtonTexture(1, image)
