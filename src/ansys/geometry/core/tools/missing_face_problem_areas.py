from ansys.api.geometry.v0.repairtools_pb2 import FixMissingFacesRequest
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from google.protobuf.wrappers_pb2 import Int32Value

from ansys.geometry.core.connection import GrpcClient


class MissingFaceProblemAreas:
    """
    Represents a duplicate face problem area with unique identifier and associated faces.

    Attributes:
        _id (str): A unique identifier for the problem area.
        _design_edges (list[str]): A list of faces associated with the design.
    """

    def __init__(self, id: str, design_edges: list[str]):
        """
        Initialize a new instance of the extra edge problem area class.

        :param id: A unique identifier for the design.
        :type id: str
        :param design_edges: A list of edges associated with the design.
        :type design_edges: list[str]
        """
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
        result = RepairToolsStub(client.channel).FixMissingFaces(
            FixMissingFacesRequest(missing_face_problem_area_id=id_value)
        )
        return result