from beartype import beartype as check_input_types

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.typing import Real


class ParamUV:
    """
    Parameter class containing 2 parameters: (u,v).
    Used in surface evaluations.
    """

    def __init__(self, u: Real = None, v: Real = None) -> None:
        self._u = u
        self._v = v

    @property
    def u(self) -> Real:
        return self._u

    @property
    def v(self) -> Real:
        return self._v

    def is_set(self) -> bool:
        return self._u is not None and self._v is not None

    @check_input_types
    def __add__(self, other: "ParamUV") -> "ParamUV":
        self._u += other._u
        self._v += other._v

    @check_input_types
    def __sub__(self, other: "ParamUV") -> "ParamUV":
        self._u -= other._u
        self._v -= other._v

    @check_input_types
    def __mul__(self, other: "ParamUV") -> "ParamUV":
        self._u *= other._u
        self._v *= other._v

    @check_input_types
    def __truediv__(self, other: "ParamUV") -> "ParamUV":
        self._u /= other._u
        self._v /= other._v


class SurfaceEvaluation:
    """Provides result class when evaluating a surface."""

    def __init__(self, parameter: ParamUV = None) -> None:
        self._parameter = parameter

    def is_set(self) -> bool:
        """Returns whether or not the parameter has been set."""
        return self._parameter.is_set()

    @property
    def parameter(self) -> Real:
        """The parameter that the evaluation is based upon."""
        raise NotImplementedError("Each evaluation must provide the parameter definition.")

    def position(self) -> Point3D:
        """The position of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the position definition.")

    def normal(self) -> UnitVector3D:
        """The position of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the position definition.")

    def u_derivative(self) -> Vector3D:
        """The u-derivative of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the u-derivative definition.")

    def v_derivative(self) -> Vector3D:
        """The v-derivative of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the v-derivative definition.")

    def uu_derivative(self) -> Vector3D:
        """The uu-derivative of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the uu-derivative definition.")

    def uv_derivative(self) -> Vector3D:
        """The uv-derivative of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the uv-derivative definition.")

    def vv_derivative(self) -> Vector3D:
        """The vv-derivative of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the vv-derivative definition.")

    def min_curvature(self) -> Real:
        """The minimum curvature of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the minimum curvature definition.")

    def min_curvature_direction(self) -> UnitVector3D:
        """The minimum curvature direction of the evaluation."""
        raise NotImplementedError(
            "Each evaluation must provide the minimum curvature direction definition."
        )

    def max_curvature(self) -> Real:
        """The maximum curvature of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the maximum curvature definition.")

    def max_curvature_direction(self) -> UnitVector3D:
        """The maximum curvature direction of the evaluation."""
        raise NotImplementedError(
            "Each evaluation must provide the maximum curvature direction definition."
        )
