


Module ``sketch``
=================



.. py:module:: ansys.geometry.core.sketch.sketch



Description
-----------

Provides for creating and managing a sketch.




Summary
-------

.. tab-set::




    .. tab-item:: Classes

        Content 2

    .. tab-item:: Functions

        Content 2

    .. tab-item:: Enumerations

        Content 2

    .. tab-item:: Attributes

        Content 2






Contents
--------

Classes
~~~~~~~

.. autoapisummary::

   ansys.geometry.core.sketch.sketch.Sketch




Attributes
~~~~~~~~~~

.. autoapisummary::

   ansys.geometry.core.sketch.sketch.SketchObject


.. py:data:: SketchObject

   Type used to refer to both ``SketchEdge`` and ``SketchFace`` as possible values.


.. py:class:: Sketch(plane: beartype.typing.Optional[ansys.geometry.core.math.Plane] = Plane())


   Provides for building 2D sketch elements.

   .. py:property:: plane
      :type: ansys.geometry.core.math.Plane

      Sketch plane configuration.


   .. py:property:: edges
      :type: beartype.typing.List[ansys.geometry.core.sketch.edge.SketchEdge]

      List of all independently sketched edges.

      Notes
      -----
      Independently sketched edges are not assigned to a face. Face edges
      are not included in this list.


   .. py:property:: faces
      :type: beartype.typing.List[ansys.geometry.core.sketch.face.SketchFace]

      List of all independently sketched faces.


   .. py:method:: translate_sketch_plane(translation: ansys.geometry.core.math.Vector3D) -> Sketch

      Translate the origin location of the active sketch plane.

      Parameters
      ----------
      translation : Vector3D
          Vector defining the translation. Meters is the expected unit.

      Returns
      -------
      Sketch
          Revised sketch state ready for further sketch actions.


   .. py:method:: translate_sketch_plane_by_offset(x: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance] = Quantity(0, DEFAULT_UNITS.LENGTH), y: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance] = Quantity(0, DEFAULT_UNITS.LENGTH), z: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance] = Quantity(0, DEFAULT_UNITS.LENGTH)) -> Sketch

      Translate the origin location of the active sketch plane by offsets.

      Parameters
      ----------
      x : Union[Quantity, Distance], default: Quantity(0, DEFAULT_UNITS.LENGTH)
          Amount to translate the origin of the x-direction.
      y : Union[Quantity, Distance], default: Quantity(0, DEFAULT_UNITS.LENGTH)
          Amount to translate the origin of the y-direction.
      z : Union[Quantity, Distance], default: Quantity(0, DEFAULT_UNITS.LENGTH)
          Amount to translate the origin of the z-direction.

      Returns
      -------
      Sketch
          Revised sketch state ready for further sketch actions.


   .. py:method:: translate_sketch_plane_by_distance(direction: ansys.geometry.core.math.UnitVector3D, distance: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance]) -> Sketch

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


   .. py:method:: get(tag: str) -> beartype.typing.List[SketchObject]

      Get a list of shapes with a given tag.

      Parameters
      ----------
      tag : str
          Tag to query against.


   .. py:method:: face(face: ansys.geometry.core.sketch.face.SketchFace, tag: beartype.typing.Optional[str] = None) -> Sketch

      Add a sketch face to the sketch.

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


   .. py:method:: edge(edge: ansys.geometry.core.sketch.edge.SketchEdge, tag: beartype.typing.Optional[str] = None) -> Sketch

      Add a sketch edge to the sketch.

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


   .. py:method:: select(*tags: str) -> Sketch

      Add all objects that match provided tags to the current context.


   .. py:method:: segment(start: ansys.geometry.core.math.Point2D, end: ansys.geometry.core.math.Point2D, tag: beartype.typing.Optional[str] = None) -> Sketch

      Add a segment sketch object to the sketch plane.

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


   .. py:method:: segment_to_point(end: ansys.geometry.core.math.Point2D, tag: beartype.typing.Optional[str] = None) -> Sketch

      Add a segment to the sketch plane starting from the previous edge end point.

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


   .. py:method:: segment_from_point_and_vector(start: ansys.geometry.core.math.Point2D, vector: ansys.geometry.core.math.Vector2D, tag: beartype.typing.Optional[str] = None)

      Add a segment to the sketch starting from a given starting point.

      Notes
      -----
      Vector magnitude determines the segment endpoint.
      Vector magnitude is assumed to use the same unit as the starting point.

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


   .. py:method:: segment_from_vector(vector: ansys.geometry.core.math.Vector2D, tag: beartype.typing.Optional[str] = None)

      Add a segment to the sketch starting from the end point of the previous edge.

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


   .. py:method:: arc(start: ansys.geometry.core.math.Point2D, end: ansys.geometry.core.math.Point2D, center: ansys.geometry.core.math.Point2D, clockwise: beartype.typing.Optional[bool] = False, tag: beartype.typing.Optional[str] = None) -> Sketch

      Add an arc to the sketch plane.

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


   .. py:method:: arc_to_point(end: ansys.geometry.core.math.Point2D, center: ansys.geometry.core.math.Point2D, clockwise: beartype.typing.Optional[bool] = False, tag: beartype.typing.Optional[str] = None) -> Sketch

      Add an arc to the sketch starting from the end point of the previous edge.

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


   .. py:method:: arc_from_three_points(start: ansys.geometry.core.math.Point2D, inter: ansys.geometry.core.math.Point2D, end: ansys.geometry.core.math.Point2D, tag: beartype.typing.Optional[str] = None) -> Sketch

      Add an arc to the sketch plane from three given points.

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


   .. py:method:: triangle(point1: ansys.geometry.core.math.Point2D, point2: ansys.geometry.core.math.Point2D, point3: ansys.geometry.core.math.Point2D, tag: beartype.typing.Optional[str] = None) -> Sketch

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
          User-defined label for identifying the face.

      Returns
      -------
      Sketch
          Revised sketch state ready for further sketch actions.


   .. py:method:: trapezoid(width: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], height: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], slant_angle: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real], nonsymmetrical_slant_angle: beartype.typing.Optional[beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real]] = None, center: beartype.typing.Optional[ansys.geometry.core.math.Point2D] = ZERO_POINT2D, angle: beartype.typing.Optional[beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real]] = 0, tag: beartype.typing.Optional[str] = None) -> Sketch

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
          The default is ``None``, in which case the trapezoid is symmetrical.
      center : Point2D, default: (0, 0)
          Center point of the trapezoid.
      angle : Optional[Union[Quantity, Angle, Real]], default: 0
          Placement angle for orientation alignment.
      tag : str, default: None
          User-defined label for identifying the face.

      Returns
      -------
      Sketch
          Revised sketch state ready for further sketch actions.


   .. py:method:: circle(center: ansys.geometry.core.math.Point2D, radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], tag: beartype.typing.Optional[str] = None) -> Sketch

      Add a circle to the plane at a given center.

      Parameters
      ----------
      center: Point2D
          Center point of the circle.
      radius : Union[Quantity, Distance, Real]
          Radius of the circle.
      tag : str, default: None
          User-defined label for identifying the face.

      Returns
      -------
      Sketch
          Revised sketch state ready for further sketch actions.


   .. py:method:: box(center: ansys.geometry.core.math.Point2D, width: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], height: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], angle: beartype.typing.Optional[beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real]] = 0, tag: beartype.typing.Optional[str] = None) -> Sketch

      Create a box on the sketch.

      Parameters
      ----------
      center: Point2D
          Center point of the box.
      width : Union[Quantity, Distance, Real]
          Width of the box.
      height : Union[Quantity, Distance, Real]
          Height of the box.
      angle : Union[Quantity, Real], default: 0
          Placement angle for orientation alignment.
      tag : str, default: None
          User-defined label for identifying the face.

      Returns
      -------
      Sketch
          Revised sketch state ready for further sketch actions.


   .. py:method:: slot(center: ansys.geometry.core.math.Point2D, width: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], height: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], angle: beartype.typing.Optional[beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real]] = 0, tag: beartype.typing.Optional[str] = None) -> Sketch

      Create a slot on the sketch.

      Parameters
      ----------
      center: Point2D
          Center point of the slot.
      width : Union[Quantity, Distance, Real]
          Width of the slot.
      height : Union[Quantity, Distance, Real]
          Height of the slot.
      angle : Union[Quantity, Angle, Real], default: 0
          Placement angle for orientation alignment.
      tag : str, default: None
          User-defined label for identifying the face.

      Returns
      -------
      Sketch
          Revised sketch state ready for further sketch actions.


   .. py:method:: ellipse(center: ansys.geometry.core.math.Point2D, major_radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], minor_radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], angle: beartype.typing.Optional[beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real]] = 0, tag: beartype.typing.Optional[str] = None) -> Sketch

      Create an ellipse on the sketch.

      Parameters
      ----------
      center: Point2D
          Center point of the ellipse.
      major_radius : Union[Quantity, Distance, Real]
          Semi-major axis of the ellipse.
      minor_radius : Union[Quantity, Distance, Real]
          Semi-minor axis of the ellipse.
      angle : Union[Quantity, Angle, Real], default: 0
          Placement angle for orientation alignment.
      tag : str, default: None
          User-defined label for identifying the face.

      Returns
      -------
      Sketch
          Revised sketch state ready for further sketch actions.


   .. py:method:: polygon(center: ansys.geometry.core.math.Point2D, inner_radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], sides: int, angle: beartype.typing.Optional[beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real]] = 0, tag: beartype.typing.Optional[str] = None) -> Sketch

      Create a polygon on the sketch.

      Parameters
      ----------
      center: Point2D
          Center point of the polygon.
      inner_radius : Union[Quantity, Distance, Real]
          Inner radius (apothem) of the polygon.
      sides : int
          Number of sides of the polygon.
      angle : Union[Quantity, Angle, Real], default: 0
          Placement angle for orientation alignment.
      tag : str, default: None
          User-defined label for identifying the face.

      Returns
      -------
      Sketch
          Revised sketch state ready for further sketch actions.


   .. py:method:: dummy_gear(origin: ansys.geometry.core.math.Point2D, outer_radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], inner_radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], n_teeth: int, tag: beartype.typing.Optional[str] = None) -> Sketch

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
          User-defined label for identifying the face.

      Returns
      -------
      Sketch
          Revised sketch state ready for further sketch actions.


   .. py:method:: spur_gear(origin: ansys.geometry.core.math.Point2D, module: ansys.geometry.core.typing.Real, pressure_angle: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real], n_teeth: int, tag: beartype.typing.Optional[str] = None) -> Sketch

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
          User-defined label for identifying the face.

      Returns
      -------
      Sketch
          Revised sketch state ready for further sketch actions.


   .. py:method:: tag(tag: str) -> None

      Add a tag to the active selection of sketch objects.

      Parameters
      ----------
      tag : str
          Tag to assign to the sketch objects.


   .. py:method:: plot(view_2d: beartype.typing.Optional[bool] = False, screenshot: beartype.typing.Optional[str] = None, use_trame: beartype.typing.Optional[bool] = None, selected_pd_objects: beartype.typing.List[pyvista.PolyData] = None, **plotting_options: beartype.typing.Optional[dict])

      Plot all objects of the sketch to the scene.

      Parameters
      ----------
      view_2d : bool, default: False
          Whether to represent the plot in a 2D format.
      screenshot : str, optional
          Path for saving a screenshot of the image that is being represented.
      use_trame : bool, default: None
          Whether to enables the use of `trame <https://kitware.github.io/trame/index.html>`_.
          The default is ``None``, in which case the ``USE_TRAME`` global
          setting is used.
      **plotting_options : dict, optional
          Keyword arguments for plotting. For allowable keyword arguments,
          see the :func:`pyvista.Plotter.add_mesh` method.


   .. py:method:: plot_selection(view_2d: beartype.typing.Optional[bool] = False, screenshot: beartype.typing.Optional[str] = None, use_trame: beartype.typing.Optional[bool] = None, **plotting_options: beartype.typing.Optional[dict])

      Plot the current selection to the scene.

      Parameters
      ----------
      view_2d : bool, default: False
          Whether to represent the plot in a 2D format.
      screenshot : str, optional
          Path for saving a screenshot of the image that is being represented.
      use_trame : bool, default: None
          Whether to enables the use of `trame <https://kitware.github.io/trame/index.html>`_.
          The default is ``None``, in which case the ``USE_TRAME`` global
          setting is used.
      **plotting_options : dict, optional
          Keyword arguments for plotting. For allowable keyword arguments,
          see the :func:`pyvista.Plotter.add_mesh` method.


   .. py:method:: sketch_polydata() -> beartype.typing.List[pyvista.PolyData]

      Get polydata configuration for all objects of the sketch to the scene.

      Returns
      -------
      List[PolyData]
          List of the polydata configuration for all edges and faces in the sketch.



