"""This module contains methods to handle repair tools for correcting and cleaning geometry."""

from ansys.api.discovery.v1.repairtools_pb2 import (
    AdjustInexactEdgesRequest,
    AdjustMergeFacesRequest,
    AdjustSimplifyRequest,
    AdjustSmallFacesRequest,
    FixCurvesDuplicateRequest,
    FixCurvesGapsRequest,
    FixDuplicateFacesRequest,
    FixExtraEdgesRequest,
    FixSplitEdgesRequest,
    SolidifyGapsRequest,
    SolidifyMissingFacesRequest,
    SolidifyStitchRequest,
)
from ansys.api.discovery.v1.repairtools_pb2_grpc import RepairToolsStub
from google.protobuf.wrappers_pb2 import BoolValue, DoubleValue
from grpc import Channel

from ansys.discovery import LOG as logger
from ansys.discovery.core.errors import protect_grpc
from ansys.discovery.models.model.body import Body


class RepairTools:
    """Provides repair tools for correcting and cleaning the imported geometry.

    Parameters
    ----------
    channel: gRPC.Channel
        gRPC channel for initializing the ``RepairToolsStub`` object.
    logger_name : str
        Instance of Discovery to connect to. For example, ``localhost:12345``.
    """

    def __init__(self, channel, logger_name):
        """Initialize the ``RepairTools`` object."""
        if isinstance(channel, Channel):
            self._repair_tools = RepairToolsStub(channel)
            self._logger = logger[logger_name]
        else:
            raise Exception("invalid gRPC channel.")

    @protect_grpc
    def solidify_stitch(
        self,
        sel,
        max_distance_value=None,
        set_check_for_coincidence=None,
        set_allow_multiple_bodies=None,
        set_maintain_components=None,
    ):
        """Detect and stitch surfaces into a single body.

        Parameters
        ----------
        sel : ansys.api.discovery.v1.models_pb2.DesignFace[]
            Faces to stitch together.
        max_distance_value: double, optional
            Maximum distance between to faces. The default is ``None``.
        set_check_for_coincidence: bool, optional
            Whether to enable the coincidence check for faces to allow
            stitching. The default is ``None``.
        set_allow_multiple_bodies: bool, optional
            Whether to allow faces from multiple bodies to be stitched
            together. The default is ``None``.
        set_maintain_components: bool, optional
            Whether to force maintaining components when faces are
            stitched together. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> faces = client.faces.all
        >>> client.repair_tools.solidify_stitch(sel=faces)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_stitch - solidify_stitch
                response:Success: True
        >>> client.repair_tools.solidify_stitch(sel=faces, max_distance_value=0.001)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_stitch - solidify_stitch
                response:Success: True
        >>> client.repair_tools.solidify_stitch(sel=faces, max_distance_value=0.001,
            set_check_for_coincidence=True)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_stitch - solidify_stitch
                response:Success: True
        >>> client.repair_tools.solidify_stitch(sel=faces, max_distance_value=0.001,
            set_check_for_coincidence=True, set_allow_multiple_bodies=True)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_stitch - solidify_stitch
                response:Success: True
        >>> client.repair_tools.solidify_stitch(sel=faces, max_distance_value=0.001,
            set_check_for_coincidence=True, set_allow_multiple_bodies=True,
            set_maintain_components=True)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_stitch - solidify_stitch
                response:Success: True
        """
        response = self._repair_tools.SolidifyStitch(
            SolidifyStitchRequest(
                selection=sel,
                maximum_distance=(
                    DoubleValue(value=max_distance_value) if max_distance_value else None
                ),
                check_for_coincidence=(
                    BoolValue(value=set_check_for_coincidence)
                    if set_check_for_coincidence
                    else None
                ),
                allow_multiple_bodies=(
                    BoolValue(value=set_allow_multiple_bodies)
                    if set_allow_multiple_bodies
                    else None
                ),
                maintain_components=(
                    BoolValue(value=set_maintain_components) if set_maintain_components else None
                ),
            )
        )
        self._logger.info("Success: " + str(response.result))
        return response.result

    @protect_grpc
    def solidify_gaps(
        self,
        sel,
        angle_value=None,
        distance_value=None,
        solidify_method_item=None,
        set_allow_multi_patch=None,
    ):
        """Detect and remove gaps between faces or surface bodies.

        Parameters
        ----------
        sel : ansys.api.discovery.v1.models_pb2.DesignFace[]
            Faces to clean gaps from.
        angle_value: value, optional
            Maximum angle allowed for gaps. The default is ``None``.
        distance_value: value, optional
            Maximum distance allowed for gaps. The default is ``None``.
        solidify_method_item: ansys.api.discovery.v1.repairtools_pb2.SolidifyFixMethodType, optional
            Fill method to use. Options are:

            - ``SolidifyFixMethodType.FILL``
            - ``SolidifyFixMethodType.PATCH_BLEND``
            - ``SolidifyFixMethodType.TRY_BOTH``

        set_allow_multi_patch: bool, optional
            Whether to allow multiple patches to fill gaps.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> from ansys.api.discovery.v0.repairtools_pb2 import SolidifyFixMethodType
        >>> faces = client.faces.all
        >>> client.repair_tools.solidify_gaps(faces)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_gaps - solidify_gaps
                response:Success: True
        >>> client.repair_tools.solidify_gaps(faces, angle_value=0.1)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_gaps - solidify_gaps
                response:Success: True
        >>> client.repair_tools.solidify_gaps(faces, angle_value=0.1, distance_value=0.01)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_gaps - solidify_gaps
                response:Success: True
        >>> client.repair_tools.solidify_gaps(faces, angle_value=0.1, distance_value=0.01,
            solidify_method_item=SolidifyFixMethodType.TRY_BOTH)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_gaps - solidify_gaps
                response:Success: True
        >>> client.repair_tools.solidify_gaps(faces, angle_value=0.1, distance_value=0.01,
            solidify_method_item=SolidifyFixMethodType.TRY_BOTH, set_allow_multi_patch=True)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_gaps - solidify_gaps
                response:Success: True
        """
        if solidify_method_item:
            response = self._repair_tools.SolidifyGaps(
                SolidifyGapsRequest(
                    selection=sel,
                    angle=DoubleValue(value=angle_value) if angle_value else None,
                    distance=DoubleValue(value=distance_value) if distance_value else None,
                    data=solidify_method_item,
                    allow_multi_patch=(
                        BoolValue(value=set_allow_multi_patch) if set_allow_multi_patch else None
                    ),
                )
            )
        else:
            response = self._repair_tools.SolidifyGaps(
                SolidifyGapsRequest(
                    selection=sel,
                    angle=DoubleValue(value=angle_value) if angle_value else None,
                    distance=DoubleValue(value=distance_value) if distance_value else None,
                    null=None,
                    allow_multi_patch=(
                        BoolValue(value=set_allow_multi_patch) if set_allow_multi_patch else None
                    ),
                )
            )

        self._logger.info("Success: " + str(response.result))
        return response.result

    @protect_grpc
    def solidify_missing_faces(
        self,
        sel,
        angle_value=None,
        distance_value=None,
        solidify_method_item=None,
        set_allow_multi_patch=None,
    ):
        """Detects and fills missing faces.

        Parameters
        ----------
        sel : ansys.discovery.models.model.Body[]
            Bodies to clean gaps from.
        angle_value: value, optional
            Maximum angle allowed for gaps. The default is ``None``.
        distance_value: value, optional
            Maximum distance allowed for gaps. The default is ``None``.
        solidify_method_item: ansys.api.discovery.v1.repairtools_pb2.SolidifyFixMethodType, optional
            Fill method to use. Options are:

            - ``SolidifyFixMethodType.FILL``
            - ``SolidifyFixMethodType.PATCH_BLEND``
            - ``SolidifyFixMethodType.TRY_BOTH``

        set_allow_multi_patch: bool, optional
            Whether to allow multiple patches to fill gaps. The default
            is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> from ansys.api.discovery.v0.repairtools_pb2 import SolidifyFixMethodType
        >>> faces = client.faces.all
        >>> client.repair_tools.solidify_missing_faces(faces)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_missing_faces - solidify_missing_faces
                response:Success: True
        >>> client.repair_tools.solidify_missing_faces(faces, angle_value=0.1)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_missing_faces - solidify_missing_faces
                response:Success: True
        >>> client.repair_tools.solidify_missing_faces(faces, angle_value=0.1, distance_value=0.0001)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_missing_faces - solidify_missing_faces
                response:Success: True
        >>> client.repair_tools.solidify_missing_faces(faces, angle_value=0.1, distance_value=0.0001,
            solidify_method_item=SolidifyFixMethodType.PATCH_BLEND)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_missing_faces - solidify_missing_faces
                response:Success: True
        >>> client.repair_tools.solidify_missing_faces(faces, angle_value=0.1, distance_value=0.0001,
            solidify_method_item=SolidifyFixMethodType.PATCH_BLEND, set_allow_multi_patch=True)
        INFO - 127.0.0.1:50055 - repair_tools - solidify_missing_faces - solidify_missing_faces
                response:Success: True
        """
        bodies = Body.convert_array_to_datamodel(sel)
        if solidify_method_item:
            response = self._repair_tools.SolidifyGaps(
                SolidifyMissingFacesRequest(
                    selection=bodies,
                    angle=DoubleValue(value=angle_value) if angle_value else None,
                    distance=DoubleValue(value=distance_value) if distance_value else None,
                    data=solidify_method_item,
                    allow_multi_patch=(
                        BoolValue(value=set_allow_multi_patch) if set_allow_multi_patch else None
                    ),
                )
            )
        else:
            response = self._repair_tools.SolidifyGaps(
                SolidifyMissingFacesRequest(
                    selection=bodies,
                    angle=DoubleValue(value=angle_value) if angle_value else None,
                    distance=DoubleValue(value=distance_value) if distance_value else None,
                    null=None,
                    allow_multi_patch=(
                        BoolValue(value=set_allow_multi_patch) if set_allow_multi_patch else None
                    ),
                )
            )
        self._logger.info("Success: " + str(response.result))
        return response.result

    @protect_grpc
    def fix_split_edges(self, sel, max_edge_length_value=None, min_edge_angle_value=None):
        """Detect and combine split edges.

        Parameters
        ----------
        sel : ansys.api.discovery.v1.models_pb2.DesignEdge[]
            Edges to combine.
        max_edge_length_value: double, optional
            Maximum edge length value to allow edge combination.
            The default is ``None``.
        min_edge_angle_value: double, optional
            Minimum edge angle value to allow combination.
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> edges=client.edges.all
        >>> client.repair_tools.fix_split_edges(edges)
        INFO - 127.0.0.1:50055 - repair_tools - fix_split_edges - fix_split_edges
                response:Success: True
        >>> client.repair_tools.fix_split_edges(edges, max_edge_length_value= 0.01)
        INFO - 127.0.0.1:50055 - repair_tools - fix_split_edges - fix_split_edges
                response:Success: True
        >>> client.repair_tools.fix_split_edges(edges, max_edge_length_value= 0.01, min_edge_angle_value=0.1)
        INFO - 127.0.0.1:50055 - repair_tools - fix_split_edges - fix_split_edges
                response:Success: True
        """
        response = self._repair_tools.FixSplitEdges(
            FixSplitEdgesRequest(
                selection=sel,
                max_edge_length=(
                    DoubleValue(value=max_edge_length_value) if max_edge_length_value else None
                ),
                min_edge_angle=(
                    DoubleValue(value=min_edge_angle_value) if min_edge_angle_value else None
                ),
            )
        )
        self._logger.info("Success: " + str(response.result))
        return response.result

    @protect_grpc
    def fix_extra_edges(self, sel):
        """Detect and remove extra edges.

        Parameters
        ----------
        sel : ansys.api.discovery.v1.models_pb2.DesignEdge[]
            Eedges to analyze and clean.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> edges = client.edges.all
        >>> client.repair_tools.fix_extra_edges(edges)
        INFO - 127.0.0.1:50055 - repair_tools - fix_extra_edges - fix_extra_edges
                response:Success: True
        """
        response = self._repair_tools.FixExtraEdges(FixExtraEdgesRequest(selection=sel))
        self._logger.info("Success: " + str(response.result))
        return response.result

    @protect_grpc
    def fix_duplicate_faces(self, sel, max_gap_value=None):
        """Detect and fix duplicate faces.

        Parameters
        ----------
        sel : ansys.api.discovery.v1.models_pb2.DesignFace[]
            Faces to analyze and fix.
        max_gap_value: double, optional
            Maximum gap value between two duplicate faces to allow removal.
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> faces = client.faces.all
        >>> client.repair_tools.fix_duplicate_faces(faces)
        INFO - 127.0.0.1:50055 - repair_tools - fix_duplicate_faces - fix_duplicate_faces
                response:Success: True
        >>> client.repair_tools.fix_duplicate_faces(faces, max_gap_value = 0.001)
        INFO - 127.0.0.1:50055 - repair_tools - fix_duplicate_faces - fix_duplicate_faces
                response:Success: True
        """
        response = self._repair_tools.FixDuplicateFaces(
            FixDuplicateFacesRequest(
                selection=sel, max_gap=DoubleValue(value=max_gap_value) if max_gap_value else None
            )
        )
        self._logger.info("Success: " + str(response.result))
        return response.result

    @protect_grpc
    def fix_curves_gaps(self, distance_value=None):
        """Detect, remove, and fix gaps between curves.

        Parameters
        ----------
        distance_value: double (optional)
            Maximum allowed distance between two curves. The default
            is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> faces = client.repair_tools.fix_curves_gaps()
        INFO - 127.0.0.1:50055 - repair_tools - fix_curves_gaps - fix_curves_gaps
                response:Success: False
        >>> faces = client.repair_tools.fix_curves_gaps(0.001)
        INFO - 127.0.0.1:50055 - repair_tools - fix_curves_gaps - fix_curves_gaps
                response:Success: False
        """

        response = self._repair_tools.FixCurvesGaps(
            FixCurvesGapsRequest(
                distance=DoubleValue(value=distance_value) if distance_value else None
            )
        )
        self._logger.info("Success: " + str(response.result))
        return response.result

    @protect_grpc
    def fix_duplicate_curves(self, distance_value=None):
        """Detect and remove duplicate curves.

        Parameters
        ----------
        distance_value: double, optional
            Maximum distance for curves to be considered duplicated.
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> faces = client.repair_tools.fix_duplicate_curves()
        INFO - 127.0.0.1:50055 - repair_tools -fix_duplicate_curves - fix_duplicate_curves
                response:Success: True
        >>> faces = client.repair_tools.fix_duplicate_curves(0.001)
        INFO - 127.0.0.1:50055 - repair_tools -fix_duplicate_curves - fix_duplicate_curves
                response:Success: True
        """

        response = self._repair_tools.FixCurvesDuplicate(
            FixCurvesDuplicateRequest(
                distance=DoubleValue(value=distance_value) if distance_value else None
            )
        )
        self._logger.info("Success: " + str(response.result))
        return response.result

    @protect_grpc
    def adjust_merge_faces(
        self,
        sel,
        tangent_faces_sel=None,
        set_allow_multi_patch=None,
        set_fail_if_can_fill=None,
        set_enforce_closed_loop_search=None,
    ):
        """Merge two or more faces.

        Parameters
        ----------
        sel : ansys.api.discovery.v1.models_pb2.DesignFace[]
            Faces to merge.
        tangent_faces_sel: ansys.api.discovery.v1.models_pb2.DesignFace[], optional
            Faces that yyou want to maintain tangency with. The default is ``None``.
        set_allow_multi_patch: bool, optional
            Whether to allow multi patches to merge faces. The default is ``None``.
        set_fail_if_can_fill: bool, optional
        set_enforce_closed_loop_search: bool, optional
            Whether to force trying to merge faces into a closed loop. The default
            is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> faces = client.repair_tools.adjust_merge_faces(faces)
        INFO - 127.0.0.1:50055 - repair_tools - adjust_merge_faces - adjust_merge_faces
                response:Adjust merge faces: True
        >>> faces = client.repair_tools.adjust_merge_faces(faces,set_allow_multi_patch=True)
        INFO - 127.0.0.1:50055 - repair_tools - adjust_merge_faces - adjust_merge_faces
                response:Adjust merge faces: True
        >>> faces = client.repair_tools.adjust_merge_faces(faces,set_allow_multi_patch=True,
            set_fail_if_can_fill=True)
        INFO - 127.0.0.1:50055 - repair_tools - adjust_merge_faces - adjust_merge_faces
                response:Adjust merge faces: True
        >>> faces = client.repair_tools.adjust_merge_faces(faces,set_allow_multi_patch=True,
            set_fail_if_can_fill=True,set_enforce_closed_loop_search=True)
        INFO - 127.0.0.1:50055 - repair_tools - adjust_merge_faces - adjust_merge_faces
                response:Adjust merge faces: True
        >>> faces = client.repair_tools.adjust_merge_faces(faces,set_allow_multi_patch=True,
            set_fail_if_can_fill=True,set_enforce_closed_loop_search=True)
        INFO - 127.0.0.1:50055 - repair_tools - adjust_merge_faces - adjust_merge_faces
                response:Adjust merge faces: True
        """
        response = self._repair_tools.AdjustMergeFaces(
            AdjustMergeFacesRequest(
                selection=sel,
                tangent_faces=tangent_faces_sel,
                allow_multi_patch=BoolValue(value=set_allow_multi_patch)
                if set_allow_multi_patch
                else None,
                fail_if_can_fill=BoolValue(value=set_fail_if_can_fill)
                if set_fail_if_can_fill
                else None,
                enforce_closed_loop_check=BoolValue(value=set_enforce_closed_loop_search)
                if set_enforce_closed_loop_search
                else None,
            )
        )
        self._logger.info("Adjust merge faces: " + str(response.result))
        return response.result

    @protect_grpc
    def adjust_small_faces(self, sel, area_value=None, width_value=None):
        """Detect and remove small or sliver faces.

        Parameters
        ----------
        sel : ansys.api.discovery.v1.models_pb2.DesignFace[]
            Faces to analyze and clean.
        area_value: double, optional
            Minimal face area. The default is ``None``.
        width_value : double, optional
            Minimal face width. The default is ``None``.

        Returns
        -------
        bool
            ``True`` if success, ``False`` otherwise.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> client.prepare_tools.fix_interference(set_cut_smaller_body=True)
        INFO - 127.0.0.1:50055 - prepare_tools - fix_interference - fix_interference
                response:Fix interferences success: True
        >>> faces = client.faces.all
        >>> client.repair_tools.adjust_small_faces(faces)
        INFO - 127.0.0.1:50055 - repair_tools - adjust_small_faces - adjust_small_faces
                response:Success: True
        >>> client.repair_tools.adjust_small_faces(faces, area_value=0.01)
        INFO - 127.0.0.1:50055 - repair_tools - adjust_small_faces - adjust_small_faces
                response:Success: True
        >>> client.repair_tools.adjust_small_faces(faces, area_value=0.01, width_value = 1)
        INFO - 127.0.0.1:50055 - repair_tools - adjust_small_faces - adjust_small_faces
                response:Success: True
        """

        response = self._repair_tools.AdjustSmallFaces(
            AdjustSmallFacesRequest(
                selection=sel,
                area=DoubleValue(value=area_value) if area_value else None,
                width=DoubleValue(value=width_value) if width_value else None,
            )
        )
        self._logger.info("Success: " + str(response.result))
        return response.result

    @protect_grpc
    def adjust_simplify(self, sel):
        """Simplify faces into planes, cones, cylinders, lines, or arcs.

        Parameters
        ----------
        sel : ansys.api.discovery.v1.models_pb2.DesignFace[]
            Faces to simplify.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> bodies = client.bodies.all
        >>> client.repair_tools.adjust_simplify(faces)
        INFO - 127.0.0.1:50055 - repair_tools - adjust_simplify - adjust_simplify
                response:Success: True
        """
        response = self._repair_tools.AdjustSimplify(AdjustSimplifyRequest(selection=sel))
        self._logger.info("Success: " + str(response.result))
        return response.result

    @protect_grpc
    def adjust_inexact_edges(self, sel):
        """Detect and fix edges that do not precisely lie at the intersection of two faces.

        Parameters
        ----------
        sel : ansys.api.discovery.v1.models_pb2.DesignEdge[]
            Edges to analyze and clean.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery(127.0.0.1:50055)
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> edges = client.edges.all
        >>> client.repair_tools.adjust_inexact_edges(edges)
        INFO - 127.0.0.1:50055 - repair_tools - adjust_inexact_edges - adjust_inexact_edges
                response:Success: True
        """
        response = self._repair_tools.AdjustInexactEdges(AdjustInexactEdgesRequest(selection=sel))
        self._logger.info("Success: " + str(response.result))
        return response.result
