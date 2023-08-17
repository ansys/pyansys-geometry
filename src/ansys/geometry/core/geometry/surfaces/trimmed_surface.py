"""Provides the ``TrimmedSurface`` class."""

from beartype.typing import TYPE_CHECKING
from pint import Quantity

from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.geometry.box_uv import BoxUV
from ansys.geometry.core.geometry.parameterization import Interval, ParamUV
from ansys.geometry.core.geometry.surfaces.surface_evaluation import SurfaceEvaluation
from ansys.geometry.core.math import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:
    from ansys.geometry.core.designer.face import Face


class TrimmedSurface:
    """TrimmedSurface class."""

    def __init__(self, desFace: "Face") -> None:
        """Construct the TrimmedSurface using the Face object argument."""
        self.face = desFace

    @property
    @protect_grpc
    def area(self) -> Quantity:
        """Calculated area of the face."""
        self.face._grpc_client.log.debug("Requesting face area from server.")
        area_response = self.face._faces_stub.GetArea(self.face._grpc_id)
        return Quantity(area_response.area, DEFAULT_UNITS.SERVER_AREA)

    @property
    def boxUV(self) -> BoxUV:
        """Calculated box UV of the face."""
        self.face._grpc_client.log.debug("Requesting box UV from server.")
        box_response = self.face._faces_stub.GetBoxUV(self.face._grpc_id)
        startU = box_response.start_u
        endU = box_response.end_u
        startV = box_response.start_v
        endV = box_response.end_v
        return BoxUV(Interval(startU, endU), Interval(startV, endV))

    def normal(self, u: float = 0.5, v: float = 0.5) -> UnitVector3D:
        """
        Get the normal direction to the face evaluated at certain UV coordinates.

        Notes
        -----
        To properly use this method, you must handle UV coordinates. Thus, you must
        know how these relate to the underlying Geometry service. It is an advanced
        method for Geometry experts only.

        Parameters
        ----------
        u : float, default: 0.5
            First coordinate of the 2D representation of a surface in UV space.
            The default is the center of the surface.
        v : float, default: 0.5
            Second coordinate of the 2D representation of a surface in UV space.
            The default is the center of the surface.

        Returns
        -------
        UnitVector3D
            The :class:`UnitVector3D <ansys.geometry.core.math.vector.unitVector3D>`
            object evaluated at the given U and V coordinates.
            This :class:`UnitVector3D <ansys.geometry.core.math.vector.unitVector3D>`
            object is perpendicular to the surface at the given UV coordinates.
        """
        direction = self.eval_proportions(u, v).normal
        if self.face.is_reversed:
            return UnitVector3D([-direction.x, -direction.y, -direction.z])
        return UnitVector3D([direction.x, direction.y, direction.z])

    def project_point(self, point: Point3D):
        """Project a point to the face."""
        boundsU = self.boxUV.IntervalU
        boundsV = self.boxUV.IntervalV
        params = self.face.surface.project_point(point).parameter
        u = params.u
        v = params.v
        return (
            (u - boundsU.start) / boundsU.get_span(),
            (v - boundsV.start) / boundsV.get_span(),
        )

    def eval_proportions(self, proportionU: Real, proportionV: Real) -> SurfaceEvaluation:
        """Evaluate the surface at a given u and v value."""
        boundsU = self.boxUV.IntervalU
        boundsV = self.boxUV.IntervalV
        return self.face.surface.evaluate(
            ParamUV(
                boundsU.start + boundsU.get_span() * proportionU,
                boundsV.start + boundsV.get_span() * proportionV,
            )
        )
