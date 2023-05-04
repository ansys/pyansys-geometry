"""Provides the ``Sketch`` class."""

from beartype import beartype as check_input_types
from beartype.typing import TYPE_CHECKING, Dict, List, Optional, Union
from pint import Quantity

from ansys.geometry.core.math import ZERO_POINT2D, Plane, Point2D, UnitVector3D, Vector2D, Vector3D
from ansys.geometry.core.misc import DEFAULT_UNITS, Angle, Distance
from ansys.geometry.core.sketch.arc import Arc
from ansys.geometry.core.sketch.box import Box
from ansys.geometry.core.sketch.circle import SketchCircle
from ansys.geometry.core.sketch.edge import SketchEdge
from ansys.geometry.core.sketch.ellipse import SketchEllipse
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.gears import DummyGear, SpurGear
from ansys.geometry.core.sketch.polygon import Polygon
from ansys.geometry.core.sketch.segment import SketchSegment
from ansys.geometry.core.sketch.slot import Slot
from ansys.geometry.core.sketch.trapezoid import Trapezoid
from ansys.geometry.core.sketch.triangle import Triangle
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from pyvista import PolyData

SketchObject = Union[SketchEdge, SketchFace]
"""Type used to refer to both ``SketchEdge`` and ``SketchFace`` as possible values."""


class Sketch:
    """Provides for building 2D sketch elements."""

    # Types of the class instance private attributes
    _faces: List[SketchFace]
    _edges: List[SketchEdge]
    _current_sketch_context: List[SketchObject]
    _tags: Dict[str, List[SketchObject]]

    @check_input_types
    def __init__(
        self,
        plane: Optional[Plane] = Plane(),
    ):
        """Initialize ``Sketch`` class."""
        self._plane = plane

        self._faces = []
        self._edges = []
        self._current_sketch_context = []

        # data structure to track tagging individual
        # sketch objects and collections of sketch objects
        self._tags = {}

    @property
    def plane(self) -> Plane:
        """Sketch plane configuration."""
        return self._plane

    @property
    def edges(self) -> List[SketchEdge]:
        """
        List all independently sketched edges.

        Notes
        -----
        Those that are not assigned to a face. Face edges are not
        included in this list.
        """
        return self._edges

    @property
    def faces(self) -> List[SketchFace]:
        """List of all independently sketched faces."""
        return self._faces

    @plane.setter
    @check_input_types
    def plane(self, plane: Plane) -> None:
        """
        Set the sketch plane configuration.

        Parameters
        ----------
        plane : Plane
            New plane for the sketch planar orientation.
        """
        self._plane = plane
        [face.plane_change(plane) for face in self.faces]
        [edge.plane_change(plane) for edge in self.edges]

    @check_input_types
    def translate_sketch_plane(self, translation: Vector3D) -> "Sketch":
        """
        Translate the origin location of the active sketch plane.

        Parameters
        ----------
        translation : Vector3D
            Vector defining the translation. Meters is the expected unit.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        self.plane = Plane(
            self.plane.origin + translation, self.plane.direction_x, self.plane.direction_y
        )
        return self

    @check_input_types
    def translate_sketch_plane_by_offset(
        self,
        x: Union[Quantity, Distance] = Quantity(0, DEFAULT_UNITS.LENGTH),
        y: Union[Quantity, Distance] = Quantity(0, DEFAULT_UNITS.LENGTH),
        z: Union[Quantity, Distance] = Quantity(0, DEFAULT_UNITS.LENGTH),
    ) -> "Sketch":
        """
        Translate the origin location of the active sketch plane by offsets.

        Parameters
        ----------
        x : Union[Quantity, Distance], default: Quantity(0, DEFAULT_UNITS.LENGTH)
            Amount to translate the origin the x-direction.
        y : Union[Quantity, Distance], default: Quantity(0, DEFAULT_UNITS.LENGTH)
            Amount to translate the origin the y-direction.
        z : Union[Quantity, Distance], default: Quantity(0, DEFAULT_UNITS.LENGTH)
            Amount to translate the origin the z-direction.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        x_magnitude = (
            x.m_as(DEFAULT_UNITS.LENGTH)
            if not isinstance(x, Distance)
            else x.value.m_as(DEFAULT_UNITS.LENGTH)
        )

        y_magnitude = (
            y.m_as(DEFAULT_UNITS.LENGTH)
            if not isinstance(y, Distance)
            else y.value.m_as(DEFAULT_UNITS.LENGTH)
        )

        z_magnitude = (
            z.m_as(DEFAULT_UNITS.LENGTH)
            if not isinstance(z, Distance)
            else z.value.m_as(DEFAULT_UNITS.LENGTH)
        )
        translation = Vector3D([x_magnitude, y_magnitude, z_magnitude])
        return self.translate_sketch_plane(translation)

    @check_input_types
    def translate_sketch_plane_by_distance(
        self, direction: UnitVector3D, distance: Union[Quantity, Distance]
    ) -> "Sketch":
        """
        Translate the origin location active sketch plane by distance.

        Parameters
        ----------
        direction : UnitVector3D
            Direction to translate the origin.
        distance : Union[Quantity, Distance]
            Distance to translate the origin.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        magnitude = (
            distance.m_as(DEFAULT_UNITS.LENGTH)
            if not isinstance(distance, Distance)
            else distance.value.m_as(DEFAULT_UNITS.LENGTH)
        )
        translation = Vector3D(
            [direction.x * magnitude, direction.y * magnitude, direction.z * magnitude]
        )
        return self.translate_sketch_plane(translation)

    @check_input_types
    def get(self, tag: str) -> List[SketchObject]:
        """
        Get a list of shapes with a given tag.

        Parameters
        ----------
        tag : str
            Tag to query against.
        """
        return self._tags[tag]

    @check_input_types
    def face(self, face: SketchFace, tag: Optional[str] = None) -> "Sketch":
        """
        Add a sketch face to the sketch.

        Parameters
        ----------
        face : SketchFace
            Face to add.
        tag : str, default: None
            User-defined label for identifying this face.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        self._faces.append(face)
        if tag:
            self._tag([face], tag)

        return self

    @check_input_types
    def edge(self, edge: SketchEdge, tag: Optional[str] = None) -> "Sketch":
        """
        Add a sketch edge to the sketch.

        Parameters
        ----------
        edge : SketchEdge
            Edge to add.
        tag : str, default: None
            User-defined label for identifying this edge.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        self._edges.append(edge)
        if tag:
            self._tag([edge], tag)

        return self

    @check_input_types
    def select(self, *tags: str) -> "Sketch":
        """Add all objects to the current context that match provided tags."""
        self._current_sketch_context = []

        for tag in tags:
            self._current_sketch_context.extend(self._tags[tag])

        return self

    def segment(self, start: Point2D, end: Point2D, tag: Optional[str] = None) -> "Sketch":
        """
        Add a segment sketch object to the sketch plane.

        Parameters
        ----------
        start : Point2D
            Point that is the start of the line segment.
        end : Point2D
            Point that is the end of the line segment.
        tag : str, default: None
            User-defined label for identifying this edge.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        segment = SketchSegment(start, end)
        return self.edge(segment, tag)

    def segment_to_point(self, end: Point2D, tag: Optional[str] = None) -> "Sketch":
        """
        Add a segment to the sketch plane starting from the previous edge end point.

        Parameters
        ----------
        end : Point2D
            Point that is the end of the line segment.
        tag : str, default: None
            User-defined label for identifying this edge.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.

        Notes
        -----
        The starting point of the created edge is based upon the current context
        of the sketch, such as the end point of a previously added edge.
        """
        segment = SketchSegment(self._single_point_context_reference(), end)
        return self.edge(segment, tag)

    @check_input_types
    def segment_from_point_and_vector(
        self, start: Point2D, vector: Vector2D, tag: Optional[str] = None
    ):
        """
        Add a segment to the sketch starting from a given starting point.

        Parameters
        ----------
        start : Point2D
            Point that is the start of the line segment.
        vector : Vector2D
            Vector defining the line segment. Vector magnitude determines
            the segment endpoint. Vector magnitude is assumed to be in the
            same unit as the starting point.
        tag : str, default: None
            User-defined label for identifying this edge.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.

        Notes
        -----
        Vector magnitude determines the segment endpoint.
        Vector magnitude is assumed to use the same unit as the starting point.
        """
        end_vec_as_point = Point2D(vector, start.unit)
        end = start + end_vec_as_point

        return self.segment(start, end, tag)

    @check_input_types
    def segment_from_vector(self, vector: Vector2D, tag: Optional[str] = None):
        """
        Add a segment to the sketch starting from the end point of the previous edge.

        Parameters
        ----------
        vector : Vector2D
            Vector defining the line segment.
        tag : str, default: None
            User-defined label for identifying this edge.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.

        Notes
        -----
        The starting point of the created edge is based upon the current context
        of the sketch, such as the end point of a previously added edge.

        Vector magnitude determines the segment endpoint.
        Vector magnitude is assumed to use the same unit as the starting point
        in the previous context.
        """
        start = self._single_point_context_reference()
        return self.segment_from_point_and_vector(start, vector, tag)

    def arc(
        self,
        start: Point2D,
        end: Point2D,
        center: Point2D,
        clockwise: Optional[bool] = False,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """
        Add an arc to the sketch plane.

        Parameters
        ----------
        start : Point2D
            Point that is the start of the arc.
        end : Point2D
            Point that is the end of the arc.
        center : Point2D
            Point that is the center of the arc.
        clockwise : bool, default: False
            Whether the arc spans the angle clockwise between the start
            and end points. By default, the arc spans the angle
            counter-clockwise. When ``True``, the arc spans the angle
            clockwise.
        tag : str, default: None
            User-defined label for identifying this edge.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        arc = Arc(center, start, end, clockwise)
        return self.edge(arc, tag)

    @check_input_types
    def arc_to_point(
        self,
        end: Point2D,
        center: Point2D,
        clockwise: Optional[bool] = False,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """
        Add an arc to the sketch starting from the end point of the previous edge.

        Parameters
        ----------
        end : Point2D
            Point that is the end of the arc.
        center : Point2D
            Point that is the center of the arc.
        clockwise : bool, default: False
            Whether the arc spans the angle clockwise between the start
            and end points. By default, the arc spans the angle
            counter-clockwise. When ``True``, the arc spans the angle
            clockwise.
        tag : str, default: None
            User-defined label for identifying this edge.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.

        Notes
        -----
        The starting point of the created edge is based upon the current context
        of the sketch, such as the end point of a previously added edge.
        """
        start = self._single_point_context_reference()
        arc = Arc(center, start, end, clockwise)
        return self.edge(arc, tag)

    def arc_from_three_points(
        self,
        start: Point2D,
        inter: Point2D,
        end: Point2D,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """
        Add an arc to the sketch plane from three given points.

        Parameters
        ----------
        start : Point2D
            Point that is the start of the arc.
        inter : Point2D
            Point that is at an intermediate location of the arc.
        end : Point2D
            Point that is the end of the arc.
        tag : str, default: None
            User-defined label for identifying this edge.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        arc = Arc.from_three_points(start, inter, end)
        return self.edge(arc, tag)

    def triangle(
        self,
        point1: Point2D,
        point2: Point2D,
        point3: Point2D,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """
        Add a triangle to the sketch using given vertex points.

        Parameters
        ----------
        point1 : Point2D
            Point that represents a vertex of the triangle.
        point2 : Point2D
            Point that represents a vertex of the triangle.
        point3 : Point2D
            Point that represents a vertex of the triangle.
        tag : str, default: None
            User-defined label for identifying this face.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        triangle = Triangle(point1, point2, point3)
        return self.face(triangle, tag)

    def trapezoid(
        self,
        width: Union[Quantity, Distance, Real],
        height: Union[Quantity, Distance, Real],
        slant_angle: Union[Quantity, Angle, Real],
        nonsymmetrical_slant_angle: Optional[Union[Quantity, Angle, Real]] = None,
        center: Optional[Point2D] = ZERO_POINT2D,
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """
        Add a triangle to the sketch using given vertex points.

        Parameters
        ----------
        width : Union[Quantity, Distance, Real]
            Width of the slot main body.
        height : Union[Quantity, Distance, Real]
            Height of the slot.
        slant_angle : Union[Quantity, Angle, Real]
            Angle for trapezoid generation.
        nonsymmetrical_slant_angle : Union[Quantity, Angle, Real], default: None
            Asymmetrical slant angles on each side of the trapezoid.
            By default, the trapezoid is symmetrical.
        center : Point2D, default: (0, 0)
            Point that represents the center of the trapezoid.
        angle : Optional[Union[Quantity, Angle, Real]], default: 0
            Placement angle for orientation alignment.
        tag : str, default: None
            User-defined label for identifying this face.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        trapezoid = Trapezoid(width, height, slant_angle, nonsymmetrical_slant_angle, center, angle)
        return self.face(trapezoid, tag)

    def circle(
        self,
        center: Point2D,
        radius: Union[Quantity, Distance, Real],
        tag: Optional[str] = None,
    ) -> "Sketch":
        """
        Add a circle to the plane at a given center.

        Parameters
        ----------
        center: Point2D
            Point that represents the center of the circle.
        radius : Union[Quantity, Distance, Real]
            Radius of the circle.
        tag : str, default: None
            User-defined label for identifying this face.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        circle = SketchCircle(center, radius, plane=self.plane)
        return self.face(circle, tag)

    def box(
        self,
        center: Point2D,
        width: Union[Quantity, Distance, Real],
        height: Union[Quantity, Distance, Real],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """
        Create a box on the sketch.

        Parameters
        ----------
        center: Point2D
            Point that represents the center of the box.
        width : Union[Quantity, Distance, Real]
            Width of the box.
        height : Union[Quantity, Distance, Real]
            Height of the box.
        angle : Union[Quantity, Real], default: 0
            Placement angle for orientation alignment.
        tag : str, default: None
            User-defined label for identifying this face.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        box = Box(center, width, height, angle)
        return self.face(box, tag)

    def slot(
        self,
        center: Point2D,
        width: Union[Quantity, Distance, Real],
        height: Union[Quantity, Distance, Real],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """
        Create a slot on the sketch.

        Parameters
        ----------
        center: Point2D
            Point that represents the center of the slot.
        width : Union[Quantity, Distance, Real]
            Width of the slot.
        height : Union[Quantity, Distance, Real]
            Height of the slot.
        angle : Union[Quantity, Angle, Real], default: 0
            Placement angle for orientation alignment.
        tag : str, default: None
            User-defined label for identifying this face.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        slot = Slot(center, width, height, angle)
        return self.face(slot, tag)

    def ellipse(
        self,
        center: Point2D,
        major_radius: Union[Quantity, Distance, Real],
        minor_radius: Union[Quantity, Distance, Real],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """
        Create an ellipse on the sketch.

        Parameters
        ----------
        center: Point2D
            Point that represents the center of the ellipse.
        major_radius : Union[Quantity, Distance, Real]
            Semi-major axis of the ellipse.
        minor_radius : Union[Quantity, Distance, Real]
            Semi-minor axis of the ellipse.
        angle : Union[Quantity, Angle, Real], default: 0
            Placement angle for orientation alignment.
        tag : str, default: None
            User-defined label for identifying this face.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        ellipse = SketchEllipse(center, major_radius, minor_radius, angle)
        return self.face(ellipse, tag)

    def polygon(
        self,
        center: Point2D,
        inner_radius: Union[Quantity, Distance, Real],
        sides: int,
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """
        Create a polygon on the sketch.

        Parameters
        ----------
        center: Point2D
            Point that represents the center of the polygon.
        inner_radius : Union[Quantity, Distance, Real]
            Inner radius (apothem) of the polygon.
        sides : int
            Number of sides of the polygon.
        angle : Union[Quantity, Angle, Real], default: 0
            Placement angle for orientation alignment.
        tag : str, default: None
            User-defined label for identifying this face.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        polygon = Polygon(center, inner_radius, sides, angle)
        return self.face(polygon, tag)

    def dummy_gear(
        self,
        origin: Point2D,
        outer_radius: Union[Quantity, Distance, Real],
        inner_radius: Union[Quantity, Distance, Real],
        n_teeth: int,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """
        Create a dummy gear on the sketch.

        Parameters
        ----------
        origin : Point2D
            Origin of the gear.
        outer_radius : Union[Quantity, Distance, Real]
            Outer radius of the gear.
        inner_radius : Union[Quantity, Distance, Real]
            Inner radius of the gear.
        n_teeth : int
            Number of teeth of the gear.
        tag : str, default: None
            User-defined label for identifying this face.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        gear = DummyGear(origin, outer_radius, inner_radius, n_teeth)
        return self.face(gear, tag)

    def spur_gear(
        self,
        origin: Point2D,
        module: Real,
        pressure_angle: Union[Quantity, Angle, Real],
        n_teeth: int,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """
        Create a spur gear on the sketch.

        Parameters
        ----------
        origin : Point2D
            Origin of the spur gear.
        module : Real
            Module of the spur gear. This is also the ratio between the pitch circle
            diameter in millimeters and the number of teeth.
        pressure_angle : Union[Quantity, Angle, Real]
            Pressure angle of the spur gear.
        n_teeth : int
            Number of teeth of the spur gear.
        tag : str, default: None
            User-defined label for identifying this face.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        gear = SpurGear(origin, module, pressure_angle, n_teeth)
        return self.face(gear, tag)

    @check_input_types
    def tag(self, tag: str) -> None:
        """
        Add a tag to the active selection of sketch objects.

        Parameters
        ----------
        tag : str
            Tag to assign the sketch objects.
        """
        self._tags[tag] = self._current_sketch_context

    def _single_point_context_reference(self) -> Point2D:
        """
        Get the last reference point from historical context.

        Notes
        -----
        If no single point context is available, ``ZERO_POINT2D`` is returned by default.
        """
        if not self._edges or len(self._edges) == 0:
            return ZERO_POINT2D

        return self._edges[-1].end

    def _tag(self, sketch_collection: List[SketchObject], tag: str) -> None:
        """
        Add a tag for a collection of sketch objects.

        Parameters
        ----------
        sketch_collection : List[SketchObject]
            Sketch objects to tag.
        tag : str, default: None
            Tag to assign to these sketch objects.
        """
        self._tags[tag] = sketch_collection

    def plot(
        self,
        view_2d: Optional[bool] = False,
        screenshot: Optional[str] = None,
        use_trame: Optional[bool] = None,
        **plotting_options: Optional[dict],
    ):
        """
        Plot all objects of the sketch to the scene.

        Parameters
        ----------
        view_2d : bool, default: False
            Specifies whether the plot should be represented in a 2D format.
            By default, this is set to ``False``.
        screenshot : str, optional
            Save a screenshot of the image being represented. The image is
            stored in the path provided as an argument.
        use_trame : bool, optional
            Enables/disables the usage of the trame web visualizer. Defaults to the
            global setting ``USE_TRAME``.
        **plotting_options : dict, optional
            Keyword arguments. For allowable keyword arguments,
            see the :func:`pyvista.Plotter.add_mesh` method.
        """
        # Show the plot requested - i.e. all polydata in sketch
        self.__show_plotter(
            self.sketch_polydata(), view_2d, screenshot, use_trame, **plotting_options
        )

    def plot_selection(
        self,
        view_2d: Optional[bool] = False,
        screenshot: Optional[str] = None,
        use_trame: Optional[bool] = None,
        **plotting_options: Optional[dict],
    ):
        """
        Plot the current selection to the scene.

        Parameters
        ----------
        view_2d : bool, default: False
            Specifies whether the plot should be represented in a 2D format.
            By default, this is set to ``False``.
        screenshot : str, optional
            Save a screenshot of the image being represented. The image is
            stored in the path provided as an argument.
        use_trame : bool, optional
            Enables/disables the usage of the trame web visualizer. Defaults to the
            global setting ``USE_TRAME``.
        **plotting_options : dict, optional
            Keyword arguments. For allowable keyword arguments,
            see the :func:`pyvista.Plotter.add_mesh` method.
        """
        # Get the selected polydata
        sketches_polydata = []
        sketches_polydata.extend(
            [
                sketch_item.visualization_polydata.transform(self._plane.transformation_matrix)
                for sketch_item in self._current_sketch_context
            ]
        )

        # Show the plot requested
        self.__show_plotter(
            polydata=sketches_polydata,
            view_2d=view_2d,
            screenshot=screenshot,
            use_trame=use_trame,
            **plotting_options,
        )

    def sketch_polydata(self) -> List["PolyData"]:
        """
        Get polydata configuration for all objects of the sketch to the scene.

        Returns
        -------
        List[PolyData]
            Set of PolyData configuration for all edges and faces in the sketch.
        """
        sketches_polydata = []
        sketches_polydata.extend(
            [
                edge.visualization_polydata.transform(self._plane.transformation_matrix)
                for edge in self.edges
            ]
        )

        sketches_polydata.extend(
            [
                face.visualization_polydata.transform(self._plane.transformation_matrix)
                for face in self.faces
            ]
        )

        return sketches_polydata

    def __show_plotter(
        self,
        polydata: List["PolyData"],
        view_2d: bool,
        screenshot: Optional[str],
        use_trame: Optional[bool] = None,
        **plotting_options: Optional[dict],
    ) -> None:
        """
        Private method handling the ``show`` call of our Plotter.

        Parameters
        ----------
        polydata: List["PolyData"]
            Set of PolyData configuration for all edges and faces to be plotted.
        view_2d : bool
            Specifies whether the plot should be represented in a 2D format.
            By default, this is set to ``False``.
        screenshot : str, optional
            Save a screenshot of the image being represented. The image is
            stored in the path provided as an argument.
        use_trame : bool, optional
            Enables/disables the usage of the trame web visualizer. Defaults to the
            global setting ``USE_TRAME``.
        **plotting_options : dict, optional
            Keyword arguments. For allowable keyword arguments,
            see the :func:`pyvista.Plotter.add_mesh` method.
        """
        from ansys.geometry.core.plotting import PlotterHelper

        pl_helper = PlotterHelper(use_trame=use_trame)
        pl = pl_helper.init_plotter()
        # Add the polydata
        pl.add_sketch_polydata(polydata, **plotting_options)

        # If you want to visualize a Sketch from the top...
        if view_2d:
            pl.scene.view_vector(
                vector=self.plane.direction_z.tolist(),
                viewup=self.plane.direction_y.tolist(),
            )

        # Finally, show the plot
        pl_helper.show_plotter(pl, screenshot=screenshot)
