from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import Vector3D


class CurveEvaluation:
    def __init__(self, parameter: float = None) -> None:
        self._parameter = parameter

    def is_set(self) -> bool:
        return self.param is not None

    @property
    def parameter(self) -> float:
        return self._parameter

    def position(self) -> Point3D:
        return Point3D([0, 0, 0])

    def first_derivative(self) -> Vector3D:
        return Vector3D([0, 0, 0])

    def second_derivative(self) -> Vector3D:
        return Vector3D([0, 0, 0])

    def curvature(self) -> float:
        return 0
