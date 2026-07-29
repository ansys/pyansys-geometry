# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Module containing the datum lines service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.datum_lines import GRPCDatumLinesService
from .conversions import build_grpc_id, from_grpc_curve_to_curve, from_line_to_grpc_line


class GRPCDatumLinesServiceV1(GRPCDatumLinesService):
    """Datum lines service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    datum lines service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.constructs.datumline_pb2_grpc import DatumLineStub

        self.stub = DatumLineStub(channel)

    @protect_grpc
    def create(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.constructs.datumline_pb2 import (
            DatumLineCreationRequest,
            DatumLineCreationRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = DatumLineCreationRequest(
            request_data=[
                DatumLineCreationRequestData(
                    line=from_line_to_grpc_line(kwargs["line"]),
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    name=kwargs["name"],
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.Create(request)

        # Return the response - formatted as a dictionary
        return {
            "lines": [
                {
                    "id": line.id.id,
                    "name": line.name,
                    "parent_id": line.parent_id.id,
                }
                for line in response.lines
            ]
        }

    @protect_grpc
    def delete(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(
            ids=[build_grpc_id(id) for id in kwargs["ids"]],
        )

        # Call the gRPC service
        response = self.stub.Delete(request)

        # Return the response - formatted as a dictionary
        return {
            "deleted_ids": [e.id for e in response.deleted_object_ids],
            "failed_ids": [e.id for e in response.failed_deletion_ids],
        }

    @protect_grpc
    def get(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import EntityRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = EntityRequest(id=build_grpc_id(kwargs["id"]))

        # Call the gRPC service
        line = self.stub.Get(request).line

        # Return the response - formatted as a dictionary
        return {
            "id": line.id.id,
            "name": line.name,
            "line": from_grpc_curve_to_curve(line.line),
            "parent_id": line.parent_id.id,
            "is_pinned": line.is_pinned,
        }

    @protect_grpc
    def get_all(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import ParentEntityRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ParentEntityRequest(parent_id=build_grpc_id(kwargs["parent_id"]))

        # Call the gRPC service
        response = self.stub.GetAll(request)

        # Return the response - formatted as a dictionary
        return {
            "lines": [
                {
                    "id": line.id.id,
                    "name": line.name,
                    "line": from_grpc_curve_to_curve(line.line),
                    "parent_id": line.parent_id.id,
                    "is_pinned": line.is_pinned,
                }
                for line in response.lines
            ]
        }

    @protect_grpc
    def get_is_deleted(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(
            ids=[build_grpc_id(id) for id in kwargs["ids"]],
        )

        # Call the gRPC service
        response = self.stub.GetIsDeleted(request)

        # Return the response - formatted as a dictionary
        return {"deleted": dict(response.deleted)}
