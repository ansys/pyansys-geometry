"""``Beam`` class module."""

from typing import TYPE_CHECKING, List, Union

from ansys.geometry.core.math import (
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    ZERO_POINT3D,
    Point3D,
    UnitVector3D,
    Vector3D,
)
from ansys.geometry.core.misc import Distance, check_type
from ansys.geometry.core.typing import RealSequence

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.component import Component


class BeamProfile:
    """
    Represents a single beam profile organized within the design assembly.

    Synchronizes to a design within a supporting geometry service instance.

    Parameters
    ----------
    id : str
        A server defined identifier for the beam profile.
    name : str
        A user-defined label for the beam profile.
    """

    def __init__(self, id: str, name: str):
        """Constructor method for ``BeamProfile``."""
        check_type(id, str)
        check_type(name, str)

        self._id = id
        self._name = name @ property

    def id(self) -> str:
        """Id of the ``BeamProfile``."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the ``BeamProfile``."""
        return self._name


class BeamCircularProfile(BeamProfile):
    """
    Represents a single beam profile organized within the design assembly.

    Synchronizes to a design within a supporting geometry service instance.

    Parameters
    ----------
    id : str
        A server defined identifier for the beam profile.
    name : str
        A user-defined label for the beam profile.
    radius : Union[Quantity, Distance]
        The radius of the circle.
    center: Point3D
        A :class:`Point3D` representing the center of the circle.
    direction_x: Optional[Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]]
        X-axis direction. By default, ``UNITVECTOR3D_X``.
    direction_y: Optional[Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]]
        Y-axis direction. By default, ``UNITVECTOR3D_Y``.
    """

    def __init__(
        self,
        id: str,
        name: str,
        radius: Union[Quantity, Distance],
        center: Union[np.ndarray, RealSequence, Point3D] = ZERO_POINT3D,
        direction_x: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        direction_y: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Y,
    ):
        """Constructor method for ``BeamCircularProfile``."""
        super().__init__(id, name)

        check_type(radius, (Quantity, Distance))
        check_type(center, (np.ndarray, List, Point3D))
        check_type(direction_x, (np.ndarray, List, UnitVector3D, Vector3D))
        check_type(direction_y, (np.ndarray, List, UnitVector3D, Vector3D))

        self._radius = radius if isinstance(radius, Distance) else Distance(radius)
        if self._radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

        self._center = Point3D(center) if not isinstance(center, Point3D) else center
        self._direction_x = (
            UnitVector3D(direction_x) if not isinstance(direction_x, UnitVector3D) else direction_x
        )
        self._direction_y = (
            UnitVector3D(direction_y) if not isinstance(direction_y, UnitVector3D) else direction_y
        )

        # everything is fixed once built
        self._radius.setflags(write=False)
        self._center.setflags(write=False)
        self._direction_x.setflags(write=False)
        self._direction_y.setflags(write=False)


class Beam:
    """
    Solid body representation with an assigned 2D cross-section.

    Synchronizes to a design within a supporting geometry service instance.

    Parameters
    ----------
    id : str
        A server defined identifier for the body.
    name : str
        A user-defined label for the body.
    segment_start : Point3D
        The start of the beam line segment.
    segment_end : Point3D
        The end of the beam line segment.
    profile : BeamProfile
        The beam profile used to create the Beam.
    parent_component : Component
        The parent component to nest the new component under within the design assembly.
    """

    def __init__(
        self,
        id: str,
        segment_start: Point3D,
        segment_end: Point3D,
        profile: BeamProfile,
        parent_component: "Component",
    ):
        """Constructor method for ``Beam``."""
        # Sanity checks - cannot check Component due to circular import issues
        check_type(id, str)
        check_type(segment_start, Point3D)
        check_type(segment_end, Point3D)
        check_type(profile, BeamProfile)

        self._id = id
        self._parent_component = parent_component
        self._segment_start = segment_start
        self._segment_end = segment_end
        self._profile = profile

    @property
    def id(self) -> str:
        """Geometry Service defined Id of the ``Beam``."""
        return self._id
