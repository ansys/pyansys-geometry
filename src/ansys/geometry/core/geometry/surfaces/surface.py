"""Provides the ``Surface`` class."""
from abc import ABC, abstractmethod

from ansys.geometry.core.geometry.parameterization import Parameterization, ParamUV
from ansys.geometry.core.geometry.surfaces.surface_evaluation import SurfaceEvaluation
from ansys.geometry.core.math import Matrix44, Point3D


class Surface(ABC):
    """
    Surface abstract base class.

    Represents a 3D surface.
    """

    @abstractmethod
    def parameterization(self) -> tuple[Parameterization, Parameterization]:
        """Parameterization of the surface as a tuple (U and V respectively)."""
        return

    @abstractmethod
    def contains_param(self, param_uv: ParamUV) -> bool:
        """Test whether a parameter is within the parametric range of the surface."""
        return

    @abstractmethod
    def contains_point(self, point: Point3D) -> bool:
        """
        Test whether the point is contained by the surface.

        The point can either lie within it, or on its boundary.
        """
        return

    @abstractmethod
    def transformed_copy(self, matrix: Matrix44) -> "Surface":
        """Create a transformed copy of the surface."""
        return

    @abstractmethod
    def __eq__(self, other: "Surface") -> bool:
        """Determine if two surfaces are equal."""
        return

    @abstractmethod
    def evaluate(self, parameter: ParamUV) -> SurfaceEvaluation:
        """Evaluate the surface at the given parameter."""
        return

    @abstractmethod
    def project_point(self, point: Point3D) -> SurfaceEvaluation:
        """
        Project a point to the surface.

        This returns the evaluation at the closest point.
        """
        return

    # TODO: Implement more surface methods
    # is_ruled
    # is_singular
    # get_length
    # intersect_curve
    # intersect_surface
    # is_coincident
