from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import Vector3D
from ansys.geometry.core.typing import Real


class CurveEvaluation:
    """Provides result class when evaluating a curve"""

    def __init__(self, parameter: float = None) -> None:
        self._parameter = parameter

    def is_set(self) -> bool:
        """Returns whether or not the parameter has been set"""
        return self._parameter is not None

    @property
    def parameter(self) -> Real:
        """The parameter that the evaluation is based upon"""
        raise NotImplementedError("Each evaluation must provide the parameter definition.")

    def position(self) -> Point3D:
        """The position of the evaluation"""
        raise NotImplementedError("Each evaluation must provide the position definition.")

    def first_derivative(self) -> Vector3D:
        """The first derivative of the evaluation"""
        raise NotImplementedError("Each evaluation must provide the first_derivative definition.")

    def second_derivative(self) -> Vector3D:
        """The second derivative of the evaluation"""
        raise NotImplementedError("Each evaluation must provide the second_derivative definition.")

    def curvature(self) -> Real:
        """The curvature of the evaluation"""
        raise NotImplementedError("Each evaluation must provide the curvature definition.")
