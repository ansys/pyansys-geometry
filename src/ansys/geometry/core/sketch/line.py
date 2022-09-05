"""``Line`` and ``Segment`` class module."""
from io import UnsupportedOperation
from typing import Optional, Union

from pint import Unit

from ansys.geometry.core import UNIT_LENGTH
from ansys.geometry.core.misc.checks import (
    check_is_pint_unit,
    check_is_point,
    check_is_unitvector,
    check_is_vector,
    check_ndarray_is_non_none,
    check_ndarray_is_non_zero,
    check_pint_unit_compatibility,
)
from ansys.geometry.core.primitives.point import Point3D
from ansys.geometry.core.primitives.vector import UnitVector3D, Vector3D

# TODO: Line at the moment is not a SketchCurve... This will be modified when we
# have the Bounded/UnboundedCurve concepts. Line should extend from UnboundedCurve
# and Segment, from BoundedCurve and Line. Bounded/Unbounded curve should not have
# incompatible implementations. One should build on top of the other if possible.


class Line:
    """
    Create a Line shape.

    Parameters
    ----------
    origin: Point3D
        Origin of the line.
    direction: Union[Vector3D, UnitVector3D]
        Direction of the line.
    """

    def __init__(self, origin: Point3D, direction: Union[Vector3D, UnitVector3D]):
        """Constructor method for ``Line``."""
        # Perform some sanity checks
        check_is_point(origin, "origin", only_3d=True)
        check_ndarray_is_non_none(origin, "origin")
        check_is_vector(direction, "direction", only_3d=True)
        check_ndarray_is_non_zero(direction, "direction")

        # If a Vector3D was provided, we should store a UnitVector3D
        try:
            check_is_unitvector(direction, "direction", only_3d=True)
        except TypeError:
            direction = UnitVector3D(direction)

        # Store instance attributes
        self._origin = origin
        self._direction = direction

    @property
    def origin(self) -> Point3D:
        """Returns the origin of the ``Line``."""
        return self._origin

    @origin.setter
    def origin(self, origin: Point3D) -> None:
        """Set the origin of the ``Line``."""
        check_is_point(origin, "origin", only_3d=True)
        check_ndarray_is_non_none(origin, "origin")
        self._origin = origin

    @property
    def direction(self) -> UnitVector3D:
        """Returns the direction of the ``Line``."""
        return self._direction

    @direction.setter
    def direction(self, direction: Union[Vector3D, UnitVector3D]) -> None:
        """Set the direction of the ``Line``."""
        check_is_vector(direction, "direction", only_3d=True)
        check_ndarray_is_non_zero(direction, "direction")

        # If a Vector3D was provided, we should store a UnitVector3D
        try:
            check_is_unitvector(direction, "direction", only_3d=True)
        except TypeError:
            direction = UnitVector3D(direction)

        self._direction = direction


class Segment(Line):
    """
    Provides Segment representation of a Line.

    Parameters
    ----------
    start: Point3D
        Start of the line segment.
    end: Point3D
        End of the line segment.
    """

    def __init__(self, start: Point3D, end: Point3D):
        """Constructor method for ``Segment``."""
        # Perform sanity checks on Point3D values given
        check_is_point(start, "start", only_3d=True)
        check_ndarray_is_non_none(start, "start")
        check_is_point(end, "end", only_3d=True)
        check_ndarray_is_non_none(end, "end")

        # Assign values to origin and end
        self._origin = start
        self._end = end

        # Check segment points values and units
        self._check_invalid_segment_points()
        self._rebase_point_units()

        # Build the direction vector
        self._direction = UnitVector3D(end - start)

    @classmethod
    def from_origin_and_vector(
        cls, origin: Point3D, vector: Vector3D, vector_units: Optional[Unit] = UNIT_LENGTH
    ):
        """Create a ``Segment`` from an origin and a vector.

        Parameters
        ----------
        origin : Point3D
            Start of the line segment.
        vector : Vector3D
            Vector defining the line segment.
        vector_units : Optional[Unit], optional
            The length units of the vector, by default ``UNIT_LENGTH``.

        Returns
        -------
        Segment
            The ``Segment`` object resulting from the inputs.
        """
        check_is_pint_unit(vector_units, "vector_units")
        check_pint_unit_compatibility(vector_units, UNIT_LENGTH)
        end_vec_as_point = Point3D(vector, vector_units)
        end_vec_as_point += origin

        return cls(origin, end_vec_as_point)

    def _check_invalid_segment_points(self):
        """Check that the origin and end points are not the same."""
        if self._origin == self._end:
            raise ValueError(
                "Parameters 'origin' and 'end' have the same values. No segment can be created."
            )

    def _rebase_point_units(self):
        """Check that the origin and end points are in the same units.

        Note
        ----
        If they are not, they will be rebased to ``UNIT_LENGTH``.
        """
        if not self._origin.unit == self._end.unit:
            self._origin.unit = self._end.unit = UNIT_LENGTH

    @property
    def start(self) -> Point3D:
        """Returns the start of the ``Segment``."""
        return self.origin

    @start.setter
    def start(self, start) -> None:
        """Set the start of the ``Segment``."""
        # Call the parent setter
        self.origin = start

        # Check segment point values and units
        self._check_invalid_segment_points()
        self._rebase_point_units()

        # Recalculate direction
        self._direction = UnitVector3D(self.end - self.origin)

    @property
    def end(self) -> Point3D:
        """Returns the end of the ``Segment``."""
        return self._end

    @end.setter
    def end(self, end) -> None:
        """Set the end of the ``Segment``."""
        check_is_point(end, "end", only_3d=True)
        check_ndarray_is_non_none(end, "end")
        self._end = end

        # Check segment point values and units
        self._check_invalid_segment_points()
        self._rebase_point_units()

        # Recalculate direction
        self._direction = UnitVector3D(self.end - self.origin)

    @Line.direction.setter
    def direction(self, direction: Union[Vector3D, UnitVector3D]) -> None:
        raise UnsupportedOperation("Segment direction is unsettable.")
