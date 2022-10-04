"""``Body`` class module."""

from typing import TYPE_CHECKING, List, Optional, Tuple, Union

from ansys.api.geometry.v0.bodies_pb2 import (
    BodyIdentifier,
    SetAssignedMaterialRequest,
    TranslateRequest,
)
from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub
from ansys.api.geometry.v0.commands_pb2 import ImprintCurvesRequest, ProjectCurvesRequest
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from pint import Quantity

from ansys.geometry.core.connection import (
    GrpcClient,
    sketch_shapes_to_grpc_geometries,
    tess_to_pd,
    unit_vector_to_grpc_direction,
)
from ansys.geometry.core.designer.edge import CurveType, Edge
from ansys.geometry.core.designer.face import Face, SurfaceType
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.materials import Material
from ansys.geometry.core.math import UnitVector
from ansys.geometry.core.misc import (
    SERVER_UNIT_LENGTH,
    SERVER_UNIT_VOLUME,
    Distance,
    check_pint_unit_compatibility,
    check_type,
)
from ansys.geometry.core.sketch import Sketch

if TYPE_CHECKING:
    from pyvista import MultiBlock, PolyData  # pragma: no cover

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
    def _grpc_id(self) -> BodyIdentifier:
        """gRPC body identifier of this body."""
        return BodyIdentifier(id=self._id)

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
    @protect_grpc
    def faces(self) -> List[Face]:
        """Loads all of the faces within the body.

        Returns
        -------
        List[Face]
        """
        self._grpc_client.log.debug(f"Retrieving faces for body {self.id} from server.")
        grpc_faces = self._bodies_stub.GetFaces(self._grpc_id)
        return [
            Face(grpc_face.id, SurfaceType(grpc_face.surface_type), self, self._grpc_client)
            for grpc_face in grpc_faces.faces
        ]

    @property
    @protect_grpc
    def edges(self) -> List[Edge]:
        """Loads all of the edges within the body.

        Returns
        -------
        List[Edge]
        """
        self._grpc_client.log.debug(f"Retrieving edges for body {self.id} from server.")
        grpc_edges = self._bodies_stub.GetEdges(self._grpc_id)
        return [
            Edge(grpc_edge.id, CurveType(grpc_edge.curve_type), self, self._grpc_client)
            for grpc_edge in grpc_edges.edges
        ]

    @property
    def is_alive(self) -> bool:
        """Boolean indicating whether the body is still alive on the server side."""
        return self._is_alive

    @property
    @protect_grpc
    def volume(self) -> Quantity:
        """Calculated volume of the body.

        Notes
        -----
        When dealing with a planar surface, a value of 0 is returned as a volume.
        """
        if self.is_surface:
            self._grpc_client.log.debug("Dealing with planar surface. Returning 0 volume.")
            return Quantity(0, SERVER_UNIT_VOLUME)
        else:
            self._grpc_client.log.debug(f"Retrieving volume for body {self.id} from server.")
            volume_response = self._bodies_stub.GetVolume(self._grpc_id)
            return Quantity(volume_response.volume, SERVER_UNIT_VOLUME)

    @protect_grpc
    def assign_material(self, material: Material) -> None:
        """Sets the provided material against the design in the active geometry
        service instance.

        Parameters
        ----------
        material : Material
            Source material data.
        """
        check_type(material, Material)
        self._grpc_client.log.debug(f"Assigning body {self.id} material {material.name}.")
        self._bodies_stub.SetAssignedMaterial(
            SetAssignedMaterialRequest(id=self._id, material=material.name)
        )

    @protect_grpc
    def imprint_curves(self, faces: List[Face], sketch: Sketch) -> Tuple[List[Edge], List[Face]]:
        """Imprints all of the specified geometries onto the specified faces of the body.

        Parameters
        ----------
        faces: List[Face]
            Specific faces to imprint the curves of the sketch.
        sketch: Sketch
            All of the curves to imprint on the faces.

        Returns
        -------
        Tuple[List[Edge], List[Face]]
            All of the impacted edges and faces from the imprint operation.
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

        self._grpc_client.log.debug(
            f"Imprinting curves provided on {self.id} "
            + f"for faces {[face.id for face in faces]}."
        )
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

        new_faces = [
            Face(grpc_face.id, grpc_face.surface_type, self, self._grpc_client)
            for grpc_face in imprint_response.faces
        ]

        return (new_edges, new_faces)

    @protect_grpc
    def project_curves(
        self,
        direction: UnitVector,
        sketch: Sketch,
        closest_face: bool,
        only_one_curve: Optional[bool] = False,
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
        only_one_curve: bool, optional
            Projects only one curve of the entire sketch provided. If ``True``, then
            the first curve is projected. By default, ``False``.

        Notes
        -----
        The ``only_one_curve`` boolean allows to optimize the server call, since
        projecting curves is an expensive operation. This reduces the workload on the
        server side.

        Returns
        -------
        List[Face]
            All of the faces from the project curves operation.
        """
        # Sanity checks
        check_type(direction, UnitVector)
        check_type(sketch, Sketch)
        check_type(closest_face, bool)

        self._grpc_client.log.debug(f"Projecting provided curves on {self.id}.")

        project_response = self._commands_stub.ProjectCurves(
            ProjectCurvesRequest(
                body=self._id,
                curves=sketch_shapes_to_grpc_geometries(
                    sketch.shapes_list if not only_one_curve else [sketch.shapes_list[0]]
                ),
                direction=unit_vector_to_grpc_direction(direction),
                closestFace=closest_face,
            )
        )

        projected_faces = [
            Face(grpc_face.id, grpc_face.surface_type, self, self._grpc_client)
            for grpc_face in project_response.faces
        ]

        return projected_faces

    @protect_grpc
    def translate(self, direction: UnitVector, distance: Union[Quantity, Distance]) -> None:
        """Translates the geometry body in the direction specified by the given distance.

        Parameters
        ----------
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

        self._grpc_client.log.debug(f"Translating body {self.id}.")

        self._bodies_stub.Translate(
            TranslateRequest(
                bodies=[self.id],
                direction=unit_vector_to_grpc_direction(direction),
                distance=magnitude,
            )
        )

    @protect_grpc
    def tessellate(self, merge: Optional[bool] = False) -> Union["PolyData", "MultiBlock"]:
        """Tessellate the body and return the geometry as triangles.

        Parameters
        ----------
        merge : bool, optional
            Merge the body into a single mesh. Enable this if you wish to
            merge the individual faces of the tessellation. This preserves
            the number of triangles and only merges the topology.
            By default, ``False``.

        Returns
        -------
        ~pyvista.PolyData, ~pyvista.MultiBlock
            Merged :class:`pyvista.PolyData` if ``merge=True`` or composite dataset.

        Examples
        --------
        Extrude a box centered at the origin to create a rectangular body and
        tessellate it.

        >>> from ansys.geometry.core.misc.units import UNITS as u
        >>> from ansys.geometry.core.sketch import Sketch
        >>> from ansys.geometry.core.math import Plane, Point, UnitVector
        >>> from ansys.geometry.core import Modeler
        >>> modeler = Modeler()
        >>> origin = Point([0, 0, 0])
        >>> plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 0, 1])
        >>> sketch = Sketch(plane)
        >>> box = sketch.draw_box(Point([2, 0, 2]), 4, 4)
        >>> design = modeler.create_design("my-design")
        >>> my_comp = design.add_component("my-comp")
        >>> body = my_comp.extrude_sketch("my-sketch", sketch, 1 * u.m)
        >>> blocks = body.tessellate()
        >>> blocks
        >>> MultiBlock (0x7f94ec757460)
             N Blocks:	6
             X Bounds:	0.000, 4.000
             Y Bounds:	-1.000, 0.000
             Z Bounds:	-0.500, 4.500

        Merge the body.

        >>> mesh = body.tessellate(merge=True)
        >>> mesh
        PolyData (0x7f94ec75f3a0)
          N Cells:	12
          N Points:	24
          X Bounds:	0.000e+00, 4.000e+00
          Y Bounds:	-1.000e+00, 0.000e+00
          Z Bounds:	-5.000e-01, 4.500e+00
          N Arrays:	0


        """
        # lazy import here to improve initial module load time
        import pyvista as pv

        if not self.is_alive:
            return pv.PolyData() if merge else pv.MultiBlock()

        self._grpc_client.log.debug(f"Requesting tesseleation for body {self.id}.")

        resp = self._bodies_stub.GetBodyTessellation(self._grpc_id)

        pdata = [tess_to_pd(tess) for tess in resp.face_tessellation.values()]
        comp = pv.MultiBlock(pdata)
        if merge:
            ugrid = comp.combine()
            return pv.PolyData(ugrid.points, ugrid.cells, n_faces=ugrid.n_cells)
        return comp

    def plot(self, merge: Optional[bool] = False, **kwargs: Optional[dict]) -> None:
        """Plot the body.

        Parameters
        ----------
        merge : bool, optional
            Merge the body into a single mesh. Enable this if you wish to
            merge the individual faces of the tessellation. This preserves
            the number of triangles and only merges the topology.
            By default, ``False``.
        **kwargs : dict, optional
            Optional keyword arguments. See :func:`pyvista.Plotter.add_mesh`
            for allowable keyword arguments.

        Examples
        --------
        Extrude a box centered at the origin to create rectangular body and
        plot it.

        >>> from ansys.geometry.core.misc.units import UNITS as u
        >>> from ansys.geometry.core.sketch import Sketch
        >>> from ansys.geometry.core.math import Plane, Point, UnitVector
        >>> from ansys.geometry.core import Modeler
        >>> modeler = Modeler()
        >>> origin = Point([0, 0, 0])
        >>> plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 0, 1])
        >>> sketch = Sketch(plane)
        >>> box = sketch.draw_box(Point([2, 0, 2]), 4, 4)
        >>> design = modeler.create_design("my-design")
        >>> mycomp = design.add_component("my-comp")
        >>> body = mycomp.extrude_sketch("my-sketch", sketch, 1 * u.m)
        >>> body.plot()

        Plot the body and color each face individually.

        >>> body.plot(multi_colors=True)

        """
        # lazy import here to improve initial module load time
        from ansys.geometry.core.plotting import Plotter

        pl = Plotter()
        pl.add_body(self, merge=merge, **kwargs)
        pl.show()
