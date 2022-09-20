"""``NamedSelection`` class module."""

from typing import List, Optional

from ansys.api.geometry.v0.namedselections_pb2 import CreateNamedSelectionRequest
from ansys.api.geometry.v0.namedselections_pb2_grpc import NamedSelectionsStub

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.misc import check_type


class NamedSelection:
    """
    A named selection organizes one or more design entities together for common actions
    against the entire group.

    Represents a single named selection within the design assembly.

    Synchronizes to a design within a supporting geometry service instance.

    Parameters
    ----------
    name : str
        A user-defined name for the named selection.
    grpc_client : GrpcClient
        An active supporting geometry service instance for design modeling.
    bodies : Optional[List[Body]]
        All bodies that should be included in the named selection.
    faces : Optional[List[Face]]
        All faces that should be included in the named selection.
    edges : Optional[List[Edge]]
        All edges that should be included in the named selection.
    """

    def __init__(
        self,
        name: str,
        grpc_client: GrpcClient,
        bodies: Optional[List[Body]] = [],
        faces: Optional[List[Face]] = [],
        edges: Optional[List[Edge]] = [],
    ):
        """Constructor method for ``NamedSelection``."""
        # Sanity checks
        check_type(name, str)
        check_type(grpc_client, GrpcClient)
        for seq_object, type_object in zip([bodies, faces, edges], [Body, Face, Edge]):
            check_type(seq_object, (list, tuple))
            for object in seq_object:
                check_type(object, type_object)

        self._grpc_client = grpc_client
        self._named_selections_stub = NamedSelectionsStub(grpc_client.channel)
        named_selection_request = CreateNamedSelectionRequest(name=name)

        self._face_ids = [face.id for face in faces]
        self._edge_ids = [edge.id for edge in edges]
        self._body_ids = [body.id for body in bodies]

        named_selection_request.members.extend(self._face_ids)
        named_selection_request.members.extend(self._edge_ids)
        named_selection_request.members.extend(self._body_ids)

        new_named_selection = self._named_selections_stub.CreateNamedSelection(
            named_selection_request
        )
        self._id = new_named_selection.id
        self._name = new_named_selection.display_name

    @property
    def id(self) -> str:
        """ID of the named-selection."""
        return self._id
