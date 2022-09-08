"""``Line`` and ``Segment`` class module."""
from typing import List, Optional, Union

import numpy as np
from pint import Unit

from ansys.geometry.core import UNIT_LENGTH, UNITS
from ansys.geometry.core.math import UNIT_VECTOR_X, UNIT_VECTOR_Y
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import QuantityVector3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc.checks import (
    check_is_pint_unit,
    check_is_point,
    check_is_quantityvector,
    check_is_unitvector,
    check_is_vector,
    check_ndarray_is_non_zero,
    check_ndarray_is_not_none,
    check_pint_unit_compatibility,
)
from ansys.geometry.core.shapes.base import BaseShape

# TODO: Line at the moment is not a BaseShape...


class Line(BaseShape):
    """
    Provides Line representation within a sketch environment.

    Parameters
    ----------
    origin: Point3D
        Origin of the line.
    direction: Union[Vector3D, UnitVector3D]
        Direction of the line.
    dir_1 : Optional[UnitVector3D]
        A :class:`UnitVector3D` representing the first fundamental direction
        of the reference plane where the shape is contained.
        By default, ``UNIT_VECTOR_X``.
    dir_2 : Optional[UnitVector3D]
        A :class:`UnitVector3D` representing the second fundamental direction
        of the reference plane where the shape is contained.
        By default, ``UNIT_VECTOR_Y``.

    Note
    ----
    The way in which the Sketching plane for the line is defined, is such that
    we first check if our direction is linearly dependent of ``dir_1`` and ``dir_2``.
    If ``True`` then we can define our BaseShape with ``dir_1`` and ``dir_2``. Otherwise,
    it will be necessary to define the BaseShape using the Line direction and another
    one of the directions. ``dir_2`` will be selected in this case.
    """

    def __init__(
        self,
        origin: Point3D,
        direction: Union[Vector3D, UnitVector3D],
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
    ):
        """Initializes the line shape."""
        # Perform some sanity checks
        check_is_vector(direction, "direction", only_3d=True)
        check_ndarray_is_non_zero(direction, "direction")

        # If a Vector3D was provided, we should store a UnitVector3D
        try:
            check_is_unitvector(direction, "direction", only_3d=True)
        except TypeError:
            direction = UnitVector3D(direction)

        # Store instance attributes
        self._direction = direction

        # Call base ctor. Directions used are based on linear dependency and orthogonality.
        if self._is_linearly_dependent(direction, dir_1, dir_2):
            super().__init__(origin, dir_1=dir_1, dir_2=dir_2, is_closed=False)
        else:
            super().__init__(origin, dir_1=direction, dir_2=dir_2, is_closed=False)

    @property
    def direction(self) -> UnitVector3D:
        """Returns the direction of the line."""
        return self._direction

    def _is_linearly_dependent(
        self, direction: UnitVector3D, dir_1: UnitVector3D, dir_2: UnitVector3D
    ) -> bool:
        """Private method for checking if the provided directions are linearly dependent.

        Parameters
        ----------
        direction : UnitVector3D
            The line's direction vector as a :class:`UnitVector3D`.
        dir_1 : UnitVector3D
            A :class:`UnitVector3D` representing the first fundamental direction
            of the reference plane where the shape is contained.
        dir_2 : UnitVector3D
            A :class:`UnitVector3D` representing the second fundamental direction
            of the reference plane where the shape is contained.

        Returns
        -------
        bool
            ``True`` if the three are linearly dependent, ``False`` otherwise.
        """
        # Check if direction is linearly dependent or not from dir_1 and dir_2
        mat = np.array([direction, dir_1, dir_2])
        (lambdas, _) = np.linalg.eig(mat.T)
        return True if any(np.isclose(lambdas, 0.0)) else False

    def local_points(self, num_points: Optional[int] = 100) -> List[Point3D]:
        """
        Returns a list containing all the points belonging to the shape.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point3D]
            A list of points representing the shape.
        """
        quantified_dir = UNITS.convert(self.direction, self.origin.unit, self.origin.base_unit)
        line_start = self.origin - quantified_dir * int(num_points / 2)
        return [line_start + delta * quantified_dir for delta in range(0, num_points)]


class Segment(Line):
    """
    Provides Segment representation of a Line.

    Parameters
    ----------
    start: Point3D
        Start of the line segment.
    end: Point3D
        End of the line segment.
    dir_1 : Optional[UnitVector3D]
        A :class:`UnitVector3D` representing the first fundamental direction
        of the reference plane where the shape is contained.
        By default, ``UNIT_VECTOR_X``.
    dir_2 : Optional[UnitVector3D]
        A :class:`UnitVector3D` representing the second fundamental direction
        of the reference plane where the shape is contained.
        By default, ``UNIT_VECTOR_Y``.
    """

    def __init__(
        self,
        start: Point3D,
        end: Point3D,
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
    ):
        """Constructor method for ``Segment``."""
        # Perform sanity checks on Point3D values given
        check_is_point(start, "start", only_3d=True)
        check_ndarray_is_not_none(start, "start")
        check_is_point(end, "end", only_3d=True)
        check_ndarray_is_not_none(end, "end")

        # Assign values to start and end
        self._origin = start
        self._end = end

        # Check segment points values and units
        self._check_invalid_segment_points()
        self._rebase_point_units()

        # Build the direction vector
        direction = UnitVector3D(end - start)

        # Call the super ctor (i.e. Line).
        super().__init__(start, direction, dir_1=dir_1, dir_2=dir_2)

    @classmethod
    def from_origin_and_vector(
        cls,
        origin: Point3D,
        vector: Vector3D,
        vector_units: Optional[Unit] = UNIT_LENGTH,
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
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
        dir_1 : Optional[UnitVector3D]
            A :class:`UnitVector3D` representing the first fundamental direction
            of the reference plane where the shape is contained.
            By default, ``UNIT_VECTOR_X``.
        dir_2 : Optional[UnitVector3D]
            A :class:`UnitVector3D` representing the second fundamental direction
            of the reference plane where the shape is contained.
            By default, ``UNIT_VECTOR_Y``.

        Returns
        -------
        Segment
            The ``Segment`` object resulting from the inputs.
        """
        check_is_pint_unit(vector_units, "vector_units")
        check_pint_unit_compatibility(vector_units, UNIT_LENGTH)
        end_vec_as_point = Point3D(vector, vector_units)
        end_vec_as_point += origin

        return cls(origin, end_vec_as_point, dir_1=dir_1, dir_2=dir_2)

    @classmethod
    def from_origin_and_quantity_vector(
        cls,
        origin: Point3D,
        quantity_vector: QuantityVector3D,
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
    ):
        """Create a ``Segment`` from an origin and a vector.

        Parameters
        ----------
        origin : Point3D
            Start of the line segment.
        quantity_vector : QuantityVector3D
            QuantityVector defining the line segment (with units).
        dir_1 : Optional[UnitVector3D]
            A :class:`UnitVector3D` representing the first fundamental direction
            of the reference plane where the shape is contained.
            By default, ``UNIT_VECTOR_X``.
        dir_2 : Optional[UnitVector3D]
            A :class:`UnitVector3D` representing the second fundamental direction
            of the reference plane where the shape is contained.
            By default, ``UNIT_VECTOR_Y``.

        Returns
        -------
        Segment
            The ``Segment`` object resulting from the inputs.
        """
        check_is_quantityvector(quantity_vector)
        return Segment.from_origin_and_vector(
            origin=origin,
            vector=quantity_vector,
            vector_units=quantity_vector.base_unit,
            dir_1=dir_1,
            dir_2=dir_2,
        )

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

    @property
    def end(self) -> Point3D:
        """Returns the end of the ``Segment``."""
        return self._end

    def local_points(self, num_points: Optional[int] = 100) -> List[Point3D]:
        """
        Returns a list containing all the points belonging to the shape.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point3D]
            A list of points representing the shape.
        """
        delta_segm = (self.end - self.start) / (num_points - 1)
        return [self.start + delta * delta_segm for delta in range(0, num_points)]
