from ansys.api.geometry.v0.edges_pb2_grpc import EdgesStub
from ansys.api.geometry.v0.models_pb2 import Edge
from ansys.api.geometry.v0.repairtools_pb2 import FixInexactEdgesRequest
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from google.protobuf.wrappers_pb2 import DoubleValue, Int32Value

from ansys.geometry.core.connection import GrpcClient


class InexactEdgeProblemAreas:
    """
    Represents an inexact edge problem area with unique identifier and associated edges.

    Attributes:
        _id (str): A unique identifier for the problem area.
        _design_edges (list[str]): A list of edges associated with the design.
    """

    def __init__(self, id: str, design_edges: list[str]):
        """
        Initialize a new instance of the inexact edge problem area class.

        :param id: A unique identifier for the design.
        :type id: str
        :param design_edges: A list of edges associated with the design.
        :type design_edges: list[str]
        """
        self.id = id
        self.design_edges = design_edges

    @property
    def id(self):
        """The id of the problem area."""
        return self._id

    @property
    def design_edges(self) -> list[str]:
        """The list of the ids of the edges connected to this problem area."""
        return self._design_edges

    def Fix(self):
        """Fixes the problem area."""
        client = GrpcClient()
        id_value = Int32Value(value=int(self._id))
        RepairToolsStub(client.channel).FixInexactEdges(
            FixInexactEdgesRequest(inexact_edge_problem_area_id=id_value)
        )
