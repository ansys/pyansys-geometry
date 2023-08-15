"""Trimmed curve class."""
from beartype.typing import TYPE_CHECKING
from pint import Quantity

from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.geometry.curves.curve_evaluation import CurveEvaluation
from ansys.geometry.core.geometry.parameterization import Interval
from ansys.geometry.core.math import Point3D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:
    from ansys.geometry.core.designer.edge import Edge


class TrimmedCurve:
    """TrimmedCurve class."""

    def __init__(self, desEdge: "Edge") -> None:
        """Construct the TrimmedCurve using the Edge object argument."""
        self.edge = desEdge

    @property
    @protect_grpc
    def length(self) -> Quantity:
        """Calculated length of the edge."""
        self.edge._grpc_client.log.debug("Requesting edge length from server.")
        length_response = self.edge._edges_stub.GetLength(self._grpc_id)
        return Quantity(length_response.length, DEFAULT_UNITS.SERVER_LENGTH)

    @property
    @protect_grpc
    def interval(self) -> Interval:
        """Calculated interval of the edge."""
        self.edge._grpc_client.log.debug("Requesting edge interval from server.")
        interva_response = self.edge._edges_stub.GetInterval(self.edge._grpc_id)
        return Interval(interva_response.start, interva_response.end)

    def evaluate(self, param: Real) -> Point3D:
        """Evaluate the curve with respect to the curve direction (reversed or not)."""
        eval = self.eval_proportion(param)
        if self.edge.is_reversed:
            eval = self.eval_proportion(1 - param)
        return eval.position

    def eval_proportion(self, param: Real) -> CurveEvaluation:
        """Evaluate the given curve at the given parameter."""
        bounds = self.interval
        return self.edge.curve.evaluate(bounds.start + bounds.get_span() * param)
