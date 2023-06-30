"""Displacement arrows widget for PyVista plotter."""
from enum import Enum

from pyvista import Plotter

from ansys.geometry.core.plotting.widgets.button import Button


class CameraPanDirection(Enum):
    """Enumerate with the possible movement directions of the camera."""

    XUP = 0, "upxarrow.png", (5, 170)
    XDOWN = 1, "downarrow.png", (5, 130)
    YUP = 2, "upyarrow.png", (35, 170)
    YDOWN = 3, "downarrow.png", (35, 130)
    ZUP = 4, "upzarrow.png", (65, 170)
    ZDOWN = 5, "downarrow.png", (65, 130)


class DisplacementArrow(Button):
    """
    Defines which arrow you will draw and what it will do.

    Parameters
    ----------
    plotter : Plotter
        Plotter on which the buttons will be drawn.
    direction : CameraPanDirection
        Direction on which the camera will move.
    """

    def __init__(self, plotter: Plotter, direction: CameraPanDirection):
        """Initialize ``DisplacementArrow`` class."""
        super().__init__(plotter, direction)
        self.direction = direction

    def callback(self, state: bool) -> None:
        """
        Move the camera in the direction that the button was defined.

        Parameters
        ----------
        state : bool
            Inherited from PyVista. State of the button, true if active. Unused
            in this case.
        """
        self.current_camera_pos = list(map(list, self.plotter.camera_position.to_list()))

        # use the length of the diagonal to adjust the movement speed
        if self.direction == CameraPanDirection.XUP:
            self.current_camera_pos[0][0] -= 0.05 * self.plotter.length
            self.current_camera_pos[1][0] -= 0.05 * self.plotter.length
        elif self.direction == CameraPanDirection.XDOWN:
            self.current_camera_pos[0][0] += 0.05 * self.plotter.length
            self.current_camera_pos[1][0] += 0.05 * self.plotter.length
        elif self.direction == CameraPanDirection.YUP:
            self.current_camera_pos[0][1] -= 0.05 * self.plotter.length
            self.current_camera_pos[1][1] -= 0.05 * self.plotter.length
        elif self.direction == CameraPanDirection.YDOWN:
            self.current_camera_pos[0][1] += 0.05 * self.plotter.length
            self.current_camera_pos[1][1] += 0.05 * self.plotter.length
        elif self.direction == CameraPanDirection.ZUP:
            self.current_camera_pos[0][2] -= 0.05 * self.plotter.length
            self.current_camera_pos[1][2] -= 0.05 * self.plotter.length
        elif self.direction == CameraPanDirection.ZDOWN:
            self.current_camera_pos[0][2] += 0.05 * self.plotter.length
            self.current_camera_pos[1][2] += 0.05 * self.plotter.length
        else:  # pragma: no cover
            raise NotImplementedError(
                f"CameraPanDirection {self.direction.name} is not implemented as a widget."
            )

        self.plotter.set_position(self.current_camera_pos[0])
        self.plotter.set_focus(self.current_camera_pos[1])
