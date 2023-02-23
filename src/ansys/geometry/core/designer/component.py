"""Provides the ``Component`` class module."""

from enum import Enum, unique
from threading import Thread

from ansys.api.geometry.v0.bodies_pb2 import (
    CreateBodyFromFaceRequest,
    CreateExtrudedBodyFromFaceProfileRequest,
    CreateExtrudedBodyRequest,
    CreatePlanarBodyRequest,
    TranslateRequest,
)
from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub
from ansys.api.geometry.v0.commands_pb2 import CreateBeamSegmentsRequest
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from ansys.api.geometry.v0.components_pb2 import CreateRequest, SetSharedTopologyRequest
from ansys.api.geometry.v0.components_pb2_grpc import ComponentsStub
from ansys.api.geometry.v0.models_pb2 import EntityIdentifier, Line
from beartype import beartype as check_input_types
from beartype.typing import TYPE_CHECKING, List, Optional, Tuple, Union
from pint import Quantity

from ansys.geometry.core.connection import (
    GrpcClient,
    plane_to_grpc_plane,
    sketch_shapes_to_grpc_geometries,
    unit_vector_to_grpc_direction,
)
from ansys.geometry.core.connection.conversions import point3d_to_grpc_point
from ansys.geometry.core.designer.beam import Beam, BeamProfile
from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.designer.coordinate_system import CoordinateSystem
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.math import Frame, Point3D, UnitVector3D
from ansys.geometry.core.misc import DEFAULT_UNITS, Distance, check_pint_unit_compatibility
from ansys.geometry.core.sketch import Sketch
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from pyvista import MultiBlock, PolyData


@unique
class SharedTopologyType(Enum):
    """Enum holding the possible values for component shared topologies by the Geometry service."""

    SHARETYPE_NONE = 0
    SHARETYPE_SHARE = 1
    SHARETYPE_MERGE = 2
    SHARETYPE_GROUPS = 3


class Component:
    """
    Provides the ``Component`` class for organizing design bodies.

    This class synchronizes to a design within a supporting Geometry service instance.

    Parameters
    ----------
    name : str
        User-defined label for the component.
    parent_component : Component
        Parent component to nest the new component under within the design assembly.
    grpc_client : GrpcClient
        Active supporting Geometry service instance for design modeling.
    """

    # Types of the class instance private attributes
    _components: List["Component"]
    _bodies: List[Body]
    _beams: List[Beam]
    _coordinate_systems: List[CoordinateSystem]

    @protect_grpc
    @check_input_types
    def __init__(self, name: str, parent_component: Optional["Component"], grpc_client: GrpcClient):
        """Constructor method for the ``Component`` class."""
        self._grpc_client = grpc_client
        self._component_stub = ComponentsStub(self._grpc_client.channel)
        self._bodies_stub = BodiesStub(self._grpc_client.channel)
        self._commands_stub = CommandsStub(self._grpc_client.channel)

        if parent_component:
            new_component = self._component_stub.Create(
                CreateRequest(name=name, parent=parent_component.id)
            )
            self._id = new_component.component.id
            self._name = new_component.component.name
        else:
            self._name = name
            self._id = None

        self._components = []
        self._bodies = []
        self._beams = []
        self._coordinate_systems = []
        self._parent_component = parent_component
        self._is_alive = True
        self._shared_topology = None

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
        """``Component`` objects inside of the component."""
        return self._components

    @property
    def bodies(self) -> List[Body]:
        """``Body`` objects inside of the component."""
        return self._bodies

    @property
    def beams(self) -> List[Beam]:
        """``Beam`` objects inside of the component."""
        return self._beams

    @property
    def coordinate_systems(self) -> List[CoordinateSystem]:
        """``CoordinateSystem`` objects inside of the component."""
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
        """Indicates the ``SharedTopologyType`` of the component (if any).

        Notes
        -----
        If no shared topology has been set, ``None`` is returned.
        """
        return self._shared_topology

    @protect_grpc
    def __fetch_sub_update_states(self, dict: dict[str, int]):
        """
        Recursively fetches the update state of every object from the server.

        Parameters
        ----------
        dict : dict[str, int]
            The dictionary that will hold the mapping between object id's and update states.
        """
        for body in self.bodies:
            dict[body.id] = body.get_update_state()
            for face in body.faces:
                dict[face.id] = face.get_update_state()
            for edge in body.edges:
                dict[edge.id] = edge.get_update_state()
        for component in self.components:
            component.__fetch_sub_update_states(dict)

    @check_input_types
    def add_component(self, name: str) -> "Component":
        """Add a new component nested under this component within the design assembly.

        Parameters
        ----------
        name : str
            User-defined label for the new component.

        Returns
        -------
        Component
            New component with no children in the design assembly.
        """
        self._components.append(Component(name, self, self._grpc_client))
        return self._components[-1]

    @protect_grpc
    @check_input_types
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
            SetSharedTopologyRequest(id=self.id, shareType=share_type.value)
        )

        # Store the SharedTopologyType set on the client
        self._shared_topology = share_type

    @protect_grpc
    @check_input_types
    def extrude_sketch(
        self, name: str, sketch: Sketch, distance: Union[Quantity, Distance, Real]
    ) -> Body:
        """Create a solid body by extruding the given sketch profile up to the given distance.

        The newly created body is nested under this component within the design assembly.

        Parameters
        ----------
        name : str
            User-defined label for the new solid body.
        sketch : Sketch
            Two-dimensional sketch source for the extrusion.
        distance : Union[Quantity, Distance, Real]
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

        self._bodies.append(Body(response.id, name, self, self._grpc_client, is_surface=False))
        return self._bodies[-1]

    @protect_grpc
    @check_input_types
    def extrude_face(self, name: str, face: Face, distance: Union[Quantity, Distance]) -> Body:
        """Extrude the face profile by a given distance to create a solid body.

        There are no modifications against the body containing the source face.

        Notes
        -----
        The source face can be anywhere within the design component hierarchy.
        Therefore, there is no validation requiring that the face is nested under the
        target component where the body is to be created.

        Parameters
        ----------
        name : str
            User-defined label for the new solid body.
        face : Face
            Target face to use as the source for the new surface.
        distance : Union[Quantity, Distance]
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

        self._bodies.append(Body(response.id, name, self, self._grpc_client, is_surface=False))
        return self._bodies[-1]

    @protect_grpc
    @check_input_types
    def create_surface(self, name: str, sketch: Sketch) -> Body:
        """Create a surface body with a sketch profile.

        The newly created body is nested under this component within the design assembly.

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
            parent=self._id,
            plane=plane_to_grpc_plane(sketch._plane),
            geometries=sketch_shapes_to_grpc_geometries(sketch._plane, sketch.edges, sketch.faces),
            name=name,
        )

        self._grpc_client.log.debug(
            f"Creating planar surface from sketch provided on {self.id}. Creating body..."
        )
        response = self._bodies_stub.CreatePlanarBody(request)

        self._bodies.append(Body(response.id, name, self, self._grpc_client, is_surface=True))
        return self._bodies[-1]

    @protect_grpc
    @check_input_types
    def create_surface_from_face(self, name: str, face: Face) -> Body:
        """Create a surface body based on a face.

        Notes
        -----
        The source face can be anywhere within the design component hierarchy.
        Therefore, there is no validation requiring that the face is nested under the
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

        self._bodies.append(Body(response.id, name, self, self._grpc_client, is_surface=True))
        return self._bodies[-1]

    @check_input_types
    def create_coordinate_system(self, name: str, frame: Frame) -> CoordinateSystem:
        """Create a coordinate system.

        The newly created coordinate system is nested under this component
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
            ``CoordinateSystem`` object.
        """
        self._coordinate_systems.append(CoordinateSystem(name, frame, self, self._grpc_client))
        return self._coordinate_systems[-1]

    @protect_grpc
    def get_update_state(self) -> int:
        """Gets the update state version number of the component from the server."""
        response = self._component_stub.GetUpdateState(EntityIdentifier(id=self.id))
        return response.state

    @protect_grpc
    @check_input_types
    def translate_bodies(
        self, bodies: List[Body], direction: UnitVector3D, distance: Union[Quantity, Distance, Real]
    ) -> None:
        """Translate the geometry bodies in a specified direction by a given distance.

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
        distance: Union[Quantity, Distance, Real]
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
                    f"Body with id {body.id} and name {body.name} is not found in this "
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
    def create_beams(
        self, segments: List[Tuple[Point3D, Point3D]], profile: BeamProfile
    ) -> List[Beam]:
        """
        Create beams under the component.

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
    def delete_component(self, component: Union["Component", str]) -> None:
        """Delete a component (itself or its children).

        Notes
        -----
        If the component is not this component (or its children), it
        is not deleted.

        Parameters
        ----------
        id : Union[Component, str]
            Name of the component or instance to delete.
        """
        id = component.id if not isinstance(component, str) else component
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
                f"Component {id} not found in this component (or sub-components)."
                + " Ignoring deletion request."
            )
            pass

    @protect_grpc
    @check_input_types
    def delete_body(self, body: Union[Body, str]) -> None:
        """Delete a body belonging to this component (or its children).

        Notes
        -----
        If the body does not belong to this component (or its children), it
        is not deleted.

        Parameters
        ----------
        id : Union[Body, str]
            Name of the body or instance to delete.
        """
        id = body.id if not isinstance(body, str) else body
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
           Component with the requested ID. If it is not found, ``None`` is returned.
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
        """Search bodies in component and nested components recursively for a body.

        Parameters
        ----------
        id : str
            ID of the body to search for.

        Returns
        -------
        Body
            Body with the requested ID. If it is not found, ``None`` is returned.
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

    def _kill_component_on_client(self) -> None:
        """Set the ``is_alive`` property of nested components and bodies to ``False``.

        Notes
        -----
        This method is recursive. It is only to be used by the
        ``delete_component()`` method and itself."""

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
            Whether to merge this component into a single dataset. If ``True``,
            all the individual bodies are effectively combined into a single
            dataset without any hierarchy.
        merge_bodies : bool, default: False
            Whether to merge each body into a single dataset. If ``True``,
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
        """Plot this component.

        Parameters
        ----------
        merge_component : bool, default: False
            Whether to merge this component into a single dataset. When ``True``,
            all the individual bodies are effectively merged into a single
            dataset without any hierarchy.
        merge_bodies : bool, default: False
            Whether to merge each body into a single dataset. When ``True``,
            all the faces of each individual body are effectively merged
            into a single dataset without separating faces.
        screenshot : str, optional
            Save a screenshot of the image being represented. The image is
            stored in the path provided as an argument.
        use_trame : bool, optional
            Enables/disables the usage of the trame web visualizer. Defaults to the
            global setting ``USE_TRAME``.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :func:`pyvista.Plotter.add_mesh` method.

        Examples
        --------
        Create 25 small cylinders in a grid-like pattern on the XY plane and
        plot them. Make the cylinders look metallic by enabling physically
        based rendering with ``pbr=True``.

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

        pl_helper = PlotterHelper(use_trame=use_trame)
        pl = pl_helper.init_plotter()
        pl.add_component(
            self, merge_bodies=merge_bodies, merge_component=merge_component, **plotting_options
        )
        pl_helper.show_plotter(pl, screenshot=screenshot)

    def __repr__(self) -> str:
        """String representation of the component."""
        alive_bodies = [1 if body.is_alive else 0 for body in self.bodies]
        alive_comps = [1 if comp.is_alive else 0 for comp in self.components]
        lines = [f"ansys.geometry.core.designer.Component {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Exists               : {self.is_alive}")
        lines.append(f"  Parent component     : {self.parent_component.name}")
        lines.append(f"  N Bodies             : {sum(alive_bodies)}")
        lines.append(f"  N Beams              : {len(self.beams)}")
        lines.append(f"  N Components         : {sum(alive_comps)}")
        lines.append(f"  N Coordinate Systems : {len(self.coordinate_systems)}")
        return "\n".join(lines)
