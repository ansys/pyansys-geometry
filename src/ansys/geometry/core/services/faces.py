"""Module consists of methods for handling faces in the active document."""
from ansys.api.geometry.v0.models_pb2 import (
    EntityIdentifier
)
from ansys.api.eometry.v0.faces_pb2 import GetAllRequest
from ansys.api.eometry.v0.faces_pb2_grpc import FacesStub
from grpc import Channel

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc


class Faces:
    """
    Provides methods for handling faces in the active document.

    Parameters
    ----------
    channel : grpc.Channel
        gRPC channel for initializing the ``FacesStub`` object.
    """

    def __init__(self, grpc_client: GrpcClient):
        """Initialize the ``Faces`` object."""
        if isinstance(grpc_client.channel, Channel):
            self._connection = FacesStub(grpc_client.channel)
            self._grpc_client = grpc_client
        else:
            raise Exception("Invalid gRPC channel.")

    @protect_grpc
    def get(self, identifier):
        """Get a face in the active document.

        Parameters
        ----------
        identifier : str
            face ID.

        Returns
        -------
        ansys.api.geometry.v0.models_pb2.Face
            face object if any.

        Examples
        --------
        Get the face that has `~sE96fde82b-d1b2-4e2c-8903-08684f0ea060.252__`
        as its ID.

        >>> from ansys.geometry.core.launcher import launch_modeler
        >>> client = launch_modeler("127.0.0.1:50053")
        >>> face = client.faces.get("~sE96fde82b-d1b2-4e2c-8903-08684f0ea060.252__")
        INFO - localhost:61251 -  faces - get - get.
                response: moniker: "~sE96fde82b-d1b2-4e2c-8903-08684f0ea060.252__"
        surface_type: SURFACETYPE_PLANE
        owner_display_name: "Solid"
        export_id: "0:252"
        area: 0.00039999999999999996
        """
        result = self._connection.GetFace(EntityIdentifier(id=identifier))
        self._grpc_client.log.debug("get.\n\tresponse: " + str(result))
        return result

    @protect_grpc
    def get_all(self, parent_item=None):
        """Get all faces in the active document or from a specified parent item.

        Parameters
        ----------
        parent_item : str, optional
            ID of the parent item if you want to retrieve all faces
            beneath a specific component. The default is ``None``.
        view_filter : ansys.api.geometry.v0.models_pb2.FaceView, optional
            Filter for the view to pick faces from. The default is ``None``.

        Returns
        -------
        ansys.api.geometry.v0.models_pb2.Face[]
           List of all faces in the active document.

        Examples
        --------
        >>> from ansys.geometry.core.launcher import launch_modeler
        >>> client = launch_modeler("127.0.0.1:50053")
        >>> faces = client.faces.get_all()
        INFO - localhost:61251 -  faces - get_all - get_all.
            response: faces { {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.79__"
        surface_type: SURFACETYPE_PLANE
        owner_display_name: "Solid"
        export_id: "0:79"
        area: 0.00039999999999999996
        }
        faces {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.82__"
        surface_type: SURFACETYPE_PLANE
        owner_display_name: "Solid"
        export_id: "0:82"
        area: 0.00039999999999999996
        }
        faces {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.85__"
        surface_type: SURFACETYPE_PLANE
        owner_display_name: "Solid"
        export_id: "0:85"
        area: 0.0004
        }
        faces {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.88__"
        surface_type: SURFACETYPE_PLANE
        owner_display_name: "Solid"
        export_id: "0:88"
        area: 0.00039999999999999996
        }
        faces {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.91__"
        surface_type: SURFACETYPE_PLANE
        owner_display_name: "Solid"
        export_id: "0:91"
        area: 0.0004
        }
        faces {
        moniker: "~sE8cac76c4-f317-478b-99fa-f0e2721bc479.94__"
        surface_type: SURFACETYPE_PLANE
        owner_display_name: "Solid"
        export_id: "0:94"
        area: 0.00039999999999999996
        }
        """
        result = self._connection.GetAll(GetAllRequest(parent=parent_item))
        self._grpc_client.log.debug("get_all.\n\tresponse: " + str(result))
        return result.faces
