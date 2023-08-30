from ansys.api.geometry.v0.repairtools_pb2 import (
    FindExtraEdgesRequest,
    FindInexactEdgesRequest,
    FindShortEdgesRequest,
    FindSplitEdgesRequest,
    FindDuplicateFacesRequest,
    FindSmallFacesRequest,
    FindMissingFacesRequest
)
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from google.protobuf.wrappers_pb2 import DoubleValue

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.tools.extra_edge_problem_areas import ExtraEdgeProblemAreas
from ansys.geometry.core.tools.inexact_edge_problem_areas import InexactEdgeProblemAreas
from ansys.geometry.core.tools.short_edge_problem_areas import ShortEdgeProblemAreas
from ansys.geometry.core.tools.split_edge_problem_areas import SplitEdgeProblemAreas
from ansys.geometry.core.tools.duplicate_face_problem_areas import DuplicateFaceProblemAreas
from ansys.geometry.core.tools.small_face_problem_areas import SmallFaceProblemAreas
from ansys.geometry.core.tools.missing_face_problem_areas import MissingFaceProblemAreas




class RepairTools:
    """Repair tools for the pygeometry."""

    def __init__(self):
        """Initialize Repair Tools class."""

    def FindSplitEdges(self, ids : list[str], angle: float = 0.0, length: float = 0.0) -> list[SplitEdgeProblemAreas]:
        """
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

        
        """

        angle_value = DoubleValue(value=float(angle))
        length_value = DoubleValue(value=float(length))
        client = GrpcClient()
        problemAreasResponse = RepairToolsStub(client.channel).FindSplitEdges(
            FindSplitEdgesRequest(
                bodies_or_faces=ids, angle=angle_value, distance=length_value
            )
        )

        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for edge_moniker in res.edge_monikers:
                connectedEdges.append(edge_moniker)
            problemArea = SplitEdgeProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemArea)

        return problemAreas

    def FindExtraEdges(self, ids: list[str])-> list[ExtraEdgeProblemAreas]:
        """
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
            FindExtraEdgesRequest(selection= ids)
        )
        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for edge_moniker in res.edge_monikers:
                connectedEdges.append(edge_moniker)
            problemArea = ExtraEdgeProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemArea)

        return problemAreas

    def FindInexactEdges(self, ids):
        """
        This method find the inexact edge problem areas and returns a list of inexact
        edge problem areas objects.

        Parameters
        ----------
        ids : ids
        Server-defined ID for the edges.

        Returns
        ----------
        list[InExactEdgeProblemArea]
            List of objects representing extra edge problem areas.
        """
        client = GrpcClient()
        problemAreasResponse = RepairToolsStub(client.channel).FindInexactEdges(
            FindInexactEdgesRequest(selection = ids)
        )
        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for edge_moniker in res.edge_monikers:
                connectedEdges.append(edge_moniker)
            problemArea = InexactEdgeProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemArea)

        return problemAreas

    def FindShortEdges(self, ids):
        """
        This method find the short edge problem areas and returns a list of short edge
        problem areas objects.

        Parameters
        ----------
        ids : string
        Server-defined ID for the edges.

        Returns
        ----------
        list[ShortEdgeProblemArea]
            List of objects representing extra edge problem areas.
        """
        client = GrpcClient()
        problemAreasResponse = RepairToolsStub(client.channel).FindShortEdges(
            FindShortEdgesRequest(selection = ids)
        )
        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for edge_moniker in res.edge_monikers:
                connectedEdges.append(edge_moniker)
            problemAreas = ShortEdgeProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemAreas)

        return problemAreas
    
    def FindDuplicateFaces(self, ids):
        """
        This method find the short edge problem areas and returns a list of short edge
        problem areas objects.

        Parameters
        ----------
        ids (list): a list of face ids.
        Server-defined ID for the edges.

        Returns
        ----------
        list[ShortEdgeProblemArea]
            List of objects representing extra edge problem areas.
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

    def FindMissingFaces(self, ids):
        """
        This method find the missing face problem areas and returns a list of missing face
        problem areas objects.

        Parameters
        ----------
        ids : string
        Server-defined ID for the edges.

        Returns
        ----------
        list[ShortEdgeProblemArea]
            List of objects representing extra edge problem areas.
        """
        client = GrpcClient()
        problemAreasResponse = RepairToolsStub(client.channel).FindMissingFaces(
            FindMissingFacesRequest(faces=monikers)
        )
        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for edge_moniker in res.edge_monikers:
                connectedEdges.append(edge_moniker)
            problemArea = MissingFaceProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemArea)

        return problemAreas
    
    def FindSmallFaces(self, ids):
        """
        This method find the missing face problem areas and returns a list of missing face
        problem areas objects.

        Parameters
        ----------
        ids : string
        Server-defined ID for the edges.

        Returns
        ----------
        list[ShortEdgeProblemArea]
            List of objects representing extra edge problem areas.
        """
        client = GrpcClient()
        problemAreasResponse = RepairToolsStub(client.channel).FindSmallFaces(
            FindSmallFacesRequest(faces=monikers)
        )
        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for face_moniker in res.face_monikers:
                connectedEdges.append(face_moniker)
            problemArea = DuplicateFaceProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemArea)

        return problemAreas
    
    def FindStitchFaces(self, ids):
        """
        This method find the missing face problem areas and returns a list of missing face
        problem areas objects.

        Parameters
        ----------
        ids : string
        Server-defined ID for the edges.

        Returns
        ----------
        list[ShortEdgeProblemArea]
            List of objects representing extra edge problem areas.
        """
        client = GrpcClient()
        problemAreasResponse = RepairToolsStub(client.channel).FindSmallFaces(
            FindSmallFacesRequest(faces=monikers)
        )
        problemAreas = []
        for res in problemAreasResponse.result:
            connectedEdges = []
            for face_moniker in res.face_monikers:
                connectedEdges.append(face_moniker)
            problemArea = DuplicateFaceProblemAreas(res.id, connectedEdges)
            problemAreas.append(problemArea)

        return problemAreas
    
