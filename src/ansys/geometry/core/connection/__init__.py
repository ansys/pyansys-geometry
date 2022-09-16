"""PyGeometry connection subpackage."""

import os

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.connection.conversions import (
    plane_to_grpc_plane,
    sketch_shapes_to_grpc_geometries,
    unit_vector_to_grpc_direction,
)
from ansys.geometry.core.connection.defaults import DEFAULT_HOST, DEFAULT_PORT
