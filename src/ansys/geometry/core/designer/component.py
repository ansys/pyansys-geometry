"""``Component`` class module."""


from io import UnsupportedOperation
from typing import Union

from ansys.api.geometry.v0.bodies_pb2 import CreateExtrudedBodyRequest
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
from ansys.geometry.core.misc import UNITS
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
        """Creates a new component nested under this component within the design assembly.

        Parameters
        ----------
        name : str
            A user-defined label assigned to the new component.
        """
        self._components.append(Component(name, self, self._grpc_client))

    def extrude_profile(self, name: str, sketch: Sketch, distance: Quantity) -> Body:
        """Creates a solid body by extruding the given profile up to the given distance.

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
        extrusion_request = CreateExtrudedBodyRequest(
            distance=distance.m_as(UNITS.m),
            parent=self.id,
            plane=plane_to_grpc_plane(sketch._plane),
            geometries=sketch_shapes_to_grpc_geometries(sketch.shapes_list),
            name=name,
        )

        extrusion_response = self._bodies_stub.CreateExtrudedBody(extrusion_request)

        self._bodies.append(Body(extrusion_response.id, name, self, self._grpc_client))
        return self._bodies[-1]
