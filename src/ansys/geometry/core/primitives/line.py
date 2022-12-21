""" Provides the ``Line`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np

from ansys.geometry.core.math import Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc.accuracy import LENGTH_ACCURACY
from ansys.geometry.core.primitives.curve_evaluation import CurveEvaluation
from ansys.geometry.core.typing import RealSequence


class Line:
    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        direction: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
    ):

        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin
        self._direction = (
            UnitVector3D(direction) if not isinstance(direction, UnitVector3D) else direction
        )

    @property
    def origin(self) -> Point3D:
        """Origin of the line."""
        return self._origin

    @origin.setter
    @check_input_types
    def origin(self, origin: Point3D) -> None:
        """Set the origin of the circle"""
        self._origin = origin

    @property
    def direction(self) -> UnitVector3D:
        """Direction of the line."""
        return self._direction

    @direction.setter
    @check_input_types
    def direction(self, direction: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D]):
        self._direction = (
            UnitVector3D(direction) if not isinstance(direction, UnitVector3D) else direction
        )

    def __eq__(self, other: object) -> bool:
        """Equals operator for the ``Line`` class."""
        if isinstance(other, Line):
            return self._origin == other.origin and self._direction == other.direction
        return False

    def evaluate(self, parameter: float) -> "LineEvaluation":
        """Evaluates the line with the given parameter and returns the evaluation."""
        return LineEvaluation(self, parameter)

    def project_point(self, point: Point3D) -> "LineEvaluation":
        origin_to_point = point - self.origin
        t = origin_to_point.dot(self.direction)
        return LineEvaluation(self, t)

    def is_coincident_line(self, other: "Line") -> bool:
        """Returns True if both lines are coincident"""
        if self == other:
            return True
        if not self.direction.is_parallel_to(other.direction):
            return False

        between = Vector3D(
            [
                self.origin.x - other.origin.x,
                self.origin.y - other.origin.y,
                self.origin.z - other.origin.z,
            ]
        )
        return np.power((self.direction % between).magnitude, 2) <= np.power(
            LENGTH_ACCURACY, 2
        ) and np.power((self.direction % between).magnitude, 2) <= np.power(LENGTH_ACCURACY, 2)

    def is_opposite_line(self, other: "Line") -> bool:
        """Returns True if lines are opposite each other"""
        if self.is_coincident_line(other):
            return self.direction.is_opposite(other.direction)
        return False


class LineEvaluation(CurveEvaluation):
    def __init__(self, line: Line, parameter: float = None) -> None:
        self._line = line
        self._parameter = parameter

    @property
    def line(self) -> Line:
        return self._line

    @property
    def parameter(self) -> float:
        return self._parameter

    def position(self) -> Point3D:
        return self.line.origin + self.parameter * self.line.direction

    def tangent(self) -> UnitVector3D:
        return self.line.direction

    def first_derivative(self) -> Vector3D:
        return self.line.direction

    def second_derivative(self) -> Vector3D:
        return Vector3D([0, 0, 0])

    def curvature(self) -> float:
        return 0
