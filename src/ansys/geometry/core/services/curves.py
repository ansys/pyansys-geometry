"""Module contains methods for handling design curves in the active document."""
from ansys.api.geometry.v0.models_pb2 import (
    EntityIdentifier
)
from ansys.api.geometry.v0.curves_pb2 import GetAllRequest
from ansys.api.geometry.v0.curves_pb2_grpc import CurvesStub
from grpc import Channel

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc


class Curves:
    """Provides useful methods for handling design curves in the document active
    in Discovery.

    Parameters
    ----------
    channel : grpc.Channel
        gRPC channel for initializing the ``CurvesStub`` object.
    """

    def __init__(self, grpc_client: GrpcClient):
        """Initialize the ``Curves`` object."""
        if isinstance(grpc_client.channel, Channel):
            self._connection = CurvesStub(grpc_client.channel)
            self._grpc_client = grpc_client
        else:
            raise Exception("Invalid gRPC channel.")

    @property
    def all(self):
        """List of all design curves."""
        return self.get_all()

    @protect_grpc
    def get(self, identifier):
        """Get a design curve in the active document.

        Parameters
        ----------
        identifier : str
            Design curve ID.

        Returns
        -------
        ansys.api.discovery.v1.models_pb2.DesignCurve
            Design curve object if any.

        Examples
        --------
        Get a master design curve from the list of design curves.

        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery()
        >>> curves = client.curves.get_all()
        >>> curve = client.curves.get(curves[0].id)
        >>> curve
        <ansys.discovery.models.model.curves.Curve object at 0x000001B7D72B6E30>
        >>> curve.id
        '~sE88968e73-d720-4ce0-836d-be2b05d64792.54__'
        >>> curve.name
        'Point'
        """
        return self._connection.Get(EntityIdentifier(id=identifier))

    @protect_grpc
    def get_all(self, parent_item=None):
        """Get all design curves in the active document or from a specified parent item.

        Parameters
        ----------
        parent_item : str, optional
            ID of the parent item if you want to retrieve all design curves
            beneath a specific component. The default is ``None``.

        Returns
        -------
        ansys.discovery.models.model.curve.Curve
            List of all design bodies in the active document.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery()
        >>> curves = client.curves.get_all()
        >>> >>> curves
        [<ansys.discovery.models.model.curves.Curve object at 0x000001B7D72B68C0>,
        <ansys.discovery.models.model.curves.Curve object at 0x000001B7D72B6CB0>]
        >>> curves[0].id
        '~sE88968e73-d720-4ce0-836d-be2b05d64792.54__'
        >>> curves[0].name
        'Point'

        """
        return self._connection.GetAll(GetAllRequest(parent=parent_item)).curves
