from ansys.api.geometry.v0.repairtools_pb2 import FixSplitEdgesRequest
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from google.protobuf.wrappers_pb2 import Int32Value

from ansys.geometry.core.connection import GrpcClient


class SplitEdgeProblemAreas:
    """
    Represents a split edge problem area with unique identifier and associated edges.

    Attributes:
        _id (str): A unique identifier for the problem area.
        _design_edges (list[str]): A list of edges associated with the design.
    """

    def __init__(self, id: str, design_edges: list[str]):
        self._id = id
        self._design_edges = design_edges

    @property
    def id(self) -> str:
        """The id of the problem area."""
        return self._id

    @property
    def design_edges(self) -> list[str]:
        """The list of the ids of the edges connected to this problem area."""
        return self._design_edges

    def Fix(self):
        """Fix the problem area."""
        client = GrpcClient()
        id_value = Int32Value(value=int(self._id))
        result = RepairToolsStub(client.channel).FixSplitEdges(
            FixSplitEdgesRequest(split_edge_problem_area_id=id_value)
        )
