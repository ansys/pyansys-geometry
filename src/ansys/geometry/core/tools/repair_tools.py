from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from ansys.api.geometry.v0.repairtools_pb2 import FindSplitEdgeProblemAreasRequest
from ansys.api.geometry.v0.repairtools_pb2 import FindExtraEdgesRequest
from ansys.api.geometry.v0.repairtools_pb2 import FindShortEdgesRequest
from ansys.api.geometry.v0.repairtools_pb2 import FindInexactEdgesRequest


from google.protobuf.wrappers_pb2 import DoubleValue
from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.tools.split_edge_problem_areas import SplitEdgeProblemAreas
from ansys.geometry.core.tools.extra_edge_problem_areas import ExtraEdgeProblemAreas
from ansys.geometry.core.tools.extra_edge_problem_areas import InexactEdgeProblemAreas
from ansys.geometry.core.tools.extra_edge_problem_areas import ShortEdgeProblemAreas


from ansys.geometry.core.designer.edge import Edge

class RepairTools:
     """
     Repair tools for the pygeometry.
     """
     def __init__(self):
          """Initialize ``Edge`` class."""
              
    
     def FindSplitEdgeProblemAreas(self, monikers, angle, length):
          """
          This method find the split edge problem areas and returns a list of split edge problem areas objects.

          Parameters
          ----------
          id : monikers
          angle : str
          length : str
          """
          angle_value = DoubleValue(value=float(angle))
          length_value = DoubleValue(value=float(length))
          client = GrpcClient()
          problemAreas = RepairToolsStub(client.channel).FindSplitEdgeProblemAreas(FindSplitEdgeProblemAreasRequest(bodies_or_faces = monikers ,angle = angle_value, distance = length_value))
        
          ans=[]
          for res in problemAreas.result:
               connectedEdges=[]
               for e in res.edge_monikers:
                    connectedEdges.append(res.id)   
               problemA=SplitEdgeProblemAreas(res.id, connectedEdges)
               ans.append(problemA)

          return ans
     
     def FindExtraEdges(self, monikers):
          """
          This method find the extra edge problem areas and returns a list of extra edge problem areas objects.

          Parameters
          ----------
          id : monikers
          Server-defined ID for the edges.
          """
          client = GrpcClient()
          problemAreas = RepairToolsStub(client.channel).FindExtraEdges(FindExtraEdgesRequest(selection = monikers))
          ans = []
          for res in problemAreas.result:
               connectedEdges = []
               for e in res.edge_monikers:
                    connectedEdges.append(res.id) 
               problemArea = ExtraEdgeProblemAreas(res.id, connectedEdges)
               ans.append(problemArea)

          return ans


     def FindInexactEdges(self, monikers):
          """
          This method find the inexact edge problem areas and returns a list of inexact edge problem areas objects.

          Parameters
          ----------
          id : monikers
          Server-defined ID for the edges.
          """
          client = GrpcClient()
          problemAreas = RepairToolsStub(client.channel).FindInexactEdges(FindInexactEdgesRequest(selection = monikers))
          ans = []
          for res in problemAreas.result:
                    connectedEdges = []
                    for e in res.edge_monikers:
                         connectedEdges.append(res.id) 
                    problemArea = InexactEdgeProblemAreas(res.id, connectedEdges)
                    ans.append(problemArea)

          return ans

     def FindShortEdges(self, monikers):
          """
          This method find the short edge problem areas and returns a list of short edge problem areas objects.

          Parameters
          ----------
          id : monikers
          Server-defined ID for the edges.
          """
          client = GrpcClient()
          problemAreas = RepairToolsStub(client.channel).FindShortEdges(FindShortEdgesRequest(selection = monikers))
          ans = []
          for res in problemAreas.result:
                    connectedEdges = []
                    for e in res.edge_monikers:
                         connectedEdges.append(res.id) 
                    problemArea = ShortEdgeProblemAreas(res.id, connectedEdges)
                    ans.append(problemArea)

          return  ans