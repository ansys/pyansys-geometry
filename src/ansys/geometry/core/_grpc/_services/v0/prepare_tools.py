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
"""Module containing the Prepare Tools service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.prepare_tools import GRPCPrepareToolsService


class GRPCPrepareToolsServiceV0(GRPCPrepareToolsService):
    """Prepare tools service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    Prepare Tools service. It is specifically designed for the v0 version
    of the Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.geometry.v0.preparetools_pb2_grpc import PrepareToolsStub

        self.stub = PrepareToolsStub(channel)

    @protect_grpc
    def extract_volume_from_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.preparetools_pb2 import ExtractVolumeFromFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ExtractVolumeFromFacesRequest(
            sealing_faces=[EntityIdentifier(id=face.id) for face in kwargs["sealing_faces"]],
            inside_faces=[EntityIdentifier(id=face.id) for face in kwargs["inside_faces"]],
        )

        # Call the gRPC service
        response = self.stub.ExtractVolumeFromFaces(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "created_bodies": [body.id for body in response.created_bodies],
        }

    @protect_grpc
    def extract_volume_from_edge_loops(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.preparetools_pb2 import ExtractVolumeFromEdgeLoopsRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ExtractVolumeFromEdgeLoopsRequest(
            sealing_edges=[EntityIdentifier(id=face.id) for face in kwargs["sealing_edges"]],
            inside_faces=[EntityIdentifier(id=face.id) for face in kwargs["inside_faces"]],
        )

        # Call the gRPC service
        response = self.stub.ExtractVolumeFromEdgeLoops(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "created_bodies": [body.id for body in response.created_bodies],
        }

    @protect_grpc
    def remove_rounds(self, **kwargs) -> dict:  # noqa: D102
        from google.protobuf.wrappers_pb2 import BoolValue

        from ansys.api.geometry.v0.models_pb2 import Face
        from ansys.api.geometry.v0.preparetools_pb2 import RemoveRoundsRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = RemoveRoundsRequest(
            selection=[Face(id=round.id) for round in kwargs["rounds"]],
            auto_shrink=BoolValue(value=kwargs["auto_shrink"]),
        )

        # Call the gRPC service
        response = self.stub.RemoveRounds(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.result,
        }

    @protect_grpc
    def share_topology(self, **kwargs) -> dict:  # noqa: D102
        from google.protobuf.wrappers_pb2 import BoolValue, DoubleValue

        from ansys.api.geometry.v0.models_pb2 import Body
        from ansys.api.geometry.v0.preparetools_pb2 import ShareTopologyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ShareTopologyRequest(
            selection=[Body(id=body.id) for body in kwargs["bodies"]],
            tolerance=DoubleValue(value=kwargs["tolerance"]),
            preserve_instances=BoolValue(value=kwargs["preserve_instances"]),
        )

        # Call the gRPC service
        response = self.stub.ShareTopology(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.result,
        }

    @protect_grpc
    def enhanced_share_topology(self, **kwargs) -> dict:  # noqa: D102
        from google.protobuf.wrappers_pb2 import BoolValue, DoubleValue

        from ansys.api.geometry.v0.models_pb2 import Body
        from ansys.api.geometry.v0.preparetools_pb2 import ShareTopologyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ShareTopologyRequest(
            selection=[Body(id=body.id) for body in kwargs["bodies"]],
            tolerance=DoubleValue(value=kwargs["tolerance"]),
            preserve_instances=BoolValue(value=kwargs["preserve_instances"]),
        )

        # Call the gRPC service
        response = self.stub.EnhancedShareTopology(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "found": response.found,
            "repaired": response.repaired,
            "created_bodies_monikers": response.created_bodies_monikers,
            "modified_bodies_monikers": response.modified_bodies_monikers,
            "deleted_bodies_monikers": response.deleted_bodies_monikers,
        }

    @protect_grpc
    def find_logos(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.models_pb2 import FindLogoOptions
        from ansys.api.geometry.v0.preparetools_pb2 import FindLogosRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindLogosRequest(
            bodies=[EntityIdentifier(id=body.id) for body in kwargs["bodies"]],
            options=FindLogoOptions(
                min_height=kwargs["min_height"],
                max_height=kwargs["max_height"],
            ),
        )

        # Call the gRPC service
        response = self.stub.FindLogos(request)

        # Return the response - formatted as a dictionary
        return {
            "id": response.id,
            "face_ids": [face.id for face in response.logo_faces],
        }

    @protect_grpc
    def find_and_remove_logos(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.models_pb2 import FindLogoOptions
        from ansys.api.geometry.v0.preparetools_pb2 import FindLogosRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindLogosRequest(
            bodies=[EntityIdentifier(id=body.id) for body in kwargs["bodies"]],
            options=FindLogoOptions(
                min_height=kwargs["min_height"],
                max_height=kwargs["max_height"],
            ),
        )

        # Call the gRPC service
        response = self.stub.FindAndRemoveLogos(request)

        # Return the response - formatted as a dictionary
        return {"success": response.success}

    @protect_grpc
    def remove_logo(self, **kwargs):  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.preparetools_pb2 import RemoveLogoRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = RemoveLogoRequest(
            face_ids=[EntityIdentifier(id=face.id) for face in kwargs["face_ids"]],
        )

        # Call the gRPC service
        response = self.stub.RemoveLogo(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
        }
