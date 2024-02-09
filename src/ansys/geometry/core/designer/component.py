# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
"""Provides for managing components."""

from enum import Enum, unique
import uuid  # TODO: Is ID even needed? Maybe use from SC?

from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
from ansys.api.geometry.v0.bodies_pb2 import (
    CreateBodyFromFaceRequest,
    CreateExtrudedBodyFromFaceProfileRequest,
    CreateExtrudedBodyRequest,
    CreatePlanarBodyRequest,
    TranslateRequest,
)
from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub
from ansys.api.geometry.v0.commands_pb2 import CreateBeamSegmentsRequest, CreateDesignPointsRequest
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from ansys.api.geometry.v0.components_pb2 import (
    CreateRequest,
    SetPlacementRequest,
    SetSharedTopologyRequest,
)
from ansys.api.geometry.v0.components_pb2_grpc import ComponentsStub
from ansys.api.geometry.v0.models_pb2 import Direction, Line
from beartype import beartype as check_input_types
from beartype.typing import TYPE_CHECKING, List, Optional, Tuple, Union
from pint import Quantity

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.connection.conversions import (
    grpc_matrix_to_matrix,
    plane_to_grpc_plane,
    point3d_to_grpc_point,
    sketch_shapes_to_grpc_geometries,
    unit_vector_to_grpc_direction,
)
from ansys.geometry.core.designer.beam import Beam, BeamProfile
from ansys.geometry.core.designer.body import Body, MasterBody
from ansys.geometry.core.designer.coordinate_system import CoordinateSystem
from ansys.geometry.core.designer.designpoint import DesignPoint
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.designer.part import MasterComponent, Part
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.math.constants import IDENTITY_MATRIX44
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc.checks import check_pint_unit_compatibility, ensure_design_is_active
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Angle, Distance
from ansys.geometry.core.sketch.sketch import Sketch
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from pyvista import MultiBlock, PolyData


@unique
class SharedTopologyType(Enum):
    """Enum for the component shared topologies available in the Geometry service."""

    SHARETYPE_NONE = 0
    SHARETYPE_SHARE = 1
    SHARETYPE_MERGE = 2
    SHARETYPE_GROUPS = 3


class Component:
    """
    Provides for creating and managing a component.

    This class synchronizes to a design within a supporting Geometry service instance.

    Parameters
    ----------
    name : str
        User-defined label for the new component.
    parent_component : Component or None
        Parent component to place the new component under within the design assembly. The
        default is ``None`` only when dealing with a ``Design`` object.
    grpc_client : GrpcClient
        Active supporting Geometry service instance for design modeling.
    template : Component, default: None
        Template to create this component from. This creates an
        instance component that shares a master with the template component.
    preexisting_id : str, default: None
        ID of a component pre-existing on the server side to use to create the component
        on the client-side data model. If an ID is specified, a new component is not
        created on the server.
    master_component : MasterComponent, default: None
        Master component to use to create a nested component instance instead
        of creating a new conponent.
    read_existing_comp : bool, default: False
        Whether an existing component on the service should be read. This
        parameter is only valid when connecting to an existing service session.
        Otherwise, avoid using this optional parameter.
    """

    # Types of the class instance private attributes
    _components: List["Component"]
    _beams: List[Beam]
    _coordinate_systems: List[CoordinateSystem]
    _design_points: List[DesignPoint]

    @protect_grpc
    @check_input_types
    def __init__(
        self,
        name: str,
        parent_component: Union["Component", None],
        grpc_client: GrpcClient,
        template: Optional["Component"] = None,
        preexisting_id: Optional[str] = None,
        master_component: Optional[MasterComponent] = None,
        read_existing_comp: bool = False,
    ):
        """Initialize the ``Component`` class."""
        # Initialize the client and stubs needed
        self._grpc_client = grpc_client
        self._component_stub = ComponentsStub(self._grpc_client.channel)
        self._bodies_stub = BodiesStub(self._grpc_client.channel)
        self._commands_stub = CommandsStub(self._grpc_client.channel)

        if preexisting_id:
            self._name = name
            self._id = preexisting_id
        else:
            if parent_component:
                template_id = template.id if template else ""
                new_component = self._component_stub.Create(
                    CreateRequest(name=name, parent=parent_component.id, template=template_id)
                )
                # Remove this method call once we know Service sends correct ObjectPath id
                self._id = new_component.component.id
                self._name = new_component.component.name
            else:
                self._name = name
                self._id = None

        # Initialize needed instance variables
        self._components = []
        self._beams = []
        self._coordinate_systems = []
        self._design_points = []
        self._parent_component = parent_component
        self._is_alive = True
        self._shared_topology = None
        self._master_component = master_component

        # Populate client data model
        if template:
            # If this is not a nested instance
            if not master_component:
                # Create new MasterComponent, but use template's Part
                master = MasterComponent(
                    uuid.uuid4(),
                    f"master_{name}",
                    template._master_component.part,
                    template._master_component.transform,
                )
                self._master_component = master

            # Recurse - Create more children components from template's remaining children
            self.__create_children(template)

        elif not read_existing_comp:
            # This is an independent Component - Create new Part and MasterComponent
            p = Part(uuid.uuid4(), f"p_{name}", [], [])
            master = MasterComponent(uuid.uuid4(), f"master_{name}", p)
            self._master_component = master

        self._master_component.occurrences.append(self)

    @property
    def id(self) -> str:
        """ID of the component."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the component."""
        return self._name

    @property
    def components(self) -> List["Component"]:
        """List of ``Component`` objects inside of the component."""
        return self._components

    @property
    def bodies(self) -> List[Body]:
        """List of ``Body`` objects inside of the component."""
        bodies = []
        for body in self._master_component.part.bodies:
            id = f"{self.id}/{body.id}" if self.parent_component else body.id
            if body.is_alive:
                bodies.append(Body(id, body.name, self, body))
        return bodies

    @property
    def beams(self) -> List[Beam]:
        """List of ``Beam`` objects inside of the component."""
        return self._beams

    @property
    def design_points(self) -> List[DesignPoint]:
        """List of ``DesignPoint`` objects inside of the component."""
        return self._design_points

    @property
    def coordinate_systems(self) -> List[CoordinateSystem]:
        """List of ``CoordinateSystem`` objects inside of the component."""
        return self._coordinate_systems

    @property
    def parent_component(self) -> Union["Component", None]:
        """Parent of the component."""
        return self._parent_component

    @property
    def is_alive(self) -> bool:
        """Whether the component is still alive on the server side."""
        return self._is_alive

    @property
    def shared_topology(self) -> Union[SharedTopologyType, None]:
        """
        Shared topology type of the component (if any).

        Notes
        -----
        If no shared topology has been set, ``None`` is returned.
        """
        return self._shared_topology

    def __create_children(self, template: "Component") -> None:
        """Create new component and child bodies in ``self`` from ``template``."""
        for template_comp in template.components:
            new_id = self.id + "/" + template_comp.id.split("/")[-1]
            new = Component(
                template_comp.name,
                self,
                self._grpc_client,
                template=template_comp,
                preexisting_id=new_id,
                master_component=template_comp._master_component,
            )
            self.components.append(new)

    def get_world_transform(self) -> Matrix44:
        """
        Get the full transformation matrix of the component in world space.

        Returns
        -------
        Matrix44
            4x4 transformation matrix of the component in world space.
        """
        if self.parent_component is None:
            return IDENTITY_MATRIX44
        return self.parent_component.get_world_transform() * self._master_component.transform

    @protect_grpc
    @ensure_design_is_active
    def modify_placement(
        self,
        translation: Optional[Vector3D] = None,
        rotation_origin: Optional[Point3D] = None,
        rotation_direction: Optional[UnitVector3D] = None,
        rotation_angle: Union[Quantity, Angle, Real] = 0,
    ):
        """
        Apply a translation and/or rotation to the existing placement matrix.

        Notes
        -----
        To reset a component's placement to an identity matrix, see
        :func:`reset_placement()` or call :func:`modify_placement()` with no arguments.

        Parameters
        ----------
        translation : Vector3D, default: None
            Vector that defines the desired translation to the component.
        rotation_origin : Point3D, default: None
            Origin that defines the axis to rotate the component about.
        rotation_direction : UnitVector3D, default: None
            Direction of the axis to rotate the component about.
        rotation_angle : Union[~pint.Quantity, Angle, Real], default: 0
            Angle to rotate the component around the axis.
        """
        t = (
            Direction(x=translation.x, y=translation.y, z=translation.z)
            if translation is not None
            else None
        )
        p = point3d_to_grpc_point(rotation_origin) if rotation_origin is not None else None
        d = (
            unit_vector_to_grpc_direction(rotation_direction)
            if rotation_direction is not None
            else None
        )
        angle = rotation_angle if isinstance(rotation_angle, Angle) else Angle(rotation_angle)

        response = self._component_stub.SetPlacement(
            SetPlacementRequest(
                id=self.id,
                translation=t,
                rotation_axis_origin=p,
                rotation_axis_direction=d,
                rotation_angle=angle.value.m,
            )
        )
        self._master_component.transform = grpc_matrix_to_matrix(response.matrix)

    def reset_placement(self):
        """
        Reset a component's placement matrix to an identity matrix.

        See :func:`modify_placement()`.
        """
        self.modify_placement()

    @check_input_types
    @ensure_design_is_active
    def add_component(self, name: str, template: Optional["Component"] = None) -> "Component":
        """
        Add a new component under this component within the design assembly.

        Parameters
        ----------
        name : str
            User-defined label for the new component.
        template : Component, default: None
            Template to create this component from. This creates an
            instance component that shares a master with the template component.

        Returns
        -------
        Component
            New component with no children in the design assembly.
        """
        new_comp = Component(name, self, self._grpc_client, template=template)
        master = new_comp._master_component
        master_id = new_comp.id.split("/")[-1]

        for comp in self._master_component.occurrences:
            if comp.id != self.id:
                comp.components.append(
                    Component(
                        name,
                        comp,
                        self._grpc_client,
                        template,
                        preexisting_id=f"{comp.id}/{master_id}",
                        master_component=master,
                        read_existing_comp=True,
                    )
                )

        self.components.append(new_comp)
        return self._components[-1]

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def set_shared_topology(self, share_type: SharedTopologyType) -> None:
        """
        Set the shared topology to apply to the component.

        Parameters
        ----------
        share_type : SharedTopologyType
            Shared topology type to assign to the component.
        """
        # Set the SharedTopologyType on the server
        self._grpc_client.log.debug(
            f"Setting shared topology type {share_type.value} on {self.id}."
        )
        self._component_stub.SetSharedTopology(
            SetSharedTopologyRequest(id=self.id, share_type=share_type.value)
        )

        # Store the SharedTopologyType set on the client
        self._shared_topology = share_type

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def extrude_sketch(
        self, name: str, sketch: Sketch, distance: Union[Quantity, Distance, Real]
    ) -> Body:
        """
        Create a solid body by extruding the sketch profile up by a given distance.

        Notes
        -----
        The newly created body is placed under this component within the design assembly.

        Parameters
        ----------
        name : str
            User-defined label for the new solid body.
        sketch : Sketch
            Two-dimensional sketch source for the extrusion.
        distance : Union[~pint.Quantity, Distance, Real]
            Distance to extrude the solid body.

        Returns
        -------
        Body
            Extruded body from the given sketch.
        """
        # Sanity checks on inputs
        distance = distance if isinstance(distance, Distance) else Distance(distance)

        # Perform extrusion request
        request = CreateExtrudedBodyRequest(
            distance=distance.value.m_as(DEFAULT_UNITS.SERVER_LENGTH),
            parent=self.id,
            plane=plane_to_grpc_plane(sketch._plane),
            geometries=sketch_shapes_to_grpc_geometries(sketch._plane, sketch.edges, sketch.faces),
            name=name,
        )

        self._grpc_client.log.debug(f"Extruding sketch provided on {self.id}. Creating body...")
        response = self._bodies_stub.CreateExtrudedBody(request)
        tb = MasterBody(response.master_id, name, self._grpc_client, is_surface=False)
        self._master_component.part.bodies.append(tb)
        return Body(response.id, response.name, self, tb)

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def extrude_face(self, name: str, face: Face, distance: Union[Quantity, Distance]) -> Body:
        """
        Extrude the face profile by a given distance to create a solid body.

        There are no modifications against the body containing the source face.

        Notes
        -----
        The source face can be anywhere within the design component hierarchy.
        Therefore, there is no validation requiring that the face is placed under the
        target component where the body is to be created.

        Parameters
        ----------
        name : str
            User-defined label for the new solid body.
        face : Face
            Target face to use as the source for the new surface.
        distance : Union[~pint.Quantity, Distance]
            Distance to extrude the solid body.

        Returns
        -------
        Body
            Extruded solid body.
        """
        # Sanity checks on inputs
        extrude_distance = distance if isinstance(distance, Quantity) else distance.value
        check_pint_unit_compatibility(extrude_distance.units, DEFAULT_UNITS.SERVER_LENGTH)

        # Take the face source directly. No need to verify the source of the face.
        request = CreateExtrudedBodyFromFaceProfileRequest(
            distance=extrude_distance.m_as(DEFAULT_UNITS.SERVER_LENGTH),
            parent=self.id,
            face=face.id,
            name=name,
        )

        self._grpc_client.log.debug(f"Extruding from face provided on {self.id}. Creating body...")
        response = self._bodies_stub.CreateExtrudedBodyFromFaceProfile(request)

        tb = MasterBody(response.master_id, name, self._grpc_client, is_surface=False)
        self._master_component.part.bodies.append(tb)
        return Body(response.id, response.name, self, tb)

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def create_surface(self, name: str, sketch: Sketch) -> Body:
        """
        Create a surface body with a sketch profile.

        The newly created body is placed under this component within the design assembly.

        Parameters
        ----------
        name : str
            User-defined label for the new surface body.
        sketch : Sketch
            Two-dimensional sketch source for the surface definition.

        Returns
        -------
        Body
            Body (as a planar surface) from the given sketch.
        """
        # Perform planar body request
        request = CreatePlanarBodyRequest(
            parent=self.id,
            plane=plane_to_grpc_plane(sketch._plane),
            geometries=sketch_shapes_to_grpc_geometries(sketch._plane, sketch.edges, sketch.faces),
            name=name,
        )

        self._grpc_client.log.debug(
            f"Creating planar surface from sketch provided on {self.id}. Creating body..."
        )
        response = self._bodies_stub.CreatePlanarBody(request)

        tb = MasterBody(response.master_id, name, self._grpc_client, is_surface=True)
        self._master_component.part.bodies.append(tb)
        return Body(response.id, response.name, self, tb)

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def create_surface_from_face(self, name: str, face: Face) -> Body:
        """
        Create a surface body based on a face.

        Notes
        -----
        The source face can be anywhere within the design component hierarchy.
        Therefore, there is no validation requiring that the face is placed under the
        target component where the body is to be created.

        Parameters
        ----------
        name : str
            User-defined label for the new surface body.
        face : Face
            Target face to use as the source for the new surface.

        Returns
        -------
        Body
            Surface body.
        """
        # Take the face source directly. No need to verify the source of the face.
        request = CreateBodyFromFaceRequest(
            parent=self.id,
            face=face.id,
            name=name,
        )

        self._grpc_client.log.debug(
            f"Creating planar surface from face provided on {self.id}. Creating body..."
        )
        response = self._bodies_stub.CreateBodyFromFace(request)

        tb = MasterBody(response.master_id, name, self._grpc_client, is_surface=True)
        self._master_component.part.bodies.append(tb)
        return Body(response.id, response.name, self, tb)

    @check_input_types
    @ensure_design_is_active
    def create_coordinate_system(self, name: str, frame: Frame) -> CoordinateSystem:
        """
        Create a coordinate system.

        The newly created coordinate system is place under this component
        within the design assembly.

        Parameters
        ----------
        name : str
            User-defined label for the new coordinate system.
        frame : Frame
            Frame defining the coordinate system bounds.

        Returns
        -------
        CoordinateSystem
        """
        self._coordinate_systems.append(CoordinateSystem(name, frame, self, self._grpc_client))
        return self._coordinate_systems[-1]

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def translate_bodies(
        self, bodies: List[Body], direction: UnitVector3D, distance: Union[Quantity, Distance, Real]
    ) -> None:
        """
        Translate the geometry bodies in a specified direction by a given distance.

        Notes
        -----
        If the body does not belong to this component (or its children), it
        is not translated.

        Parameters
        ----------
        bodies: List[Body]
            List of bodies to translate by the same distance.
        direction: UnitVector3D
            Direction of the translation.
        distance: Union[~pint.Quantity, Distance, Real]
            Magnitude of the translation.

        Returns
        -------
        None
        """
        body_ids_found = []

        for body in bodies:
            body_requested = self.search_body(body.id)
            if body_requested:
                body_ids_found.append(body_requested.id)
            else:
                self._grpc_client.log.warning(
                    f"Body with ID {body.id} and name {body.name} is not found in this "
                    + "component (or subcomponents). Ignoring this translation request."
                )
                pass

        distance = distance if isinstance(distance, Distance) else Distance(distance)

        translation_magnitude = distance.value.m_as(DEFAULT_UNITS.SERVER_LENGTH)

        self._grpc_client.log.debug(f"Translating {body_ids_found}...")
        self._bodies_stub.Translate(
            TranslateRequest(
                ids=body_ids_found,
                direction=unit_vector_to_grpc_direction(direction),
                distance=translation_magnitude,
            )
        )

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def create_beams(
        self, segments: List[Tuple[Point3D, Point3D]], profile: BeamProfile
    ) -> List[Beam]:
        """
        Create beams under the component.

        Notes
        -----
        The newly created beams synchronize to a design within a supporting
        Geometry service instance.

        Parameters
        ----------
        segments : List[Tuple[Point3D, Point3D]]
            List of start and end pairs, each specifying a single line segment.
        profile : BeamProfile
            Beam profile to use to create the beams.
        """
        request = CreateBeamSegmentsRequest(parent=self.id, profile=profile.id)

        for segment in segments:
            request.lines.append(
                Line(start=point3d_to_grpc_point(segment[0]), end=point3d_to_grpc_point(segment[1]))
            )

        self._grpc_client.log.debug(f"Creating beams on {self.id}...")
        response = self._commands_stub.CreateBeamSegments(request)
        self._grpc_client.log.debug(f"Beams successfully created.")

        # Note: The current gRPC API simply returns a list of IDs. There is no additional
        # information to correlate/merge against, so it is fully assumed that the list is
        # returned in order with a 1 to 1 index match to the request segments list.
        new_beams = []
        n_beams = len(response.ids)
        for index in range(n_beams):
            new_beams.append(
                Beam(response.ids[index], segments[index][0], segments[index][1], profile, self)
            )

        self._beams.extend(new_beams)
        return self._beams[-n_beams:]

    def create_beam(self, start: Point3D, end: Point3D, profile: BeamProfile) -> Beam:
        """
        Create a beam under the component.

        The newly created beam synchronizes to a design within a supporting
        Geometry service instance.

        Parameters
        ----------
        start : Point3D
            Starting point of the beam line segment.
        end : Point3D
            Ending point of the beam line segment.
        profile : BeamProfile
            Beam profile to use to create the beam.
        """
        return self.create_beams([(start, end)], profile)[0]

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def delete_component(self, component: Union["Component", str]) -> None:
        """
        Delete a component (itself or its children).

        Notes
        -----
        If the component is not this component (or its children), it
        is not deleted.

        Parameters
        ----------
        component : Union[Component, str]
            ID of the component or instance to delete.
        """
        id = component if isinstance(component, str) else component.id
        component_requested = self.search_component(id)

        if component_requested:
            # If the component belongs to this component (or nested components)
            # call the server deletion mechanism
            self._component_stub.Delete(EntityIdentifier(id=id))

            # If the component was deleted from the server side... "kill" it
            # on the client side
            component_requested._kill_component_on_client()
            self._grpc_client.log.debug(f"Component {component_requested.id} has been deleted.")
        else:
            self._grpc_client.log.warning(
                f"Component {id} not found in this component (or subcomponents)."
                + " Ignoring deletion request."
            )
            pass

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def delete_body(self, body: Union[Body, str]) -> None:
        """
        Delete a body belonging to this component (or its children).

        Notes
        -----
        If the body does not belong to this component (or its children), it
        is not deleted.

        Parameters
        ----------
        body : Union[Body, str]
            ID of the body or instance to delete.
        """
        id = body if isinstance(body, str) else body.id
        body_requested = self.search_body(id)

        if body_requested:
            # If the body belongs to this component (or nested components)
            # call the server deletion mechanism
            self._bodies_stub.Delete(EntityIdentifier(id=id))

            # If the body was deleted from the server side... "kill" it
            # on the client side
            body_requested._is_alive = False
            self._grpc_client.log.debug(f"Body {body_requested.id} has been deleted.")
        else:
            self._grpc_client.log.warning(
                f"Body {id} is not found in this component (or subcomponents)."
                + " Ignoring this deletion request."
            )
            pass

    def add_design_point(
        self,
        name: str,
        point: Point3D,
    ) -> DesignPoint:
        """
        Create a single design point.

        Parameters
        ----------
        name : str
            User-defined label for the design points.
        points : Point3D
            3D point constituting the design point.
        """
        return self.add_design_points(name, [point])[0]

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def add_design_points(
        self,
        name: str,
        points: List[Point3D],
    ) -> List[DesignPoint]:
        """
        Create a list of design points.

        Parameters
        ----------
        name : str
            User-defined label for the list of design points.
        points : List[Point3D]
            List of the 3D points that constitute the list of design points.
        """
        # Create DesignPoint objects server-side
        self._grpc_client.log.debug(f"Creating design points on {self.id}...")
        response = self._commands_stub.CreateDesignPoints(
            CreateDesignPointsRequest(
                points=[point3d_to_grpc_point(point) for point in points], parent=self.id
            )
        )
        self._grpc_client.log.debug("Design points successfully created.")

        # Once created on the server, create them client side
        new_design_points = []
        n_design_points = len(response.ids)
        for index in range(n_design_points):
            new_design_points.append((DesignPoint(response.ids[index], name, points[index], self)))
        self._design_points.extend(new_design_points)

        # Finally return the list of created DesignPoint objects
        return self._design_points[-n_design_points:]

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def delete_beam(self, beam: Union[Beam, str]) -> None:
        """
        Delete an existing beam belonging to this component (or its children).

        Notes
        -----
        If the beam does not belong to this component (or its children), it
        is not deleted.

        Parameters
        ----------
        beam : Union[Beam, str]
            ID of the beam or instance to delete.
        """
        id = beam if isinstance(beam, str) else beam.id
        beam_requested = self.search_beam(id)

        if beam_requested:
            # If the beam belongs to this component (or nested components)
            # call the server deletion mechanism
            #
            # Server-side, the same deletion request has to be performed
            # as for deleting a Body
            #
            self._commands_stub.DeleteBeam(EntityIdentifier(id=beam_requested.id))

            # If the beam was deleted from the server side... "kill" it
            # on the client side
            beam_requested._is_alive = False
            self._grpc_client.log.debug(f"Beam {beam_requested.id} has been deleted.")
        else:
            self._grpc_client.log.warning(
                f"Beam {id} not found in this component (or subcomponents)."
                + " Ignoring deletion request."
            )
            pass

    @check_input_types
    def search_component(self, id: str) -> Union["Component", None]:
        """
        Search nested components recursively for a component.

        Parameters
        ----------
        id : str
            ID of the component to search for.

        Returns
        -------
        Component
           Component with the requested ID. If this ID is not found, ``None`` is returned.
        """
        # Check if the requested component is this one
        if self.id == id and self.is_alive:
            return self

        # If no luck, search on nested components
        result = None
        for component in self.components:
            result = component.search_component(id)
            if result:
                return result

        # If you reached this point... this means that no component was found!
        return None

    @check_input_types
    def search_body(self, id: str) -> Union[Body, None]:
        """
        Search bodies in the component and nested components recursively for a body.

        Parameters
        ----------
        id : str
            ID of the body to search for.

        Returns
        -------
        Body
            Body with the requested ID. If the ID is not found, ``None`` is returned.
        """
        # Search in component's bodies
        for body in self.bodies:
            if body.id == id and body.is_alive:
                return body

        # If no luck, search on nested components
        result = None
        for component in self.components:
            result = component.search_body(id)
            if result:
                return result

        # If you reached this point... this means that no body was found!
        return None

    @check_input_types
    def search_beam(self, id: str) -> Union[Beam, None]:
        """
        Search beams in the component and nested components recursively for a beam.

        Parameters
        ----------
        id : str
            ID of the beam to search for.

        Returns
        -------
        Union[Beam, None]
            Beam with the requested ID. If the ID is not found, ``None`` is returned.
        """
        # Search in component's beams
        for beam in self.beams:
            if beam.id == id and beam.is_alive:
                return beam

        # If no luck, search on nested components
        result = None
        for component in self.components:
            result = component.search_beam(id)
            if result:
                return result

        # If you reached this point... this means that no beam was found!
        return None

    def _kill_component_on_client(self) -> None:
        """
        Set the ``is_alive`` property of nested objects to ``False``.

        Notes
        -----
        This method is recursive. It is only to be used by the
        :func:`delete_component()` method and itself.
        """
        # Kill all its bodies, beams and coordinate systems
        for elem in [*self.bodies, *self.beams, *self._coordinate_systems]:
            elem._is_alive = False

        # Now, go to the nested components and kill them as well
        for component in self.components:
            component._kill_component_on_client()

        # Kill itself
        self._is_alive = False

    def tessellate(
        self, merge_component: bool = False, merge_bodies: bool = False
    ) -> Union["PolyData", "MultiBlock"]:
        """
        Tessellate the component.

        Parameters
        ----------
        merge_component : bool, default: False
            Whether to merge this component into a single dataset. When ``True``,
            all the individual bodies are effectively combined into a single
            dataset without any hierarchy.
        merge_bodies : bool, default: False
            Whether to merge each body into a single dataset. When ``True``,
            all the faces of each individual body are effectively
            merged into a single dataset without separating faces.

        Returns
        -------
        ~pyvista.PolyData, ~pyvista.MultiBlock
            Merged :class:`pyvista.PolyData` if ``merge_component=True`` or a
            composite dataset.

        Examples
        --------
        Create two stacked bodies and return the tessellation as two merged bodies:

        >>> from ansys.geometry.core.sketch import Sketch
        >>> from ansys.geometry.core import Modeler
        >>> from ansys.geometry.core.math import Point2D, Point3D, Plane
        >>> from ansys.geometry.core.misc import UNITS
        >>> from ansys.geometry.core.plotting import Plotter
        >>> modeler = Modeler("10.54.0.72", "50051")
        >>> sketch_1 = Sketch()
        >>> box = sketch_1.box(
        >>>    Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(5, UNITS.m))
        >>> sketch_1.circle(Point2D([0, 0], UNITS.m), Quantity(25, UNITS.m))
        >>> design = modeler.create_design("MyDesign")
        >>> comp = design.add_component("MyComponent")
        >>> distance = Quantity(10, UNITS.m)
        >>> body = comp.extrude_sketch("Body", sketch=sketch_1, distance=distance)
        >>> sketch_2 = Sketch(Plane([0, 0, 10]))
        >>> box = sketch_2.box(
        >>>    Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(5, UNITS.m))
        >>> circle = sketch_2.circle(Point2D([0, 0], UNITS.m), Quantity(25, UNITS.m))
        >>> body = comp.extrude_sketch("Body", sketch=sketch_2, distance=distance)
        >>> dataset = comp.tessellate(merge_bodies=True)
        >>> dataset
        MultiBlock (0x7ff6bcb511e0)
          N Blocks:     2
          X Bounds:     -25.000, 25.000
          Y Bounds:     -24.991, 24.991
          Z Bounds:     0.000, 20.000
        """
        import pyvista as pv

        # Tessellate the bodies in this component
        datasets = [body.tessellate(merge_bodies) for body in self.bodies]

        blocks_list = [pv.MultiBlock(datasets)]

        # Now, go recursively inside its subcomponents (with no arguments) and
        # merge the PolyData obtained into our blocks
        for comp in self._components:
            if not comp.is_alive:
                continue
            blocks_list.append(comp.tessellate(merge_bodies=merge_bodies))

        # Transform the list of MultiBlock objects into a single MultiBlock
        blocks = pv.MultiBlock(blocks_list)

        if merge_component:
            ugrid = blocks.combine()
            # Convert to polydata as it's slightly faster than extract surface
            return pv.PolyData(ugrid.points, ugrid.cells, n_faces=ugrid.n_cells)
        return blocks

    def plot(
        self,
        merge_component: bool = False,
        merge_bodies: bool = False,
        screenshot: Optional[str] = None,
        use_trame: Optional[bool] = None,
        **plotting_options: Optional[dict],
    ) -> None:
        """
        Plot the component.

        Parameters
        ----------
        merge_component : bool, default: False
            Whether to merge the component into a single dataset. When ``True``,
            all the individual bodies are effectively merged into a single
            dataset without any hierarchy.
        merge_bodies : bool, default: False
            Whether to merge each body into a single dataset. When ``True``,
            all the faces of each individual body are effectively merged
            into a single dataset without separating faces.
        screenshot : str, default: None
            Path for saving a screenshot of the image being represented.
        use_trame : bool, default: None
            Whether to enable the use of `trame <https://kitware.github.io/trame/index.html>`_.
            The default is ``None``, in which case the ``USE_TRAME`` global setting
            is used.
        **plotting_options : dict, default: None
            Keyword arguments for plotting. For allowable keyword arguments, see the

        Examples
        --------
        Create 25 small cylinders in a grid-like pattern on the XY plane and
        plot them. Make the cylinders look metallic by enabling
        physically-based rendering with ``pbr=True``.

        >>> from ansys.geometry.core.misc.units import UNITS as u
        >>> from ansys.geometry.core.sketch import Sketch
        >>> from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
        >>> from ansys.geometry.core import Modeler
        >>> import numpy as np
        >>> modeler = Modeler()
        >>> origin = Point3D([0, 0, 0])
        >>> plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])
        >>> design = modeler.create_design("my-design")
        >>> mycomp = design.add_component("my-comp")
        >>> n = 5
        >>> xx, yy = np.meshgrid(
        ...     np.linspace(-4, 4, n),
        ...     np.linspace(-4, 4, n),
        ... )
        >>> for x, y in zip(xx.ravel(), yy.ravel()):
        ...     sketch = Sketch(plane)
        ...     sketch.circle(Point2D([x, y]), 0.2*u.m)
        ...     mycomp.extrude_sketch(f"body-{x}-{y}", sketch, 1 * u.m)
        >>> mycomp
        ansys.geometry.core.designer.Component 0x2203cc9ec50
            Name                 : my-comp
            Exists               : True
            Parent component     : my-design
            N Bodies             : 25
            N Components         : 0
            N Coordinate Systems : 0
        >>> mycomp.plot(pbr=True, metallic=1.0)
        """
        from ansys.geometry.core.plotting import PlotterHelper

        PlotterHelper(use_trame=use_trame).plot(
            self,
            merge_bodies=merge_bodies,
            merge_component=merge_component,
            screenshot=screenshot,
            **plotting_options,
        )

    def __repr__(self) -> str:
        """Represent the ``Component`` as a string."""
        alive_bodies = [1 if body.is_alive else 0 for body in self.bodies]
        alive_beams = [1 if beam.is_alive else 0 for beam in self.beams]
        alive_coords = [1 if cs.is_alive else 0 for cs in self.coordinate_systems]
        alive_comps = [1 if comp.is_alive else 0 for comp in self.components]
        lines = [f"ansys.geometry.core.designer.Component {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Exists               : {self.is_alive}")
        lines.append(f"  Parent component     : {self.parent_component.name}")
        lines.append(f"  N Bodies             : {sum(alive_bodies)}")
        lines.append(f"  N Beams              : {sum(alive_beams)}")
        lines.append(f"  N Coordinate Systems : {sum(alive_coords)}")
        lines.append(f"  N Design Points      : {len(self.design_points)}")
        lines.append(f"  N Components         : {sum(alive_comps)}")
        return "\n".join(lines)
