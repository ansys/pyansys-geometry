"""Provides the ``SurfaceEvaluation`` class."""

from functools import cached_property

from ansys.geometry.core.math import Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.primitives.parameterization import ParamUV
from ansys.geometry.core.typing import Real


class SurfaceEvaluation:
    """Provides result class when evaluating a surface."""

    def __init__(self, parameter: ParamUV) -> None:
        """Initialize ``SurfaceEvaluation`` class."""
        self._parameter = parameter

    @property
    def parameter(self) -> Real:
        """The parameter that the evaluation is based upon."""
        raise NotImplementedError("Each evaluation must provide the parameter definition.")

    @cached_property
    def position(self) -> Point3D:
        """The point on the surface, based on the evaluation."""
        raise NotImplementedError("Each evaluation must provide the position definition.")

    @cached_property
    def normal(self) -> UnitVector3D:
        """The normal to the surface."""
        raise NotImplementedError("Each evaluation must provide the position definition.")

    @cached_property
    def u_derivative(self) -> Vector3D:
        """The first derivative with respect to u."""
        raise NotImplementedError("Each evaluation must provide the u-derivative definition.")

    @cached_property
    def v_derivative(self) -> Vector3D:
        """The first derivative with respect to v."""
        raise NotImplementedError("Each evaluation must provide the v-derivative definition.")

    @cached_property
    def uu_derivative(self) -> Vector3D:
        """The second derivative with respect to u."""
        raise NotImplementedError("Each evaluation must provide the uu-derivative definition.")

    @cached_property
    def uv_derivative(self) -> Vector3D:
        """The second derivative with respect to u and v."""
        raise NotImplementedError("Each evaluation must provide the uv-derivative definition.")

    @cached_property
    def vv_derivative(self) -> Vector3D:
        """The second derivative with respect to v."""
        raise NotImplementedError("Each evaluation must provide the vv-derivative definition.")

    @cached_property
    def min_curvature(self) -> Real:
        """The minimum curvature."""
        raise NotImplementedError("Each evaluation must provide the minimum curvature definition.")

    @cached_property
    def min_curvature_direction(self) -> UnitVector3D:
        """The minimum curvature direction."""
        raise NotImplementedError(
            "Each evaluation must provide the minimum curvature direction definition."
        )

    @cached_property
    def max_curvature(self) -> Real:
        """The maximum curvature."""
        raise NotImplementedError("Each evaluation must provide the maximum curvature definition.")

    @cached_property
    def max_curvature_direction(self) -> UnitVector3D:
        """The maximum curvature direction."""
        raise NotImplementedError(
            "Each evaluation must provide the maximum curvature direction definition."
        )
