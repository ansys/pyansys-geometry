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

"""Module containing the Body Selection service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.body_selection import GRPCBodySelectionService
from .conversions import (
    build_grpc_id,
    from_area_to_grpc_quantity,
    from_length_to_grpc_quantity,
    from_volume_to_grpc_quantity,
    serialize_body_group_response,
    serialize_body_selection_response,
)


class GRPCBodySelectionServiceV1(GRPCBodySelectionService):
    """Body Selection service for gRPC communication with the Geometry server (v1).

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2_grpc import (
            BodySelectionStub,
        )

        self.stub = BodySelectionStub(channel)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _input_request(self, kwargs):
        """Build a ``BodySelectionInputRequest`` from ``body_ids``."""
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            BodySelectionInputRequest,
            BodySelectionInputRequestData,
        )

        return BodySelectionInputRequest(
            request_data=[
                BodySelectionInputRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]]
                )
            ]
        )

    def _extend_request(self, kwargs):
        """Build a ``BodySelectionExtendRequest``."""
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            BodySelectionExtendRequest,
            BodySelectionExtendRequestData,
        )

        return BodySelectionExtendRequest(
            request_data=[
                BodySelectionExtendRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    scope=kwargs["scope"],
                )
            ]
        )

    # ── Static factory ────────────────────────────────────────────────────────

    @protect_grpc
    def get_all_visible_bodies(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            GetAllVisibleBodiesRequest,
        )

        return serialize_body_selection_response(
            self.stub.GetAllVisibleBodies(GetAllVisibleBodiesRequest())
        )

    @protect_grpc
    def get_all_bodies(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            GetAllBodiesRequest,
        )

        return serialize_body_selection_response(self.stub.GetAllBodies(GetAllBodiesRequest()))

    @protect_grpc
    def get_all_surface_bodies(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            GetAllSurfaceBodiesRequest,
        )

        return serialize_body_selection_response(
            self.stub.GetAllSurfaceBodies(GetAllSurfaceBodiesRequest())
        )

    @protect_grpc
    def get_all_solid_bodies(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            GetAllSolidBodiesRequest,
        )

        return serialize_body_selection_response(
            self.stub.GetAllSolidBodies(GetAllSolidBodiesRequest())
        )

    @protect_grpc
    def get_bodies_from_named_selection(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            GetBodiesFromNamedSelectionRequest,
            GetBodiesFromNamedSelectionRequestData,
        )

        # kwargs: name, filter_type, ignore_case  (may be lists for batch)
        request = GetBodiesFromNamedSelectionRequest(
            request_data=[
                GetBodiesFromNamedSelectionRequestData(
                    name=kwargs["name"],
                    filter_type=kwargs["filter_type"].value,
                    ignore_case=kwargs["ignore_case"],
                )
            ]
        )
        return serialize_body_selection_response(self.stub.GetBodiesFromNamedSelection(request))

    @protect_grpc
    def get_bodies_with_name(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            GetBodiesWithNameRequest,
            GetBodiesWithNameRequestData,
        )

        request = GetBodiesWithNameRequest(
            request_data=[
                GetBodiesWithNameRequestData(
                    name=kwargs["name"],
                    filter_type=kwargs["filter_type"].value,
                    ignore_case=kwargs["ignore_case"],
                )
            ]
        )
        return serialize_body_selection_response(self.stub.GetBodiesWithName(request))

    @protect_grpc
    def get_bodies_with_volume(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            GetBodiesWithVolumeRequest,
            GetBodiesWithVolumeRequestData,
        )

        data = GetBodiesWithVolumeRequestData(
            min=from_volume_to_grpc_quantity(kwargs["min"]),
            max=from_volume_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
        )

        return serialize_body_selection_response(
            self.stub.GetBodiesWithVolume(GetBodiesWithVolumeRequest(request_data=[data]))
        )

    @protect_grpc
    def get_bodies_with_surface_area(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            GetBodiesWithSurfaceAreaRequest,
            GetBodiesWithSurfaceAreaRequestData,
        )

        data = GetBodiesWithSurfaceAreaRequestData(
            min=from_area_to_grpc_quantity(kwargs["min"]),
            max=from_area_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
        )

        return serialize_body_selection_response(
            self.stub.GetBodiesWithSurfaceArea(GetBodiesWithSurfaceAreaRequest(request_data=[data]))
        )

    @protect_grpc
    def get_bodies_with_x_location(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            GetBodiesWithLocationRequest,
            GetBodiesWithLocationRequestData,
        )

        data = GetBodiesWithLocationRequestData(
            min=from_length_to_grpc_quantity(kwargs["min"]) if kwargs["min"] is not None else None,
            max=from_length_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
            range_type=kwargs["range_type"].value,
        )

        return serialize_body_selection_response(
            self.stub.GetBodiesWithXLocation(GetBodiesWithLocationRequest(request_data=[data]))
        )

    @protect_grpc
    def get_bodies_with_y_location(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            GetBodiesWithLocationRequest,
            GetBodiesWithLocationRequestData,
        )

        data = GetBodiesWithLocationRequestData(
            min=from_length_to_grpc_quantity(kwargs["min"]) if kwargs["min"] is not None else None,
            max=from_length_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
            range_type=kwargs["range_type"].value,
        )

        return serialize_body_selection_response(
            self.stub.GetBodiesWithYLocation(GetBodiesWithLocationRequest(request_data=[data]))
        )

    @protect_grpc
    def get_bodies_with_z_location(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            GetBodiesWithLocationRequest,
            GetBodiesWithLocationRequestData,
        )

        data = GetBodiesWithLocationRequestData(
            min=from_length_to_grpc_quantity(kwargs["min"]) if kwargs["min"] is not None else None,
            max=from_length_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
            range_type=kwargs["range_type"].value,
        )

        return serialize_body_selection_response(
            self.stub.GetBodiesWithZLocation(GetBodiesWithLocationRequest(request_data=[data]))
        )

    @protect_grpc
    def get_bodies_with_color(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            GetBodiesWithColorRequest,
            GetBodiesWithColorRequestData,
        )

        request = GetBodiesWithColorRequest(
            request_data=[GetBodiesWithColorRequestData(color=kwargs["color"])]
        )
        return serialize_body_selection_response(self.stub.GetBodiesWithColor(request))

    # ── Instance operations ───────────────────────────────────────────────────

    @protect_grpc
    def invert_body_selection(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            InvertBodySelectionRequest,
            InvertBodySelectionRequestData,
        )

        request = InvertBodySelectionRequest(
            request_data=[
                InvertBodySelectionRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    scope=kwargs["scope"].value,
                )
            ]
        )
        return serialize_body_selection_response(self.stub.InvertBodySelection(request))

    # ── Filter ────────────────────────────────────────────────────────────────

    @protect_grpc
    def filter_bodies_by_volume(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesByVolumeRequest,
            FilterBodiesByVolumeRequestData,
        )

        data = FilterBodiesByVolumeRequestData(
            body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
            min=from_volume_to_grpc_quantity(kwargs["min"]),
            max=(
                from_volume_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None
            ),
        )

        return serialize_body_selection_response(
            self.stub.FilterBodiesByVolume(FilterBodiesByVolumeRequest(request_data=[data]))
        )

    @protect_grpc
    def filter_bodies_max_volume(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.FilterBodiesMaxVolume(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_bodies_min_volume(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.FilterBodiesMinVolume(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_bodies_by_surface_area(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesBySurfaceAreaRequest,
            FilterBodiesBySurfaceAreaRequestData,
        )

        data = FilterBodiesBySurfaceAreaRequestData(
            body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
            min=from_area_to_grpc_quantity(kwargs["min"]),
            max=(from_area_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None),
        )

        return serialize_body_selection_response(
            self.stub.FilterBodiesBySurfaceArea(
                FilterBodiesBySurfaceAreaRequest(request_data=[data])
            )
        )

    @protect_grpc
    def filter_bodies_max_surface_area(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.FilterBodiesMaxSurfaceArea(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_bodies_min_surface_area(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.FilterBodiesMinSurfaceArea(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_bodies_by_face_count(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesByIntRangeRequest,
            FilterBodiesByIntRangeRequestData,
        )

        data = FilterBodiesByIntRangeRequestData(
            body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
            min=kwargs["min"],
            max=kwargs["max"] if kwargs["max"] is not None else None,
        )

        return serialize_body_selection_response(
            self.stub.FilterBodiesByFaceCount(FilterBodiesByIntRangeRequest(request_data=[data]))
        )

    @protect_grpc
    def filter_bodies_max_face_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.FilterBodiesMaxFaceCount(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_bodies_min_face_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.FilterBodiesMinFaceCount(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_bodies_by_edge_count(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesByIntRangeRequest,
            FilterBodiesByIntRangeRequestData,
        )

        data = FilterBodiesByIntRangeRequestData(
            body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
            min=kwargs["min"],
            max=kwargs["max"] if kwargs["max"] is not None else None,
        )

        return serialize_body_selection_response(
            self.stub.FilterBodiesByEdgeCount(FilterBodiesByIntRangeRequest(request_data=[data]))
        )

    @protect_grpc
    def filter_bodies_max_edge_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.FilterBodiesMaxEdgeCount(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_bodies_min_edge_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.FilterBodiesMinEdgeCount(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_bodies_by_loop_count(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesByIntRangeRequest,
            FilterBodiesByIntRangeRequestData,
        )

        data = FilterBodiesByIntRangeRequestData(
            body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
            min=kwargs["min"],
            max=kwargs["max"] if kwargs["max"] is not None else None,
        )

        return serialize_body_selection_response(
            self.stub.FilterBodiesByLoopCount(FilterBodiesByIntRangeRequest(request_data=[data]))
        )

    @protect_grpc
    def filter_bodies_max_loop_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.FilterBodiesMaxLoopCount(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_bodies_min_loop_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.FilterBodiesMinLoopCount(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_bodies_by_number_surfaces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesBySurfaceCountRequest,
            FilterBodiesBySurfaceCountRequestData,
        )

        data = FilterBodiesBySurfaceCountRequestData(
            body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
            surface_type=kwargs["surface_type"],
            min=kwargs["min"],
            max=kwargs["max"] if kwargs["max"] is not None else None,
        )

        return serialize_body_selection_response(
            self.stub.FilterBodiesByNumberSurfaces(
                FilterBodiesBySurfaceCountRequest(request_data=[data])
            )
        )

    @protect_grpc
    def filter_bodies_by_number_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesByCurveCountRequest,
            FilterBodiesByCurveCountRequestData,
        )

        data = FilterBodiesByCurveCountRequestData(
            body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
            curve_type=kwargs["curve_type"],
            min=kwargs["min"],
            max=kwargs["max"] if kwargs["max"] is not None else None,
        )

        return serialize_body_selection_response(
            self.stub.FilterBodiesByNumberCurves(
                FilterBodiesByCurveCountRequest(request_data=[data])
            )
        )

    @protect_grpc
    def filter_bodies_max_number_surfaces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesBySurfaceTypeRequest,
            FilterBodiesBySurfaceTypeRequestData,
        )

        request = FilterBodiesBySurfaceTypeRequest(
            request_data=[
                FilterBodiesBySurfaceTypeRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    surface_type=kwargs["surface_type"],
                )
            ]
        )
        return serialize_body_selection_response(self.stub.FilterBodiesMaxNumberSurfaces(request))

    @protect_grpc
    def filter_bodies_max_number_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesByCurveTypeRequest,
            FilterBodiesByCurveTypeRequestData,
        )

        request = FilterBodiesByCurveTypeRequest(
            request_data=[
                FilterBodiesByCurveTypeRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    curve_type=kwargs["curve_type"],
                )
            ]
        )
        return serialize_body_selection_response(self.stub.FilterBodiesMaxNumberCurves(request))

    @protect_grpc
    def filter_bodies_min_number_surfaces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesBySurfaceTypeRequest,
            FilterBodiesBySurfaceTypeRequestData,
        )

        request = FilterBodiesBySurfaceTypeRequest(
            request_data=[
                FilterBodiesBySurfaceTypeRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    surface_type=kwargs["surface_type"],
                )
            ]
        )
        return serialize_body_selection_response(self.stub.FilterBodiesMinNumberSurfaces(request))

    @protect_grpc
    def filter_bodies_min_number_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesByCurveTypeRequest,
            FilterBodiesByCurveTypeRequestData,
        )

        request = FilterBodiesByCurveTypeRequest(
            request_data=[
                FilterBodiesByCurveTypeRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    curve_type=kwargs["curve_type"],
                )
            ]
        )
        return serialize_body_selection_response(self.stub.FilterBodiesMinNumberCurves(request))

    @protect_grpc
    def filter_bodies_by_number_surfaces_percentile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesBySurfaceTypePercentileRequest,
            FilterBodiesBySurfaceTypePercentileRequestData,
        )

        request = FilterBodiesBySurfaceTypePercentileRequest(
            request_data=[
                FilterBodiesBySurfaceTypePercentileRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    surface_type=kwargs["surface_type"],
                    min_percentile=kwargs["min_percentile"],
                    max_percentile=kwargs["max_percentile"],
                )
            ]
        )
        return serialize_body_selection_response(
            self.stub.FilterBodiesByNumberSurfacesPercentile(request)
        )

    @protect_grpc
    def filter_bodies_by_number_curves_percentile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesByCurveTypePercentileRequest,
            FilterBodiesByCurveTypePercentileRequestData,
        )

        request = FilterBodiesByCurveTypePercentileRequest(
            request_data=[
                FilterBodiesByCurveTypePercentileRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    curve_type=kwargs["curve_type"],
                    min_percentile=kwargs["min_percentile"],
                    max_percentile=kwargs["max_percentile"],
                )
            ]
        )
        return serialize_body_selection_response(
            self.stub.FilterBodiesByNumberCurvesPercentile(request)
        )

    @protect_grpc
    def filter_bodies_by_color(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesByColorRequest,
            FilterBodiesByColorRequestData,
        )

        request = FilterBodiesByColorRequest(
            request_data=[
                FilterBodiesByColorRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    color=kwargs["color"],
                )
            ]
        )
        return serialize_body_selection_response(self.stub.FilterBodiesByColor(request))

    @protect_grpc
    def filter_bodies_by_name(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesByNameRequest,
            FilterBodiesByNameRequestData,
        )

        request = FilterBodiesByNameRequest(
            request_data=[
                FilterBodiesByNameRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    name=kwargs["name"],
                    filter_type=kwargs["filter_type"],
                    ignore_case=kwargs["ignore_case"],
                )
            ]
        )
        return serialize_body_selection_response(self.stub.FilterBodiesByName(request))

    @protect_grpc
    def filter_bodies_containing_surface_types(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesContainingSurfaceTypesRequest,
            FilterBodiesContainingSurfaceTypesRequestData,
        )

        request = FilterBodiesContainingSurfaceTypesRequest(
            request_data=[
                FilterBodiesContainingSurfaceTypesRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    surface_types=kwargs["surface_types"].value,
                    exclusive=kwargs["exclusive"],
                )
            ]
        )
        return serialize_body_selection_response(
            self.stub.FilterBodiesContainingSurfaceTypes(request)
        )

    @protect_grpc
    def filter_bodies_containing_curve_types(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesContainingCurveTypesRequest,
            FilterBodiesContainingCurveTypesRequestData,
        )

        request = FilterBodiesContainingCurveTypesRequest(
            request_data=[
                FilterBodiesContainingCurveTypesRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    curve_types=kwargs["curve_types"].value,
                    exclusive=kwargs["exclusive"],
                )
            ]
        )
        return serialize_body_selection_response(
            self.stub.FilterBodiesContainingCurveTypes(request)
        )

    @protect_grpc
    def filter_bodies_volume_percentile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesPercentileRequest,
            FilterBodiesPercentileRequestData,
        )

        request = FilterBodiesPercentileRequest(
            request_data=[
                FilterBodiesPercentileRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    min_percentile=kwargs["min_percentile"],
                    max_percentile=kwargs["max_percentile"],
                )
            ]
        )
        return serialize_body_selection_response(self.stub.FilterBodiesVolumePercentile(request))

    @protect_grpc
    def filter_bodies_surface_area_percentile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesPercentileRequest,
            FilterBodiesPercentileRequestData,
        )

        request = FilterBodiesPercentileRequest(
            request_data=[
                FilterBodiesPercentileRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    min_percentile=kwargs["min_percentile"],
                    max_percentile=kwargs["max_percentile"],
                )
            ]
        )
        return serialize_body_selection_response(
            self.stub.FilterBodiesSurfaceAreaPercentile(request)
        )

    @protect_grpc
    def filter_bodies_face_count_percentile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesPercentileRequest,
            FilterBodiesPercentileRequestData,
        )

        request = FilterBodiesPercentileRequest(
            request_data=[
                FilterBodiesPercentileRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    min_percentile=kwargs["min_percentile"],
                    max_percentile=kwargs["max_percentile"],
                )
            ]
        )
        return serialize_body_selection_response(self.stub.FilterBodiesFaceCountPercentile(request))

    @protect_grpc
    def filter_bodies_edge_count_percentile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesPercentileRequest,
            FilterBodiesPercentileRequestData,
        )

        request = FilterBodiesPercentileRequest(
            request_data=[
                FilterBodiesPercentileRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    min_percentile=kwargs["min_percentile"],
                    max_percentile=kwargs["max_percentile"],
                )
            ]
        )
        return serialize_body_selection_response(self.stub.FilterBodiesEdgeCountPercentile(request))

    @protect_grpc
    def filter_bodies_loop_count_percentile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            FilterBodiesPercentileRequest,
            FilterBodiesPercentileRequestData,
        )

        request = FilterBodiesPercentileRequest(
            request_data=[
                FilterBodiesPercentileRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    min_percentile=kwargs["min_percentile"],
                    max_percentile=kwargs["max_percentile"],
                )
            ]
        )
        return serialize_body_selection_response(self.stub.FilterBodiesLoopCountPercentile(request))

    @protect_grpc
    def filter_surface_bodies(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.FilterSurfaceBodies(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_solid_bodies(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.FilterSolidBodies(self._input_request(kwargs))
        )

    # ── Extend ────────────────────────────────────────────────────────────────

    @protect_grpc
    def extend_to_same_volume(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.ExtendToSameVolume(self._extend_request(kwargs))
        )

    @protect_grpc
    def extend_to_same_surface_area(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.ExtendToSameSurfaceArea(self._extend_request(kwargs))
        )

    @protect_grpc
    def extend_to_same_number_of_faces(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.ExtendToSameNumberOfFaces(self._extend_request(kwargs))
        )

    @protect_grpc
    def extend_to_same_number_of_edges(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.ExtendToSameNumberOfEdges(self._extend_request(kwargs))
        )

    @protect_grpc
    def extend_to_same_color(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.ExtendToSameColor(self._extend_request(kwargs))
        )

    @protect_grpc
    def extend_to_same_name(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.ExtendToSameName(self._extend_request(kwargs))
        )

    @protect_grpc
    def extend_nearby_bodies(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.bodyselection_pb2 import (
            ExtendNearbyBodiesRequest,
            ExtendNearbyBodiesRequestData,
        )

        request = ExtendNearbyBodiesRequest(
            request_data=[
                ExtendNearbyBodiesRequestData(
                    body_ids=[build_grpc_id(bid) for bid in kwargs["body_ids"]],
                    distance=from_length_to_grpc_quantity(kwargs["distance"]),
                    scope=kwargs["scope"],
                )
            ]
        )
        return serialize_body_selection_response(self.stub.ExtendNearbyBodies(request))

    # ── OrderBy ───────────────────────────────────────────────────────────────

    @protect_grpc
    def order_bodies_by_volume(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.OrderBodiesByVolume(self._input_request(kwargs))
        )

    @protect_grpc
    def order_bodies_by_surface_area(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.OrderBodiesBySurfaceArea(self._input_request(kwargs))
        )

    @protect_grpc
    def order_bodies_by_face_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.OrderBodiesByFaceCount(self._input_request(kwargs))
        )

    @protect_grpc
    def order_bodies_by_edge_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.OrderBodiesByEdgeCount(self._input_request(kwargs))
        )

    @protect_grpc
    def order_bodies_by_loop_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.OrderBodiesByLoopCount(self._input_request(kwargs))
        )

    @protect_grpc
    def order_bodies_by_number_of_surfaces(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.OrderBodiesByNumberOfSurfaces(self._input_request(kwargs))
        )

    @protect_grpc
    def order_bodies_by_number_of_curves(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_selection_response(
            self.stub.OrderBodiesByNumberOfCurves(self._input_request(kwargs))
        )

    # ── GroupBy ───────────────────────────────────────────────────────────────

    @protect_grpc
    def group_bodies_by_volume(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_group_response(
            self.stub.GroupBodiesByVolume(self._input_request(kwargs))
        )

    @protect_grpc
    def group_bodies_by_surface_area(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_group_response(
            self.stub.GroupBodiesBySurfaceArea(self._input_request(kwargs))
        )

    @protect_grpc
    def group_bodies_by_face_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_group_response(
            self.stub.GroupBodiesByFaceCount(self._input_request(kwargs))
        )

    @protect_grpc
    def group_bodies_by_edge_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_group_response(
            self.stub.GroupBodiesByEdgeCount(self._input_request(kwargs))
        )

    @protect_grpc
    def group_bodies_by_loop_count(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_group_response(
            self.stub.GroupBodiesByLoopCount(self._input_request(kwargs))
        )

    @protect_grpc
    def group_bodies_by_color(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_group_response(
            self.stub.GroupBodiesByColor(self._input_request(kwargs))
        )

    @protect_grpc
    def group_bodies_by_name(self, **kwargs) -> dict:  # noqa: D102
        return serialize_body_group_response(
            self.stub.GroupBodiesByName(self._input_request(kwargs))
        )
