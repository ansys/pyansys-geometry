# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
"""Module containing the components service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.components import GRPCComponentsService
from .conversions import (
    build_grpc_id,
    from_angle_to_grpc_quantity,
    from_grpc_matrix_to_matrix,
    from_point3d_to_grpc_point,
    from_unit_vector_to_grpc_direction,
)


class GRPCComponentsServiceV1(GRPCComponentsService):
    """Components service for gRPC communication with the Geometry server.

    This class provides methods to call components in the
    Geometry server using gRPC. It is specifically designed for the v1
    version of the Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.component_pb2_grpc import ComponentStub

        self.stub = ComponentStub(channel)

    @protect_grpc
    def create(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.component_pb2 import (
            CreateComponentData,
            CreateRequest,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateRequest(
            components=[
                CreateComponentData(
                    name=kwargs["name"],
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    template_id=build_grpc_id(kwargs["template_id"]),
                    instance_name=kwargs["instance_name"],
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.Create(request)

        # Return the response - formatted as a dictionary
        # Note: response.components is a repeated field, we return the first one
        component = response.components[0]
        return {
            "id": component.id.id,
            "name": component.name,
            "instance_name": component.instance_name,
            "template": kwargs["template_id"],  # template_id from input
            "component": component,
        }

    @protect_grpc
    def set_name(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.designmessages_pb2 import (
            SetDesignEntityNameRequest,
            SetDesignEntityNameRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetDesignEntityNameRequest(
            request_data=[
                SetDesignEntityNameRequestData(
                    id=build_grpc_id(kwargs["id"]),
                    name=kwargs["name"],
                )
            ]
        )

        # Call the gRPC service
        _ = self.stub.SetName(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def set_placement(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.component_pb2 import (
            PlacementData,
            SetPlacementRequest,
        )

        # Create the direction and point objects
        translation = (
            from_unit_vector_to_grpc_direction(kwargs["translation"].normalize())
            if kwargs["translation"] is not None
            else None
        )
        origin = (
            from_point3d_to_grpc_point(kwargs["rotation_axis_origin"])
            if kwargs["rotation_axis_origin"] is not None
            else None
        )
        direction = (
            from_unit_vector_to_grpc_direction(kwargs["rotation_axis_direction"])
            if kwargs["rotation_axis_direction"] is not None
            else None
        )

        # Create the request with repeated ids and placements
        request = SetPlacementRequest(
            ids=[build_grpc_id(kwargs["id"])],
            placements=[
                PlacementData(
                    translation=translation,
                    rotation_axis_origin=origin,
                    rotation_axis_direction=direction,
                    rotation_angle=from_angle_to_grpc_quantity(kwargs["rotation_angle"]),
                )
            ],
        )

        # Call the gRPC service
        response = self.stub.SetPlacement(request)

        # Return the response - formatted as a dictionary
        # Note: response.matrices is a map<string, Matrix>
        # Get the matrix for our component ID
        matrix_value = response.matrices.get(kwargs["id"])
        return {"matrix": from_grpc_matrix_to_matrix(matrix_value) if matrix_value else None}

    @protect_grpc
    def set_shared_topology(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.component_pb2 import (
            SetSharedTopologyRequest,
            SharedTopologyData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetSharedTopologyRequest(
            shared_topologies=[
                SharedTopologyData(
                    id=build_grpc_id(kwargs["id"]),
                    share_type=kwargs["share_type"].value,
                )
            ]
        )

        # Call the gRPC service
        _ = self.stub.SetSharedTopology(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def delete(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        _ = self.stub.Delete(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def import_groups(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.component_pb2 import ImportGroupsRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ImportGroupsRequest(
            id=build_grpc_id(kwargs["id"]),
        )

        # Call the gRPC service
        _ = self.stub.ImportGroups(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def make_independent(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.component_pb2 import MakeIndependentRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = MakeIndependentRequest(
            ids=[build_grpc_id(id) for id in kwargs["ids"]],
        )

        # Call the gRPC service
        _ = self.stub.MakeIndependent(request)

        # Return the response - formatted as a dictionary
        return {}
