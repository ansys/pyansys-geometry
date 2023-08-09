from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from ansys.geometry.core.connection import GrpcClient
from ansys.api.geometry.v0.edges_pb2_grpc import EdgesStub
from ansys.api.geometry.v0.repairtools_pb2 import FixExtraEdgesRequest
from ansys.api.geometry.v0.models_pb2 import Edge
from google.protobuf.wrappers_pb2 import DoubleValue
from google.protobuf.wrappers_pb2 import Int32Value


class ExtraEdgeProblemAreas:
    """
    """
    def __init__(self, id, design_edges):
        self.id = id
        self.design_edges = design_edges

    @property
    def id(self):
        """
        The id of the problem area.
        """
        return self._id

    @property
    def design_edges(self):
        """
        The list of the edges connected to this problem area.
        """
        return self._design_edges
    
    def Fix(self):
        """
        The fix method for the problem area. 
        """
        client = GrpcClient()
        id_value = Int32Value(value=int(self.id))
        RepairToolsStub(client.channel).FixExtraEdges(FixExtraEdgesRequest(extra_edge_problem_area_id=id_value))
       