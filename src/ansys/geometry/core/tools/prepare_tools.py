"""Module for handling Prepare Tools tabulation in Discovery or SpaceClaim."""

from ansys.api.geometry.v0.preparetools_pb2 import (
    FixInterferenceRequest,
    FixShortEdgesRequest,
    RemoveFacesRequest,
    RemoveRoundsRequest,
    ShareTopologyRequest,
    UnshareTopologyRequest,
)
from ansys.api.geometry.v0.preparetools_pb2_grpc import PrepareToolsStub
from google.protobuf.wrappers_pb2 import BoolValue, DoubleValue
from grpc import Channel

from ansys.discovery import LOG as logger
from ansys.discovery.core.errors import protect_grpc
from ansys.discovery.models.model.body import Body


class PrepareTools:
    """
    Provides remote access to Prepare Tools tabulation in
    Discovery.

    Parameters
    ----------
    channel : grpc.Channel
        gRPC channel for initializing the ``PrepareToolsStub`` object.
    logger_name : str
        Name of the instance of Discovery to connect to. For example,
        ``localhost:12345``.
    """

    def __init__(self, channel, logger_name):
        """Initialize the ``PrepareTools`` object."""
        if isinstance(channel, Channel):
            self._prepare_tools = PrepareToolsStub(channel)
            self._logger = logger[logger_name]
        else:
            raise Exception("Ivalid gRPC channel.")

    @protect_grpc
    def fix_interference(self, sel=None, set_cut_smaller_body=None):
        """Detect and fix interfering bodies.

        Parameters
        ----------
        sel : ansys.discovery.models.model[], optional
            Bodies with interferences to clean. If this parameter is not defined,
            interferences are detected and fixed for all bodies.
        set_cut_smaller_body: bool, optional
            Whether to remove the interference from the smaller body instead of the
            the bigger body. The default is ``None``, in which case the interference
            is removed from the bigger body.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50050)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50050
        INFO - 127.0.0.1:50050 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50050 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> client.prepare_tools.fix_interference(set_cut_smaller_body=True)
        INFO - 127.0.0.1:50055 -  prepare_tools - fix_interference - fix_interference
                response:Fix interferences success: True
        >>> bodies = client.bodies.all
        >>> client.prepare_tools.fix_interference(bodies)
        INFO - 127.0.0.1:50055 -  prepare_tools - fix_interference - fix_interference
                response:Fix interferences success: True
        >>> client.prepare_tools.fix_interference(bodies, set_cut_smaller_body=True)
        INFO - 127.0.0.1:50055 -  prepare_tools - fix_interference - fix_interference
                response:Fix interferences success: True
        """
        bodies = Body.convert_array_to_datamodel(sel)
        response = self._prepare_tools.FixInterference(
            FixInterferenceRequest(
                selection=bodies,
                cut_smaller_body=BoolValue(value=set_cut_smaller_body)
                if set_cut_smaller_body
                else None,
            )
        )
        self._logger.info("Fix interferences success: " + str(response.result))
        return response.result

    @protect_grpc
    def fix_short_edges(self, sel=None, max_edge_length_value=None):
        """Detects short edges below a specified length and selectively changes them to T edges.

        Parameters
        ----------
        sel : ansys.api.discovery.v1.models_pb2.DesignEdge[], optional
            Edges can be below the specified minimal length. If this parameter is
            not defined, short edges are detected and fixed for all bodies.
        max_edge_length_value: double, optional
            Maximum edge length for determining short edges.

        Returns
        -------
            None

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> client.prepare_tools.fix_short_edges(max_edge_length_value=0.1)
        INFO - 127.0.0.1:50055 -  prepare_tools - fix_short_edges - fix_short_edges
                response:Fix short edges success: True
        >>> edges = client.edges.all
        >>> client.prepare_tools.fix_short_edges(sel=edges)
        INFO - 127.0.0.1:50055 -  prepare_tools - fix_short_edges - fix_short_edges
                response:Fix short edges success: True
        >>> client.prepare_tools.fix_short_edges(sel=edges, max_edge_length_value=0.1)
        INFO - 127.0.0.1:50055 -  prepare_tools - fix_short_edges - fix_short_edges
                response:Fix short edges success: True
        """
        response = self._prepare_tools.FixShortEdges(
            FixShortEdgesRequest(
                selection=sel if sel else [],
                max_edge_length=DoubleValue(value=max_edge_length_value)
                if max_edge_length_value
                else None,
            )
        )
        self._logger.info("Fix short edges success: " + str(response.result))
        return response.result

    @protect_grpc
    def remove_round_faces(self, sel, set_auto_shrink=None):
        """Remove round faces from the model.

        Parameters
        ----------
        sel : ansys.api.discovery.v1.models_pb2.DesignFace[]
            Round faces to remove.
        set_auto_shrink: bool, optional
            Split off the ends of selected round chains when trying to fill them.

        Returns
        -------
        ansys.api.discovery.v1.preparetools_pb2.RemoveRoundsResponse.result
            ``True`` if round faces are removed from the model, ``False`` otherwise.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> faces = client.faces.all
        INFO - 127.0.0.1:50055 -  design_faces - get_all - get_all
                response:design_faces {
        moniker: "~sE79a717c9-ab27-42af-9a2b-8df0703a6201.71__"
        surface_type: SURFACETYPE_PLANE
        owner_display_name: "Solid"
        export_id: "0:71"
        area: 0.0002070102000000001
        }
        design_faces {
        moniker: "~sE79a717c9-ab27-42af-9a2b-8df0703a6201.74__"
        surface_type: SURFACETYPE_PLANE
        owner_display_name: "Solid"
        export_id: "0:74"
        area: 0.00034100000000000005
        }
        design_faces {
        moniker: "~sE79a717c9-ab27-42af-9a2b-8df0703a6201.77__"
        surface_type: SURFACETYPE_PLANE
        owner_display_name: "Solid"
        export_id: "0:77"
        area: 0.00014409579999999996
        }
        design_faces {
        moniker: "~sE79a717c9-ab27-42af-9a2b-8df0703a6201.80__"
        surface_type: SURFACETYPE_PLANE
        owner_display_name: "Solid"
        export_id: "0:80"
        area: 0.00014737270752233377
        }
        design_faces {
        moniker: "~sE79a717c9-ab27-42af-9a2b-8df0703a6201.83__"
        surface_type: SURFACETYPE_PLANE
        owner_display_name: "Solid"
        export_id: "0:83"
        area: 0.00034099999999999994
        }
        design_faces {
        moniker: "~sE79a717c9-ab27-42af-9a2b-8df0703a6201.86__"
        surface_type: SURFACETYPE_PLANE
        owner_display_name: "Solid"
        export_id: "0:86"
        area: 0.0003981324275169663
        }
        design_faces {
        moniker: "~sE79a717c9-ab27-42af-9a2b-8df0703a6201.16198__"
        surface_type: SURFACETYPE_CYLINDER
        owner_display_name: "Solid"
        export_id: "0:16198"
        area: 9.267698328089891e-05
        }
        >>> client.prepare_tools.remove_round_faces(sel=[faces[6]])
        INFO - 127.0.0.1:50055 -  prepare_tools - remove_round_faces - remove_round_faces
                response:Remove round faces success: True
        >>> client.prepare_tools.remove_round_faces(sel=[faces[6]], set_auto_shrink=True)
        INFO - 127.0.0.1:50055 -  prepare_tools - remove_round_faces - remove_round_faces
                response:Remove round faces success: True
        """
        response = self._prepare_tools.RemoveRounds(
            RemoveRoundsRequest(
                selection=sel,
                auto_shrink=BoolValue(value=set_auto_shrink) if set_auto_shrink else None,
            )
        )
        self._logger.info("Remove round faces success: " + str(response.result))
        return response.result

    @protect_grpc
    def remove_faces(self, sel):
        """Remove faces from a model by filling faces or extending neighboring faces.

        Parameters
        ----------
        sel : ansys.api.discovery.v1.models_pb2.DesignFace[]
            Faces to remove.

        Returns
        -------
        ansys.api.discovery.v1.preparetools_pb2.RemoveFacesResponse.result

            ``True`` if faces are removed from the model, ``False`` otherwise.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> client.prepare_tools.fix_interference(set_cut_smaller_body=True)
        INFO - 127.0.0.1:50055 -  prepare_tools - fix_interference - fix_interference
                response:Fix interferences success: True
        >>> bodies = client.bodies.all
        >>> client.prepare_tools.fix_interference(bodies)
        INFO - 127.0.0.1:50055 -  prepare_tools - fix_interference - fix_interference
                response:Fix interferences success: True
        >>> client.prepare_tools.remove_faces(sel=[faces2[6], faces[25], faces[29]])
        INFO - 127.0.0.1:50055 -  prepare_tools - remove_faces - remove_faces
                response:Remove faces success: True
        """
        response = self._prepare_tools.RemoveFaces(RemoveFacesRequest(selection=sel))
        self._logger.info("Remove faces success: " + str(response.result))
        return response.result

    @protect_grpc
    def share_topology(self, sel=None, tolerance_value=None, set_preserve_instances=None):
        """Share coincident topology among bodies in the model.

        Parameters
        ----------
        sel : ansys.discovery.models.model.Body[], optional
            Bodies where coincident topologies are to be found and shared.
            The default is ``None``.
        tolerance_value: value, optional
            Coincidence tolerance. The default is ``None``.
        set_preserve_instances : bool, optional
            Whether geometry instances are to be preserved even if they are shared.
            The default is ``None``.

        Returns
        -------
        ansys.api.discovery.v1.preparetools_pb2.ShareTopologyResponse.result
            ``True`` if the bodies share coincident topologies of the model, ``False`` otherwise.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> client.prepare_tools.share_topology()
        INFO - 127.0.0.1:50055 -  prepare_tools - share_topology - share_topology
                response:Share topology success: True
        >>> bodies = client.bodies.all
        >>> client.prepare_tools.share_topology(sel=bodies)
        INFO - 127.0.0.1:50055 -  prepare_tools - share_topology - share_topology
                response:Share topology success: True
        >>> client.prepare_tools.share_topology(sel=bodies, tolerance_value=0.0001)
        INFO - 127.0.0.1:50055 -  prepare_tools - share_topology - share_topology
                response:Share topology success: True
        >>> client.prepare_tools.share_topology(sel=bodies, tolerance_value=0.0001, set_preserve_instances=True)
        INFO - 127.0.0.1:50055 -  prepare_tools - share_topology - share_topology
                response:Share topology success: True
        >>> client.prepare_tools.share_topology(tolerance_value=0.0001, set_preserve_instances=True)
        INFO - 127.0.0.1:50055 -  prepare_tools - share_topology - share_topology
                response:Share topology success: True
        >>> client.prepare_tools.share_topology(tolerance_value=0.0001)
        INFO - 127.0.0.1:50055 -  prepare_tools - share_topology - share_topology
                response:Share topology success: True
        >>> client.prepare_tools.share_topology(set_preserve_instances=True)
        INFO - 127.0.0.1:50055 -  prepare_tools - share_topology - share_topology
                response:Share topology success: True
        """
        bodies = Body.convert_array_to_datamodel(sel)
        response = self._prepare_tools.ShareTopology(
            ShareTopologyRequest(
                selection=bodies,
                tolerance=DoubleValue(value=tolerance_value) if tolerance_value else None,
                preserve_instances=BoolValue(value=set_preserve_instances)
                if set_preserve_instances
                else None,
            )
        )
        self._logger.info("Share topology success: " + str(response.result))
        return response.result

    @protect_grpc
    def unshare_topology(self, set_include_groups=None, set_unshare_lower_topology=None):
        """Unshare shared topology.

        Parameters
        ----------
        set_include_groups : bool, optional
            Whether to also unshare group topologies. The default is ``None``.
        set_unshare_lower_topology: bool, optional
            Whether to also unshare lower-tree hierarchy topologies. The
            default is ``None``.

        Returns
        -------
        ansys.api.discovery.v1.preparetools_pb2.UnshareTopologyResponse.result
            ``True`` if the shared topology from the model is removed or unshared, ``False`` otherwise.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> client.prepare_tools.unshare_topology()
        INFO - 127.0.0.1:50055 -  prepare_tools - unshare_topology - unshare_topology
                response:Unshare topology success: True
        >>> client.prepare_tools.unshare_topology(set_include_groups=True)
        INFO - 127.0.0.1:50055 -  prepare_tools - unshare_topology - unshare_topology
                response:Unshare topology success: True
        >>> client.prepare_tools.unshare_topology(set_include_groups=True, set_unshare_lower_topology=True)
        INFO - 127.0.0.1:50055 -  prepare_tools - unshare_topology - unshare_topology
                response:Unshare topology success: True
        >>> client.prepare_tools.unshare_topology(set_unshare_lower_topology=True)
        INFO - 127.0.0.1:50055 -  prepare_tools - unshare_topology - unshare_topology
                response:Unshare topology success: True
        """
        response = self._prepare_tools.UnshareTopology(
            UnshareTopologyRequest(
                include_groups=BoolValue(value=set_include_groups) if set_include_groups else None,
                unshare_lower_topology=BoolValue(value=set_unshare_lower_topology)
                if set_unshare_lower_topology
                else None,
            )
        )
        self._logger.info("Unshare topology success: " + str(response.result))
        return response.result
