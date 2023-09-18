"""Provides tools for repairing bodies."""

from ansys.api.geometry.v0.repairtools_pb2 import (
    FindDuplicateFacesRequest,
    FindExtraEdgesRequest,
    FindInexactEdgesRequest,
    FindMissingFacesRequest,
    FindShortEdgesRequest,
    FindSmallFacesRequest,
    FindSplitEdgesRequest,
    FindStitchFacesRequest,
)
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from google.protobuf.wrappers_pb2 import DoubleValue

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.tools.duplicate_face_problem_areas import DuplicateFaceProblemAreas
from ansys.geometry.core.tools.extra_edge_problem_areas import ExtraEdgeProblemAreas
from ansys.geometry.core.tools.inexact_edge_problem_areas import InexactEdgeProblemAreas
from ansys.geometry.core.tools.missing_face_problem_areas import MissingFaceProblemAreas
from ansys.geometry.core.tools.short_edge_problem_areas import ShortEdgeProblemAreas
from ansys.geometry.core.tools.small_face_problem_areas import SmallFaceProblemAreas
from ansys.geometry.core.tools.split_edge_problem_areas import SplitEdgeProblemAreas
from ansys.geometry.core.tools.stitch_face_problem_areas import StitchFaceProblemAreas


class RepairTools:
    """Repair tools for the pygeometry."""

    def __init__(self):
        """Initialize Repair Tools class."""

    def FindSplitEdges(
        self, ids: list[str], angle: float = 0.0, length: float = 0.0
    ) -> list[SplitEdgeProblemAreas]:
        """
        Find split edges in the given list of bodies.

        This method finds the split edge problem areas and returns a list of split edge
        problem areas objects.

        Parameters
        ----------
        ids : list[str]
            Server-defined ID for the edges.
        angle : float
            The maximum angle between edges.
        length : float
            The maximum length of the edges.

        Returns
        ----------
        list[SplitEdgeProblemAreas]
            List of objects representing split edge problem areas.
        """
        angle_value = DoubleValue(value=float(angle))
        length_value = DoubleValue(value=float(length))
        client = GrpcClient()
        problemAreasResponse = RepairToolsStub(client.channel).FindSplitEdges(
            FindSplitEdgesRequest(bodies_or_faces=ids, angle=angle_value, distance=length_value)
        )

        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for edge_moniker in res.edge_monikers:
                connectedEdges.append(edge_moniker)
            problemArea = SplitEdgeProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemArea)

        return problemAreas

    def FindExtraEdges(self, ids: list[str]) -> list[ExtraEdgeProblemAreas]:
        """
        Find the extra edges in the given list of bodies.

        This method find the extra edge problem areas and returns a list of extra edge
        problem areas objects.

        Parameters
        ----------
        ids : list[str]
            Server-defined ID for the edges.

        Returns
        ----------
        list[ExtraEdgeProblemArea]
            List of objects representing extra edge problem areas.
        """
        client = GrpcClient()
        problemAreasResponse = RepairToolsStub(client.channel).FindExtraEdges(
            FindExtraEdgesRequest(selection=ids)
        )
        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for edge_moniker in res.edge_monikers:
                connectedEdges.append(edge_moniker)
            problemArea = ExtraEdgeProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemArea)

        return problemAreas

    def FindInexactEdges(self, ids) -> list[InexactEdgeProblemAreas]:
        """
        Find inexact edges in the given list of bodies.

        This method find the inexact edge problem areas and returns a list of inexact
        edge problem areas objects.

        Parameters
        ----------
        ids : ids
        Server-defined ID for the edges.

        Returns
        ----------
        list[InExactEdgeProblemArea]
            List of objects representing inexact edge problem areas.
        """
        client = GrpcClient()
        problemAreasResponse = RepairToolsStub(client.channel).FindInexactEdges(
            FindInexactEdgesRequest(selection=ids)
        )
        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for edge_moniker in res.edge_monikers:
                connectedEdges.append(edge_moniker)
            problemArea = InexactEdgeProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemArea)

        return problemAreas

    def FindShortEdges(self, ids) -> list[ShortEdgeProblemAreas]:
        """
        Find the short edge problem areas.

        This method finds the short edge problem areas and returns a list of problem areas ids.

        Parameters
        ----------
        ids : string
        Server-defined ID for the edges.

        Returns
        ----------
        list[ShortEdgeProblemArea]
            List of objects representing short edge problem areas.
        """
        client = GrpcClient()
        problemAreasResponse = RepairToolsStub(client.channel).FindShortEdges(
            FindShortEdgesRequest(selection=ids)
        )
        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for edge_moniker in res.edge_monikers:
                connectedEdges.append(edge_moniker)
            problemAreas = ShortEdgeProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemAreas)

        return problemAreas

    def FindDuplicateFaces(self, ids) -> list[DuplicateFaceProblemAreas]:
        """
        Find the duplicate face problem areas.

        This method finds the duplicate face problem areas and returns a list of
        duplicate face problem areas objects.

        Parameters
        ----------
        ids (list): a list of face ids.
        Server-defined ID for the edges.

        Returns
        ----------
        list[DuplicateFaceProblemAreas]
            List of objects representing duplicate face problem areas.
        """
        client = GrpcClient()
        problemAreasResponse = RepairToolsStub(client.channel).FindDuplicateFaces(
            FindDuplicateFacesRequest(faces=ids)
        )
        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for face_moniker in res.face_monikers:
                connectedEdges.append(face_moniker)
            problemArea = DuplicateFaceProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemArea)

        return problemAreas

    def FindMissingFaces(self, ids) -> list[MissingFaceProblemAreas]:
        """
        Find the missing faces.

        This method find the missing face problem areas and returns a list of missing
        face problem areas objects.

        Parameters
        ----------
        ids : string
        Server-defined ID for the edges.

        Returns
        ----------
        list[MissingFaceProblemAreas]
            List of objects representing missing face problem areas.
        """
        client = GrpcClient()
        problemAreasResponse = RepairToolsStub(client.channel).FindMissingFaces(
            FindMissingFacesRequest(faces=ids)
        )
        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for edge_moniker in res.edge_monikers:
                connectedEdges.append(edge_moniker)
            problemArea = MissingFaceProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemArea)

        return problemAreas

    def FindSmallFaces(self, ids) -> list[SmallFaceProblemAreas]:
        """
        Find the small face problem areas.

        This method finds and returns a list of ids of small face problem areas
        objects.

        Parameters
        ----------
        ids : string
        Server-defined ID for the edges.

        Returns
        ----------
        list[SmallFaceProblemAreas]
            List of objects representing small face problem areas.
        """
        client = GrpcClient()
        problemAreasResponse = RepairToolsStub(client.channel).FindSmallFaces(
            FindSmallFacesRequest(selection=ids)
        )
        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for face_moniker in res.face_monikers:
                connectedEdges.append(face_moniker)
            problemArea = SmallFaceProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemArea)

        return problemAreas

    def FindStitchFaces(self, ids) -> list[StitchFaceProblemAreas]:
        """
        Return the list of stitch face problem areas.

        This method find the stitch face problem areas and returns a list of ids of stitch face
        problem areas objects.

        Parameters
        ----------
        ids : string
        Server-defined ID for the edges.

        Returns
        ----------
        list[StitchFaceProblemAreas]
            List of objects representing stitch face problem areas.
        """
        client = GrpcClient()
        problemAreasResponse = RepairToolsStub(client.channel).FindStitchFaces(
            FindStitchFacesRequest(faces=ids)
        )
        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for face_moniker in res.body_monikers:
                connectedEdges.append(face_moniker)
            problemArea = StitchFaceProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemArea)

        return problemAreas
