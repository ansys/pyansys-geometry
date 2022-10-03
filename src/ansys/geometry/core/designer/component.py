"""``Component`` class module."""

from enum import Enum, unique
from threading import Thread
from typing import TYPE_CHECKING, List, Optional, Union

from ansys.api.geometry.v0.bodies_pb2 import (
    BodyIdentifier,
    CreateBodyFromFaceRequest,
    CreateExtrudedBodyFromFaceProfileRequest,
    CreateExtrudedBodyRequest,
    CreatePlanarBodyRequest,
    TranslateRequest,
)
from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub
from ansys.api.geometry.v0.components_pb2 import (
    ComponentIdentifier,
    CreateComponentRequest,
    SetComponentSharedTopologyRequest,
)
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
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.math import Frame, UnitVector
from ansys.geometry.core.misc import (
    SERVER_UNIT_LENGTH,
    Distance,
    check_pint_unit_compatibility,
    check_type,
)
from ansys.geometry.core.sketch import Sketch

if TYPE_CHECKING:
    from pyvista import MultiBlock, PolyData  # pragma: no cover


@unique
class SharedTopologyType(Enum):
    """Enum holding the possible values for component shared topologies by the geometry service."""

    SHARETYPE_NONE = 0
    SHARETYPE_SHARE = 1
    SHARETYPE_MERGE = 2
    SHARETYPE_GROUPS = 3


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

    @protect_grpc
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
        self._is_alive = True
        self._shared_topology = None

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

    @property
    def is_alive(self) -> bool:
        """Boolean indicating whether the component is still alive on the server side."""
        return self._is_alive

    @property
    def shared_topology(self) -> Union[SharedTopologyType, None]:
        """Indicates the SharedTopology type of the component (if any).

        Notes
        -----
        If no shared topology has been set it will return ``None``.
        """
        return self._shared_topology

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

    @protect_grpc
    def set_shared_topology(self, share_type: SharedTopologyType) -> None:
        """Defines the shared topology to be applied to the component.

        Parameters
        ----------
        share_type : SharedTopologyType
            The shared topology type to be assigned to the component.
        """
        # Sanity checks on inputs
        check_type(share_type, SharedTopologyType)

        # Set the SharedTopologyType on the server
        self._component_stub.SetComponentSharedTopology(
            SetComponentSharedTopologyRequest(component=self.id, shareType=share_type.value)
        )

        # Store the SharedTopologyType set on the client
        self._shared_topology = share_type

    @protect_grpc
    def extrude_sketch(
        self, name: str, sketch: Sketch, distance: Union[Quantity, Distance]
    ) -> Body:
        """Creates a solid body by extruding the given sketch profile up to the given distance.

        The resulting body created is nested under this component within the design assembly.

        Parameters
        ----------
        name : str
            A user-defined label assigned to the resulting solid body.
        sketch : Sketch
            The two-dimensional sketch source for extrusion.
        distance : Union[Quantity, Distance]
            The distance to extrude the solid body.

        Returns
        -------
        Body
            Extruded ``Body`` object from the given ``Sketch``.
        """
        # Sanity checks on inputs
        check_type(name, str)
        check_type(sketch, Sketch)
        check_type(distance, (Quantity, Distance))
        extrude_distance = distance if isinstance(distance, Quantity) else distance.value
        check_pint_unit_compatibility(extrude_distance.units, SERVER_UNIT_LENGTH)

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

    @protect_grpc
    def extrude_face(self, name: str, face: Face, distance: Union[Quantity, Distance]) -> Body:
        """Extrudes the face profile by the given distance to create a new solid body.
        There are no modifications against the body containing the source face.

        Notes
        -----
        The source face can be anywhere within the design component hierarchy, and
        therefore there is no validation requiring the face is nested under the
        target component where the new body will be created.

        Parameters
        ----------
        name : str
            A user-defined label assigned to the resulting solid body.
        face : Face
            The target face to use as the source for the new surface.
        distance : Union[Quantity, Distance]
            The distance to extrude the solid body.

        Returns
        -------
        Body
            Extruded solid ``Body`` object.
        """
        # Sanity checks on inputs
        check_type(name, str)
        check_type(distance, (Quantity, Distance))
        extrude_distance = distance if isinstance(distance, Quantity) else distance.value
        check_pint_unit_compatibility(extrude_distance.units, SERVER_UNIT_LENGTH)

        # Take the face source directly. No need to verify the source of the face.
        request = CreateExtrudedBodyFromFaceProfileRequest(
            distance=distance.m_as(SERVER_UNIT_LENGTH),
            parent=self.id,
            face=face.id,
            name=name,
        )

        response = self._bodies_stub.CreateExtrudedBodyFromFaceProfile(request)

        self._bodies.append(Body(response.id, name, self, self._grpc_client, is_surface=False))
        return self._bodies[-1]

    @protect_grpc
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

    @protect_grpc
    def create_surface_from_face(self, name: str, face: Face) -> Body:
        """Creates a new surface body based upon the provided face.

        Notes
        -----
        The source face can be anywhere within the design component hierarchy, and
        therefore there is no validation requiring the face is nested under the
        target component where the new body will be created.

        Parameters
        ----------
        name : str
            A user-defined label assigned to the resulting surface body.
        face : Face
            The target face to use as the source for the new surface.

        Returns
        -------
        Body
            Surface ``Body`` object.
        """
        # Sanity checks on inputs
        check_type(name, str)

        # Take the face source directly. No need to verify the source of the face.
        request = CreateBodyFromFaceRequest(
            parent=self.id,
            face=face.id,
            name=name,
        )

        response = self._bodies_stub.CreateBodyFromFace(request)

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

    @protect_grpc
    def translate_bodies(
        self, bodies: List[Body], direction: UnitVector, distance: Union[Quantity, Distance]
    ) -> None:
        """Translates the geometry bodies in the direction specified by the given distance.

        Notes
        -----
        If the body does not belong to this component (or its children), it
        will not be translated.

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

        check_type(bodies, list)
        [check_type(body, Body) for body in bodies]
        check_type(direction, UnitVector)
        check_type(distance, (Quantity, Distance))
        check_pint_unit_compatibility(distance, SERVER_UNIT_LENGTH)
        body_ids_found = []

        for body in bodies:
            body_requested = self.search_body(body.id)
            if body_requested:
                body_ids_found.append(body_requested.id)
            else:
                self._grpc_client.log.warning(
                    f"Body with id {body.id} and name {body.name} not found in this "
                    + "component (or sub-components). Ignoring translation request."
                )
                pass

        magnitude = (
            distance.m_as(SERVER_UNIT_LENGTH)
            if not isinstance(distance, Distance)
            else distance.value.m_as(SERVER_UNIT_LENGTH)
        )

        self._bodies_stub.Translate(
            TranslateRequest(
                bodies=body_ids_found,
                direction=unit_vector_to_grpc_direction(direction),
                distance=magnitude,
            )
        )

    @protect_grpc
    def delete_component(self, component: Union["Component", str]) -> None:
        """Deletes an existing component (itself or its children).

        Notes
        -----
        If the component is not this component (or its children), it
        will not be deleted.

        Parameters
        ----------
        id : Union[Component, str]
            The name of the component or instance that should be deleted.
        """
        check_type(component, (Component, str))

        id = component.id if not isinstance(component, str) else component
        component_requested = self.search_component(id)

        if component_requested:
            # If the component belongs to this component (or nested components)
            # call the server deletion mechanism
            self._component_stub.DeleteComponent(ComponentIdentifier(id=id))

            # If the component was deleted from the server side... "kill" it
            # on the client side
            component_requested._kill_component_on_client()
        else:
            self._grpc_client.log.warning(
                f"Component {id} not found in this component (or sub-components)."
                + " Ignoring deletion request."
            )
            pass

    @protect_grpc
    def delete_body(self, body: Union[Body, str]) -> None:
        """Deletes an existing body belonging to this component (or its children).

        Notes
        -----
        If the body does not belong to this component (or its children), it
        will not be deleted.

        Parameters
        ----------
        id : Union[Body, str]
            The name of the body or instance that should be deleted.
        """
        check_type(body, (Body, str))

        id = body.id if not isinstance(body, str) else body
        body_requested = self.search_body(id)

        if body_requested:
            # If the body belongs to this component (or nested components)
            # call the server deletion mechanism
            self._bodies_stub.Delete(BodyIdentifier(id=id))

            # If the body was deleted from the server side... "kill" it
            # on the client side
            body_requested._is_alive = False
        else:
            self._grpc_client.log.warning(
                f"Body {id} not found in this component (or sub-components)."
                + " Ignoring deletion request."
            )
            pass

    def search_component(self, id: str) -> "Component":
        """Recursive search on available nested components.

        Parameters
        ----------
        id : str
            The ``Component`` ID we are searching for.

        Returns
        -------
        Component
            The ``Component`` with the requested ID. If not found, it will return ``None``.
        """

        # Sanity check on input
        check_type(id, str)

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

    def search_body(self, id: str) -> Body:
        """Recursive search on available bodies in component and nested components.

        Parameters
        ----------
        id : str
            The ``Body`` ID we are searching for.

        Returns
        -------
        Body
            The ``Body`` with the requested ID. If not found, it will return ``None``.
        """

        # Sanity check on input
        check_type(id, str)

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

    def _kill_component_on_client(self) -> None:
        """Sets the ``is_alive`` property of nested components and bodies to ``False``.

        Notes
        -----
        Only to be used by the ``delete_component`` method and itself (this method
        is recursive)."""

        # Kill all its bodies
        for body in self.bodies:
            body._is_alive = False

        # Now, go to the nested components and kill them as well
        for component in self.components:
            component._kill_component_on_client()

        # Kill itself
        self._is_alive = False

    def tessellate(
        self, merge_component: bool = False, merge_bodies: bool = False
    ) -> Union["PolyData", "MultiBlock"]:
        """Tessellate this component.

        Parameters
        ----------
        merge_component : bool, default: False
            Merge this component into a single dataset. This effectively
            combines all the individual bodies into a single dataset without
            any hierarchy.
        merge_bodies : bool, default: False
            Merge each body into a single dataset. This effectively combines
            all the faces of each individual body into a single dataset
            without separating faces.

        Returns
        -------
        ~pyvista.PolyData, ~pyvista.MultiBlock
            Merged :class:`pyvista.PolyData` if ``merge_component=True`` or
            composite dataset.

        Examples
        --------
        Create two stacked bodies and return the tessellation as two merged bodies.

        >>> from ansys.geometry.core.sketch import Sketch
        >>> from ansys.geometry.core import Modeler
        >>> from ansys.geometry.core.math import Point, Plane
        >>> from ansys.geometry.core.misc import UNITS
        >>> from ansys.geometry.core.plotting.plotter import Plotter
        >>> modeler = Modeler("10.54.0.72", "50051")
        >>> sketch_1 = Sketch()
        >>> box = sketch_1.draw_box(Point([10, 10, 0]), width=10, height=5)
        >>> circle = sketch_1.draw_circle(Point([0, 0, 0]), radius=25 * UNITS.m)
        >>> design = modeler.create_design("MyDesign")
        >>> comp = design.add_component("MyComponent")
        >>> body = comp.extrude_sketch("MyBody", sketch=sketch_1, distance=10 * UNITS.m)
        >>> sketch_2 = Sketch(Plane([0, 0, 10]))
        >>> box = sketch_2.draw_box(Point([10, 10, 10]), width=10, height=5)
        >>> circle = sketch_2.draw_circle(Point([0, 0, 10]), radius=25 * UNITS.m)
        >>> body = comp.extrude_sketch("MyBody", sketch=sketch_2, distance=10 * UNITS.m)
        >>> dataset = comp.tessellate(merge_bodies=True)
        >>> dataset
        MultiBlock (0x7ff6bcb511e0)
          N Blocks:     2
          X Bounds:     -25.000, 25.000
          Y Bounds:     -24.991, 24.991
          Z Bounds:     0.000, 20.000

        """
        import pyvista as pv

        datasets = []

        def get_tessellation(body: Body):
            datasets.append(body.tessellate(merge=merge_bodies))

        # Tessellate the bodies in this component
        threads = []
        for body in self.bodies:
            thread = Thread(target=get_tessellation, args=(body,))
            thread.start()
            threads.append(thread)
        [thread.join() for thread in threads]
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
            # convert to polydata as it's slightly faster than extract surface
            return pv.PolyData(ugrid.points, ugrid.cells, n_faces=ugrid.n_cells)
        return blocks

    def plot(
        self, merge_component: bool = False, merge_bodies: bool = False, **kwargs: Optional[dict]
    ) -> None:
        """Plot this component.

        Parameters
        ----------
        merge_component : bool, default: False
            Merge this component into a single dataset. This effectively
            combines all the individual bodies into a single dataset without
            any hierarchy.
        merge_bodies : bool, default: False
            Merge each body into a single dataset. This effectively combines
            all the faces of each individual body into a single dataset
            without.
        **kwargs : dict, optional
            Optional keyword arguments. See :func:`pyvista.Plotter.add_mesh`
            for allowable keyword arguments.

        Examples
        --------
        Create 25 small cylinders in a grid-like pattern on the XY plane and
        plot them. Make the cylinders look metallic by enabling physically
        based rendering with ``pbr=True``.

        >>> from ansys.geometry.core.misc.units import UNITS as u
        >>> from ansys.geometry.core.sketch import Sketch
        >>> from ansys.geometry.core.math import Plane, Point, UnitVector
        >>> from ansys.geometry.core import Modeler
        >>> import numpy as np
        >>> modeler = Modeler()
        >>> origin = Point([0, 0, 0])
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
        ...     sketch.draw_circle(Point([x, y, 0]), 0.2*u.m)
        ...     mycomp.extrude_sketch(f"body-{x}-{y}", sketch, 1 * u.m)
        >>> mycomp
        ansys.geometry.core.designer.Component 0x7f45c3396370
          Exists               : True
          N Bodies             : 25
          N Components         : 0
          N Coordinate Systems : 0
        >>> mycomp.plot(pbr=True, metallic=1.0)

        """
        from ansys.geometry.core.plotting import Plotter

        pl = Plotter()
        pl.add_component(self, merge_bodies=merge_bodies, merge_component=merge_component, **kwargs)
        pl.show()

    def __repr__(self) -> str:
        """Representation of the component."""
        lines = [f"ansys.geometry.core.designer.Component {hex(id(self))}"]
        lines.append(f"  Exists               : {self.is_alive}")
        lines.append(f"  N Bodies             : {len(self.bodies)}")
        lines.append(f"  N Components         : {len(self.components)}")
        lines.append(f"  N Coordinate Systems : {len(self.coordinate_systems)}")

        return "\n".join(lines)
