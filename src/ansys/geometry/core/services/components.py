"""This module gets the components of the active document."""
from ansys.api.geometry.v0.models_pb2 import (
    EntityIdentifier
)
from ansys.api.geometry.v0.components_pb2 import GetAllRequest
from ansys.api.geometry.v0.components_pb2_grpc import ComponentsStub
from grpc import Channel

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc


class Components:
    """
    Gets components in the Discovery model hierarchy.

    Parameters
    ----------
    channel : grpc.Channel
        gRPC channel for initializing the ``ComponentsStub`` object.
    """

    def __init__(self, grpc_client: GrpcClient, commands):
        """Initialize the ``Components`` object."""
        if isinstance(grpc_client.channel, Channel):
            self._connection = ComponentsStub(grpc_client.channel)
            self._grpc_client = grpc_client
        else:
            raise Exception("Invalid gRPC channel.")

    @protect_grpc
    def get(self, identifier):
        """Get a component in the active document.

        Parameters
        ----------
        identifier : str
            Component ID.

        Returns
        -------
        ansys.discovery.models.model.component.Component
            Component object if any.

            The component members are:

            - moniker : str
            - display_name : str
            - part_occurrence : ansys.api.discovery.v1.models_pb2.Part
            - placement : ansys.api.discovery.v1.models_pb2.Matrix

        Examples
        --------
        Get the component that has ``~sE410badd1-1268-4236-b8aa-a29f1e07cbfc.277__``
        as its ID.

        >>> discovery = launch_discovery()
        >>> component = discovery.components.get("~sE410badd1-1268-4236-b8aa-a29f1e07cbfc.277__")
        >>> component
        <ansys.discovery.models.model.component.Component object at 0x000001AEA9D6E740>
        """
        return self._connection.Get(EntityIdentifier(id=identifier))

    @protect_grpc
    def get_all(self, parent_item=None):
        """Get all components in the active document or from a specified parent item.

        Parameters
        ----------
        parent_item : str, optional
            ID of the parent item if you want to retrieve all components
            beneath a specific component. The default is ``None``.
        view_filter : ansys.api.discovery.v1.models_pb2.ComponentView, optional
            Filter for the view to pick components from. The default is ``None``.

        Returns
        -------
        ansys.discovery.models.model.component.Component
            Array of all components in the active document.

            The array members are:

            - id : str
            - name : str
            - can_suppress : bool
            - is_deleted : bool

        Examples
        --------
        Get all components in the active document.

        >>> discovery = launch_discovery()
        >>> components = discovery.geometry.components.get_all()
        >>> components
        [<ansys.discovery.models.model.component.Component object at 0x000001AEA7CBA890>]
        """
        return self._connection.GetAll(GetAllRequest(parent=parent_item)).components
