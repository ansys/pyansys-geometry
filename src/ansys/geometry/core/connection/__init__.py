"""PyGeometry connection subpackage."""

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.connection.conversions import (
    frame_to_grpc_frame,
    grpc_frame_to_frame,
    grpc_matrix_to_matrix,
    plane_to_grpc_plane,
    point3d_to_grpc_point,
    sketch_shapes_to_grpc_geometries,
    tess_to_pd,
    unit_vector_to_grpc_direction,
)
from ansys.geometry.core.connection.defaults import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    GEOMETRY_SERVICE_DOCKER_IMAGE,
)
from ansys.geometry.core.connection.launcher import (
    launch_local_modeler,
    launch_modeler,
    launch_remote_modeler,
)
from ansys.geometry.core.connection.local_instance import GeometryContainers, LocalDockerInstance
