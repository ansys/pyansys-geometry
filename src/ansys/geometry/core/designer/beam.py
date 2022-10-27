"""``Beam`` class module."""

from beartype.typing import TYPE_CHECKING, Union

from ansys.geometry.core.math import Point3D, UnitVector3D
from ansys.geometry.core.misc import Distance, check_type

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

    Notes
    -----
    ``BeamProfile`` objects are expected to be created from the ``Design`` object.
    This means that users are not expected to instantiate their own ``BeamProfile``. They
    should call the specific ``Design`` API for the ``BeamProfile`` desired.
    """

    def __init__(self, id: str, name: str):
        """Constructor method for ``BeamProfile``."""
        check_type(id, str)
        check_type(name, str)

        self._id = id
        self._name = name

    @property
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
    radius : Distance
        The radius of the circle.
    center: Point3D
        A :class:`Point3D <ansys.geometry.core.math.point.Point3D>` representing
        the center of the circle.
    direction_x: UnitVector3D
        X-axis direction.
    direction_y: UnitVector3D
        Y-axis direction.

    Notes
    -----
    ``BeamProfile`` objects are expected to be created from the ``Design`` object.
    This means that users are not expected to instantiate their own ``BeamProfile``. They
    should call the specific ``Design`` API for the ``BeamProfile`` desired.
    """

    def __init__(
        self,
        id: str,
        name: str,
        radius: Distance,
        center: Point3D,
        direction_x: UnitVector3D,
        direction_y: UnitVector3D,
    ):
        """Constructor method for ``BeamCircularProfile``."""
        super().__init__(id, name)

        # Store specific BeamCircularProfile variables
        self._radius = radius
        self._center = center
        self._dir_x = direction_x
        self._dir_y = direction_y

    @property
    def radius(self) -> Distance:
        """Returns the radius of the ``BeamCircularProfile``."""
        return self._radius

    @property
    def center(self) -> Point3D:
        """Returns the center of the ``BeamCircularProfile``."""
        return self._center

    @property
    def direction_x(self) -> UnitVector3D:
        """Returns the X-axis direction of the ``BeamCircularProfile``."""
        return self._dir_x

    @property
    def direction_y(self) -> UnitVector3D:
        """Returns the Y-axis direction of the ``BeamCircularProfile``."""
        return self._dir_y

    def __repr__(self) -> str:
        """String representation of the circular beam profile."""
        lines = [f"ansys.geometry.core.designer.BeamCircularProfile {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Radius               : {str(self.radius.value)}")
        lines.append(
            f"  Center               : [{','.join([str(x) for x in self.center])}] in meters"
        )
        lines.append(f"  Direction x          : [{','.join([str(x) for x in self.direction_x])}]")
        lines.append(f"  Direction y          : [{','.join([str(x) for x in self.direction_y])}]")
        return "\n".join(lines)


class Beam:
    """
    Simplified solid body representation with an assigned 2D cross-section.

    Synchronizes to a design within a supporting geometry service instance.

    Parameters
    ----------
    id : str
        A server defined identifier for the body.
    name : str
        A user-defined label for the body.
    start : Point3D
        The start of the beam line segment.
    end : Point3D
        The end of the beam line segment.
    profile : BeamProfile
        The beam profile used to create the Beam.
    parent_component : Component
        The parent component to nest the new beam under within the design assembly.
    """

    def __init__(
        self,
        id: str,
        start: Point3D,
        end: Point3D,
        profile: BeamProfile,
        parent_component: "Component",
    ):
        """Constructor method for ``Beam``."""
        # Sanity checks - cannot check Component due to circular import issues
        check_type(id, str)
        check_type(start, Point3D)
        check_type(end, Point3D)
        check_type(profile, BeamProfile)

        self._id = id
        self._parent_component = parent_component
        self._start = start
        self._end = end
        self._profile = profile

    @property
    def id(self) -> str:
        """Geometry Service defined Id of the ``Beam``."""
        return self._id

    @property
    def start(self) -> Point3D:
        """The start of the beam line segment."""
        return self._start

    @property
    def end(self) -> Point3D:
        """The end of the beam line segment."""
        return self._end

    @property
    def profile(self) -> BeamProfile:
        """The beam profile of the beam line segment."""
        return self._profile

    @property
    def parent_component(self) -> Union["Component", None]:
        """Component node the ``Beam`` is under."""
        return self._parent_component

    def __repr__(self) -> str:
        """String representation of the beam."""
        lines = [f"ansys.geometry.core.designer.Beam {hex(id(self))}"]
        lines.append(
            f"  Start                : [{','.join([str(x) for x in self.start])}] in meters"
        )
        lines.append(f"  End                  : [{','.join([str(x) for x in self.end])}] in meters")
        lines.append(f"  Parent component     : {self.parent_component.name}")
        lines.extend(["\n", "  Beam Profile info", "  -----------------", str(self.profile)])
        return "\n".join(lines)
