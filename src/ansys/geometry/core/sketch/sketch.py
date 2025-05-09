# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Provides for creating and managing a sketch."""

from typing import TYPE_CHECKING

from beartype import beartype as check_input_types
from pint import Quantity

from ansys.geometry.core.math.constants import ZERO_POINT2D
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector2D, Vector3D
from ansys.geometry.core.misc.checks import graphics_required
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Angle, Distance
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

SketchObject = SketchEdge | SketchFace
"""Type to refer to both ``SketchEdge`` and ``SketchFace``."""


class Sketch:
    """Provides for building 2D sketch elements."""

    # Types of the class instance private attributes
    _faces: list[SketchFace]
    _edges: list[SketchEdge]
    _current_sketch_context: list[SketchObject]
    _tags: dict[str, list[SketchObject]]

    @check_input_types
    def __init__(
        self,
        plane: Plane = Plane(),
    ):
        """Initialize the ``Sketch`` class."""
        self._plane = plane

        self._faces = []
        self._edges = []
        self._current_sketch_context = []
        self._sketches_polydata_selection = []

        # data structure to track tagging individual
        # sketch objects and collections of sketch objects
        self._tags = {}

    @property
    def plane(self) -> Plane:
        """Sketch plane configuration."""
        return self._plane

    @property
    def edges(self) -> list[SketchEdge]:
        """List of all independently sketched edges.

        Notes
        -----
        Independently sketched edges are not assigned to a face. Face edges
        are not included in this list.
        """
        return self._edges

    @property
    def faces(self) -> list[SketchFace]:
        """List of all independently sketched faces."""
        return self._faces

    @plane.setter
    @check_input_types
    def plane(self, plane: Plane) -> None:
        """Set the sketch plane configuration.

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
        """Translate the origin location of the active sketch plane.

        Parameters
        ----------
        translation : Vector3D
            Vector defining the translation. Default units are the expected
            units, otherwise it will be inconsistent.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        new_origin = Point3D(
            [
                self.plane.origin.x.m_as(DEFAULT_UNITS.LENGTH) + translation.x,
                self.plane.origin.y.m_as(DEFAULT_UNITS.LENGTH) + translation.y,
                self.plane.origin.z.m_as(DEFAULT_UNITS.LENGTH) + translation.z,
            ]
        )
        # Set the same unit system as the plane origin
        new_origin.unit = self.plane.origin.unit
        self.plane = Plane(new_origin, self.plane.direction_x, self.plane.direction_y)
        return self

    @check_input_types
    def translate_sketch_plane_by_offset(
        self,
        x: Quantity | Distance = Quantity(0, DEFAULT_UNITS.LENGTH),
        y: Quantity | Distance = Quantity(0, DEFAULT_UNITS.LENGTH),
        z: Quantity | Distance = Quantity(0, DEFAULT_UNITS.LENGTH),
    ) -> "Sketch":
        """Translate the origin location of the active sketch plane by offsets.

        Parameters
        ----------
        x : ~pint.Quantity | Distance, default: ~pint.Quantity(0, ``DEFAULT_UNITS.LENGTH``)
            Amount to translate the origin of the x-direction.
        y : ~pint.Quantity | Distance, default: ~pint.Quantity(0, ``DEFAULT_UNITS.LENGTH``)
            Amount to translate the origin of the y-direction.
        z : ~pint.Quantity | Distance, default: ~pint.Quantity(0, ``DEFAULT_UNITS.LENGTH``)
            Amount to translate the origin of the z-direction.

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
        self, direction: UnitVector3D, distance: Quantity | Distance
    ) -> "Sketch":
        """Translate the origin location active sketch plane by distance.

        Parameters
        ----------
        direction : UnitVector3D
            Direction to translate the origin.
        distance : ~pint.Quantity | Distance
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
    def get(self, tag: str) -> list[SketchObject]:
        """Get a list of shapes with a given tag.

        Parameters
        ----------
        tag : str
            Tag to query against.
        """
        return self._tags[tag]

    @check_input_types
    def face(self, face: SketchFace, tag: str | None = None) -> "Sketch":
        """Add a sketch face to the sketch.

        Parameters
        ----------
        face : SketchFace
            Face to add.
        tag : str, default: None
            User-defined label for identifying the face.

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
    def edge(self, edge: SketchEdge, tag: str | None = None) -> "Sketch":
        """Add a sketch edge to the sketch.

        Parameters
        ----------
        edge : SketchEdge
            Edge to add.
        tag : str, default: None
            User-defined label for identifying the edge.

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
        """Add all objects that match provided tags to the current context."""
        self._current_sketch_context = []

        for tag in tags:
            self._current_sketch_context.extend(self._tags[tag])

        return self

    def segment(self, start: Point2D, end: Point2D, tag: str | None = None) -> "Sketch":
        """Add a segment sketch object to the sketch plane.

        Parameters
        ----------
        start : Point2D
            Starting point of the line segment.
        end : Point2D
            Ending point of the line segment.
        tag : str, default: None
            User-defined label for identifying the edge.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        segment = SketchSegment(start, end)
        return self.edge(segment, tag)

    def segment_to_point(self, end: Point2D, tag: str | None = None) -> "Sketch":
        """Add a segment to the sketch plane starting from the previous end point.

        Parameters
        ----------
        end : Point2D
            Ending point of the line segment.
        tag : str, default: None
            User-defined label for identifying the edge.

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
        self, start: Point2D, vector: Vector2D, tag: str | None = None
    ):
        """Add a segment to the sketch starting from a given starting point.

        Parameters
        ----------
        start : Point2D
            Starting point of the line segment.
        vector : Vector2D
            Vector defining the line segment. Vector magnitude determines
            the segment endpoint. Vector magnitude is assumed to be in the
            same unit as the starting point.
        tag : str, default: None
            User-defined label for identifying the edge.

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
    def segment_from_vector(self, vector: Vector2D, tag: str | None = None):
        """Add a segment to the sketch starting from the previous end point.

        Parameters
        ----------
        vector : Vector2D
            Vector defining the line segment.
        tag : str, default: None
            User-defined label for identifying the edge.

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
        clockwise: bool = False,
        tag: str | None = None,
    ) -> "Sketch":
        """Add an arc to the sketch plane.

        Parameters
        ----------
        start : Point2D
            Starting point of the arc.
        end : Point2D
            Ending point of the arc.
        center : Point2D
            Center point of the arc.
        clockwise : bool, default: False
            Whether the arc spans the angle clockwise between the start
            and end points. When ``False `` (default), the arc spans the angle
            counter-clockwise. When ``True``, the arc spans the angle
            clockwise.
        tag : str, default: None
            User-defined label for identifying the edge.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        arc = Arc(start, end, center, clockwise)
        return self.edge(arc, tag)

    @check_input_types
    def arc_to_point(
        self,
        end: Point2D,
        center: Point2D,
        clockwise: bool = False,
        tag: str | None = None,
    ) -> "Sketch":
        """Add an arc to the sketch starting from the previous end point.

        Parameters
        ----------
        end : Point2D
            Ending point of the arc.
        center : Point2D
            Center point of the arc.
        clockwise : bool, default: False
            Whether the arc spans the angle clockwise between the start
            and end points. When ``False`` (default), the arc spans the angle
            counter-clockwise. When ``True``, the arc spans the angle
            clockwise.
        tag : str, default: None
            User-defined label for identifying the edge.

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
        arc = Arc(start, end, center, clockwise)
        return self.edge(arc, tag)

    def arc_from_three_points(
        self,
        start: Point2D,
        inter: Point2D,
        end: Point2D,
        tag: str | None = None,
    ) -> "Sketch":
        """Add an arc to the sketch plane from three given points.

        Parameters
        ----------
        start : Point2D
            Starting point of the arc.
        inter : Point2D
            Intermediate point (location) of the arc.
        end : Point2D
            End point of the arc.
        tag : str, default: None
            User-defined label for identifying the edge.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        arc = Arc.from_three_points(start, inter, end)
        return self.edge(arc, tag)

    def arc_from_start_end_and_radius(
        self,
        start: Point2D,
        end: Point2D,
        radius: Quantity | Distance | Real,
        convex_arc: bool = False,
        clockwise: bool = False,
        tag: str | None = None,
    ) -> "Sketch":
        """Add an arc from the start, end points and a radius.

        Parameters
        ----------
        start : Point2D
            Starting point of the arc.
        end : Point2D
            Ending point of the arc.
        radius : ~pint.Quantity | Distance | Real
            Radius of the arc.
        convex_arc : bool, default: False
            Whether the arc is convex. The default is ``False``.
            When ``False`` , the arc spans the concave version of the arc.
            When ``True``, the arc spans the convex version of the arc.
        clockwise : bool, default: False
            Whether the arc spans the angle clockwise between the start
            and end points. When ``False``, the arc spans the angle
            counter-clockwise. When ``True``, the arc spans the angle
            clockwise.
        tag : str, default: None
            User-defined label for identifying the edge.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        arc = Arc.from_start_end_and_radius(
            start,
            end,
            radius,
            convex_arc=convex_arc,
            clockwise=clockwise,
        )
        return self.edge(arc, tag)

    def arc_from_start_center_and_angle(
        self,
        start: Point2D,
        center: Point2D,
        angle: Quantity | Angle | Real,
        clockwise: bool = False,
        tag: str | None = None,
    ) -> "Sketch":
        """Add an arc from the start, center point, and angle.

        Parameters
        ----------
        start : Point2D
            Starting point of the arc.
        center : Point2D
            Center point of the arc.
        angle : ~pint.Quantity | Angle | Real
            Angle of the arc.
        clockwise : bool, default: False
            Whether the arc spans the angle clockwise. The default is ``False``.
            When ``False`` , the arc spans the angle counter-clockwise.
            When ``True``, the arc spans the angle clockwise.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        arc = Arc.from_start_center_and_angle(
            start,
            center,
            angle,
            clockwise=clockwise,
        )
        return self.edge(arc, tag)

    def triangle(
        self,
        point1: Point2D,
        point2: Point2D,
        point3: Point2D,
        tag: str | None = None,
    ) -> "Sketch":
        """Add a triangle to the sketch using given vertex points.

        Parameters
        ----------
        point1 : Point2D
            Point that represents a vertex of the triangle.
        point2 : Point2D
            Point that represents a vertex of the triangle.
        point3 : Point2D
            Point that represents a vertex of the triangle.
        tag : str, default: None
            User-defined label for identifying the face.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        triangle = Triangle(point1, point2, point3)
        return self.face(triangle, tag)

    def trapezoid(
        self,
        base_width: Quantity | Distance | Real,
        height: Quantity | Distance | Real,
        base_angle: Quantity | Angle | Real,
        base_asymmetric_angle: Quantity | Angle | Real | None = None,
        center: Point2D = ZERO_POINT2D,
        angle: Quantity | Angle | Real = 0,
        tag: str | None = None,
    ) -> "Sketch":
        """Add a trapezoid to the sketch using given vertex points.

        Parameters
        ----------
        base_width : ~pint.Quantity | Distance | Real
            Width of the lower base of the trapezoid.
        height : ~pint.Quantity | Distance | Real
            Height of the slot.
        base_angle : ~pint.Quantity | Distance | Real
            Angle for trapezoid generation. Represents the angle
            on the base of the trapezoid.
        base_asymmetric_angle : ~pint.Quantity | Angle | Real | None, default: None
            Asymmetrical angles on each side of the trapezoid.
            The default is ``None``, in which case the trapezoid is symmetrical. If
            provided, the trapezoid is asymmetrical and the right corner angle
            at the base of the trapezoid is set to the provided value.
        center: Point2D, default: ZERO_POINT2D
            Center point of the trapezoid.
        angle : ~pint.Quantity | Angle | Real, default: 0
            Placement angle for orientation alignment.
        tag : str, default: None
            User-defined label for identifying the face.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.

        Notes
        -----
        If an asymmetric base angle is defined, the base angle is
        applied to the left-most angle, and the asymmetric base angle
        is applied to the right-most angle.
        """
        trapezoid = Trapezoid(base_width, height, base_angle, base_asymmetric_angle, center, angle)
        return self.face(trapezoid, tag)

    def circle(
        self,
        center: Point2D,
        radius: Quantity | Distance | Real,
        tag: str | None = None,
    ) -> "Sketch":
        """Add a circle to the plane at a given center.

        Parameters
        ----------
        center: Point2D
            Center point of the circle.
        radius : ~pint.Quantity | Distance | Real
            Radius of the circle.
        tag : str, default: None
            User-defined label for identifying the face.

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
        width: Quantity | Distance | Real,
        height: Quantity | Distance | Real,
        angle: Quantity | Angle | Real = 0,
        tag: str | None = None,
    ) -> "Sketch":
        """Create a box on the sketch.

        Parameters
        ----------
        center: Point2D
            Center point of the box.
        width : ~pint.Quantity | Distance | Real
            Width of the box.
        height : ~pint.Quantity | Distance | Real
            Height of the box.
        angle : ~pint.Quantity | Angle | Real, default: 0
            Placement angle for orientation alignment.
        tag : str, default: None
            User-defined label for identifying the face.

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
        width: Quantity | Distance | Real,
        height: Quantity | Distance | Real,
        angle: Quantity | Angle | Real = 0,
        tag: str | None = None,
    ) -> "Sketch":
        """Create a slot on the sketch.

        Parameters
        ----------
        center: Point2D
            Center point of the slot.
        width : ~pint.Quantity | Distance | Real
            Width of the slot.
        height : ~pint.Quantity | Distance | Real
            Height of the slot.
        angle : ~pint.Quantity | Angle | Real, default: 0
            Placement angle for orientation alignment.
        tag : str, default: None
            User-defined label for identifying the face.

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
        major_radius: Quantity | Distance | Real,
        minor_radius: Quantity | Distance | Real,
        angle: Quantity | Angle | Real = 0,
        tag: str | None = None,
    ) -> "Sketch":
        """Create an ellipse on the sketch.

        Parameters
        ----------
        center: Point2D
            Center point of the ellipse.
        major_radius : ~pint.Quantity | Distance | Real
            Semi-major axis of the ellipse.
        minor_radius : ~pint.Quantity | Distance | Real
            Semi-minor axis of the ellipse.
        angle : ~pint.Quantity | Angle | Real, default: 0
            Placement angle for orientation alignment.
        tag : str, default: None
            User-defined label for identifying the face.

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
        inner_radius: Quantity | Distance | Real,
        sides: int,
        angle: Quantity | Angle | Real = 0,
        tag: str | None = None,
    ) -> "Sketch":
        """Create a polygon on the sketch.

        Parameters
        ----------
        center: Point2D
            Center point of the polygon.
        inner_radius : ~pint.Quantity | Distance | Real
            Inner radius (apothem) of the polygon.
        sides : int
            Number of sides of the polygon.
        angle : ~pint.Quantity | Angle | Real, default: 0
            Placement angle for orientation alignment.
        tag : str, default: None
            User-defined label for identifying the face.

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
        outer_radius: Quantity | Distance | Real,
        inner_radius: Quantity | Distance | Real,
        n_teeth: int,
        tag: str | None = None,
    ) -> "Sketch":
        """Create a dummy gear on the sketch.

        Parameters
        ----------
        origin : Point2D
            Origin of the gear.
        outer_radius : ~pint.Quantity | Distance | Real
            Outer radius of the gear.
        inner_radius : ~pint.Quantity | Distance | Real
            Inner radius of the gear.
        n_teeth : int
            Number of teeth of the gear.
        tag : str, default: None
            User-defined label for identifying the face.

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
        pressure_angle: Quantity | Angle | Real,
        n_teeth: int,
        tag: str | None = None,
    ) -> "Sketch":
        """Create a spur gear on the sketch.

        Parameters
        ----------
        origin : Point2D
            Origin of the spur gear.
        module : Real
            Module of the spur gear. This is also the ratio between the pitch circle
            diameter in millimeters and the number of teeth.
        pressure_angle : ~pint.Quantity | Angle | Real
            Pressure angle of the spur gear.
        n_teeth : int
            Number of teeth of the spur gear.
        tag : str, default: None
            User-defined label for identifying the face.

        Returns
        -------
        Sketch
            Revised sketch state ready for further sketch actions.
        """
        gear = SpurGear(origin, module, pressure_angle, n_teeth)
        return self.face(gear, tag)

    @check_input_types
    def tag(self, tag: str) -> None:
        """Add a tag to the active selection of sketch objects.

        Parameters
        ----------
        tag : str
            Tag to assign to the sketch objects.
        """
        self._tags[tag] = self._current_sketch_context

    def _single_point_context_reference(self) -> Point2D:
        """Get the last reference point from historical context.

        Notes
        -----
        If no single point context is available, ``ZERO_POINT2D`` is returned.
        """
        if not self._edges or len(self._edges) == 0:
            return ZERO_POINT2D

        return self._edges[-1].end

    def _tag(self, sketch_collection: list[SketchObject], tag: str) -> None:
        """Add a tag for a collection of sketch objects.

        Parameters
        ----------
        sketch_collection : list[SketchObject]
            Sketch objects to tag.
        tag : str, default: None
            Tag to assign to these sketch objects.
        """
        self._tags[tag] = sketch_collection

    @graphics_required
    def plot(
        self,
        view_2d: bool = False,
        screenshot: str | None = None,
        use_trame: bool | None = None,
        selected_pd_objects: list["PolyData"] = None,
        **plotting_options: dict | None,
    ):
        """Plot all objects of the sketch to the scene.

        Parameters
        ----------
        view_2d : bool, default: False
            Whether to represent the plot in a 2D format.
        screenshot : str, optional
            Path for saving a screenshot of the image that is being represented.
        use_trame : bool, default: None
            Whether to enables the use of `trame <https://kitware.github.io/trame/index.html>`_.
            The default is ``None``, in which case the
            ``ansys.tools.visualization_interface.USE_TRAME`` global setting is used.
        **plotting_options : dict, optional
            Keyword arguments for plotting. For allowable keyword arguments,
            see the :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.
        """
        # Show the plot requested - i.e. all polydata in sketch
        from ansys.geometry.core.plotting import GeometryPlotter

        if view_2d:
            vector = self.plane.direction_z.tolist()
            viewup = self.plane.direction_y.tolist()
            view_2d_dict = {"vector": vector, "viewup": viewup}
        else:
            view_2d_dict = None
        plotting_options.pop("view_2d", None)
        if selected_pd_objects is not None:
            pl = GeometryPlotter(use_trame=use_trame)
            pl.plot(
                selected_pd_objects,
                opacity=0.7,  # We are passing PD objects directly... apply opacity to all of them
                **plotting_options,
            )
            pl.show(
                screenshot=screenshot,
                view_2d=view_2d_dict,
                **plotting_options,
            )
        else:
            pl = GeometryPlotter(use_trame=use_trame)
            pl.plot(self.sketch_polydata_faces(), opacity=0.7, **plotting_options)
            pl.plot(self.sketch_polydata_edges(), **plotting_options)
            pl.show(screenshot=screenshot, view_2d=view_2d_dict, **plotting_options)

    @graphics_required
    def plot_selection(
        self,
        view_2d: bool = False,
        screenshot: str | None = None,
        use_trame: bool | None = None,
        **plotting_options: dict | None,
    ):
        """Plot the current selection to the scene.

        Parameters
        ----------
        view_2d : bool, default: False
            Whether to represent the plot in a 2D format.
        screenshot : str, optional
            Path for saving a screenshot of the image that is being represented.
        use_trame : bool, default: None
            Whether to enables the use of `trame <https://kitware.github.io/trame/index.html>`_.
            The default is ``None``, in which case the
            ``ansys.tools.visualization_interface.USE_TRAME`` global setting is used.
        **plotting_options : dict, optional
            Keyword arguments for plotting. For allowable keyword arguments,
            see the :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.
        """
        # Get the selected polydata
        sketches_polydata_selection = []
        sketches_polydata_selection.extend(
            [
                sketch_item.visualization_polydata.transform(
                    self._plane.transformation_matrix, inplace=True
                )
                for sketch_item in self._current_sketch_context
            ]
        )
        self.plot(
            view_2d=view_2d,
            screenshot=screenshot,
            use_trame=use_trame,
            selected_pd_objects=sketches_polydata_selection,
            **plotting_options,
        )

    def sketch_polydata(self) -> list["PolyData"]:
        """Get polydata configuration for all objects of the sketch.

        Returns
        -------
        list[~pyvista.PolyData]
            List of the polydata configuration for all edges and faces in the sketch.
        """
        sketches_polydata = []
        sketches_polydata.extend(self.sketch_polydata_edges())
        sketches_polydata.extend(self.sketch_polydata_faces())
        return sketches_polydata

    def sketch_polydata_faces(self) -> list["PolyData"]:
        """Get polydata configuration for all faces of the sketch to the scene.

        Returns
        -------
        list[~pyvista.PolyData]
            List of the polydata configuration for faces in the sketch.
        """
        sketches_polydata_faces = [
            face.visualization_polydata.transform(self._plane.transformation_matrix, inplace=True)
            for face in self.faces
        ]
        return sketches_polydata_faces

    def sketch_polydata_edges(self) -> list["PolyData"]:
        """Get polydata configuration for all edges of the sketch to the scene.

        Returns
        -------
        list[~pyvista.PolyData]
            List of the polydata configuration for edges in the sketch.
        """
        sketches_polydata_edges = [
            edge.visualization_polydata.transform(self._plane.transformation_matrix, inplace=True)
            for edge in self.edges
        ]
        return sketches_polydata_edges
