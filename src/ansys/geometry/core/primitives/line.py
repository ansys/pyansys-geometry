"""Provides the ``Line`` class."""

from functools import cached_property
import math

from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np

from ansys.geometry.core.math import Matrix44, Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc.accuracy import LENGTH_ACCURACY
from ansys.geometry.core.primitives.curve_evaluation import CurveEvaluation
from ansys.geometry.core.primitives.parameterization import (
    Interval,
    Parameterization,
    ParamForm,
    ParamType,
)
from ansys.geometry.core.typing import RealSequence


class Line:
    """
    Provides 3D ``Line`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Origin of the line.
    direction : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Direction of the line.
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        direction: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
    ):
        """Initialize the ``Line`` class."""
        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin
        self._direction = (
            UnitVector3D(direction) if not isinstance(direction, UnitVector3D) else direction
        )

    @property
    def origin(self) -> Point3D:
        """Origin of the line."""
        return self._origin

    @property
    def direction(self) -> UnitVector3D:
        """Direction of the line."""
        return self._direction

    def __eq__(self, other: object) -> bool:
        """Equals operator for the ``Line`` class."""
        if isinstance(other, Line):
            return self._origin == other.origin and self._direction == other.direction
        return False

    def evaluate(self, parameter: float) -> "LineEvaluation":
        """
        Evaluate the line at the given parameter.

        Parameters
        ----------
        parameter : Real
            The parameter at which to evaluate the line.

        Returns
        -------
        LineEvaluation
            The resulting evaluation.
        """
        return LineEvaluation(self, parameter)

    def transformed_copy(self, matrix: Matrix44) -> "Line":
        """
        Create a transformed copy of the line based on a transformation matrix.

        Parameters
        ----------
        matrix : Matrix44
            The transformation matrix to apply to the line.

        Returns
        -------
        Line
            A new line that is the transformed copy of the original line.
        """
        old_origin_4d = np.array([[self.origin[0]], [self.origin[1]], [self.origin[2]], [1]])
        new_origin_4d = matrix * old_origin_4d
        new_point = Point3D([new_origin_4d[0], new_origin_4d[1], new_origin_4d[2]])
        new_axis = matrix * np.append(self._direction, 0)
        return Line(new_point, UnitVector3D(new_axis[0:3]))

    def project_point(self, point: Point3D) -> "LineEvaluation":
        """
        Project a point onto the line and return its ``LineEvaluation``.

        Parameters
        ----------
        point : Point3D
            The point to project onto the line.

        Returns
        -------
        LineEvaluation
            The resulting evaluation.
        """
        origin_to_point = point - self.origin
        t = origin_to_point.dot(self.direction)
        return LineEvaluation(self, t)

    def is_coincident_line(self, other: "Line") -> bool:
        """
        Determine if this line is coincident with another.

        Parameters
        ----------
        other : Line
            The line to determine coincidence with.

        Returns
        -------
        bool
            Returns ``True`` if this line is coincident with the other.
        """
        if self == other:
            return True
        if not self.direction.is_parallel_to(other.direction):
            return False

        between = Vector3D(self.origin - other.origin)

        return math.pow((self.direction % between).magnitude, 2) <= math.pow(
            LENGTH_ACCURACY, 2
        ) and math.pow((self.direction % between).magnitude, 2) <= math.pow(LENGTH_ACCURACY, 2)

    def is_opposite_line(self, other: "Line") -> bool:
        """
        Determine if this line is opposite another.

        Parameters
        ----------
        other : Line
            The line to determine opposition with.

        Returns
        -------
        bool
            Returns ``True`` if this line is opposite to the other.
        """
        if self.is_coincident_line(other):
            return self.direction.is_opposite(other.direction)
        return False

    def get_parameterization(self) -> Parameterization:
        """
        Return the parametrization of a ``Line`` instance.

        The parameter of a line specifies the distance from the `origin` in the
        direction of `direction`.

        Returns
        -------
        Parameterization
            Information about how a line is parameterized.
        """
        return Parameterization(ParamForm.OPEN, ParamType.LINEAR, Interval(np.NINF, np.inf))


class LineEvaluation(CurveEvaluation):
    """Provides result class when evaluating a line."""

    def __init__(self, line: Line, parameter: float = None) -> None:
        """``LineEvaluation`` class constructor."""
        self._line = line
        self._parameter = parameter

    @property
    def line(self) -> Line:
        """The line being evaluated."""
        return self._line

    @property
    def parameter(self) -> float:
        """The parameter that the evaluation is based upon."""
        return self._parameter

    @cached_property
    def position(self) -> Point3D:
        """
        The position of the evaluation.

        Returns
        -------
        Point3D
            The point that lies on the line at this evaluation.
        """
        return self.line.origin + self.parameter * self.line.direction

    @cached_property
    def tangent(self) -> UnitVector3D:
        """
        The tangent of the evaluation.

        This is always equal to the direction of the line.

        Returns
        -------
        UnitVector3D
            The tangent unit vector to the line at this evaluation.
        """
        return self.line.direction

    @cached_property
    def first_derivative(self) -> Vector3D:
        """
        The first derivative of the evaluation.

        This is always equal to the direction of the line.

        Returns
        -------
        Vector3D
            The first derivative of this evaluation.
        """
        return self.line.direction

    @cached_property
    def second_derivative(self) -> Vector3D:
        """
        The second derivative of the evaluation.

        This is always equal to a zero vector.

        Returns
        -------
        Vector3D
            The second derivative of this evaluation. Always ``Vector3D([0, 0, 0])``.
        """
        return Vector3D([0, 0, 0])

    @cached_property
    def curvature(self) -> float:
        """
        The curvature of the line.

        This will always be 0.

        Returns
        -------
        Real
            The curvature of the line. Always 0.
        """
        return 0
