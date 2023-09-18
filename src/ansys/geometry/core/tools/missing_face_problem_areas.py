"""Problem areas definition related to missing faces."""
from ansys.api.geometry.v0.repairtools_pb2 import FixMissingFacesRequest
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from google.protobuf.wrappers_pb2 import Int32Value

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.tools.repair_tool_message import RepairToolMessage


class MissingFaceProblemAreas:
    """
    Provides missing face problem area definition.

    Represents a duplicate face problem area with unique identifier and associated faces.

    Attributes:
        _id (str): A unique identifier for the problem area.
        _edges (list[str]): A list of faces associated with the design.
    """

    def __init__(self, id: str, edges: list[str]):
        """
        Initialize a new instance of the missing face problem area class.

        :param id: A unique identifier for the design.
        :type id: str
        :param edges: A list of edges associated with the design.
        :type edges: list[str]
        """
        self._id = id
        self._edges = edges

    @property
    def id(self) -> str:
        """The id of the problem area."""
        return self._id

    @property
    def edges(self) -> list[str]:
        """The list of the ids of the edges connected to this problem area."""
        return self._edges

    def Fix(self):
        """Fix the problem area."""
        client = GrpcClient()
        id_value = Int32Value(value=int(self._id))
        response = RepairToolsStub(client.channel).FixMissingFaces(
            FixMissingFacesRequest(missing_face_problem_area_id=id_value)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message
