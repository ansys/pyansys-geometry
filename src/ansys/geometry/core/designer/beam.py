"""``Beam`` class module."""

from typing import TYPE_CHECKING, List, Union

import numpy as np
from pint import Quantity

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

        if not self._direction_x.is_perpendicular_to(self._direction_y):
            raise ValueError("Direction x and direction y must be perpendicular.")

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
        return self._direction_x

    @property
    def direction_y(self) -> UnitVector3D:
        """Returns the Y-axis direction of the ``BeamCircularProfile``."""
        return self._direction_y

    def __repr__(self) -> str:
        """String representation of the circular beam profile."""
        lines = [f"ansys.geometry.core.designer.BeamCircularProfile {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Radius               : {self.radius}")
        lines.append(f"  Center               : {self.center}")
        lines.append(f"  Direction x          : {self.direction_x}")
        lines.append(f"  Direction y          : {self.direction_y}")
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
    def start(self) -> str:
        """The start of the beam line segment."""
        return self._start

    @property
    def end(self) -> str:
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
        lines.append(f"  Start                : {self.start}")
        lines.append(f"  End                  : {self.end}")
        lines.append(f"  Profile              : {self.profile.name}")
        lines.append(f"  Parent component     : {self.parent_component.name}")
        return "\n".join(lines)
