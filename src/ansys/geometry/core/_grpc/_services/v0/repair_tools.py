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
"""Module containing the repair tools service implementation (abstraction layer).

This module defines an abstract base class for a gRPC-based repair tools service.
The class provides a set of abstract methods for identifying and repairing various
geometry issues, such as split edges, extra edges, duplicate faces, and more.
"""

from abc import ABC, abstractmethod
import grpc
from ..base.repair_tools import GRPCRepairToolsService
from ansys.geometry.core.errors import protect_grpc
from google.protobuf.wrappers_pb2 import BoolValue, DoubleValue



class GRPCRepairToolsServiceV0(GRPCRepairToolsService):

    @protect_grpc
    def __init__(self, channel: grpc.Channel):
        from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub

        self.stub = RepairToolsStub(channel)

    @protect_grpc
    def find_split_edges(self, **kwargs):

        from ansys.api.geometry.v0.repairtools_pb2 import FindSplitEdgesRequest
        
        request = FindSplitEdgesRequest(
            bodies_or_faces=kwargs["bodies_or_faces"],
            angle=kwargs["angle"],
            distance=kwargs["distance"],
        )
        return self.stub.FindSplitEdges(request)

    @protect_grpc
    def find_extra_edges(self, **kwargs):
        from ansys.api.geometry.v0.repairtools_pb2 import FindExtraEdgesRequest
        request = FindExtraEdgesRequest(selection=kwargs["selection"])
        return self.stub.FindExtraEdges(request)

    @protect_grpc
    def find_inexact_edges(self, **kwargs):
        from ansys.api.geometry.v0.repairtools_pb2 import FindInexactEdgesRequest
        request = FindInexactEdgesRequest(selection=kwargs["selection"])
        return self.stub.FindInexactEdges(request)    
    
    
    @protect_grpc
    def find_short_edges(self, **kwargs):
        from ansys.api.geometry.v0.repairtools_pb2 import FindShortEdgesRequest
        request = FindShortEdgesRequest(
            selection=kwargs["selection"],
            max_edge_length=DoubleValue(value=kwargs["length"]),
        )
        return self.stub.FindShortEdges(request)
    
    @protect_grpc
    def find_duplicate_faces(self, **kwargs):
        from ansys.api.geometry.v0.repairtools_pb2 import FindDuplicateFacesRequest
        request = FindDuplicateFacesRequest(faces=kwargs["faces"])
        return self.stub.FindDuplicateFaces(request)


    @protect_grpc
    def find_missing_faces(self, **kwargs):
        from ansys.api.geometry.v0.repairtools_pb2 import FindMissingFacesRequest
        request = FindMissingFacesRequest(faces=kwargs["faces"])
        return self.stub.FindMissingFaces(request)    

    @protect_grpc
    def find_small_faces(self, **kwargs):
        from ansys.api.geometry.v0.repairtools_pb2 import FindSmallFacesRequest
        request = FindSmallFacesRequest(selection=kwargs["selection"])
        return self.stub.FindSmallFaces(request)
    
    @protect_grpc
    def find_stitch_faces(self, **kwargs):
        from ansys.api.geometry.v0.repairtools_pb2 import FindStitchFacesRequest
        request = FindStitchFacesRequest(faces=kwargs["faces"])
        return self.stub.FindStitchFaces(request)
    
    @protect_grpc
    def find_simplify(self, **kwargs):
        from ansys.api.geometry.v0.repairtools_pb2 import FindAdjustSimplifyRequest
        request = FindAdjustSimplifyRequest(selection=kwargs["selection"])
        return self.stub.FindAdjustSimplify(request)
    
    @protect_grpc
    def find_and_fix_simplify(self, **kwargs):
        from ansys.api.geometry.v0.repairtools_pb2 import FindAdjustSimplifyRequest
        request = FindAdjustSimplifyRequest(
            selection=kwargs["selection"],
            comprehensive=kwargs["comprehensive_result"],
        )
        return self.stub.FindAndSimplify(request) 
    
    @protect_grpc
    def inspect_geometry(self, **kwargs):
        from ansys.api.geometry.v0.repairtools_pb2 import InspectGeometryRequest
        request = InspectGeometryRequest(bodies=kwargs.get("bodies", []))
        return self.stub.InspectGeometry(request)
    
    @protect_grpc
    def repair_geometry(self, **kwargs):
        from ansys.api.geometry.v0.repairtools_pb2 import RepairGeometryRequest
        request = RepairGeometryRequest(bodies=kwargs.get("bodies", []))
        return self.stub.RepairGeometry(request)
    
    @protect_grpc
    def find_interferences(self, **kwargs):
        from ansys.api.geometry.v0.repairtools_pb2 import FindInterferenceRequest
        request = FindInterferenceRequest(
            bodies=kwargs["bodies"],
            cut_smaller_body=BoolValue(value=kwargs["cut_smaller_body"]),
        )
        return self.stub.FindInterference(request)    

    def find_and_fix_short_edges(self, **kwargs): raise NotImplementedError
    def find_and_fix_extra_edges(self, **kwargs): raise NotImplementedError
    def find_and_fix_split_edges(self, **kwargs): raise NotImplementedError