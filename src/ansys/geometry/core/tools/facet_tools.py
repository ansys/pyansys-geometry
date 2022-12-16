"""Module contains the preparation tools for models."""

from ansys.api.geometry.v0.facettools_pb2 import ShrinkWrapBodyRequest, ShrinkWrapMeshRequest
from ansys.api.geometry.v0.facettools_pb2_grpc import FacetToolsStub
from ansys.api.geometry.v0.models_pb2 import ShrinkWrapOptions
from grpc import Channel

from ansys.geometry import LOG as logger
from ansys.geometry.core.errors import protect_grpc


class FacetTools:
    """Provides model preparation tools.

    Parameters
    ----------
    channel : grpc.Channel
        gRPC channel for initializing the ``FacetToolsStub`` object.
    logger_name : str
        Instance of Discovery to connect to. For example, ``localhost:12345``.
    """

    def __init__(self, channel, logger_name):
        """Initialize the ``FacetTools`` object."""
        if isinstance(channel, Channel):
            self._connection = FacetToolsStub(channel)
            self._logger = logger[logger_name]
        else:
            raise Exception("invalid gRPC channel.")

    @protect_grpc
    def shrinkwrap_body(self, sel=None, options_shrinkwrap=None):
        """Shrink wrap bodies.

        Parameters
        ----------
        sel : ansys.discovery.models.model.Body[], optional
            Bodies to shrink wrap. The default is ``None``.
        options_shrinkwrap: options object, optional
            Object that defines the shrink wrap parameters. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery("127.0.0.1:50055")
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> bodies = client.bodies.all
        >>> options = OptionsShrinkWrap()
        >>> options.keep_original = False
        >>> options.preserve_features = False
        >>> options.min_size = 0.0005
        >>> options.max_size = 0.0005
        >>> options.secondary_size = None
        >>> options.angle_tolerance = None
        >>> options.curvature_normal_angle = 0.00
        >>> client.facet_tools.shrinkwrap_body(bodies, options)
        INFO - 127.0.0.1:50055 -  facet_tools - shrinkwrap_body - shrinkwrap_body.
                response:Shrink wrap body with options success: True
        """
        if options_shrinkwrap is None:

            response = self._connection.ShrinkWrapBody(
                ShrinkWrapBodyRequest(selection=sel if sel else [])
            )
            self._logger.info("Shrink wrap body without options success: " + str(response.result))

        else:
            soptions = ShrinkWrapOptions(
                size=options_shrinkwrap.min_size,
                keep_original_bodies=options_shrinkwrap.keep_original,
                preserve_features=options_shrinkwrap.preserve_features,
                angle_tolerance=options_shrinkwrap.angle_tolerance,
                secondary_size_enabled=True,
                secondary_size=options_shrinkwrap.secondary_size,
                max_size_enabled=True,
                max_size=options_shrinkwrap.max_size,
                curvature_angle=options_shrinkwrap.curvature_normal_angle,
            )

            response = self._connection.ShrinkWrapBody(
                ShrinkWrapBodyRequest(selection=sel, options=soptions)
            )
            self._logger.info("Shrink wrap body with options success: " + str(response.result))
        return response.result

    @protect_grpc
    def shrinkwrap_mesh(self, sel=None, options_shrinkwrap=None):
        """Shrink wrap mesh.

        Parameters
        ----------
        sel : ansys.api.discovery.v1.models_pb2.DesignMesh[], optional
            Meshes to shrink wrap. The default is ``None``.
        options_shrinkwrap: options object (optional)
            Object that defines the shrink wrap parameters. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.discovery.core.launcher import launch_discovery
        >>> client = launch_discovery("127.0.0.1:50055")
        INFO -  -  connection - connect - Connection: gRPC channel created.
        INFO -  -  connection - wait_for_transient_failure - Connection: idle.
        INFO -  -  connection - wait_for_transient_failure - Connection: connecting.
        INFO -  -  connection - wait_for_transient_failure - Connection: ready.
        INFO -  -  connection - connect - Connection: connected to: 127.0.0.1:50055
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization...
        INFO - 127.0.0.1:50055 -  discovery - _initialize_stubs - Ansys Discovery API client initialization done.
        >>> meshes = client.meshes.get_all()
        >>> options = OptionsShrinkWrap()
        >>> options.keep_original = False
        >>> options.preserve_features = False
        >>> options.min_size = 0.0005
        >>> options.max_size = 0.0005
        >>> options.secondary_size = None
        >>> options.angle_tolerance = None
        >>> options.curvature_normal_angle = 0.00
        >>> client.facet_tools.shrinkwrap_mesh(meshes, options)
        INFO - 127.0.0.1:50055 -  facet_tools - shrinkwrap_mesh - shrinkwrap_mesh.
                response:Shrink wrap body with options success: TrueTrue
        """

        if options_shrinkwrap is None:
            response = self._connection.ShrinkWrapMesh(
                ShrinkWrapMeshRequest(selection=sel if sel else [])
            )
            self._logger.info("Shrink wrap mesh without options success: " + str(response.result))

            response = self._connection.ShrinkWrapMesh(
                ShrinkWrapMeshRequest(selection=sel if sel else [])
            )

        else:
            soptions = ShrinkWrapOptions(
                size=options_shrinkwrap.min_size,
                keep_original_bodies=options_shrinkwrap.keep_original,
                preserve_features=options_shrinkwrap.preserve_features,
                angle_tolerance=options_shrinkwrap.angle_tolerance,
                secondary_size_enabled=True,
                secondary_size=options_shrinkwrap.secondary_size,
                max_size_enabled=True,
                max_size=options_shrinkwrap.max_size,
                curvature_angle=options_shrinkwrap.curvature_normal_angle,
            )

            response = self._connection.ShrinkWrapMesh(
                ShrinkWrapBodyRequest(selection=sel if sel else [], options=soptions)
            )
            self._logger.info("Shrink wrap mesh with options success: " + str(response.result))
        return response.result


class OptionsShrinkWrap:
    """Provides options for shrink wrapping bodies or meshes.

    Parameters
    ----------
    max_size : float, optional
        Maximum size of the mesh or body to shrink wrap.
        The default is `None`.
    min_size : float, optional
       Minimum size of the mesh or body to shrink wrap.
        The default is `None`.
    secondary_size : int, optional
        Secondary size of the mesh or body.
        The default is `0`.
    angle_tolerance : degree, optional
        Tolerance angle of mesh or body while wrapping.
        The default is `0`.
    curvature_normal_angle : degree, optional
        Alignment angle for shrink wrapping the mesh or body.
        The default is `0`.
    keep_original : bool, optional
        Whether to keep the original size. The default is ``True``.
    preserve_features : bool, optional
        Whether to preserve the features of the mesh or body. The default is ``True``.
    """

    def __init__(self):
        """Constructor for shrink wrap options."""
        self.max_size = None
        self.min_size = None
        self.secondary_size = 0
        self.angle_tolerance = 0
        self.curvature_normal_angle = 0
        self.keep_original = False
        self.preserve_features = False
