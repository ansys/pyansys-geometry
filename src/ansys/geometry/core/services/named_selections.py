"""Module contains methods for handling named selections in the active document."""
from ansys.api.geometry.v0.models_pb2 import (
    EntityIdentifier
)

from ansys.api.geometry.v0.namedselections_pb2_grpc import NamedSelectionsStub
from grpc import Channel

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc

class NamedSelections:
    """
    Provides for creating, deleting, and handling named selections remotely.

    Parameters
    ----------
    channel : grpc.Channel
        gRPC channel for initializing the ``NamedSelectionStub`` object.
    logger_name : str
        Instance of Discovery to connect to. For example, ``localhost:12345``.
    """

    def __init__(self, grpc_client: GrpcClient):
        """Initialize the ``NamedSelection`` object."""
        if isinstance(grpc_client.channel, Channel):
            self._connection = NamedSelectionsStub(grpc_client.channel)
            self._grpc_client = grpc_client
        else:
            raise Exception("Invalid gRPC channel.")

    @protect_grpc
    def get(self, identifier):
        """Get a named selection from an opened document.

        Use this method to get an existing named selection owned by the
        active document.

        Parameters
        ----------
        identifier : str
            The named selection identifier.

        Returns
        -------
        ansys.discovery.models.model.named_selection.NamedSelection
            Named selection object if any.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery()
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: localhost:52079
        INFO - localhost:52079 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - localhost:52079 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> named_selections = client.named_selections.get_all()
        >>> named_selection = client.named_selections.get(named_selections[0].id)
        <ansys.discovery.models.model.named_selection.NamedSelection object at 0x000001D6FCB06830>
        """
        return self._connection.Get(
            EntityIdentifier(id=identifier)
        )

    @protect_grpc
    def get_all(self, parent_item=None):
        """Get all named selections in the active document or from a specified parent item.

        Parameters
        ----------
        parent_item : str
            ID of the parent item if you want to retrieve all named selections
            beneath a specific component. The default is ``None``.
        view_filter : ansys.api.discovery.v1.models_pb2.NamedSelectionView, optional
            Filter for the view to pick named selections from. The default is ``None``.

        Returns
        -------
        ansys.discovery.models.model.named_selection.NamedSelection
            List of all named selections intthe active document.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery()
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: localhost:52079
        INFO - localhost:52079 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - localhost:52079 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> named_selections = client.named_selections.get_all()
        >>> named_selections
        [<ansys.discovery.models.model.named_selection.NamedSelection object at 0x000001D6FEBAF940>]
        """
        return self._connection.GetAll(GetAllRequest(parent=parent_item)).named_selections
