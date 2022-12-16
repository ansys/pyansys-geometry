"""This module contains methods for handling bodies in the active document."""
from ansys.api.geometry.v0.models_pb2 import (
    EntityIdentifier
)

from ansys.geometry.core.designer.body import Body
from ansys.api.geometry.v0.models_pb2 import Body as GRPCBody
from ansys.api.geometry.v0.Bodies_pb2 import GetRequest,GetType, ListBodiesRequest
from ansys.api.geometry.v0.Bodies_pb2_grpc import BodiesStub
from grpc import Channel

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc

class Bodies:
    """
    Provides methods for handling bodies in the active document.

    Parameters
    ----------
    channel : grpc.Channel
        gRPC channel for initializing the ``BodiesStub`` object.
    """

    def __init__(self, grpc_client: GrpcClient):
        """Initialize the ``Bodies`` object."""
        if isinstance(grpc_client.channel, Channel):
            self._connection = BodiesStub(grpc_client.channel)
            self._grpc_client = grpc_client
        else:
            raise Exception("Invalid gRPC channel.")

    @protect_grpc
    def get(self, identifier, type= GetType.NONE):
        """Get a body in the active document.

        Parameters
        ----------
        identifier : str
            body ID.

        Returns
        -------
        ansys.api.discovery.v1.models_pb2.Body
            body object if any.

        Examples
        --------
        Get a master body that has ``~sE410badd1-1268-4236-b8aa-a29f1e07cbfc.277__``
        as its ID.

        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery("127.0.0.1:50053")
        >>> bodies = client.bodies.get_all()
        >>> bodies
        [<ansys.discovery.models.model.body.Body object at 0x000001AEA9DAF8E0>]
        >>> body = client.bodies.get(bodies[0].id)
        >>> body
        <ansys.discovery.models.model.body.Body object at 0x000001AEA9DAFD60>
        """
        return self._connection.Get(GetRequest(id=identifier, body_type= type))


    @protect_grpc
    def get_master(self, identifier):
        """Get a master body in the active document.

        Parameters
        ----------
        identifier : str
            Master body ID.

        Returns
        -------
        ansys.api.discovery.v1.models_pb2.Body
            Master body object if any.

        Examples
        --------
        Get a master body that has ``~sE410badd1-1268-4236-b8aa-a29f1e07cbfc.277__``
        as its ID.

        >>> discovery = launch_discovery()
        >>> master = discovery.bodies.get_master(
            "~sE410badd1-1268-4236-b8aa-a29f1e07cbfc.277__")
        >>> master
        <ansys.discovery.models.model.body.Body object at 0x000001AEA9DAF9D0>
        """
        return self._connection.GetMaster(EntityIdentifier(id=identifier))

    @protect_grpc
    def get_original(self, identifier):
        """Get an original body in the active document.

        Parameters
        ----------
        identifier : str
            Original body ID.

        Returns
        -------
        ansys.api.discovery.v1.models_pb2.Body
            Original body object if any.

        Examples
        --------
        Get the original body that has `~sE410badd1-1268-4236-b8aa-a29f1e07cbfc.277__`
        as its ID.

        >>> discovery = launch_discovery()
        >>> original = discovery.bodies.get_original(
            "~sE410badd1-1268-4236-b8aa-a29f1e07cbfc.277__")
        """
        return self._connection.GetOriginal(EntityIdentifier(id=identifier))

    @protect_grpc
    def get_parent(self, identifier):
        """Get the parent part of a body in the active document.

        Parameters
        ----------
        identifier : str
            body ID.

        Returns
        -------
        ansys.api.discovery.v1.models_pb2.Part
            Parent part object if any.

        Examples
        --------
        Get the parent part of a body that has `~sE410badd1-1268-4236-b8aa-a29f1e07cbfc.277__`
        as its ID.

        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery()
        >>> parent = client.bodies.get_parent(
            "~sE410badd1-1268-4236-b8aa-a29f1e07cbfc.277__")
        """
        return self._connection.GetParent(EntityIdentifier(id=identifier))

    @protect_grpc
    def get_all(self, parent_item=None):
        """Get all bodies in the active document or from a specified parent item.

        Parameters
        ----------
        parent_item : str, optional
            ID of the parent item if you want to retrieve all bodies
            beneath a specific component. The default is ``None``.
        view_filter : ansys.api.discovery.v1.models_pb2.BodyView, optional
            Filter for the view to pick bodies from. The default is ``None``.

        Returns
        -------
        ansys.discovery.models.model.body.Body
            List of all bodies in the active document.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery()
        >>> bodies = client.bodies.get_all()
        >>> bodies
        [<ansys.discovery.models.model.body.Body object at 0x000001AEA9DAF8E0>]
        """
        return self._connection.GetAll(GetAllRequest(parent=parent_item)).bodies

