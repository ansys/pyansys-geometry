"""This module contains methods to interact with parts of the active document."""
from ansys.api.geometry.v0.models_pb2 import (
    EntityIdentifier
)
from ansys.api.geometry.v0.parts_pb2 import ExportPartRequest, GetAllRequest
from ansys.api.geometry.v0.parts_pb2_grpc import PartsStub
from grpc import Channel
import numpy

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc

class Parts:
    """
    Provides access to the parts in the active document.

    Parameters
    ----------
    channel : grpc.Channel
        gRPC channel for initializing the ``PartStub`` object.
    logger_name : str
        Instance of Discovery to connect to. For example, ``localhost:12345``.
    """

    def __init__(self, grpc_client: GrpcClient):
        """Initialize the ``Parts`` object."""
        if isinstance(grpc_client.channel, Channel):
            self._connection = PartsStub(grpc_client.channel)
            self._grpc_client = grpc_client
        else:
            raise Exception("Invalid gRPC channel.")

    @protect_grpc
    def get(self, identifier):
        """Get a part in the active document.

        Parameters
        ----------
        identifier : str
          Part ID.

        Returns
        -------
        ansys.discovery.models.model.part.Part
          Part object if any.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery()
        >>> parts = client.parts.get_all()
        >>> part = client.parts.get(parts[0].id)
        <ansys.discovery.models.model.part.Part object at 0x000001D6FEBAFD30>
        """
        return self._connection.Get(EntityIdentifier(id=identifier))

    @protect_grpc
    def get_all(self, parent_item=None, view_filter=None):
        """Get all parts in the active document or from a specified parent item.

        Parameters
        ----------
        parent_item : str, optional
            ID of the parent item if you want to retrieve all parts beneath a
            specific component. The default is ``None``.
        view_filter : ansys.api.discovery.v1.models_pb2.PartView, optional
            Filter for the view to pick parts from. The default is ``None``.

        Returns
        -------
        ansys.api.discovery.v1.models_pb2.Part[]
            List of all parts in the active document.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery()
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - wait_for_transient_failure - Connection: idle.
        INFO -  -  connection - wait_for_transient_failure - Connection: connecting.
        INFO -  -  connection - wait_for_transient_failure - Connection: ready.
        INFO -  -  connection - connect - Connection: connected to: localhost:52079
        INFO - localhost:52079 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - localhost:52079 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> parts = discovery.parts.get_all()
        >>> parts
        [<ansys.discovery.models.model.part.Part object at 0x000001D6FEBAF670>, <ansys.discovery.models.model.part.Part object at 0x000001D6FEBAFA00>]
        """
        return self._connection.GetAll(GetAllRequest(parent=parent_item)).parts

    @protect_grpc
    def export(self, part_identifier, export_format):
        """Export a part.

        Use this method to export a part in a specific format. If the export
        succeeds, this method will return the exported part file content.
        No file will be created, the export data will be only present into the
        return value.

        Parameters
        ----------
        part_identifier : str
           Part ID.
        export_format : ansys.api.discovery.v1.parts_pb2.PartExportFormat
            Format to export the part to. Options are:

            - ``PARTEXPORTFORMAT_ACIS_TEXT = 0``
            - ``PARTEXPORTFORMAT_ACIS_BINARY = 1``
            - ``PARTEXPORTFORMAT_PARASOLID_TEXT = 2``
            - ``PARTEXPORTFORMAT_PARASOLID_BINARY = 3``
            - ``PARTEXPORTFORMAT_STEP = 4``

        Returns
        -------
        str
            Raw exported data.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery()
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: localhost:52079
        INFO - localhost:52079 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - localhost:52079 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> from ansys.api.discovery.v0.parts_pb2 import PartExportFormat
        >>> export_format = PartExportFormat.PARTEXPORTFORMAT_ACIS_TEXT
        >>> parts = discovery.parts.Export(
        "~sEcecd7389-8d6b-44b6-968e-715dcbf0ffa9.631__", exportFormat)
        """

        result = []
        response_iterator = self._connection.ExportPart(
            ExportPartRequest(moniker=part_identifier, format=export_format)
        )
        init_done = False
        content_type = ""
        for response in response_iterator:
            if init_done == False:
                content_type = response.content_type
                init_done = True
            result.append(response.data)

        array = numpy.array(result)
        self._grpc_client.log.debug("export." + str(array))
        return array, content_type