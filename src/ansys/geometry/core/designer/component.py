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
from typing import TYPE_CHECKING, Optional, Union
import uuid

from beartype import beartype as check_input_types
from pint import Quantity

from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
from ansys.api.geometry.v0.bodies_pb2 import (
    CreateBodyFromFaceRequest,
    CreateExtrudedBodyFromFaceProfileRequest,
    CreateExtrudedBodyFromLoftProfilesRequest,
    CreateExtrudedBodyRequest,
    CreatePlanarBodyRequest,
    CreateSphereBodyRequest,
    CreateSweepingChainRequest,
    CreateSweepingProfileRequest,
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
from ansys.api.geometry.v0.models_pb2 import Direction, Line, TrimmedCurveList
from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.connection.conversions import (
    grpc_matrix_to_matrix,
    plane_to_grpc_plane,
    point3d_to_grpc_point,
    sketch_shapes_to_grpc_geometries,
    trimmed_curve_to_grpc_trimmed_curve,
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
from ansys.geometry.core.misc.checks import ensure_design_is_active, min_backend_version
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Angle, Distance
from ansys.geometry.core.shapes.curves.circle import Circle
from ansys.geometry.core.shapes.curves.trimmed_curve import TrimmedCurve
from ansys.geometry.core.shapes.parameterization import Interval
from ansys.geometry.core.sketch.sketch import Sketch
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from pyvista import MultiBlock, PolyData


@unique
class SharedTopologyType(Enum):
    """Shared topologies available."""

    SHARETYPE_NONE = 0
    SHARETYPE_SHARE = 1
    SHARETYPE_MERGE = 2
    SHARETYPE_GROUPS = 3


@unique
class ExtrusionDirection(Enum):
    """Enum for extrusion direction definition."""

    POSITIVE = "+"
    NEGATIVE = "-"

    @classmethod
    def from_string(cls, string: str, use_default_if_error: bool = False) -> "ExtrusionDirection":
        """Convert a string to an ``ExtrusionDirection`` enum."""
        if string == "+":
            return cls.POSITIVE
        elif string == "-":
            return cls.NEGATIVE
        elif use_default_if_error:
            from ansys.geometry.core.logger import LOG

            LOG.warning("Invalid extrusion direction. Using default value (+).")
            return cls.POSITIVE
        else:  # pragma: no cover
            raise ValueError(f"Invalid extrusion direction: {string}.")


class Component:
    """Provides for creating and managing a component.

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
    instance_name: str, default: None
        User defined optional name for the component instance.
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
    _components: list["Component"]
    _beams: list[Beam]
    _coordinate_systems: list[CoordinateSystem]
    _design_points: list[DesignPoint]

    @protect_grpc
    @check_input_types
    def __init__(
        self,
        name: str,
        parent_component: Union["Component", None],
        grpc_client: GrpcClient,
        template: Optional["Component"] = None,
        instance_name: Optional[str] = None,
        preexisting_id: str | None = None,
        master_component: MasterComponent | None = None,
        read_existing_comp: bool = False,
    ):
        """Initialize the ``Component`` class."""
        # Initialize the client and stubs needed
        self._grpc_client = grpc_client
        self._component_stub = ComponentsStub(self._grpc_client.channel)
        self._bodies_stub = BodiesStub(self._grpc_client.channel)
        self._commands_stub = CommandsStub(self._grpc_client.channel)

        # Align instance name behavior with the server - empty string if None
        instance_name = instance_name if instance_name else ""

        if preexisting_id:
            self._name = name
            self._id = preexisting_id
            self._instance_name = instance_name
        else:
            if parent_component:
                template_id = template.id if template else ""
                new_component = self._component_stub.Create(
                    CreateRequest(
                        name=name,
                        parent=parent_component.id,
                        template=template_id,
                        instance_name=instance_name,
                    )
                )

                # Remove this method call once we know Service sends correct ObjectPath id
                self._id = new_component.component.id
                self._name = new_component.component.name
                self._instance_name = new_component.component.instance_name
            else:
                self._name = name
                self._id = None
                self._instance_name = instance_name

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
    def instance_name(self) -> str:
        """Name of the component instance."""
        return self._instance_name

    @property
    def components(self) -> list["Component"]:
        """List of ``Component`` objects inside of the component."""
        return self._components

    @property
    def bodies(self) -> list[Body]:
        """List of ``Body`` objects inside of the component."""
        bodies = []
        for body in self._master_component.part.bodies:
            id = f"{self.id}/{body.id}" if self.parent_component else body.id
            if body.is_alive:
                bodies.append(Body(id, body.name, self, body))
        return bodies

    @property
    def beams(self) -> list[Beam]:
        """List of ``Beam`` objects inside of the component."""
        return self._beams

    @property
    def design_points(self) -> list[DesignPoint]:
        """List of ``DesignPoint`` objects inside of the component."""
        return self._design_points

    @property
    def coordinate_systems(self) -> list[CoordinateSystem]:
        """List of ``CoordinateSystem`` objects inside of the component."""
        return self._coordinate_systems

    @property
    def parent_component(self) -> "Component":
        """Parent of the component."""
        return self._parent_component

    @property
    def is_alive(self) -> bool:
        """Whether the component is still alive on the server side."""
        return self._is_alive

    @property
    def shared_topology(self) -> SharedTopologyType | None:
        """Shared topology type of the component (if any).

        Notes
        -----
        If no shared topology has been set, ``None`` is returned.
        """
        return self._shared_topology

    def __create_children(self, template: "Component") -> None:
        """Create new component and child bodies from ``template``."""
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
        """Get the full transformation matrix of the component in world space.

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
        translation: Vector3D | None = None,
        rotation_origin: Point3D | None = None,
        rotation_direction: UnitVector3D | None = None,
        rotation_angle: Quantity | Angle | Real = 0,
    ):
        """Apply a translation and/or rotation to the placement matrix.

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
        rotation_angle : ~pint.Quantity | Angle | Real, default: 0
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
        """Reset a component's placement matrix to an identity matrix.

        See :func:`modify_placement()`.
        """
        self.modify_placement()

    @check_input_types
    @ensure_design_is_active
    def add_component(
        self, name: str, template: Optional["Component"] = None, instance_name: str = None
    ) -> "Component":
        """Add a new component under this component within the design assembly.

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
        new_comp = Component(
            name, self, self._grpc_client, template=template, instance_name=instance_name
        )
        master = new_comp._master_component
        master_id = new_comp.id.split("/")[-1]
        for comp in self._master_component.occurrences:
            if comp.id != self.id:
                comp.components.append(
                    Component(
                        name,
                        comp,
                        self._grpc_client,
                        template=template,
                        instance_name=instance_name,
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
        """Set the shared topology to apply to the component.

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
        self,
        name: str,
        sketch: Sketch,
        distance: Quantity | Distance | Real,
        direction: ExtrusionDirection | str = ExtrusionDirection.POSITIVE,
    ) -> Body:
        """Create a solid body by extruding the sketch profile a distance.

        Notes
        -----
        The newly created body is placed under this component within the design assembly.

        Parameters
        ----------
        name : str
            User-defined label for the new solid body.
        sketch : Sketch
            Two-dimensional sketch source for the extrusion.
        distance : ~pint.Quantity | Distance | Real
            Distance to extrude the solid body.
        direction : ExtrusionDirection | str, default: "+"
            Direction for extruding the solid body.
            The default is to extrude in the positive normal direction of the sketch.
            Options are "+" and "-" as a string, or the enum values.

        Returns
        -------
        Body
            Extruded body from the given sketch.
        """
        # Sanity checks on inputs
        distance = distance if isinstance(distance, Distance) else Distance(distance)
        if isinstance(direction, str):
            direction = ExtrusionDirection.from_string(direction, use_default_if_error=True)

        # Perform extrusion request
        request = CreateExtrudedBodyRequest(
            distance=distance.value.m_as(DEFAULT_UNITS.SERVER_LENGTH),
            parent=self.id,
            plane=plane_to_grpc_plane(sketch._plane),
            geometries=sketch_shapes_to_grpc_geometries(sketch._plane, sketch.edges, sketch.faces),
            name=name,
        )

        # Check the direction - if it is -, flip the distance
        if direction is ExtrusionDirection.NEGATIVE:
            request.distance = -request.distance

        self._grpc_client.log.debug(f"Extruding sketch provided on {self.id}. Creating body...")
        response = self._bodies_stub.CreateExtrudedBody(request)
        tb = MasterBody(response.master_id, name, self._grpc_client, is_surface=False)
        self._master_component.part.bodies.append(tb)
        return Body(response.id, response.name, self, tb)

    @min_backend_version(24, 2, 0)
    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def sweep_sketch(
        self,
        name: str,
        sketch: Sketch,
        path: list[TrimmedCurve],
    ) -> Body:
        """Create a body by sweeping a planar profile along a path.

        Notes
        -----
        The newly created body is placed under this component within the design assembly.

        Parameters
        ----------
        name : str
            User-defined label for the new solid body.
        sketch : Sketch
            Two-dimensional sketch source for the extrusion.
        path : list[TrimmedCurve]
            The path to sweep the profile along.

        Returns
        -------
        Body
            Created body from the given sketch.
        """
        # Convert each ``TrimmedCurve`` in path to equivalent gRPC type
        path_grpc = []
        for tc in path:
            path_grpc.append(trimmed_curve_to_grpc_trimmed_curve(tc))

        request = CreateSweepingProfileRequest(
            name=name,
            parent=self.id,
            plane=plane_to_grpc_plane(sketch._plane),
            geometries=sketch_shapes_to_grpc_geometries(sketch._plane, sketch.edges, sketch.faces),
            path=path_grpc,
        )

        self._grpc_client.log.debug(f"Creating a sweeping profile on {self.id}. Creating body...")
        response = self._bodies_stub.CreateSweepingProfile(request)
        tb = MasterBody(response.master_id, name, self._grpc_client, is_surface=False)
        self._master_component.part.bodies.append(tb)
        return Body(response.id, response.name, self, tb)

    @min_backend_version(24, 2, 0)
    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def sweep_chain(
        self,
        name: str,
        path: list[TrimmedCurve],
        chain: list[TrimmedCurve],
    ) -> Body:
        """Create a body by sweeping a chain of curves along a path.

        Notes
        -----
        The newly created body is placed under this component within the design assembly.

        Parameters
        ----------
        name : str
            User-defined label for the new solid body.
        path : list[TrimmedCurve]
            The path to sweep the chain along.
        chain : list[TrimmedCurve]
            A chain of trimmed curves.

        Returns
        -------
        Body
            Created body from the given sketch.
        """
        # Convert each ``TrimmedCurve`` in path and chain to equivalent gRPC types
        path_grpc = [trimmed_curve_to_grpc_trimmed_curve(tc) for tc in path]
        chain_grpc = [trimmed_curve_to_grpc_trimmed_curve(tc) for tc in chain]

        request = CreateSweepingChainRequest(
            name=name,
            parent=self.id,
            path=path_grpc,
            chain=chain_grpc,
        )

        self._grpc_client.log.debug(f"Creating a sweeping chain on {self.id}. Creating body...")
        response = self._bodies_stub.CreateSweepingChain(request)
        tb = MasterBody(response.master_id, name, self._grpc_client, is_surface=True)
        self._master_component.part.bodies.append(tb)
        return Body(response.id, response.name, self, tb)

    @min_backend_version(24, 2, 0)
    @check_input_types
    def revolve_sketch(
        self,
        name: str,
        sketch: Sketch,
        axis: Vector3D,
        angle: Quantity | Angle | Real,
        rotation_origin: Point3D,
    ) -> Body:
        """Create a solid body by revolving a sketch profile around an axis.

        Parameters
        ----------
        name : str
            User-defined label for the new solid body.
        sketch : Sketch
            Two-dimensional sketch source for the revolve.
        axis : Vector3D
            Axis of rotation for the revolve.
        angle : ~pint.Quantity | Angle | Real
            Angle to revolve the solid body around the axis. The angle can be positive or negative.
        rotation_origin : Point3D
            Origin of the axis of rotation.

        Returns
        -------
        Body
            Revolved body from the given sketch.
        """
        # Based on the reference axis and the sketch plane's normal, retrieve the orthogonal
        # vector (i.e. this is the reference vector for the Circle object). Assuming a distance of 1
        # we revolve around the axis the angle given.
        rotation_vector = sketch._plane.normal.cross(axis)

        # Define the revolve path
        circle = Circle(
            rotation_origin,
            radius=Distance(1),
            reference=rotation_vector,
            axis=axis,
        )
        angle = angle if isinstance(angle, Angle) else Angle(angle)
        interval = (
            Interval(0, angle.value.m_as(DEFAULT_UNITS.SERVER_ANGLE))
            if angle.value.m >= 0
            else Interval(angle.value.m_as(DEFAULT_UNITS.SERVER_ANGLE), 0)
        )
        path = circle.trim(interval)

        # Create the revolved body by delegating to the sweep method
        return self.sweep_sketch(name, sketch, [path])

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def extrude_face(
        self,
        name: str,
        face: Face,
        distance: Quantity | Distance,
        direction: ExtrusionDirection | str = ExtrusionDirection.POSITIVE,
    ) -> Body:
        """Extrude the face profile by a given distance to create a solid body.

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
        distance : ~pint.Quantity | Distance | Real
            Distance to extrude the solid body.
        direction : ExtrusionDirection | str, default: "+"
            Direction for extruding the solid body's face.
            The default is to extrude in the positive normal direction of the face.
            Options are "+" and "-" as a string, or the enum values.

        Returns
        -------
        Body
            Extruded solid body.
        """
        # Sanity checks on inputs
        distance = distance if isinstance(distance, Distance) else Distance(distance)
        if isinstance(direction, str):
            direction = ExtrusionDirection.from_string(direction, use_default_if_error=True)

        # Take the face source directly. No need to verify the source of the face.
        request = CreateExtrudedBodyFromFaceProfileRequest(
            distance=distance.value.m_as(DEFAULT_UNITS.SERVER_LENGTH),
            parent=self.id,
            face=face.id,
            name=name,
        )

        # Check the direction - if it is -, flip the distance
        if direction is ExtrusionDirection.NEGATIVE:
            request.distance = -request.distance

        self._grpc_client.log.debug(f"Extruding from face provided on {self.id}. Creating body...")
        response = self._bodies_stub.CreateExtrudedBodyFromFaceProfile(request)

        tb = MasterBody(response.master_id, name, self._grpc_client, is_surface=False)
        self._master_component.part.bodies.append(tb)
        return Body(response.id, response.name, self, tb)

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    @min_backend_version(24, 2, 0)
    def create_sphere(self, name: str, center: Point3D, radius: Distance) -> Body:
        """Create a sphere body defined by the center point and the radius.

        Parameters
        ----------
        name : str
            Body name.
        center : Point3D
            Center point of the sphere.
        radius : Distance
            Radius of the sphere.

        Returns
        -------
        Body
            Sphere body object.
        """
        request = CreateSphereBodyRequest(
            name=name,
            parent=self.id,
            center=point3d_to_grpc_point(center),
            radius=radius.value.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        )
        self._grpc_client.log.debug(f"Creating a sphere body on {self.id} .")
        response = self._bodies_stub.CreateSphereBody(request)
        tb = MasterBody(response.master_id, name, self._grpc_client, is_surface=False)
        self._master_component.part.bodies.append(tb)
        return Body(response.id, response.name, self, tb)

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    @min_backend_version(24, 2, 0)
    def create_body_from_loft_profile(
        self,
        name: str,
        profiles: list[list[TrimmedCurve]],
        periodic: bool = False,
        ruled: bool = False,
    ) -> Body:
        """Create a lofted body from a collection of trimmed curves.

        Parameters
        ----------
        name : str
            Name of the lofted body.
        profiles : list[list[TrimmedCurve]]
            Collection of lists of trimmed curves (profiles) defining the lofted body's shape.
        periodic : bool, default: False
            Whether the lofted body should have periodic continuity.
        ruled : bool
            Whether the lofted body should be ruled.

        Returns
        -------
        Body
            Created lofted body object.

        Notes
        -----
        Surfaces produced have a U parameter in the direction of the profile curves,
        and a V parameter in the direction of lofting.
        Profiles can have different numbers of segments. A minimum twist solution is
        produced.
        Profiles should be all closed or all open. Closed profiles cannot contain inner
        loops. If closed profiles are supplied, a closed (solid) body is produced, if
        possible. Otherwise, an open (sheet) body is produced.
        The periodic argument applies when the profiles are closed. It is ignored if
        the profiles are open.

        If ``periodic=True``, at least three profiles must be supplied. The loft continues
        from the last profile back to the first profile to produce surfaces that are
        periodic in V.

        If ``periodic=False``, at least two profiles must be supplied. If the first
        and last profiles are planar, end capping faces are created. Otherwise, an open
        (sheet) body is produced.
        If ``ruled=True``, separate ruled surfaces are produced between each pair of profiles.
        If ``periodic=True``, the loft continues from the last profile back to the first
        profile, but the surfaces are not periodic.
        """
        profiles_grpc = [
            TrimmedCurveList(curves=[trimmed_curve_to_grpc_trimmed_curve(tc) for tc in profile])
            for profile in profiles
        ]

        request = CreateExtrudedBodyFromLoftProfilesRequest(
            name=name, parent=self.id, profiles=profiles_grpc, periodic=periodic, ruled=ruled
        )
        self._grpc_client.log.debug(f"Creating a loft profile body on {self.id} .")
        response = self._bodies_stub.CreateExtrudedBodyFromLoftProfiles(request)
        tb = MasterBody(response.master_id, name, self._grpc_client, is_surface=False)
        self._master_component.part.bodies.append(tb)
        return Body(response.id, response.name, self, tb)

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def create_surface(self, name: str, sketch: Sketch) -> Body:
        """Create a surface body with a sketch profile.

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
        """Create a surface body based on a face.

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
        """Create a coordinate system.

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
        self, bodies: list[Body], direction: UnitVector3D, distance: Quantity | Distance | Real
    ) -> None:
        """Translate the bodies in a specified direction by a distance.

        Notes
        -----
        If the body does not belong to this component (or its children), it
        is not translated.

        Parameters
        ----------
        bodies: list[Body]
            list of bodies to translate by the same distance.
        direction: UnitVector3D
            Direction of the translation.
        distance: ~pint.Quantity | Distance | Real
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
        self, segments: list[tuple[Point3D, Point3D]], profile: BeamProfile
    ) -> list[Beam]:
        """Create beams under the component.

        Notes
        -----
        The newly created beams synchronize to a design within a supporting
        Geometry service instance.

        Parameters
        ----------
        segments : list[tuple[Point3D, Point3D]]
            list of start and end pairs, each specifying a single line segment.
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
        self._grpc_client.log.debug("Beams successfully created.")

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
        """Create a beam under the component.

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
        """Delete a component (itself or its children).

        Notes
        -----
        If the component is not this component (or its children), it
        is not deleted.

        Parameters
        ----------
        component : Component | str
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
    def delete_body(self, body: Body | str) -> None:
        """Delete a body belonging to this component (or its children).

        Notes
        -----
        If the body does not belong to this component (or its children), it
        is not deleted.

        Parameters
        ----------
        body : Body | str
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
        """Create a single design point.

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
        points: list[Point3D],
    ) -> list[DesignPoint]:
        """Create a list of design points.

        Parameters
        ----------
        name : str
            User-defined label for the list of design points.
        points : list[Point3D]
            list of the 3D points that constitute the list of design points.
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
    def delete_beam(self, beam: Beam | str) -> None:
        """Delete an existing beam belonging to this component's scope.

        Notes
        -----
        If the beam belongs to this component's children, it is deleted.
        If the beam does not belong to this component (or its children), it
        is not deleted.

        Parameters
        ----------
        beam : Beam | str
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
        """Search nested components recursively for a component.

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
    def search_body(self, id: str) -> Body | None:
        """Search bodies in the component's scope.

        Notes
        -----
        This method searches for bodies in the component and nested components
        recursively.

        Parameters
        ----------
        id : str
            ID of the body to search for.

        Returns
        -------
        Body | None
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
    def search_beam(self, id: str) -> Beam | None:
        """Search beams in the component's scope.

        Notes
        -----
        This method searches for beams in the component and nested components
        recursively.

        Parameters
        ----------
        id : str
            ID of the beam to search for.

        Returns
        -------
        Beam | None
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
        """Set the ``is_alive`` property of nested objects to ``False``.

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
        """Tessellate the component.

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
        screenshot: str | None = None,
        use_trame: bool | None = None,
        use_service_colors: bool | None = None,
        **plotting_options: dict | None,
    ) -> None:
        """Plot the component.

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
            The default is ``None``, in which case the
            ``ansys.tools.visualization_interface.USE_TRAME`` global setting is used.
        use_service_colors : bool, default: None
            Whether to use the colors assigned to the body in the service. The default
            is ``None``, in which case the ``ansys.geometry.core.USE_SERVICE_COLORS``
            global setting is used.
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
        ...     sketch.circle(Point2D([x, y]), 0.2 * u.m)
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
        import ansys.geometry.core as pyansys_geometry
        from ansys.geometry.core.plotting import GeometryPlotter
        from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot

        use_service_colors = (
            use_service_colors
            if use_service_colors is not None
            else pyansys_geometry.USE_SERVICE_COLORS
        )

        mesh_object = (
            self
            if use_service_colors
            else MeshObjectPlot(
                custom_object=self,
                mesh=self.tessellate(merge_component=merge_component, merge_bodies=merge_bodies),
            )
        )
        pl = GeometryPlotter(use_trame=use_trame, use_service_colors=use_service_colors)
        pl.plot(mesh_object, **plotting_options)
        pl.show(screenshot=screenshot, **plotting_options)

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

    @check_input_types
    def tree_print(
        self,
        consider_comps: bool = True,
        consider_bodies: bool = True,
        consider_beams: bool = True,
        depth: int | None = None,
        indent: int = 4,
        sort_keys: bool = False,
        return_list: bool = False,
        skip_loc_header: bool = False,
    ) -> None | list[str]:
        """Print the component in tree format.

        Parameters
        ----------
        consider_comps : bool, default: True
            Whether to print the nested components.
        consider_bodies : bool, default: True
            Whether to print the bodies.
        consider_beams : bool, default: True
            Whether to print the beams.
        depth : int | None, default: None
            Depth level to print. If None, it prints all levels.
        indent : int, default: 4
            Indentation level. Minimum is 2 - if less than 2, it is set to 2
            by default.
        sort_keys : bool, default: False
            Whether to sort the keys alphabetically.
        return_list : bool, default: False
            Whether to return a list of strings or print out
            the tree structure.
        skip_loc_header : bool, default: False
            Whether to skip the location header. Mostly for internal use.

        Returns
        -------
        None | list[str]
            Tree-style printed component or list of strings representing the component tree.
        """

        def build_parent_tree(comp: Component, parent_tree: str = "") -> str:
            """Private function to build the parent tree of a component."""
            if comp.parent_component is None:
                # We reached the top level component... return the parent tree
                return "Root component (Design)" if not parent_tree else parent_tree
            else:
                if parent_tree == "":
                    # Should only happen in the first call
                    parent_tree = comp.name

                # Add the parent component to the parent tree and continue
                return build_parent_tree(
                    comp.parent_component, f"{comp.parent_component.name} > {parent_tree}"
                )

        # Indentation should be at least 2
        indent = max(2, indent)

        # Initialize the lines list
        lines: list[str] = []

        # Add the location header if requested - and only on the first call
        # (subsequent calls will have the skip_loc_header set to True)
        if not skip_loc_header:
            lines.append(f">>> Tree print view of component '{self.name}'")
            lines.append("")
            lines.append("Location")
            lines.append(f"{'-' * len(lines[-1])}")
            lines.append(f"{build_parent_tree(self)}")
            lines.append("")
            lines.append("Subtree")
            lines.append(f"{'-' * len(lines[-1])}")

        lines.append(f"(comp) {self.name}")
        # Print the bodies
        if consider_bodies:
            # Check if the bodies should be sorted
            if sort_keys:
                body_names = [body.name for body in sorted(self.bodies, key=lambda body: body.name)]
            else:
                body_names = [body.name for body in self.bodies]

            # Add the bodies to the lines (with indentation)
            lines.extend([f"|{'-' * (indent-1)}(body) {name}" for name in body_names])

        # Print the beams
        if consider_beams:
            # Check if the bodies should be sorted
            if sort_keys:
                # TODO: Beams should also have names...
                # https://github.com/ansys/pyansys-geometry/issues/1319
                beam_names = [
                    beam.id
                    for beam in sorted(self.beams, key=lambda beam: beam.id)
                    if beam.is_alive
                ]
            else:
                beam_names = [beam.id for beam in self.beams if beam.is_alive]

            # Add the bodies to the lines (with indentation)
            lines.extend([f"|{'-' * (indent-1)}(beam) {name}" for name in beam_names])

        # Print the nested components
        if consider_comps:
            # Check if the components should be sorted
            comps = (
                self.components
                if not sort_keys
                else sorted(self.components, key=lambda comp: comp.name)
            )
            comps = [comp for comp in comps if comp.is_alive]

            # Add the components to the lines (recursive)
            if depth is None or depth > 1:
                n_comps = len(comps)
                for idx, comp in enumerate(comps):
                    subcomp = comp.tree_print(
                        consider_comps=consider_comps,
                        consider_bodies=consider_bodies,
                        consider_beams=consider_beams,
                        depth=None if depth is None else depth - 1,
                        indent=indent,
                        sort_keys=sort_keys,
                        return_list=True,
                        skip_loc_header=True,
                    )

                    # Add indentation to the subcomponent lines
                    lines.append(f"|{'-' * (indent-1)}(comp) {comp.name}")

                    # Determine the prefix for the subcomponent lines and add them
                    prefix = f"{' ' * indent}" if idx == (n_comps - 1) else f":{' ' * (indent-1)}"
                    lines.extend([f"{prefix}{line}" for line in subcomp[1:]])

            else:
                lines.extend([f"|{'-' * (indent-1)}(comp) {comp.name}" for comp in comps])

        return lines if return_list else print("\n".join(lines))
