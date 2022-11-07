"""``DesignPoint`` class module."""

from beartype.typing import TYPE_CHECKING, Union

from ansys.geometry.core.math import Point3D
from ansys.geometry.core.misc import check_type

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.component import Component


class DesignPoint:
    """
    Represents a list of 3D points creates a single Design Points.

    Parameters
    ----------
    id : str
        Server-defined ID for the design points.
    name : str
        User-defined label for the design points.
    points : Point3D
        3D point constituting the design points.
    parent_component : Component
        Parent component to nest the new beam under within the design assembly.
    """

    def __init__(self, id: str, name: str, point: Point3D, parent_component: "Component"):

        """Constructor method for the ``DesignPoints`` class."""
        from ansys.geometry.core.designer.component import Component

        check_type(id, str)
        check_type(name, str)
        check_type(point, Point3D)
        check_type(parent_component, Component)

        self._id = id
        self._name = name
        self._design_point = point
        self._parent_component = parent_component

    @property
    def id(self) -> str:
        """ID of the design points."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the design points."""
        return self._name

    @property
    def value(self) -> Point3D:
        """List of 3D points for create design points."""
        return self._design_point

    @property
    def parent_component(self) -> Union["Component", None]:
        """Component node that the beam`` is under."""
        return self._parent_component

    def __repr__(self) -> str:
        """String representation of the design points."""
        lines = [f"ansys.geometry.core.designer.DesignPoints {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Design Point         : {self.value}")
        return "\n".join(lines)
