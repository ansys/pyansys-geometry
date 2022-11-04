"""``Beam`` class module."""

from beartype.typing import TYPE_CHECKING, List

from ansys.geometry.core.math import Point3D
from ansys.geometry.core.misc import check_type

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.component import Component


class DesignPoints:
    def __init__(self, id: str, name: str, points: List[Point3D], parent_component: "Component"):
        from ansys.geometry.core.designer.component import Component

        """Constructor method for the ``DesignPoints`` class."""
        check_type(id, str)
        check_type(name, str)
        [check_type(point, Point3D) for point in points]
        check_type(parent_component, Component)
        self._id = id
        self._name = name
        self._design_points = points
        self._parent_component = parent_component

    @property
    def id(self) -> str:
        """ID of the beam profile."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the beam profile."""
        return self._name

    @property
    def design_points(self) -> List[Point3D]:
        return self._design_points
