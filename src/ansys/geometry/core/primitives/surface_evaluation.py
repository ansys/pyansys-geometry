from beartype import beartype as check_input_types

from ansys.geometry.core.math import Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.typing import Real


class ParamUV:
    """
    Parameter class containing 2 parameters: (u, v). Likened to a 2D point in UV space
    Used as an argument in parametric surface evaluations. This matches the service
    implementation for the Geometry Service.

    Parameters
    ----------
    u : Real
        u-parameter.
    v : Real
        v-parameter.
    """

    def __init__(self, u: Real, v: Real) -> None:
        self._u = u
        self._v = v

    @property
    def u(self) -> Real:
        """u-parameter."""
        return self._u

    @property
    def v(self) -> Real:
        """v-parameter."""
        return self._v

    @check_input_types
    def __add__(self, other: "ParamUV") -> "ParamUV":
        """Adds the u and v components of the other ParamUV to this ParamUV."""
        self._u += other._u
        self._v += other._v

    @check_input_types
    def __sub__(self, other: "ParamUV") -> "ParamUV":
        """Subtracts the u and v components of the other ParamUV from this ParamUV."""
        self._u -= other._u
        self._v -= other._v

    @check_input_types
    def __mul__(self, other: "ParamUV") -> "ParamUV":
        """Multiplies the u and v components of this ParamUV by the other ParamUV."""
        self._u *= other._u
        self._v *= other._v

    @check_input_types
    def __truediv__(self, other: "ParamUV") -> "ParamUV":
        """Divides the u and v components of this ParamUV by the other ParamUV."""
        self._u /= other._u
        self._v /= other._v


class SurfaceEvaluation:
    """Provides result class when evaluating a surface."""

    def __init__(self, parameter: ParamUV) -> None:
        self._parameter = parameter

    @property
    def parameter(self) -> Real:
        """The parameter that the evaluation is based upon."""
        raise NotImplementedError("Each evaluation must provide the parameter definition.")

    def position(self) -> Point3D:
        """The point on the surface, based on the evaluation."""
        raise NotImplementedError("Each evaluation must provide the position definition.")

    def normal(self) -> UnitVector3D:
        """The normal to the surface."""
        raise NotImplementedError("Each evaluation must provide the position definition.")

    def u_derivative(self) -> Vector3D:
        """The first derivative with respect to u."""
        raise NotImplementedError("Each evaluation must provide the u-derivative definition.")

    def v_derivative(self) -> Vector3D:
        """The first derivative with respect to v."""
        raise NotImplementedError("Each evaluation must provide the v-derivative definition.")

    def uu_derivative(self) -> Vector3D:
        """The second derivative with respect to u."""
        raise NotImplementedError("Each evaluation must provide the uu-derivative definition.")

    def uv_derivative(self) -> Vector3D:
        """The second derivative with respect to u and v."""
        raise NotImplementedError("Each evaluation must provide the uv-derivative definition.")

    def vv_derivative(self) -> Vector3D:
        """The second derivative with respect to v."""
        raise NotImplementedError("Each evaluation must provide the vv-derivative definition.")

    def min_curvature(self) -> Real:
        """The minimum curvature."""
        raise NotImplementedError("Each evaluation must provide the minimum curvature definition.")

    def min_curvature_direction(self) -> UnitVector3D:
        """The minimum curvature direction."""
        raise NotImplementedError(
            "Each evaluation must provide the minimum curvature direction definition."
        )

    def max_curvature(self) -> Real:
        """The maximum curvature."""
        raise NotImplementedError("Each evaluation must provide the maximum curvature definition.")

    def max_curvature_direction(self) -> UnitVector3D:
        """The maximum curvature direction."""
        raise NotImplementedError(
            "Each evaluation must provide the maximum curvature direction definition."
        )
