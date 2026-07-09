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

"""Module containing the Face Selection service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.face_selection import GRPCFaceSelectionService
from .conversions import (
    build_grpc_id,
    from_area_to_grpc_quantity,
    from_length_to_grpc_quantity,
    serialize_face_group_response,
    serialize_face_selection_response,
)


class GRPCFaceSelectionServiceV1(GRPCFaceSelectionService):
    """Face Selection service for gRPC communication with the Geometry server (v1).

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2_grpc import (
            FaceSelectionStub,
        )

        self.stub = FaceSelectionStub(channel)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _input_request(self, kwargs):
        """Build a ``FaceSelectionInputRequest`` from ``face_ids``."""
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FaceSelectionInputRequest,
            FaceSelectionInputRequestData,
        )

        return FaceSelectionInputRequest(
            request_data=[
                FaceSelectionInputRequestData(
                    face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]]
                )
            ]
        )

    def _extend_request(self, kwargs):
        """Build a ``FaceSelectionExtendRequest``."""
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FaceSelectionExtendRequest,
            FaceSelectionExtendRequestData,
        )

        return FaceSelectionExtendRequest(
            request_data=[
                FaceSelectionExtendRequestData(
                    face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
                    scope=kwargs["scope"],
                )
            ]
        )

    # ── Static factory ────────────────────────────────────────────────────────

    @protect_grpc
    def get_all_visible_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            GetAllVisibleFacesRequest,
        )

        return serialize_face_selection_response(
            self.stub.GetAllVisibleFaces(GetAllVisibleFacesRequest())
        )

    @protect_grpc
    def get_all_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            GetAllFacesRequest,
        )

        return serialize_face_selection_response(self.stub.GetAllFaces(GetAllFacesRequest()))

    @protect_grpc
    def get_faces_from_named_selection(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            GetFacesFromNamedSelectionRequest,
            GetFacesFromNamedSelectionRequestData,
        )

        request = GetFacesFromNamedSelectionRequest(
            request_data=[GetFacesFromNamedSelectionRequestData(name=kwargs["name"])]
        )
        return serialize_face_selection_response(self.stub.GetFacesFromNamedSelection(request))

    @protect_grpc
    def get_faces_with_area(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            GetFacesWithAreaRequest,
            GetFacesWithAreaRequestData,
        )

        data = GetFacesWithAreaRequestData(
            min=from_area_to_grpc_quantity(kwargs["min"]),
            max=from_area_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
        )
        return serialize_face_selection_response(
            self.stub.GetFacesWithArea(GetFacesWithAreaRequest(request_data=[data]))
        )

    @protect_grpc
    def get_faces_with_x_location(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            GetFacesWithLocationRequest,
            GetFacesWithLocationRequestData,
        )

        data = GetFacesWithLocationRequestData(
            min=from_length_to_grpc_quantity(kwargs["min"]) if kwargs["min"] is not None else None,
            max=from_length_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
            range_type=kwargs["range_type"].value,
        )
        return serialize_face_selection_response(
            self.stub.GetFacesWithXLocation(GetFacesWithLocationRequest(request_data=[data]))
        )

    @protect_grpc
    def get_faces_with_y_location(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            GetFacesWithLocationRequest,
            GetFacesWithLocationRequestData,
        )

        data = GetFacesWithLocationRequestData(
            min=from_length_to_grpc_quantity(kwargs["min"]) if kwargs["min"] is not None else None,
            max=from_length_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
            range_type=kwargs["range_type"].value,
        )
        return serialize_face_selection_response(
            self.stub.GetFacesWithYLocation(GetFacesWithLocationRequest(request_data=[data]))
        )

    @protect_grpc
    def get_faces_with_z_location(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            GetFacesWithLocationRequest,
            GetFacesWithLocationRequestData,
        )

        data = GetFacesWithLocationRequestData(
            min=from_length_to_grpc_quantity(kwargs["min"]) if kwargs["min"] is not None else None,
            max=from_length_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
            range_type=kwargs["range_type"].value,
        )
        return serialize_face_selection_response(
            self.stub.GetFacesWithZLocation(GetFacesWithLocationRequest(request_data=[data]))
        )

    @protect_grpc
    def get_faces_with_color(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            GetFacesWithColorRequest,
            GetFacesWithColorRequestData,
        )

        request = GetFacesWithColorRequest(
            request_data=[GetFacesWithColorRequestData(color=kwargs["color"])]
        )
        return serialize_face_selection_response(self.stub.GetFacesWithColor(request))

    # ── Instance operations ───────────────────────────────────────────────────

    @protect_grpc
    def invert_face_selection(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            InvertFaceSelectionRequest,
            InvertFaceSelectionRequestData,
        )

        request = InvertFaceSelectionRequest(
            request_data=[
                InvertFaceSelectionRequestData(
                    face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
                    scope=kwargs["scope"].value,
                )
            ]
        )
        return serialize_face_selection_response(self.stub.InvertFaceSelection(request))

    # ── Filter ────────────────────────────────────────────────────────────────

    @protect_grpc
    def filter_faces_by_area(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FilterFacesByAreaRequest,
            FilterFacesByAreaRequestData,
        )

        data = FilterFacesByAreaRequestData(
            face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
            min=from_area_to_grpc_quantity(kwargs["min"]),
            max=from_area_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
        )
        return serialize_face_selection_response(
            self.stub.FilterFacesByArea(FilterFacesByAreaRequest(request_data=[data]))
        )

    @protect_grpc
    def filter_faces_max_area(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.FilterFacesMaxArea(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_faces_min_area(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.FilterFacesMinArea(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_faces_by_perimeter(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FilterFacesByPerimeterRequest,
            FilterFacesByPerimeterRequestData,
        )

        data = FilterFacesByPerimeterRequestData(
            face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
            min=from_length_to_grpc_quantity(kwargs["min"]),
            max=(
                from_length_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None
            ),
        )
        return serialize_face_selection_response(
            self.stub.FilterFacesByPerimeter(FilterFacesByPerimeterRequest(request_data=[data]))
        )

    @protect_grpc
    def filter_faces_max_perimeter(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.FilterFacesMaxPerimeter(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_faces_min_perimeter(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.FilterFacesMinPerimeter(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_faces_by_edge_count(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FilterFacesByIntRangeRequest,
            FilterFacesByIntRangeRequestData,
        )

        data = FilterFacesByIntRangeRequestData(
            face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
            min=kwargs["min"],
            max=kwargs["max"] if kwargs["max"] is not None else None,
        )
        return serialize_face_selection_response(
            self.stub.FilterFacesByEdgeCount(FilterFacesByIntRangeRequest(request_data=[data]))
        )

    @protect_grpc
    def filter_faces_max_edge_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.FilterFacesMaxEdgeCount(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_faces_min_edge_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.FilterFacesMinEdgeCount(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_faces_by_loop_count(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FilterFacesByIntRangeRequest,
            FilterFacesByIntRangeRequestData,
        )

        data = FilterFacesByIntRangeRequestData(
            face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
            min=kwargs["min"],
            max=kwargs["max"] if kwargs["max"] is not None else None,
        )
        return serialize_face_selection_response(
            self.stub.FilterFacesByLoopCount(FilterFacesByIntRangeRequest(request_data=[data]))
        )

    @protect_grpc
    def filter_faces_max_loop_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.FilterFacesMaxLoopCount(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_faces_min_loop_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.FilterFacesMinLoopCount(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_faces_by_number_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FilterFacesByCurveCountRequest,
            FilterFacesByCurveCountRequestData,
        )

        data = FilterFacesByCurveCountRequestData(
            face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
            curve_type=kwargs["curve_type"],
            min=kwargs["min"],
            max=kwargs["max"] if kwargs["max"] is not None else None,
        )
        return serialize_face_selection_response(
            self.stub.FilterFacesByNumberCurves(
                FilterFacesByCurveCountRequest(request_data=[data])
            )
        )

    @protect_grpc
    def filter_faces_max_number_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FilterFacesByCurveTypeRequest,
            FilterFacesByCurveTypeRequestData,
        )

        request = FilterFacesByCurveTypeRequest(
            request_data=[
                FilterFacesByCurveTypeRequestData(
                    face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
                    curve_type=kwargs["curve_type"],
                )
            ]
        )
        return serialize_face_selection_response(self.stub.FilterFacesMaxNumberCurves(request))

    @protect_grpc
    def filter_faces_min_number_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FilterFacesByCurveTypeRequest,
            FilterFacesByCurveTypeRequestData,
        )

        request = FilterFacesByCurveTypeRequest(
            request_data=[
                FilterFacesByCurveTypeRequestData(
                    face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
                    curve_type=kwargs["curve_type"],
                )
            ]
        )
        return serialize_face_selection_response(self.stub.FilterFacesMinNumberCurves(request))

    @protect_grpc
    def filter_faces_containing_curve_types(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FilterFacesContainingCurveTypesRequest,
            FilterFacesContainingCurveTypesRequestData,
        )

        request = FilterFacesContainingCurveTypesRequest(
            request_data=[
                FilterFacesContainingCurveTypesRequestData(
                    face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
                    curve_types=kwargs["curve_types"].value,
                    exclusive=kwargs["exclusive"],
                )
            ]
        )
        return serialize_face_selection_response(
            self.stub.FilterFacesContainingCurveTypes(request)
        )

    @protect_grpc
    def filter_faces_by_color(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FilterFacesByColorRequest,
            FilterFacesByColorRequestData,
        )

        request = FilterFacesByColorRequest(
            request_data=[
                FilterFacesByColorRequestData(
                    face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
                    color=kwargs["color"],
                )
            ]
        )
        return serialize_face_selection_response(self.stub.FilterFacesByColor(request))

    @protect_grpc
    def filter_faces_area_percentile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FilterFacesPercentileRequest,
            FilterFacesPercentileRequestData,
        )

        request = FilterFacesPercentileRequest(
            request_data=[
                FilterFacesPercentileRequestData(
                    face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
                    min_percentile=kwargs["min_percentile"],
                    max_percentile=kwargs["max_percentile"],
                )
            ]
        )
        return serialize_face_selection_response(self.stub.FilterFacesAreaPercentile(request))

    @protect_grpc
    def filter_faces_perimeter_percentile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FilterFacesPercentileRequest,
            FilterFacesPercentileRequestData,
        )

        request = FilterFacesPercentileRequest(
            request_data=[
                FilterFacesPercentileRequestData(
                    face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
                    min_percentile=kwargs["min_percentile"],
                    max_percentile=kwargs["max_percentile"],
                )
            ]
        )
        return serialize_face_selection_response(self.stub.FilterFacesPerimeterPercentile(request))

    @protect_grpc
    def filter_faces_edge_count_percentile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FilterFacesPercentileRequest,
            FilterFacesPercentileRequestData,
        )

        request = FilterFacesPercentileRequest(
            request_data=[
                FilterFacesPercentileRequestData(
                    face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
                    min_percentile=kwargs["min_percentile"],
                    max_percentile=kwargs["max_percentile"],
                )
            ]
        )
        return serialize_face_selection_response(self.stub.FilterFacesEdgeCountPercentile(request))

    @protect_grpc
    def filter_faces_loop_count_percentile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FilterFacesPercentileRequest,
            FilterFacesPercentileRequestData,
        )

        request = FilterFacesPercentileRequest(
            request_data=[
                FilterFacesPercentileRequestData(
                    face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
                    min_percentile=kwargs["min_percentile"],
                    max_percentile=kwargs["max_percentile"],
                )
            ]
        )
        return serialize_face_selection_response(self.stub.FilterFacesLoopCountPercentile(request))

    @protect_grpc
    def filter_faces_by_number_curves_percentile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            FilterFacesByCurveTypePercentileRequest,
            FilterFacesByCurveTypePercentileRequestData,
        )

        request = FilterFacesByCurveTypePercentileRequest(
            request_data=[
                FilterFacesByCurveTypePercentileRequestData(
                    face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
                    curve_type=kwargs["curve_type"],
                    min_percentile=kwargs["min_percentile"],
                    max_percentile=kwargs["max_percentile"],
                )
            ]
        )
        return serialize_face_selection_response(
            self.stub.FilterFacesByNumberCurvesPercentile(request)
        )

    # ── Extend ────────────────────────────────────────────────────────────────

    @protect_grpc
    def extend_to_same_area(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.ExtendToSameArea(self._extend_request(kwargs))
        )

    @protect_grpc
    def extend_to_same_number_of_edges(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.ExtendToSameNumberOfEdges(self._extend_request(kwargs))
        )

    @protect_grpc
    def extend_to_same_number_of_loops(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.ExtendToSameNumberOfLoops(self._extend_request(kwargs))
        )

    @protect_grpc
    def extend_to_same_color(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.ExtendToSameColor(self._extend_request(kwargs))
        )

    @protect_grpc
    def extend_to_coincident(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.ExtendToCoincident(self._extend_request(kwargs))
        )

    @protect_grpc
    def extend_to_coaxial_faces(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.ExtendToCoaxialFaces(self._extend_request(kwargs))
        )

    # ── OrderBy ───────────────────────────────────────────────────────────────

    @protect_grpc
    def order_faces_by_area(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.OrderFacesByArea(self._input_request(kwargs))
        )

    @protect_grpc
    def order_faces_by_perimeter(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.OrderFacesByPerimeter(self._input_request(kwargs))
        )

    @protect_grpc
    def order_faces_by_edge_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.OrderFacesByEdgeCount(self._input_request(kwargs))
        )

    @protect_grpc
    def order_faces_by_loop_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_selection_response(
            self.stub.OrderFacesByLoopCount(self._input_request(kwargs))
        )

    @protect_grpc
    def order_faces_by_number_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.faceselection_pb2 import (
            OrderFacesByCurveTypeRequest,
            OrderFacesByCurveTypeRequestData,
        )

        request = OrderFacesByCurveTypeRequest(
            request_data=[
                OrderFacesByCurveTypeRequestData(
                    face_ids=[build_grpc_id(fid) for fid in kwargs["face_ids"]],
                    curve_type=kwargs["curve_type"],
                )
            ]
        )
        return serialize_face_selection_response(self.stub.OrderFacesByNumberCurves(request))

    # ── GroupBy ───────────────────────────────────────────────────────────────

    @protect_grpc
    def group_faces_by_area(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_group_response(
            self.stub.GroupFacesByArea(self._input_request(kwargs))
        )

    @protect_grpc
    def group_faces_by_perimeter(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_group_response(
            self.stub.GroupFacesByPerimeter(self._input_request(kwargs))
        )

    @protect_grpc
    def group_faces_by_body(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_group_response(
            self.stub.GroupFacesByBody(self._input_request(kwargs))
        )

    @protect_grpc
    def group_faces_by_edge_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_group_response(
            self.stub.GroupFacesByEdgeCount(self._input_request(kwargs))
        )

    @protect_grpc
    def group_faces_by_loop_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_group_response(
            self.stub.GroupFacesByLoopCount(self._input_request(kwargs))
        )

    @protect_grpc
    def group_faces_by_color(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_group_response(
            self.stub.GroupFacesByColor(self._input_request(kwargs))
        )

    @protect_grpc
    def group_faces_by_coincident(self, **kwargs) -> dict:  # noqa: D102
        return serialize_face_group_response(
            self.stub.GroupFacesByCoincident(self._input_request(kwargs))
        )
