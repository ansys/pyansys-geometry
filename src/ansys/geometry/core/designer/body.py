"""``Body`` class module."""

from typing import TYPE_CHECKING, List

from ansys.api.geometry.v0.bodies_pb2 import BodyIdentifier, SetAssignedMaterialRequest
from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub
from ansys.api.geometry.v0.commands_pb2 import ImprintCurvesRequest, ProjectCurvesRequest
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from pint import Quantity

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.connection.conversions import (
    sketch_shapes_to_grpc_geometries,
    unit_vector_to_grpc_direction,
)
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.materials import Material
from ansys.geometry.core.math import Vector
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.sketch import Sketch

if TYPE_CHECKING:
    from ansys.geometry.core.designer.component import Component


class Body:
    """
    Represents solids and surfaces organized within the design assembly.

    Synchronizes to a design within a supporting geometry service instance.

    Parameters
    ----------
    id : str
        A server defined identifier for the body.
    name : str
        A user-defined label for the body.
    parent_component : Component
        The parent component to nest the new component under within the design assembly.
    grpc_client : GrpcClient
        An active supporting geometry service instance for design modeling.
    """

    def __init__(self, id: str, name: str, parent_component: "Component", grpc_client: GrpcClient):
        """Constructor method for ``Body``."""

        self._id = id
        self._name = name
        self._parent_component = parent_component
        self._grpc_client = grpc_client
        self._bodies_stub = BodiesStub(self._grpc_client.channel)
        self._commands_stub = CommandsStub(self._grpc_client.channel)
        self._volume = Quantity(0, None)
        self._faces = []

    @property
    def volume(self) -> Quantity:
        """Calculated volume of the face."""
        if self._volume.m == 0:
            volume_response = self._bodies_stub.GetVolume(BodyIdentifier(id=self._id))
            self._volume = Quantity(volume_response.volume, (UNITS.m * UNITS.m * UNITS.m))
        return self._volume

    def assign_material(self, material: Material) -> None:
        """Sets the provided material against the design in the active geometry service instance.

        Parameters
        ----------
        material : Material
            Source material data.
        """
        self._bodies_stub.SetAssignedMaterial(
            SetAssignedMaterialRequest(id=self._id, material=material._display_name)
        )

    @property
    def faces(self) -> List[Face]:
        """Lazy-loads all of the faces within the body.

        Returns
        ----------
        List[Face]
        """
        if len(self._faces) == 0:
            grpc_faces = self._bodies_stub.GetFaces(BodyIdentifier(id=self._id))

            self._faces = [
                Face(grpc_face.id, grpc_face.surface_type, self, self._grpc_client)
                for grpc_face in grpc_faces.faces
            ]

        return self._faces

    def imprint_curves(self, faces: List[Face], sketch: Sketch) -> List[Edge]:
        """Imprints all of the specified geometries onto the specified faces of the body.

        Parameters
        ----------
        faces: List[Face]
            Specific faces to imprint the curves of the sketch.
        sketch: Sketch
            All of the curves to imprint on the faces.

        Returns
        -------
        List[Edge]
            All of the impacted edges from the imprint operation.
        """
        # TODO: Verify that each of the faces provided are part of this body
        imprint_response = self._commands_stub.ImprintCurves(
            ImprintCurvesRequest(
                body=self._id,
                curves=sketch_shapes_to_grpc_geometries(sketch.shapes_list),
                faces=[face._id for face in faces],
            )
        )

        new_edges = [
            Edge(grpc_edge.id, grpc_edge.curve_type, self, self._grpc_client)
            for grpc_edge in imprint_response.edges
        ]

        return new_edges

    def project_curves(self, direction: Vector, sketch: Sketch, closest_face: bool) -> List[Face]:
        """Projects all of the specified geometries onto the body.

        Parameters
        ----------
        direction: UnitVector
            Establishes the direction of the projection.
        sketch: Sketch
            All of the curves to project on the body.
        closest_face: bool
            Signifies whether to target the closest face with the projection.

        Returns
        -------
        List[Face]
            All of the faces from the project curves operation.
        """
        project_response = self._commands_stub.ProjectCurves(
            ProjectCurvesRequest(
                body=self._id,
                curves=sketch_shapes_to_grpc_geometries(sketch.shapes_list),
                direction=unit_vector_to_grpc_direction(direction),
                closestFace=closest_face,
            )
        )

        projected_faces = [
            Face(grpc_face.id, grpc_face.surface_type, self, self._grpc_client)
            for grpc_face in project_response.faces
        ]

        return projected_faces
