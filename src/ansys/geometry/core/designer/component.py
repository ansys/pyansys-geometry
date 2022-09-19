"""``Component`` class module."""


from typing import Union

from ansys.api.geometry.v0.bodies_pb2 import CreateExtrudedBodyRequest, CreatePlanarBodyRequest
from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub
from ansys.api.geometry.v0.components_pb2 import CreateComponentRequest
from ansys.api.geometry.v0.components_pb2_grpc import ComponentsStub
from pint import Quantity

from ansys.geometry.core.connection import (
    GrpcClient,
    plane_to_grpc_plane,
    sketch_shapes_to_grpc_geometries,
)
from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.misc import SERVER_UNIT_LENGTH, check_pint_unit_compatibility, check_type
from ansys.geometry.core.sketch import Sketch


class Component:
    """
    Provides class for organizing design bodies.

    Synchronizes to a design within a supporting geometry service instance.

    Parameters
    ----------
    name : str
        A user-defined label for the design.
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
        self._parent_component = parent_component

    @property
    def id(self) -> str:
        """Id of the ``Component``."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the ``Component``."""
        return self._name

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
        check_type(name, str)
        self._components.append(Component(name, self, self._grpc_client))
        return self._components[-1]

    def extrude_sketch(self, name: str, sketch: Sketch, distance: Quantity) -> "Body":
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
        """
        # Sanity checks on inputs
        check_type(name, str)
        check_type(sketch, Sketch)
        check_type(distance, Quantity)
        check_pint_unit_compatibility(distance, SERVER_UNIT_LENGTH)

        # Perform extrusion request
        extrusion_request = CreateExtrudedBodyRequest(
            distance=distance.m_as(SERVER_UNIT_LENGTH),
            parent=self._id,
            plane=plane_to_grpc_plane(sketch._plane),
            geometries=sketch_shapes_to_grpc_geometries(sketch.shapes_list),
            name=name,
        )

        extrusion_response = self._bodies_stub.CreateExtrudedBody(extrusion_request)

        self._bodies.append(Body(extrusion_response.id, name, self, self._grpc_client))
        return self._bodies[-1]

    def generate_surface(self, name: str, sketch: Sketch) -> "Body":
        """Creates a surface body with the given sketch profile.

        The resulting body created is nested under this component within the design assembly.

        Parameters
        ----------
        name : str
            A user-defined label assigned to the resulting surface body.
        sketch : Sketch
            The two-dimensional sketch source for surface definition.
        """
        # Sanity checks on inputs
        check_type(name, str)
        check_type(sketch, Sketch)

        # Perform planar body request
        planar_body_request = CreatePlanarBodyRequest(
            parent=self._id,
            plane=plane_to_grpc_plane(sketch._plane),
            geometries=sketch_shapes_to_grpc_geometries(sketch.shapes_list),
            name=name,
        )

        planar_body_response = self._bodies_stub.CreatePlanarBody(planar_body_request)

        self._bodies.append(Body(planar_body_response.id, name, self, self._grpc_client))
        return self._bodies[-1]
