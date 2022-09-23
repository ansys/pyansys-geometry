"""``Body`` class module."""

from typing import TYPE_CHECKING, List

from ansys.api.geometry.v0.bodies_pb2 import BodyIdentifier, SetAssignedMaterialRequest
from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub
from ansys.api.geometry.v0.commands_pb2 import ImprintCurvesRequest, ProjectCurvesRequest
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from pint import Quantity

from ansys.geometry.core.connection import (
    GrpcClient,
    sketch_shapes_to_grpc_geometries,
    unit_vector_to_grpc_direction,
)
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.designer.face import Face, SurfaceType
from ansys.geometry.core.materials import Material
from ansys.geometry.core.math import UnitVector
from ansys.geometry.core.misc import SERVER_UNIT_VOLUME, check_type
from ansys.geometry.core.sketch import Sketch

if TYPE_CHECKING:
    from ansys.geometry.core.designer.component import Component  # pragma: no cover


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
    is_surface : bool, optional
        Boolean indicating whether the ``Body`` is in fact a surface or an actual
        3D object (with volume). By default, ``False``.
    """

    def __init__(
        self,
        id: str,
        name: str,
        parent_component: "Component",
        grpc_client: GrpcClient,
        is_surface: bool = False,
    ):
        """Constructor method for ``Body``."""
        # Sanity checks - cannot check Component due to circular import issues
        check_type(id, str)
        check_type(name, str)
        check_type(grpc_client, GrpcClient)
        check_type(is_surface, bool)

        self._id = id
        self._name = name
        self._parent_component = parent_component
        self._grpc_client = grpc_client
        self._is_surface = is_surface
        self._is_alive = True
        self._bodies_stub = BodiesStub(self._grpc_client.channel)
        self._commands_stub = CommandsStub(self._grpc_client.channel)

    @property
    def id(self) -> str:
        """Id of the ``Body``."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the ``Body``."""
        return self._name

    @property
    def is_surface(self) -> bool:
        """Returns ``True`` if the ``Body`` object is a planar body."""
        return self._is_surface

    @property
    def faces(self) -> List[Face]:
        """Loads all of the faces within the body.

        Returns
        ----------
        List[Face]
        """
        grpc_faces = self._bodies_stub.GetFaces(BodyIdentifier(id=self._id))

        return [
            Face(grpc_face.id, SurfaceType(grpc_face.surface_type), self, self._grpc_client)
            for grpc_face in grpc_faces.faces
        ]

    @property
    def is_alive(self) -> bool:
        """Boolean indicating whether the body is still alive on the server side."""
        return self._is_alive

    @property
    def volume(self) -> Quantity:
        """Calculated volume of the body.

        Notes
        -----
        When dealing with a planar surface, a value of 0 is returned as a volume.
        """
        if self.is_surface:
            # TODO : maybe raise an error?
            return Quantity(0, SERVER_UNIT_VOLUME)
        else:
            volume_response = self._bodies_stub.GetVolume(BodyIdentifier(id=self._id))
            return Quantity(volume_response.volume, SERVER_UNIT_VOLUME)

    def assign_material(self, material: Material) -> None:
        """Sets the provided material against the design in the active geometry
        service instance.

        Parameters
        ----------
        material : Material
            Source material data.
        """
        check_type(material, Material)
        self._bodies_stub.SetAssignedMaterial(
            SetAssignedMaterialRequest(id=self._id, material=material.name)
        )

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
        # Sanity checks
        check_type(faces, (list, tuple))
        for face in faces:
            check_type(face, Face)
        check_type(sketch, Sketch)

        # Verify that each of the faces provided are part of this body
        body_faces = self.faces
        for provided_face in faces:
            is_found = False
            for body_face in body_faces:
                if provided_face.id == body_face.id:
                    is_found = True
                    break
            if not is_found:
                raise ValueError(f"Face with id {provided_face.id} is not part of this body.")

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

        # TODO: Critical to get back faces and edges from server to synchronize body
        # TODO: Request gRPC signature update to return faces and edges impacted
        return new_edges

    def project_curves(
        self, direction: UnitVector, sketch: Sketch, closest_face: bool
    ) -> List[Face]:
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
        # Sanity checks
        check_type(direction, UnitVector)
        check_type(sketch, Sketch)
        check_type(closest_face, bool)

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
