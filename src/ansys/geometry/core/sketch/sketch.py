"""``Sketch`` class module."""

from typing import Dict, List, Optional, Union

from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math import Plane, Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.math.constants import ZERO_POINT2D
from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.math.vector import Vector2D
from ansys.geometry.core.misc import Angle, Distance
from ansys.geometry.core.misc.measurements import UNIT_LENGTH
from ansys.geometry.core.shapes import (
    Arc,
    BaseShape,
    Box,
    Circle,
    Ellipse,
    Line,
    Polygon,
    Segment,
    Slot,
)
from ansys.geometry.core.sketch.arc import SketchArc
from ansys.geometry.core.sketch.circle import SketchCircle
from ansys.geometry.core.sketch.edge import SketchEdge
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.segment import SketchSegment
from ansys.geometry.core.sketch.trapezoid import Trapezoid
from ansys.geometry.core.sketch.triangle import Triangle
from ansys.geometry.core.typing import Real

SketchObject = Union[SketchEdge, SketchFace]


class Sketch:
    """
    Provides Sketch class for building 2D sketch elements.
    """

    _faces: List[SketchFace]
    _edges: List[SketchEdge]

    _current_sketch_context: List[SketchObject]

    _tags: Dict[str, List[SketchObject]]

    def __init__(
        self,
        plane: Optional[Plane] = Plane(),
    ):
        """Constructor method for ``Sketch``."""
        self._plane = plane
        self._shapes_list = []

        self._faces = []
        self._edges = []
        self._current_sketch_context = []

        # data structure to track tagging individual
        # sketch objects and collections of sketch objects
        self._tags = {}

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

    @property
    def shapes_list(self):
        """Returns the sketched curves."""
        return self._shapes_list

    def get(self, tag: str) -> List[SketchObject]:
        """Returns the list of shapes that were tagged by the provided label.

        Parameters
        ----------
        tag : str
            The tag to query against.
        """
        return self._tags[tag]

    def append_shape(self, shape: BaseShape):
        """Appends a new shape to the list of shapes in the sketch.

        Parameters
        ----------
        shape : BaseShape
            The shape to the added to the sketch.

        """
        if self._plane == shape.plane:
            self.shapes_list.append(shape)
        else:
            raise ValueError("The provided shape does not belong to the same plane as the Sketch.")

    def draw_box(
        self,
        center: Point3D,
        width: Union[Quantity, Distance, Real],
        height: Union[Quantity, Distance, Real],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Create a box shape on the sketch.

        Parameters
        ----------
        center: Point3D
            A :class:`Point3D` representing the center of the box.
        width : Union[Quantity, Distance, Real]
            The width of the box.
        height : Union[Quantity, Distance, Real]
            The height of the box.
        angle : Optional[Union[Quantity, Real]]
            The placement angle for orientation alignment.

        Returns
        -------
        Box
            An object representing the box added to the sketch.
        """
        box = Box(self._plane, center, width, height, angle)
        self.append_shape(box)
        return box

    def draw_slot(
        self,
        center: Point3D,
        width: Union[Quantity, Distance, Real],
        height: Union[Quantity, Distance, Real],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Create a slot shape on the sketch.

        Parameters
        ----------
        center: Point3D
            A :class:`Point3D` representing the center of the slot.
        width : Union[Quantity, Distance, Real]
            The width of the slot.
        height : Union[Quantity, Distance, Real]
            The height of the slot.
        angle : Optional[Union[Quantity, Angle, Real]]
            The placement angle for orientation alignment.

        Returns
        -------
        Slot
            An object representing the slot added to the sketch.
        """
        slot = Slot(self._plane, center, width, height, angle)
        self.append_shape(slot)
        return slot

    def draw_circle(self, center: Point3D, radius: Union[Quantity, Distance]):
        """Create a circle shape on the sketch.

        Parameters
        ----------
        center: Point3D
            A :class:`Point3D` representing the center of the circle.
        radius : Union[Quantity, Distance]
            The radius of the circle.

        Returns
        -------
        Circle
            An object representing the circle added to the sketch.

        """
        circle = Circle(self._plane, center, radius)
        self.append_shape(circle)
        return circle

    def draw_ellipse(
        self,
        center: Point3D,
        semi_major_axis: Union[Quantity, Distance],
        semi_minor_axis: Union[Quantity, Distance],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Create an ellipse shape on the sketch.

        Parameters
        ----------
        center: Point3D
            A :class:`Point3D` representing the center of the ellipse.
        semi_major_axis : Union[Quantity, Distance]
            The semi-major axis of the ellipse.
        semi_minor_axis : Union[Quantity, Distance]
            The semi-minor axis of the ellipse.
        angle : Optional[Union[Quantity, Angle, Real]]
            The placement angle for orientation alignment.

        Returns
        -------
        Ellipse
            An object representing the ellipse added to the sketch.

        """
        ellipse = Ellipse(self._plane, center, semi_major_axis, semi_minor_axis, angle)
        self.append_shape(ellipse)
        return ellipse

    def draw_segment(
        self,
        start: Point3D,
        end: Point3D,
    ) -> Segment:
        """
        Add a segment sketch object to the sketch plane.

        Parameters
        ----------
        start : Point3D
            Start of the line segment.
        end : Point3D
            End of the line segment.

        Returns
        -------
        Segment
            An object representing the segment added to the sketch.

        """
        segment = Segment(self._plane, start, end)
        self.append_shape(segment)
        return segment

    def draw_line(
        self,
        start: Point3D,
        direction: Union[Vector3D, UnitVector3D],
    ) -> Line:
        """
        Add a line sketch object to the sketch plane.

        Parameters
        ----------
        start : Point3D
            Origin/start of the line.
        direction: Union[Vector3D, UnitVector3D]
            Direction of the line.

        Returns
        -------
        Line
            An object representing the line added to the sketch.

        """
        line = Line(self._plane, start, direction)
        self.append_shape(line)
        return line

    def draw_polygon(
        self,
        center: Point3D,
        inner_radius: Union[Vector3D, UnitVector3D],
        sides: int,
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Create a polygon shape on the sketch.

        Parameters
        ----------
        center: Point3D
            A :class:`Point3D` representing the center of the polygon.
        inner_radius : Union[Quantity, Distance]
            The inradius(apothem) of the polygon.
        sides : int
            Number of sides of the polygon.
        angle : Optional[Union[Quantity, Angle, Real]]
            The placement angle for orientation alignment.

        Returns
        -------
        Polygon
            An object for modelling polygonal shapes.

        """
        polygon = Polygon(self._plane, center, inner_radius, sides, angle)
        self.append_shape(polygon)
        return polygon

    def draw_arc(
        self, center: Point3D, start: Point3D, end: Point3D, axis: Optional[UnitVector3D] = None
    ):
        """Create an arc shape on the sketch.

        Parameters
        ----------
        center : Point3D
            A :class:``Point3D`` representing the center of the arc.
        start : Point3D
            A :class:``Point3D`` representing the start of the shape.
        end : Point3D
            A :class:``Point3D`` representing the end of the shape.
        axis : Optional[UnitVector3D]
            A :class:``UnitVector3D`` determining the rotation direction of the arc.
            It is expected to be orthogonal to the provided plane.
            +z for counter-clockwise rotation. -z for clockwise rotation.
            If not provided, the default will be counter-clockwise rotation.

        Returns
        -------
        Arc
            An object representing the arc added to the sketch.

        """
        arc = Arc(self._plane, center, start, end, axis)
        self.append_shape(arc)
        return arc

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
        segment = SketchSegment(start, end)
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
        segment = SketchSegment(self._single_point_context_reference(), end)

        return self.edge(segment, tag)

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
        end_vec_as_point += start

        return self.segment(start, end_vec_as_point, tag)

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
        negative_angle: Optional[bool] = False,
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
        negative_angle : bool, optional
            By default the arc spans the shortest angular sector between
            ``start`` and ``end``.

            By setting this to ``True``, the longest angular sector is
            used instead (i.e. the negative coterminal angle to the
            shortest one).
        tag: str, optional
            A user-defined label identifying this specific edge.

        Returns
        -------
        Sketch
            The revised sketch state ready for further sketch actions.
        """
        arc = SketchArc(center, start, end, negative_angle)
        return self.edge(arc, tag)

    def arc_to_point(
        self,
        end: Point2D,
        center: Point2D,
        negative_angle: Optional[bool] = False,
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
        negative_angle : bool, optional
            By default the arc spans the shortest angular sector between
            ``start`` and ``end``.

            By setting this to ``True``, the longest angular sector is
            used instead (i.e. the negative coterminal angle to the
            shortest one).
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
        arc = SketchArc(center, start, end, negative_angle)
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
        circle = SketchCircle(center, radius)
        return self.face(circle, tag)

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
        """Plot a sketch to the scene.

        Parameters
        ----------
        **kwargs : dict, optional
            Optional keyword arguments. See :func:`pyvista.Plotter.add_mesh`
            for allowable keyword arguments.

        """
        from ansys.geometry.core.plotting.plotter import Plotter

        sketches_polydata = []
        pl = Plotter()
        for edge in self.edges:

            if isinstance(edge, SketchArc):
                # pyvista CircularArc does not have a plane input to use for the sketch,
                # so must sketch in x/y plane and then transform
                arc = pv.CircularArc(
                    [
                        edge.start.x.m_as(edge.start.base_unit),
                        edge.start.y.m_as(edge.start.base_unit),
                        0,
                    ],
                    [edge.end.x.m_as(edge.end.base_unit), edge.end.y.m_as(edge.end.base_unit), 0],
                    [
                        edge.center.x.m_as(edge.center.base_unit),
                        edge.center.y.m_as(edge.center.base_unit),
                        0,
                    ],
                    negative=edge.negative_angle,
                )
                arc.transform(self._plane.transformation_matrix)
                sketches_polydata.append(arc)
            elif isinstance(edge, SketchSegment):
                transformed_start = self._plane.transform_point2D_global_to_local(edge.start)
                transformed_end = self._plane.transform_point2D_global_to_local(edge.end)
                segment = pv.Line(transformed_start, transformed_end)
                sketches_polydata.append(segment)
            else:
                raise ValueError("The sketch cannot be plotted")

        for face in self.faces:
            if isinstance(face, SketchCircle):
                circle = pv.Circle(face.radius.m_as(UNIT_LENGTH))
                circle.translate(
                    [face.center.x.m_as(UNIT_LENGTH), face.center.y.m_as(UNIT_LENGTH), 0],
                    inplace=True,
                )
                circle.transform(self._plane.transformation_matrix)
                sketches_polydata.append(circle)
            elif isinstance(face, Triangle):
                triangle = pv.Triangle(
                    [
                        self._plane.transform_point2D_global_to_local(face.point1),
                        self._plane.transform_point2D_global_to_local(face.point2),
                        self._plane.transform_point2D_global_to_local(face.point3),
                    ]
                )
                sketches_polydata.append(triangle)
            elif isinstance(face, Trapezoid):
                # pyvista rectangle does not have validation or restrictions
                trapezoid = pv.Rectangle(
                    [
                        self._plane.transform_point2D_global_to_local(face._point1),
                        self._plane.transform_point2D_global_to_local(face._point2),
                        self._plane.transform_point2D_global_to_local(face._point3),
                        self._plane.transform_point2D_global_to_local(face._point4),
                    ]
                )
                sketches_polydata.append(trapezoid)

        pl.add_polydata(sketches_polydata, **kwargs)
        pl.show()
