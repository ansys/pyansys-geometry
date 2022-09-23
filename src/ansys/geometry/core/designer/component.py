"""``Component`` class module."""


from typing import List, Union

from ansys.api.geometry.v0.bodies_pb2 import (
    CreateExtrudedBodyRequest,
    CreatePlanarBodyRequest,
    TranslateRequest,
)
from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub
from ansys.api.geometry.v0.components_pb2 import CreateComponentRequest
from ansys.api.geometry.v0.components_pb2_grpc import ComponentsStub
from pint import Quantity

from ansys.geometry.core.connection import (
    GrpcClient,
    plane_to_grpc_plane,
    sketch_shapes_to_grpc_geometries,
    unit_vector_to_grpc_direction,
)
from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.designer.coordinatesystem import CoordinateSystem
from ansys.geometry.core.math import Frame, UnitVector
from ansys.geometry.core.misc import (
    SERVER_UNIT_LENGTH,
    Distance,
    check_pint_unit_compatibility,
    check_type,
)
from ansys.geometry.core.sketch import Sketch


class Component:
    """
    Provides class for organizing design bodies.

    Synchronizes to a design within a supporting geometry service instance.

    Parameters
    ----------
    name : str
        A user-defined label for the component.
    parent_component : Component
        The parent component to nest the new component under within the design assembly.
    grpc_client : GrpcClient
        An active supporting geometry service instance for design modeling.
    """

    def __init__(
        self, name: str, parent_component: Union["Component", None], grpc_client: GrpcClient
    ):
        """Constructor method for ``Component``."""
        # Sanity checks
        check_type(grpc_client, GrpcClient)
        check_type(name, str)
        check_type(parent_component, (Component, type(None)))

        self._grpc_client = grpc_client
        self._component_stub = ComponentsStub(self._grpc_client.channel)
        self._bodies_stub = BodiesStub(self._grpc_client.channel)

        if parent_component:
            new_component = self._component_stub.CreateComponent(
                CreateComponentRequest(display_name=name, parent=parent_component.id)
            )
            self._id = new_component.component.id
            self._name = new_component.component.display_name
        else:
            self._name = name
            self._id = None

        self._components = []
        self._bodies = []
        self._coordinate_systems = []
        self._parent_component = parent_component

    @property
    def id(self) -> str:
        """Id of the ``Component``."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the ``Component``."""
        return self._name

    @property
    def components(self) -> List["Component"]:
        """``Component`` objects inside of the ``Component``."""
        return self._components

    @property
    def bodies(self) -> List[Body]:
        """``Body`` objects inside of the ``Component``."""
        return self._bodies

    @property
    def coordinate_systems(self) -> List[CoordinateSystem]:
        """``CoordinateSystem`` objects inside of the ``Component``."""
        return self._coordinate_systems

    @property
    def parent_component(self) -> Union["Component", None]:
        """Parent of the ``Component``."""
        return self._parent_component

    def add_component(self, name: str) -> "Component":
        """Creates a new component nested under this component within the design assembly.

        Parameters
        ----------
        name : str
            A user-defined label assigned to the new component.

        Returns
        -------
        Component
            A newly created component with no children in the design assembly.
        """
        self._components.append(Component(name, self, self._grpc_client))
        return self._components[-1]

    def extrude_sketch(self, name: str, sketch: Sketch, distance: Quantity) -> Body:
        """Creates a solid body by extruding the given sketch profile up to the given distance.

        The resulting body created is nested under this component within the design assembly.

        Parameters
        ----------
        name : str
            A user-defined label assigned to the resulting solid body.
        sketch : Sketch
            The two-dimensional sketch source for extrusion.
        distance : Quantity
            The distance to extrude the solid body.

        Returns
        -------
        Body
            Extruded ``Body`` object from the given ``Sketch``.
        """
        # Sanity checks on inputs
        check_type(name, str)
        check_type(sketch, Sketch)
        check_type(distance, Quantity)
        check_pint_unit_compatibility(distance, SERVER_UNIT_LENGTH)

        # Perform extrusion request
        request = CreateExtrudedBodyRequest(
            distance=distance.m_as(SERVER_UNIT_LENGTH),
            parent=self.id,
            plane=plane_to_grpc_plane(sketch._plane),
            geometries=sketch_shapes_to_grpc_geometries(sketch.shapes_list),
            name=name,
        )

        response = self._bodies_stub.CreateExtrudedBody(request)

        self._bodies.append(Body(response.id, name, self, self._grpc_client, is_surface=False))
        return self._bodies[-1]

    def create_surface(self, name: str, sketch: Sketch) -> Body:
        """Creates a surface body with the given sketch profile.

        The resulting body created is nested under this component within the design assembly.

        Parameters
        ----------
        name : str
            A user-defined label assigned to the resulting surface body.
        sketch : Sketch
            The two-dimensional sketch source for surface definition.

        Returns
        -------
        Body
            ``Body`` object (as a planar surface) from the given ``Sketch``.
        """
        # Sanity checks on inputs
        check_type(name, str)
        check_type(sketch, Sketch)

        # Perform planar body request
        request = CreatePlanarBodyRequest(
            parent=self._id,
            plane=plane_to_grpc_plane(sketch._plane),
            geometries=sketch_shapes_to_grpc_geometries(sketch.shapes_list),
            name=name,
        )
        response = self._bodies_stub.CreatePlanarBody(request)

        self._bodies.append(Body(response.id, name, self, self._grpc_client, is_surface=True))
        return self._bodies[-1]

    def create_coordinate_system(self, name: str, frame: Frame) -> CoordinateSystem:
        """Creates a coordinate system.

        The resulting coordinate system created is nested under this component
        within the design assembly.

        Parameters
        ----------
        name : str
            A user-defined label for the coordinate system.
        frame : Frame
            The frame defining the coordinate system bounds.

        Returns
        -------
        CoordinateSystem
            ``CoordinateSystem`` object.
        """
        # Sanity checks on inputs
        check_type(name, str)
        check_type(frame, Frame)

        self._coordinate_systems.append(CoordinateSystem(name, frame, self, self._grpc_client))
        return self._coordinate_systems[-1]

    def translate_bodies(
        self, bodies: List[Body], direction: UnitVector, distance: Union[Quantity, Distance]
    ) -> None:
        """Translates the geometry bodies in the direction specified by the given distance.

        Parameters
        ----------
        bodies: List[Body]
            A list of bodies to translate by the same distance.
        direction: UnitVector
            The direction of the translation.
        distance: Union[Quantity, Distance]
            The magnitude of the translation.

        Returns
        -------
        None
        """
        check_type(direction, UnitVector)
        check_type(distance, (Quantity, Distance))
        check_pint_unit_compatibility(distance, SERVER_UNIT_LENGTH)

        magnitude = (
            distance.m_as(SERVER_UNIT_LENGTH)
            if not isinstance(distance, Distance)
            else distance.value.m_as(SERVER_UNIT_LENGTH)
        )

        # TODO Wait for proto update so bodies is repeated string
        for body in bodies:
            translation_request = TranslateRequest(
                id=body.id,
                direction=unit_vector_to_grpc_direction(direction),
                distance=magnitude,
            )

            self._bodies_stub.Translate(translation_request)

        # TODO Consider what needs to be invalidated client-side after server-side modifications.
