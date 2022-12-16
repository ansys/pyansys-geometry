"""Module contains methods for handling  edges in the active document."""
from ansys.api.geometry.v0.models_pb2 import (
    EntityIdentifier
)

from ansys.geometry.core.designer.edge import Edge
from ansys.api.geometry.v0.models_pb2 import Edge as GRPCEdge
from ansys.api.geometry.v0.edges_pb2 import GetAllRequest
from ansys.api.geometry.v0.edges_pb2_grpc import EdgesStub
from grpc import Channel

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc


class Edges:
    """
    Provides methods for handling  edges in the active document.

    Parameters
    ----------
    channel : grpc.Channel
        gRPC channel for initializing the ``EdgesStub`` object.
    logger_name : str
        Instance of Discovery to connect to. For example, ``localhost:12345``.
    """

    def __init__(self, grpc_client: GrpcClient):
        """Initialize the ``Edges`` object."""
        if isinstance(grpc_client.channel, Channel):
            self._connection = EdgesStub(grpc_client.channel)
            self._grpc_client = grpc_client
        else:
            raise Exception("Invalid gRPC channel.")
 
    @protect_grpc
    def get(self, identifier):
        """Get a  edge in the active document.

        Parameters
        ----------
        identifier : str
            Design edge ID.

        Returns
        -------
        ansys.api.discovery.v1.models_pb2.DesignEdge
            Design edge object if any.

        Examples
        --------
        Get the  edge that has `~sE8cac76c4-f317-478b-99fa-f0e2721bc479.2008__`
        as its ID.

        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery()
        >>> edge = client.edges.get("~sE8cac76c4-f317-478b-99fa-f0e2721bc479.2008__")
        INFO - localhost:61251 -  edges - get - get.
            response: moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.2008__"
        curve_type: CURVETYPE_LINE
        owner_display_name: "Solid"
        export_id: "0:2008"
        length: 0.02
        """
        result = self._connection.Get(EntityIdentifier(id=identifier))
        self._grpc_client.log.debug("get.\n\tresponse: " + str(result))
        
        return result

    @protect_grpc
    def get_all(self, parent_item=None):
        """Get all  edges in the active document or from a specified parent item.

        Parameters
        ----------
        parent_item : str, optional
            ID of the parent item if you want to retrieve all  edges
            beneath a specific component. The default is ``None``.
        view_filter: ansys.api.discovery.v1.models_pb2.DesignEdgeView
            Filter for the view to pick  edges from. The default is ``None``.

        Returns
        -------
        ansys.api.discovery.v1.models_pb2.DesignEdge[]
            List of all  edges in the active document or from the specified
            parent item.

        Examples
        --------
        Get all  edges in the active document that contain only a cube.

        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery()
        >>> edges = client.edges.get_all()
        INFO - localhost:61251 -  edges - get_all - get_all.
            response: edges {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.97__"
        curve_type: CURVETYPE_LINE
        owner_display_name: "Solid"
        export_id: "0:97"
        length: 0.019999999999999997
        }
        edges {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.100__"
        curve_type: CURVETYPE_LINE
        owner_display_name: "Solid"
        export_id: "0:100"
        length: 0.02
        }
        edges {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.103__"
        curve_type: CURVETYPE_LINE
        owner_display_name: "Solid"
        export_id: "0:103"
        length: 0.02
        }
        edges {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.106__"
        curve_type: CURVETYPE_LINE
        owner_display_name: "Solid"
        export_id: "0:106"
        length: 0.02
        }
        edges {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.109__"
        curve_type: CURVETYPE_LINE
        owner_display_name: "Solid"
        export_id: "0:109"
        length: 0.019999999999999997
        }
        edges {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.112__"
        curve_type: CURVETYPE_LINE
        owner_display_name: "Solid"
        export_id: "0:112"
        length: 0.02
        }
        edges {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.115__"
        curve_type: CURVETYPE_LINE
        owner_display_name: "Solid"
        export_id: "0:115"
        length: 0.02
        }
        edges {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.118__"
        curve_type: CURVETYPE_LINE
        owner_display_name: "Solid"
        export_id: "0:118"
        length: 0.02
        }
        edges {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.121__"
        curve_type: CURVETYPE_LINE
        owner_display_name: "Solid"
        export_id: "0:121"
        length: 0.019999999999999997
        }
        edges {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.124__"
        curve_type: CURVETYPE_LINE
        owner_display_name: "Solid"
        export_id: "0:124"
        length: 0.02
        }
        edges {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.127__"
        curve_type: CURVETYPE_LINE
        owner_display_name: "Solid"
        export_id: "0:127"
        length: 0.019999999999999997
        }
        edges {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.130__"
        curve_type: CURVETYPE_LINE
        owner_display_name: "Solid"
        export_id: "0:130"
        length: 0.02
        }
        """
        result = self._connection.GetAll(GetAllRequest(parent=parent_item))
        self._grpc_client.log.debug("get_all.\n\tresponse: " + str(result))
        return result.edges

    def _fold_into_edge(self, grpc_edge : GRPCEdge):
        return Edge( id = grpc_edge.id,
                    curve_type = grpc_edge.curve_type,
                    body = None,
                    grpc_client = self._grpc_client)