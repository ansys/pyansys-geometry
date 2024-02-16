# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""PyAnsys Geometry connection subpackage."""

from ansys.geometry.core.connection.backend import ApiVersions, BackendType
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
from ansys.geometry.core.connection.docker_instance import (
    GeometryContainers,
    LocalDockerInstance,
    get_geometry_container_type,
)
from ansys.geometry.core.connection.launcher import (
    launch_docker_modeler,
    launch_modeler,
    launch_modeler_with_discovery,
    launch_modeler_with_discovery_and_pimlight,
    launch_modeler_with_geometry_service,
    launch_modeler_with_geometry_service_and_pimlight,
    launch_modeler_with_spaceclaim,
    launch_modeler_with_spaceclaim_and_pimlight,
    launch_remote_modeler,
)
from ansys.geometry.core.connection.product_instance import ProductInstance
