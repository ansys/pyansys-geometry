"""PyGeometry connection subpackage."""

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.connection.conversions import (
    plane_to_grpc_plane,
    sketch_shapes_to_grpc_geometries,
    tess_to_pd,
    unit_vector_to_grpc_direction,
)
from ansys.geometry.core.connection.defaults import DEFAULT_HOST, DEFAULT_PORT
from ansys.geometry.core.connection.launcher import (
    launch_local_modeler,
    launch_modeler,
    launch_remote_modeler,
)
from ansys.geometry.core.connection.localinstance import LocalDockerInstance
