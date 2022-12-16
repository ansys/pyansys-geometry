"""Module contains methods to handle design meshes in the active document."""
from ansys.api.geometry.v0.models_pb2 import (
    EntityIdentifier
)
from ansys.api.geometry.v0.designmeshes_pb2 import GetAllRequest
from ansys.api.geometry.v0.designmeshes_pb2_grpc import MeshesStub
from grpc import Channel

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc


class Meshes:
    """Provides useful methods for handling design meshes in the document active
    in the modeler.

    Parameters
    ----------
    channel : grpc.Channel
        gRPC channel for initializing the ``MeshesStub`` object.
    """

    def __init__(self, grpc_client: GrpcClient):
        """Initialize the ``Meshes`` object."""
        if isinstance(grpc_client.channel, Channel):
            self._connection = MeshesStub(grpc_client.channel)
            self._grpc_client = grpc_client
        else:
            raise Exception("Invalid gRPC channel.")

    @protect_grpc
    def get(self, identifier):
        """Get a design mesh in the active document.

        Parameters
        ----------
        identifier : str
             mesh ID.

        Returns
        -------
        ansys.api.geometry.v0.models_pb2.MeshResponse
             mesh object if any.

        Examples
        --------
        Get the design mesh that has ``~sE8cac76c4-f317-478b-99fa-f0e2721bc479.88__``
        as its ID.

        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery("127.0.0.1:50053")
        >>> mesh = client.meshes.get("~sE8cac76c4-f317-478b-99fa-f0e2721bc479.88__")
        INFO - localhost:61251 -  design_meshes - get_all - get_all.
            response:moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.88__"
        display_name: "Solid"
        """
        result = self._connection.Get(EntityIdentifier(id=identifier))
        self._grpc_client.log.debug("get.\n\tresponse: " + str(result))
        return result

    @protect_grpc
    def get_all(self, parent_item=None):
        """Get all design meshes in the active document.

         Parameters
         ----------
        parent_item : str, optional
             ID of the parent item if you want to get all design meshes
             beneath a specific component. The default is ``None``.

         Returns
         -------
         ansys.api.geometry.v0.models_pb2.MeshesResponse
             List of all design meshes in the active document.

         Examples
         --------
         >>> from ansys.discovery.core.launcher import launch_discovery
         >>> client = launch_discovery("127.0.0.1:50053")
         >>> meshes = client.meshes.get_all()
         INFO - localhost:61251 -  design_meshes - get_all - get_all.
             response:[moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.88__"
         display_name: "Solid"
         , moniker: "~sE96fde82b-d1b2-4e2c-8903-08684f0ea060.255__"
         display_name: "Solid"
         ]
        """

        result = self._connection.GetAll(GetAllRequest(parent=parent_item))
        self._grpc_client.log.debug("get_all.\n\tresponse: " + str(result))
        return result.meshes
