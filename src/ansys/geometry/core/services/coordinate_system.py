"""Module contains methods to interact with coordinate systems in Discovery or SpaceClaim."""
from ansys.api.geometry.v0.models_pb2 import (
    EntityIdentifier
)
from ansys.api.geometry.v0.coordinatesystems_pb2 import (
    GetAllRequest,
)
from ansys.api.geometry.v0.coordinatesystems_pb2_grpc import CoordinateSystemsStub
from grpc import Channel

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc


class CoordinateSystem:
    """
    Provides for either getting existing or creating new
    coordinate systems in Discovery.

    Parameters
    ----------
    channel : grpc.Channel
        gRPC channel for initializing the ``CoordinateSystemsStub`` object.
    """

    def __init__(self, grpc_client: GrpcClient):
        """Initialize the ``CoordinateSystem`` object."""
        if isinstance(grpc_client.channel, Channel):
            self._connection = CoordinateSystemsStub(grpc_client.channel)
            self._grpc_client = grpc_client
        else:
            raise Exception("Invalid gRPC channel.")

    @protect_grpc
    def get(self, identifier):
        """Get a coordinate system from the active document.

        Parameters
        ----------
        identifier : str
            Coordinate system ID.

        Returns
        -------
        ansys.api.discovery.v1.models_pb2.CoordinateSystem
            Coordinate system object if any.

        Examples
        --------
        Get the coordinate system that has `~sE410badd1-1268-4236-b8aa-a29f1e07cbfc.277__`
        as its ID.

        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client  = launch_discovery("127.0.0.1:50053")
        >>> coordinate = client.coordinate_system.get(
            "~sE410badd1-1268-4236-b8aa-a29f1e07cbfc.277__")
        """
        result = self._connection.Get(
            EntityIdentifier(id=identifier)
        )
        self._grpc_client.log.debug("Get request.\n\tresponse: " + str(result))
        return result

    @protect_grpc
    def get_all(self, parent_item=None, view_filter=None):
        """Get all coordinate systems in the active document or from a specified parent item.

        Parameters
        ----------
        parent_item : str, optional
            ID of the parent item if you want to retrieve all coordinate systems
            beneath a specific component. The default is ``None``.
        view_filter : ansys.api.discovery.v1.models_pb2.CoordinateSystemView, optional
            Filter for the view to pick coordinate systems from. The default is ``None``.

        Returns
        -------
        ansys.api.discovery.v1.models_pb2.CoordinateSystem[]
            List of all coordinate systems in the active document or from the specified parent item.

        Examples
        --------
        Get all coordinate systems in the active document.

        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery("127.0.0.1:50053")
        >>> coordinates=client.coordinate_system.get_all()
        INFO - localhost:51454 -  coordinate_system - get_all - GetAll request.
        response: coordinate_systems {
            moniker: "~sC_~pPbb2369ba-edea-471b-855d-efc1f7f729f4.2___"
            frame {
                origin {
                }
                dir_x {
                    x: 1.0
                }
                dir_y {
                    y: 1.0
                }
                dir_z {
                    z: 1.0
                }
            }
        }
        """
        result = self._connection.GetAll(
            GetAllRequest(parent=parent_item)
        )
        self._grpc_client.log.debug("GetAll request.\n\tresponse: " + str(result))
        return result.coordinate_systems
