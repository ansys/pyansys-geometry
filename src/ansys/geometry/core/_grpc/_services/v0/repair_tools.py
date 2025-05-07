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
"""Module containing the repair tools service implementation for v0.

This module defines an abstract base class for a gRPC-based repair tools service.
The class provides a set of abstract methods for identifying and repairing various
geometry issues, such as split edges, extra edges, duplicate faces etc.
"""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.repair_tools import GRPCRepairToolsService


class GRPCRepairToolsServiceV0(GRPCRepairToolsService):  # noqa: D102
    """Repair tools service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    Repair Tools service. It is specifically designed for the v0 version
    of the Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):
        from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub

        self.stub = RepairToolsStub(channel)

    @protect_grpc
    def find_split_edges(self, **kwargs) -> dict:  # noqa: D102
        """Identify split edges in the geometry.

        This method interacts with the gRPC service to identify split edges
        in the provided geometry based on the input parameters.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments containing the input parameters for the request.
            - bodies_or_faces: list
                List of body or face identifiers to inspect.
            - angle: float
                The angle threshold for identifying split edges.
            - distance: float
                The distance threshold for identifying split edges.

        Returns
        -------
        dict
            A dictionary containing the identified split edge problems. Each problem
            includes an ID and a list of associated edge monikers.

            Example:
            {
                "problems": [
                    {
                        "id": "problem_id_1",
                        "edges": ["edge_1", "edge_2"]
                    },
                    ...
                ]
            }
        """
        from google.protobuf.wrappers_pb2 import DoubleValue

        from ansys.api.geometry.v0.repairtools_pb2 import FindSplitEdgesRequest

        # Create the gRPC request
        request = FindSplitEdgesRequest(
            bodies_or_faces=kwargs["bodies_or_faces"],
            angle=DoubleValue(value=float(kwargs["angle"])),
            distance=DoubleValue(value=float(kwargs["distance"])),
        )

        # Call the gRPC service
        response = self.stub.FindSplitEdges(request)

        # Format and return the response as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "edges": res.edge_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_extra_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindExtraEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindExtraEdgesRequest(selection=kwargs["selection"])

        # Return the response - formatted as a dictionary
        response = self.stub.FindExtraEdges(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "edges": res.edge_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_inexact_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindInexactEdgesRequest

        request = FindInexactEdgesRequest(selection=kwargs["selection"])

        # Call the gRPC service
        response = self.stub.FindInexactEdges(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "edges": res.edge_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_short_edges(self, **kwargs) -> dict:  # noqa: D102
        from google.protobuf.wrappers_pb2 import DoubleValue

        from ansys.api.geometry.v0.repairtools_pb2 import FindShortEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindShortEdgesRequest(
            selection=kwargs["selection"],
            max_edge_length=DoubleValue(value=kwargs["length"]),
        )

        # Call the gRPC service
        response = self.stub.FindShortEdges(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "edges": res.edge_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_duplicate_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindDuplicateFacesRequest

        request = FindDuplicateFacesRequest(faces=kwargs["faces"])

        # Call the gRPC service
        response = self.stub.FindDuplicateFaces(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "faces": res.face_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_missing_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindMissingFacesRequest

        request = FindMissingFacesRequest(faces=kwargs["faces"])
        # Call the gRPC service
        response = self.stub.FindMissingFaces(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "edges": res.edge_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_small_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindSmallFacesRequest

        request = FindSmallFacesRequest(selection=kwargs["selection"])
        # Call the gRPC service
        response = self.stub.FindSmallFaces(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "faces": res.face_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_stitch_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindStitchFacesRequest

        request = FindStitchFacesRequest(faces=kwargs["faces"])
        # Call the gRPC service
        response = self.stub.FindStitchFaces(request)
        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "bodies": res.body_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_simplify(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindAdjustSimplifyRequest

        request = FindAdjustSimplifyRequest(selection=kwargs["selection"])

        # Call the gRPC service
        response = self.stub.FindAdjustSimplify(request)
        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "bodies": res.body_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_and_fix_simplify(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindAdjustSimplifyRequest

        request = FindAdjustSimplifyRequest(
            selection=kwargs["selection"],
            comprehensive=kwargs["comprehensive_result"],
        )
        # Call the gRPC service
        response = self.stub.FindAndSimplify(request)
        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "found": response.found,
            "repaired": response.repaired,
            "created_bodies_monikers": [],
            "modified_bodies_monikers": [],
        }

    @protect_grpc
    def inspect_geometry(self, **kwargs) -> dict:  # noqa: D102
        """Inspect the geometry for issues.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments containing the input parameters for the inspection.
            - bodies: list
                List of bodies to inspect.

        Returns
        -------
        dict
            A dictionary containing the serialized inspection results.
        """
        from ansys.api.geometry.v0.repairtools_pb2 import InspectGeometryRequest

        # Create the gRPC request
        request = InspectGeometryRequest(bodies=kwargs.get("bodies", []))

        # Call the gRPC service
        inspect_result_response = self.stub.InspectGeometry(request)

        # Serialize and return the response
        return self.serialize_inspect_result_response(inspect_result_response)

    @protect_grpc
    def repair_geometry(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import RepairGeometryRequest

        request = RepairGeometryRequest(bodies=kwargs.get("bodies", []))

        # Call the gRPC service
        response = self.stub.RepairGeometry(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.result.success,
        }

    @protect_grpc
    def find_interferences(self, **kwargs) -> dict:  # noqa: D102
        from google.protobuf.wrappers_pb2 import BoolValue

        from ansys.api.geometry.v0.repairtools_pb2 import FindInterferenceRequest

        request = FindInterferenceRequest(
            bodies=kwargs["bodies"],
            cut_smaller_body=BoolValue(value=kwargs["cut_smaller_body"]),
        )

        # Call the gRPC service
        response = self.stub.FindInterference(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "bodies": res.body_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_and_fix_short_edges(self, **kwargs):  # noqa: D102
        from google.protobuf.wrappers_pb2 import DoubleValue

        from ansys.api.geometry.v0.repairtools_pb2 import FindShortEdgesRequest

        request = FindShortEdgesRequest(
            selection=kwargs["selection"],
            max_edge_length=DoubleValue(value=kwargs["length"]),
            comprehensive=kwargs["comprehensive_result"],
        )
        # Call the gRPC service
        response = self.stub.FindAndFixShortEdges(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "found": response.found,
            "repaired": response.repaired,
            "created_bodies_monikers": [],
            "modified_bodies_monikers": [],
        }

    @protect_grpc
    def find_and_fix_extra_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindExtraEdgesRequest

        request = FindExtraEdgesRequest(
            selection=kwargs["selection"],
            comprehensive=kwargs["comprehensive_result"],
        )
        # Call the gRPC service
        response = self.stub.FindAndFixExtraEdges(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "found": response.found,
            "repaired": response.repaired,
            "created_bodies_monikers": response.created_bodies_monikers,
            "modified_bodies_monikers": response.modified_bodies_monikers,
        }

    @protect_grpc
    def find_and_fix_split_edges(self, **kwargs) -> dict:  # noqa: D102
        from google.protobuf.wrappers_pb2 import DoubleValue

        from ansys.api.geometry.v0.repairtools_pb2 import FindSplitEdgesRequest

        request = FindSplitEdgesRequest(
            bodies_or_faces=kwargs["bodies_or_faces"],
            angle=DoubleValue(value=float(kwargs["angle"])),
            distance=DoubleValue(value=float(kwargs["length"])),
            comprehensive=kwargs["comprehensive_result"],
        )

        # Call the gRPC service
        response = self.stub.FindAndFixSplitEdges(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "found": response.found,
            "repaired": response.repaired,
            "created_bodies_monikers": [],
            "modified_bodies_monikers": [],
        }

    @staticmethod
    def serialize_inspect_result_response(response) -> dict:
        """Serialize the InspectGeometryResponse to a dictionary."""

        def serialize_body(body):
            return {
                "id": body.id,
                "name": body.name,
                "can_suppress": body.can_suppress,
                "transform_to_master": {
                    "m00": body.transform_to_master.m00,
                    "m11": body.transform_to_master.m11,
                    "m22": body.transform_to_master.m22,
                    "m33": body.transform_to_master.m33,
                },
                "master_id": body.master_id,
                "parent_id": body.parent_id,
            }

        def serialize_face(face):
            return {
                "id": face.id,
                "surface_type": face.surface_type,
                "export_id": face.export_id,
                "is_reversed": getattr(face, "is_reversed", False),
                "parent_id": face.parent_id.id,
            }

        def serialize_edge(edge):
            return {
                "id": edge.id,
                "curve_type": edge.curve_type,
                "export_id": edge.export_id,
                "length": edge.length,
                "owner_id": edge.owner_id,
                "parent": serialize_body(edge.parent) if hasattr(edge, "parent") else None,
            }

        def serialize_issue(issue):
            return {
                "message_type": issue.message_type,
                "message_id": issue.message_id,
                "message": issue.message,
                "faces": [serialize_face(f) for f in issue.faces],
                "edges": [serialize_edge(e) for e in issue.edges],
            }

        return {
            "issues_by_body": [
                {
                    "body": serialize_body(body_issues.body),
                    "issues": [serialize_issue(i) for i in body_issues.issues],
                }
                for body_issues in response.issues_by_body
            ]
        }
