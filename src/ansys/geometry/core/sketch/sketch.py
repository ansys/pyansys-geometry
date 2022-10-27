"""``Sketch`` class module."""

from beartype import beartype as check_input_types
from beartype.typing import Dict, List, Optional, Union
from pint import Quantity

from ansys.geometry.core.math import ZERO_POINT2D, Plane, Point2D, UnitVector3D, Vector2D, Vector3D
from ansys.geometry.core.misc import UNIT_LENGTH, Angle, Distance
from ansys.geometry.core.sketch.arc import Arc
from ansys.geometry.core.sketch.box import Box
from ansys.geometry.core.sketch.circle import Circle
from ansys.geometry.core.sketch.edge import SketchEdge
from ansys.geometry.core.sketch.ellipse import Ellipse
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.polygon import Polygon
from ansys.geometry.core.sketch.segment import Segment
from ansys.geometry.core.sketch.slot import Slot
from ansys.geometry.core.sketch.trapezoid import Trapezoid
from ansys.geometry.core.sketch.triangle import Triangle
from ansys.geometry.core.typing import Real

SketchObject = Union[SketchEdge, SketchFace]
"""Type used to refer to both SketchEdge and SketchFace as possible values."""


class Sketch:
    """
    Provides Sketch class for building 2D sketch elements.
    """

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
        """Constructor method for ``Sketch``."""
        self._plane = plane

        self._faces = []
        self._edges = []
        self._current_sketch_context = []

        # data structure to track tagging individual
        # sketch objects and collections of sketch objects
        self._tags = {}

    @property
    def plane(self) -> Plane:
        """
        Returns sketch plane configuration.

        Returns
        -------
        Plane
            The plane containing the sketch.
        """

        return self._plane

    @plane.setter
    @check_input_types
    def plane(self, plane: Plane) -> None:
        """
        Sets the sketch plane configuration.

        Parameters
        ----------
        plane : Plane
            The updated sketch planar orientation.
        """
        self._plane = plane

    @property
    def edges(self) -> List[SketchEdge]:
        """
        Returns all independently sketched edges.

        Returns
        -------
        List[SketchEdge]
            Sketched edges that are not assigned to a face.
        """

        return self._edges

    @property
    def faces(self) -> List[SketchFace]:
        """
        Returns all independently sketched faces.

        Returns
        -------
        List[Sketchface]
            list of sketched faces.
        """

        return self._faces

    @check_input_types
    def translate_sketch_plane(self, translation: Vector3D) -> "Sketch":
        """
        Convenience method to translate the active sketch plane origin location.

        Parameters
        ----------
        translation : Vector3D
            The vector defining the translation, expecting values in meters.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.
        """
        self.plane = Plane(
            self.plane.origin + translation, self.plane.direction_x, self.plane.direction_y
        )
        return self

    @check_input_types
    def translate_sketch_plane_by_offset(
        self,
        x: Union[Quantity, Distance] = Quantity(0, UNIT_LENGTH),
        y: Union[Quantity, Distance] = Quantity(0, UNIT_LENGTH),
        z: Union[Quantity, Distance] = Quantity(0, UNIT_LENGTH),
    ) -> "Sketch":
        """
        Convenience method to translate the active sketch plane origin location.

        Parameters
        ----------
        x : Union[Quantity, Distance], default: Quantity(0, UNIT_LENGTH)
            The amount to translate the origin the x-direction.
        y : Union[Quantity, Distance], default: Quantity(0, UNIT_LENGTH)
            The amount to translate the origin the y-direction.
        z : Union[Quantity, Distance], default: Quantity(0, UNIT_LENGTH)
            The amount to translate the origin the z-direction.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.
        """
        x_magnitude = (
            x.m_as(UNIT_LENGTH) if not isinstance(x, Distance) else x.value.m_as(UNIT_LENGTH)
        )

        y_magnitude = (
            y.m_as(UNIT_LENGTH) if not isinstance(y, Distance) else y.value.m_as(UNIT_LENGTH)
        )

        z_magnitude = (
            z.m_as(UNIT_LENGTH) if not isinstance(z, Distance) else z.value.m_as(UNIT_LENGTH)
        )
        translation = Vector3D([x_magnitude, y_magnitude, z_magnitude])
        return self.translate_sketch_plane(translation)

    @check_input_types
    def translate_sketch_plane_by_distance(
        self, direction: UnitVector3D, distance: Union[Quantity, Distance]
    ) -> "Sketch":
        """
        Convenience method to translate the active sketch plane origin location.

        Parameters
        ----------
        direction : UnitVector3D
            The direction the origin should be translated.
        distance : Union[Quantity, Distance]
            The distance to translate the origin.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.
        """
        magnitude = (
            distance.m_as(UNIT_LENGTH)
            if not isinstance(distance, Distance)
            else distance.value.m_as(UNIT_LENGTH)
        )
        translation = Vector3D(
            [direction.x * magnitude, direction.y * magnitude, direction.z * magnitude]
        )
        return self.translate_sketch_plane(translation)

    @check_input_types
    def get(self, tag: str) -> List[SketchObject]:
        """Returns the list of shapes that were tagged by the provided label.

        Parameters
        ----------
        tag : str
            The tag to query against.
        """
        return self._tags[tag]

    @check_input_types
    def face(self, face: SketchFace, tag: Optional[str] = None) -> "Sketch":
        """
        Add a SketchFace to the sketch.

        Parameters
        ----------
        face : SketchFace
            A face to add to the sketch.
        tag : str, optional
            A user-defined label identifying this specific face.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.
        """
        self._faces.append(face)
        if tag:
            self._tag([face], tag)

        return self

    @check_input_types
    def edge(self, edge: SketchEdge, tag: Optional[str] = None) -> "Sketch":
        """
        Add a SketchEdge to the sketch.

        Parameters
        ----------
        edge : SketchEdge
            A edge to add to the sketch.
        tag : str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.
        """
        self._edges.append(edge)
        if tag:
            self._tag([edge], tag)

        return self

    @check_input_types
    def select(self, *tags: str) -> "Sketch":
        """
        Add all objects to current context that match the provided tags.
        """

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
            Start of the line segment.
        end : Point2D
            End of the line segment.
        tag: str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.
        """
        segment = Segment(start, end)
        return self.edge(segment, tag)

    def segment_to_point(self, end: Point2D, tag: Optional[str] = None) -> "Sketch":
        """
        Add a segment to the sketch plane starting from previous edge end point.

        Parameters
        ----------
        end : Point2D
            End of the line segment.
        tag : str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.

        Notes
        -----
        The starting point of the created edge is based upon the current context
        of the sketch, such as the end point of a previously added edge.
        """
        segment = Segment(self._single_point_context_reference(), end)
        return self.edge(segment, tag)

    @check_input_types
    def segment_from_point_and_vector(
        self, start: Point2D, vector: Vector2D, tag: Optional[str] = None
    ):
        """
        Add a segment to the sketch starting from a provided starting point.

        Parameters
        ----------
        start : Point2D
            Start of the line segment.
        vector : Vector2D
            Vector defining the line segment. Vector magnitude determines segment endpoint.
            Vector magnitude assumed to be in the same unit as the starting point.
        tag : str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.

        Notes
        -----
        Vector magnitude determines segment endpoint.
        Vector magnitude assumed to use the same unit as the starting point.
        """
        end_vec_as_point = Point2D(vector, start.unit)
        end = start + end_vec_as_point

        return self.segment(start, end, tag)

    @check_input_types
    def segment_from_vector(self, vector: Vector2D, tag: Optional[str] = None):
        """
        Add a segment to the sketch starting from previous edge end point.

        Parameters
        ----------
        vector : Vector2D
            Vector defining the line segment.
        tag: str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.

        Notes
        -----
        The starting point of the created edge is based upon the current context
        of the sketch, such as the end point of a previously added edge.

        Vector magnitude determines segment endpoint.
        Vector magnitude assumed to use the same unit as the starting point in the previous context.
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
        Add an arc object to the sketch plane.

        Parameters
        ----------
        start : Point2D
            Start of the arc.
        end : Point2D
            End of the arc.
        center : Point2D
            Center of the arc.
        clockwise : bool, optional
            By default the arc spans the counter-clockwise angle between
            ``start`` and ``end``. By setting this to ``True``, the clockwise
            angle is used instead.
        tag: str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.
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
        Add an arc to the sketch starting from previous edge end point.

        Parameters
        ----------
        end : Point2D
            End of the arc.
        center : Point2D
            Center of the arc.
        clockwise : bool, optional
            By default the arc spans the counter-clockwise angle between
            ``start`` and ``end``. By setting this to ``True``, the clockwise
            angle is used instead.
        tag: str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.

        Notes
        -----
        The starting point of the created edge is based upon the current context
        of the sketch, such as the end point of a previously added edge.
        """
        start = self._single_point_context_reference()
        arc = Arc(center, start, end, clockwise)
        return self.edge(arc, tag)

    def triangle(
        self,
        point1: Point2D,
        point2: Point2D,
        point3: Point2D,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """
        Add a triangle to the using the explicit vertex points provided.

        Parameters
        ----------
        point1: Point2D
            A :class:`Point2D` representing the a triangle vertex.
        point2: Point2D
            A :class:`Point2D` representing the a triangle vertex.
        point3: Point2D
            A :class:`Point2D` representing the a triangle vertex.
        tag: str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.
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
        Add a triangle to the using the explicit vertex points provided.

        Parameters
        ----------
        width : Union[Quantity, Distance, Real]
            The width of the slot main body.
        height : Union[Quantity, Distance, Real]
            The height of the slot.
        slant_angle : Union[Quantity, Angle, Real]
            The angle for trapezoid generation.
        nonsymmetrical_slant_angle : Optional[Union[Quantity, Angle, Real]]
            Enables asymmetrical slant angles on each side of the trapezoid.
            If not defined, the trapezoid will be symmetrical.
        center: Optional[Point2D]
            A :class:`Point2D` representing the center of the trapezoid.
            Defaults to (0, 0)
        angle : Optional[Union[Quantity, Angle, Real]]
            The placement angle for orientation alignment.
        tag: str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.
        """
        trapezoid = Trapezoid(width, height, slant_angle, nonsymmetrical_slant_angle, center, angle)
        return self.face(trapezoid, tag)

    def circle(
        self,
        center: Point2D,
        radius: Union[Quantity, Distance],
        tag: Optional[str] = None,
    ) -> "Sketch":
        """
        Add a circle to the plane at the provided center.

        Parameters
        ----------
        center: Point2D
            A :class:`Point2D` representing the center of the circle.
        radius : Union[Quantity, Distance]
            The radius of the circle.
        tag: str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.
        """
        circle = Circle(center, radius)
        return self.face(circle, tag)

    def box(
        self,
        center: Point2D,
        width: Union[Quantity, Distance, Real],
        height: Union[Quantity, Distance, Real],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """Create a box shape on the sketch.

        Parameters
        ----------
        center: Point2D
            A :class:`Point2D` representing the center of the box.
        width : Union[Quantity, Distance, Real]
            The width of the box.
        height : Union[Quantity, Distance, Real]
            The height of the box.
        angle : Optional[Union[Quantity, Real]]
            The placement angle for orientation alignment.
        tag : str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.
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
        """Create a slot shape on the sketch.

        Parameters
        ----------
        center: Point2D
            A :class:`Point2D` representing the center of the slot.
        width : Union[Quantity, Distance, Real]
            The width of the slot.
        height : Union[Quantity, Distance, Real]
            The height of the slot.
        angle : Optional[Union[Quantity, Angle, Real]]
            The placement angle for orientation alignment.
        tag : str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Slot
            An object representing the slot added to the sketch.
        """
        slot = Slot(center, width, height, angle)
        return self.face(slot, tag)

    def ellipse(
        self,
        center: Point2D,
        semi_major_axis: Union[Quantity, Distance],
        semi_minor_axis: Union[Quantity, Distance],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """Create an ellipse shape on the sketch.

        Parameters
        ----------
        center: Point2D
            A :class:`Point2D` representing the center of the ellipse.
        semi_major_axis : Union[Quantity, Distance]
            The semi-major axis of the ellipse.
        semi_minor_axis : Union[Quantity, Distance]
            The semi-minor axis of the ellipse.
        angle : Optional[Union[Quantity, Angle, Real]]
            The placement angle for orientation alignment.
        tag : str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Ellipse
            An object representing the ellipse added to the sketch.

        """
        ellipse = Ellipse(center, semi_major_axis, semi_minor_axis, angle)
        return self.face(ellipse, tag)

    def polygon(
        self,
        center: Point2D,
        inner_radius: Union[Quantity, Distance],
        sides: int,
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
        tag: Optional[str] = None,
    ) -> "Sketch":
        """Create a polygon shape on the sketch.

        Parameters
        ----------
        center: Point2D
            A :class:`Point2D` representing the center of the polygon.
        inner_radius : Union[Quantity, Distance]
            The inradius(apothem) of the polygon.
        sides : int
            Number of sides of the polygon.
        angle : Optional[Union[Quantity, Angle, Real]]
            The placement angle for orientation alignment.
        tag : str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Polygon
            An object for modelling polygonal shapes.

        """
        polygon = Polygon(center, inner_radius, sides, angle)
        return self.face(polygon, tag)

    @check_input_types
    def tag(self, tag: str) -> None:
        """
        Adds a tag for the active selection of sketch objects.

        Parameters
        ----------
        tag : str
            The tag to assign against the sketch objects.
        """
        self._tags[tag] = self._current_sketch_context

    def _single_point_context_reference(self) -> Point2D:
        """
        Gets the last reference point from historical context.

        Notes
        -----
        If no single point context available, ``ZERO_POINT2D`` returned by default.
        """
        if not self._edges or len(self._edges) == 0:
            return ZERO_POINT2D

        return self._edges[-1].end

    def _tag(self, sketch_collection: List[SketchObject], tag: str) -> None:
        """
        Adds a tag for a collection of sketch objects.

        Parameters
        ----------
        sketch_collection : List[SketchObject]
            The sketch objects to tag.
        tag : str
            The tag to assign against the sketch objects.
        """
        self._tags[tag] = sketch_collection

    def plot(
        self,
        **kwargs: Optional[dict],
    ):
        """Plot all objects of the sketch to the scene.

        Parameters
        ----------
        **kwargs : dict, optional
            Optional keyword arguments. See :func:`pyvista.Plotter.add_mesh`
            for allowable keyword arguments.

        """
        from ansys.geometry.core.plotting.plotter import Plotter

        pl = Plotter()
        pl.add_polydata(self.sketch_polydata(), **kwargs)
        pl.show()

    def plot_selection(
        self,
        **kwargs: Optional[dict],
    ):
        """Plot the current selection to the scene.

        Parameters
        ----------
        **kwargs : dict, optional
            Optional keyword arguments. See :func:`pyvista.Plotter.add_mesh`
            for allowable keyword arguments.

        """
        from ansys.geometry.core.plotting.plotter import Plotter

        sketches_polydata = []
        pl = Plotter()

        sketches_polydata.extend(
            [
                sketch_item.visualization_polydata.transform(self._plane.transformation_matrix)
                for sketch_item in self._current_sketch_context
            ]
        )

        pl.add_polydata(sketches_polydata, **kwargs)
        pl.show()

    def sketch_polydata(self):
        """
        Returns PolyData configuration for all
        objects of the sketch to the scene.
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
