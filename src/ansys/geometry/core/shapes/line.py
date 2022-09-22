"""``Line`` and ``Segment`` class module."""
from typing import List, Optional, Union

import numpy as np
from pint import Unit

from ansys.geometry.core.math import Plane, Point, QuantityVector, UnitVector, Vector
from ansys.geometry.core.misc import (
    UNIT_LENGTH,
    UNITS,
    check_ndarray_is_all_nan,
    check_ndarray_is_non_zero,
    check_pint_unit_compatibility,
    check_type,
)
from ansys.geometry.core.shapes.base import BaseShape


class Line(BaseShape):
    """
    Provides Line representation within a sketch environment.

    Parameters
    ----------
    plane : Plane
        A :class:`Plane` representing the planar surface where the shape is contained.
    start: Point
        Starting point of the line.
    direction: Union[Vector, UnitVector]
        Direction of the line.

    Note
    ----
    The proposed line should be contained inside the given plane. Otherwise,
    the construction of this object will not be possible (it will raise an error).
    """

    def __init__(
        self,
        plane: Plane,
        start: Point,
        direction: Union[Vector, UnitVector],
    ):
        """Initializes the line shape."""
        # Call the BaseShape ctor.
        super().__init__(plane, is_closed=False)

        # Perform some sanity checks
        check_type(direction, Vector)
        check_type(start, Point)
        check_ndarray_is_non_zero(direction, "direction")
        check_ndarray_is_all_nan(start, "start")

        # If a Vector was provided, we should store a UnitVector
        try:
            check_type(direction, UnitVector)
        except TypeError:
            direction = UnitVector(direction)

        # Store instance attributes
        self._direction = direction
        self._start = start

        # Check if the line definition is consistent with the provided plane
        if not self.__is_contained_in_plane():
            raise ValueError("The provided line definition is not contained in the plane.")

    @property
    def origin(self) -> Point:
        """The origin property."""
        return self._start

    @property
    def direction(self) -> UnitVector:
        """Returns the direction of the line."""
        return self._direction

    @property
    def start(self) -> Point:
        """Returns the starting point of the line."""
        return self._start

    @property
    def components(self) -> List["BaseShape"]:
        """Returns a list containing all simple geometries forming the shape.

        Returns
        -------
        List[BaseShape]
            A list of component geometries forming the shape.
        """
        return [self]

    def __is_contained_in_plane(self) -> bool:
        """Private method for checking if the line definition is contained in
        the plane provided

        Returns
        -------
        bool
            Returns ``True`` if the line defined is contained in the plane.
        """
        # First check if the point is contained in the plane
        if not self._plane.is_point_contained(self._start):
            return False

        # Then, check if direction is linearly dependent or not from
        # i and j (the vectors defining your plane)
        mat = np.array([self.direction, self.plane.direction_x, self.plane.direction_y])
        (lambdas, _) = np.linalg.eig(mat.T)
        return True if any(np.isclose(lambdas, 0.0)) else False

    def local_points(self, num_points: Optional[int] = 100) -> List[Point]:
        """
        Returns a list containing all the points belonging to the shape.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point]
            A list of points representing the shape.
        """
        quantified_dir = UNITS.convert(self.direction, self.start.unit, self.start.base_unit)
        line_start = self.start - quantified_dir * int(num_points / 2)
        return [Point(line_start + delta * quantified_dir) for delta in range(0, num_points)]

    def points(self, num_points: Optional[int] = 100) -> List[Point]:
        """Returns a list containing all the points belonging to the shape.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point]
            A list of points representing the shape.
        """
        return self.plane.origin + self.local_points(num_points)


class Segment(Line):
    """
    Provides Segment representation of a Line.

    Parameters
    ----------
    plane : Plane
        A :class:`Plane` representing the planar surface where the shape is contained.
    start: Point
        Start of the line segment.
    end: Point
        End of the line segment.
    """

    def __init__(
        self,
        plane: Plane,
        start: Point,
        end: Point,
    ):
        """Constructor method for ``Segment``."""
        # Perform sanity checks on Point values given
        check_type(start, Point)
        check_ndarray_is_all_nan(start, "start")
        check_type(end, Point)
        check_ndarray_is_all_nan(end, "end")

        # Assign values to start and end
        self._start = start
        self._end = end

        # Check segment points values and units
        self.__check_invalid_segment_points()
        self.__rebase_point_units()

        # Build the direction vector
        direction = UnitVector(end - start)

        # Call the super ctor (i.e. Line).
        super().__init__(plane, start, direction)

    @property
    def end(self) -> Point:
        """Returns the end of the ``Segment``."""
        return self._end

    @property
    def components(self) -> List["BaseShape"]:
        """Returns a list containing all simple geometries forming the shape.

        Returns
        -------
        List[BaseShape]
            A list of component geometries forming the shape.
        """
        return [self]

    @classmethod
    def from_start_point_and_vector(
        cls,
        start: Point,
        vector: Vector,
        vector_units: Optional[Unit] = UNIT_LENGTH,
        plane: Optional[Plane] = Plane(),
    ):
        """Create a ``Segment`` from a starting ``Point`` and a vector.

        Parameters
        ----------
        start : Point
            Start of the line segment.
        vector : Vector
            Vector defining the line segment.
        vector_units : ~pint.Unit, optional
            The length units of the vector, by default ``UNIT_LENGTH``.
        plane : Plane, optional
            A :class:`Plane` representing the planar surface where the shape is contained.

        Returns
        -------
        Segment
            The ``Segment`` object resulting from the inputs.
        """
        check_type(vector_units, Unit)
        check_pint_unit_compatibility(vector_units, UNIT_LENGTH)
        end_vec_as_point = Point(vector, vector_units)
        end_vec_as_point += start

        return cls(plane, start, end_vec_as_point)

    @classmethod
    def from_start_point_and_quantity_vector(
        cls,
        start: Point,
        quantity_vector: QuantityVector,
        plane: Optional[Plane] = Plane(),
    ):
        """Create a ``Segment`` from a starting ``Point`` and a vector.

        Parameters
        ----------
        start : Point
            Start of the line segment.
        quantity_vector : QuantityVector
            QuantityVector defining the line segment (with units).
        plane : Plane, optional
            A :class:`Plane` representing the planar surface where the shape is contained.
            By default, the base XY-Plane.

        Returns
        -------
        Segment
            The ``Segment`` object resulting from the inputs.
        """
        check_type(quantity_vector, QuantityVector)
        return Segment.from_start_point_and_vector(
            start=start,
            vector=quantity_vector,
            vector_units=quantity_vector.base_unit,
            plane=plane,
        )

    def __check_invalid_segment_points(self):
        """Check that the start and end points are not the same."""
        if self._start == self._end:
            raise ValueError(
                "Parameters 'start' and 'end' have the same values. No segment can be created."
            )

    def __rebase_point_units(self):
        """Check that the start and end points are in the same units.

        Note
        ----
        If they are not, they will be rebased to ``UNIT_LENGTH``.
        """
        if not self._start.unit == self._end.unit:
            self._start.unit = self._end.unit = UNIT_LENGTH

    def local_points(self, num_points: Optional[int] = 100) -> List[Point]:
        """
        Returns a list containing all the points belonging to the shape.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point]
            A list of points representing the shape.
        """
        start = Point(
            self.plane.global_to_local @ (self.start - self.plane.origin), self.start.unit
        )

        end = Point(self.plane.global_to_local @ (self.end - self.plane.origin), self.end.unit)

        delta_segm = (end - start) / (num_points - 1)
        return [Point(start + delta * delta_segm) for delta in range(0, num_points)]

    def points(self, num_points: Optional[int] = 100) -> List[Point]:
        """Returns a list containing all the points belonging to the shape.

        Parameters
        ----------
        num_points : int, optional
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point]
            A list of points representing the shape.
        """
        return self.local_points(num_points)
