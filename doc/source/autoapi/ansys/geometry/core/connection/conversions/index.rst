


Module ``conversions``
======================



.. py:module:: ansys.geometry.core.connection.conversions



Description
-----------

Module providing for conversions.




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


Functions
~~~~~~~~~

.. autoapisummary::

   ansys.geometry.core.connection.conversions.unit_vector_to_grpc_direction
   ansys.geometry.core.connection.conversions.frame_to_grpc_frame
   ansys.geometry.core.connection.conversions.plane_to_grpc_plane
   ansys.geometry.core.connection.conversions.sketch_shapes_to_grpc_geometries
   ansys.geometry.core.connection.conversions.sketch_edges_to_grpc_geometries
   ansys.geometry.core.connection.conversions.sketch_arc_to_grpc_arc
   ansys.geometry.core.connection.conversions.sketch_ellipse_to_grpc_ellipse
   ansys.geometry.core.connection.conversions.sketch_circle_to_grpc_circle
   ansys.geometry.core.connection.conversions.point3d_to_grpc_point
   ansys.geometry.core.connection.conversions.point2d_to_grpc_point
   ansys.geometry.core.connection.conversions.sketch_polygon_to_grpc_polygon
   ansys.geometry.core.connection.conversions.sketch_segment_to_grpc_line
   ansys.geometry.core.connection.conversions.tess_to_pd
   ansys.geometry.core.connection.conversions.grpc_matrix_to_matrix
   ansys.geometry.core.connection.conversions.grpc_frame_to_frame



.. py:function:: unit_vector_to_grpc_direction(unit_vector: ansys.geometry.core.math.UnitVector3D) -> ansys.api.geometry.v0.models_pb2.Direction

   Convert a ``UnitVector3D`` class to a unit vector Geometry service gRPC message.

   Parameters
   ----------
   unit_vector : UnitVector3D
       Source vector data.

   Returns
   -------
   GRPCDirection
       Geometry service gRPC direction message.


.. py:function:: frame_to_grpc_frame(frame: ansys.geometry.core.math.Frame) -> ansys.api.geometry.v0.models_pb2.Frame

   Convert a ``Frame`` class to a frame Geometry service gRPC message.

   Parameters
   ----------
   frame : Frame
       Source frame data.

   Returns
   -------
   GRPCFrame
       Geometry service gRPC frame message. The unit for the frame origin is meters.


.. py:function:: plane_to_grpc_plane(plane: ansys.geometry.core.math.Plane) -> ansys.api.geometry.v0.models_pb2.Plane

   Convert a ``Plane`` class to a plane Geometry service gRPC message.

   Parameters
   ----------
   plane : Plane
       Source plane data.

   Returns
   -------
   GRPCPlane
       Geometry service gRPC plane message. The unit is meters.


.. py:function:: sketch_shapes_to_grpc_geometries(plane: ansys.geometry.core.math.Plane, edges: beartype.typing.List[ansys.geometry.core.sketch.SketchEdge], faces: beartype.typing.List[ansys.geometry.core.sketch.SketchFace], only_one_curve: beartype.typing.Optional[bool] = False) -> ansys.api.geometry.v0.models_pb2.Geometries

   Convert lists of ``SketchEdge`` and ``SketchFace`` to a ``Geometries`` gRPC message.

   Parameters
   ----------
   plane : Plane
       Plane for positioning the 2D sketches.
   edges : List[SketchEdge]
       Source edge data.
   faces : List[SketchFace]
       Source face data.
   shapes : List[BaseShape]
       Source shape data.
   only_one_curve : bool, default: False
       Whether to project one curve of the whole set of geometries to
       enhance performance.

   Returns
   -------
   Geometries
       Geometry service gRPC geometries message. The unit is meters.


.. py:function:: sketch_edges_to_grpc_geometries(edges: beartype.typing.List[ansys.geometry.core.sketch.SketchEdge], plane: ansys.geometry.core.math.Plane) -> beartype.typing.Tuple[beartype.typing.List[ansys.api.geometry.v0.models_pb2.Line], beartype.typing.List[ansys.api.geometry.v0.models_pb2.Arc]]

   Convert a list of ``SketchEdge`` to a ``Geometries`` gRPC message.

   Parameters
   ----------
   edges : List[SketchEdge]
       Source edge data.
   plane : Plane
       Plane for positioning the 2D sketches.

   Returns
   -------
   Tuple[List[GRPCLine], List[GRPCArc]]
       Geometry service gRPC line and arc messages. The unit is meters.


.. py:function:: sketch_arc_to_grpc_arc(arc: ansys.geometry.core.sketch.Arc, plane: ansys.geometry.core.math.Plane) -> ansys.api.geometry.v0.models_pb2.Arc

   Convert an ``Arc`` class to an arc Geometry service gRPC message.

   Parameters
   ----------
   arc : Arc
       Source arc data.
   plane : Plane
       Plane for positioning the arc within.

   Returns
   -------
   GRPCArc
       Geometry service gRPC arc message. The unit is meters.


.. py:function:: sketch_ellipse_to_grpc_ellipse(ellipse: ansys.geometry.core.sketch.SketchEllipse, plane: ansys.geometry.core.math.Plane) -> ansys.api.geometry.v0.models_pb2.Ellipse

   Convert a ``SketchEllipse`` class to an ellipse Geometry service gRPC message.

   Parameters
   ----------
   ellipse : SketchEllipse
       Source ellipse data.

   Returns
   -------
   GRPCEllipse
       Geometry service gRPC ellipse message. The unit is meters.


.. py:function:: sketch_circle_to_grpc_circle(circle: ansys.geometry.core.sketch.SketchCircle, plane: ansys.geometry.core.math.Plane) -> ansys.api.geometry.v0.models_pb2.Circle

   Convert a ``SketchCircle`` class to a circle Geometry service gRPC message.

   Parameters
   ----------
   circle : SketchCircle
       Source circle data.
   plane : Plane
       Plane for positioning the circle.

   Returns
   -------
   GRPCCircle
       Geometry service gRPC circle message. The unit is meters.


.. py:function:: point3d_to_grpc_point(point: ansys.geometry.core.math.Point3D) -> ansys.api.geometry.v0.models_pb2.Point

   Convert a ``Point3D`` class to a point Geometry service gRPC message.

   Parameters
   ----------
   point : Point3D
       Source point data.

   Returns
   -------
   GRPCPoint
       Geometry service gRPC point message. The unit is meters.


.. py:function:: point2d_to_grpc_point(plane: ansys.geometry.core.math.Plane, point2d: ansys.geometry.core.math.Point2D) -> ansys.api.geometry.v0.models_pb2.Point

   Convert a ``Point2D`` class to a point Geometry service gRPC message.

   Parameters
   ----------
   plane : Plane
       Plane for positioning the 2D point.
   point : Point2D
       Source point data.

   Returns
   -------
   GRPCPoint
       Geometry service gRPC point message. The unit is meters.


.. py:function:: sketch_polygon_to_grpc_polygon(polygon: ansys.geometry.core.sketch.Polygon, plane: ansys.geometry.core.math.Plane) -> ansys.api.geometry.v0.models_pb2.Polygon

   Convert a ``Polygon`` class to a polygon Geometry service gRPC message.

   Parameters
   ----------
   polygon : Polygon
       Source polygon data.

   Returns
   -------
   GRPCPolygon
       Geometry service gRPC polygon message. The unit is meters.


.. py:function:: sketch_segment_to_grpc_line(segment: ansys.geometry.core.sketch.SketchSegment, plane: ansys.geometry.core.math.Plane) -> ansys.api.geometry.v0.models_pb2.Line

   Convert a ``Segment`` class to a line Geometry service gRPC message.

   Parameters
   ----------
   segment : SketchSegment
       Source segment data.

   Returns
   -------
   GRPCLine
       Geometry service gRPC line message. The unit is meters.


.. py:function:: tess_to_pd(tess: ansys.api.geometry.v0.models_pb2.Tessellation) -> pyvista.PolyData

   Convert an ``ansys.api.geometry.Tessellation`` to ``pyvista.PolyData``.


.. py:function:: grpc_matrix_to_matrix(m: ansys.api.geometry.v0.models_pb2.Matrix) -> ansys.geometry.core.math.Matrix44

   Convert an ``ansys.api.geometry.Matrix`` to a ``Matrix44``.


.. py:function:: grpc_frame_to_frame(frame: ansys.api.geometry.v0.models_pb2.Frame) -> ansys.geometry.core.math.Frame

   Convert an ``ansys.api.geometry.Frame`` gRPC message to a ``Frame`` class.

   Parameters
   ----------
   GRPCFrame
       Geometry service gRPC frame message. The unit for the frame origin is meters.

   Returns
   -------
   frame : Frame
       Resulting converted frame.


