"""``NamedSelection`` class module."""

from typing import List, Optional

from ansys.api.geometry.v0.namedselections_pb2 import CreateNamedSelectionRequest
from ansys.api.geometry.v0.namedselections_pb2_grpc import NamedSelectionsStub

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.errors import protect_grpc
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

    @protect_grpc
    def __init__(
        self,
        name: str,
        grpc_client: GrpcClient,
        bodies: Optional[List[Body]] = None,
        faces: Optional[List[Face]] = None,
        edges: Optional[List[Edge]] = None,
    ):
        """Constructor method for ``NamedSelection``."""

        if bodies is None:
            bodies = []
        if faces is None:
            faces = []
        if edges is None:
            edges = []
        # Sanity checks
        check_type(name, str)
        check_type(grpc_client, GrpcClient)
        for seq_object, type_object in zip([bodies, faces, edges], [Body, Face, Edge]):
            check_type(seq_object, (list, tuple))
            for object in seq_object:
                check_type(object, type_object)

        self._grpc_client = grpc_client
        self._named_selections_stub = NamedSelectionsStub(grpc_client.channel)

        # All ids should be unique - no duplicated values
        ids = set()

        # Loop over bodies, faces and edges
        [ids.add(body.id) for body in bodies]
        [ids.add(face.id) for face in faces]
        [ids.add(edge.id) for edge in edges]

        named_selection_request = CreateNamedSelectionRequest(name=name, members=ids)
        self._grpc_client.log.debug("Requesting creation of Named selection.")
        new_named_selection = self._named_selections_stub.CreateNamedSelection(
            named_selection_request
        )
        self._id = new_named_selection.id
        self._name = new_named_selection.display_name

    @property
    def id(self) -> str:
        """ID of the ``NamedSelection``."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the ``NamedSelection``."""
        return self._name
