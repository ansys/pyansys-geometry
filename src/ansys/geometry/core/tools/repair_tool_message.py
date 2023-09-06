from ansys.api.geometry.v0.repairtools_pb2 import FixMissingFacesRequest
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from google.protobuf.wrappers_pb2 import Int32Value

from ansys.geometry.core.connection import GrpcClient


class RepairToolMessage:


    def __init__(self, success: bool, created_bodies: list[str], modified_bodies: list[str] ):
        """
        Initialize a new instance of the extra edge problem area class.

        :param id: A unique identifier for the design.
        :type id: str
        :param design_edges: A list of edges associated with the design.
        :type design_edges: list[str]
        """
        self._success = success
        self._created_bodies = created_bodies
        self._modified_bodies = modified_bodies


    @property
    def success(self) -> bool:
        """The success of the repair operation."""
        return self._success

    @property
    def created_bodies(self) -> list[str]:
        """The success of the repair operation."""
        return self._created_bodies
    
    @property
    def modified_bodies(self) -> list[str]:
        """The success of the repair operation."""
        return self._modified_bodies