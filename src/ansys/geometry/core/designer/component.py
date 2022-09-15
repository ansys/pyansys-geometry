"""``Component`` class module."""


from io import UnsupportedOperation
from typing import Union

from ansys.api.geometry.v0.bodies_pb2 import CreateExtrudedBodyRequest
from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub
from ansys.api.geometry.v0.components_pb2 import CreateComponentRequest
from ansys.api.geometry.v0.components_pb2_grpc import ComponentsStub
from pint import Quantity

from ansys.geometry.core.connection import Conversions, GrpcClient
from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.sketch import Sketch


class Component:
    """
    Provides class for organizing design bodies.

    Synchronizes to a server.
    """

    def __init__(
        self, name: str, parent_component: Union["Component", None], grpc_client: GrpcClient
    ):
        """Constructor method for ``Component``."""
        self._grpc_client = grpc_client
        self._component_stub = ComponentsStub(self._grpc_client.channel)
        self._bodies_stub = BodiesStub(self._grpc_client.channel)

        if parent_component:
            new_component = self._component_stub.CreateComponent(
                CreateComponentRequest(display_name=name, parent=parent_component.id)
            )
            self._id = new_component.id
            self._name = new_component.name
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

    @id.setter
    def id(self, id: str) -> None:
        if self._parent_component is None:
            self._id = id
        else:
            raise UnsupportedOperation("Component id setter cannot be accessed.")

    @property
    def name(self) -> str:
        """Name of the ``Component``."""
        return self._name

    def add_component(self, name: str):
        self._components.append(Component(name, self, self._grpc_client))

    def extrude_profile(self, name: str, sketch: Sketch, distance: Quantity):
        extrusion_request = CreateExtrudedBodyRequest(
            distance=distance.m_as(UNITS.m),
            parent=self.id,
            plane=Conversions.plane_to_grpc_plane(sketch._plane),
            geometries=Conversions.sketch_shapes_to_grpc_geometries(sketch.shapes_list),
            name=name,
        )

        extrusion_response = self._bodies_stub.CreateExtrudedBody(extrusion_request)

        self._bodies.append(Body(extrusion_response.id, name, self))
