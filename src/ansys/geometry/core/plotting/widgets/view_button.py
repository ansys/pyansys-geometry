"""Module containing the ViewButton widget."""

from enum import Enum

from pyvista import Plotter

from ansys.geometry.core.plotting.widgets.button import Button


class ViewDirection(Enum):
    """Enumerate with the available views."""

    XYPLUS = 0, "+xy.png", (5, 220)
    XYMINUS = 1, "-xy.png", (5, 251)
    XZPLUS = 2, "+xz.png", (5, 282)
    XZMINUS = 3, "-xz.png", (5, 313)
    YZPLUS = 4, "+yz.png", (5, 344)
    YZMINUS = 5, "-yz.png", (5, 375)
    ISOMETRIC = 6, "isometric.png", (5, 406)


class ViewButton(Button):
    """
    Changes the view of a plot to the one selected.

    Parameters
    ----------
    plotter : Plotter
        Plotter on which the buttons will be drawn.
    direction : ViewDirection
        Direction of the view.
    """

    def __init__(self, plotter: Plotter, direction: tuple):
        """Initialize ``ViewButton`` class."""
        super().__init__(plotter, direction)
        self.direction = direction

    def callback(self, state: bool) -> None:
        """
        Change the view of the camera depending on button interaction.

        Parameters
        ----------
        state : bool
            True if the button is active.

        Raises
        ------
        NotImplementedError
            Raised if the specified direction is not implemented.
        """
        if self.direction == ViewDirection.XYPLUS:
            self.plotter.view_xy()
        elif self.direction == ViewDirection.XYMINUS:
            self.plotter.view_yx()
        elif self.direction == ViewDirection.XZPLUS:
            self.plotter.view_xz()
        elif self.direction == ViewDirection.XZMINUS:
            self.plotter.view_zx()
        elif self.direction == ViewDirection.YZPLUS:
            self.plotter.view_yz()
        elif self.direction == ViewDirection.YZMINUS:
            self.plotter.view_zy()
        elif self.direction == ViewDirection.ISOMETRIC:
            self.plotter.view_isometric()
        else:  # pragma: no cover
            raise NotImplementedError(
                f"ViewDirection {self.direction.name} is not implemented as a widget."
            )
