


Module ``face``
===============



.. py:module:: ansys.geometry.core.designer.face



Description
-----------

Module for managing a face.




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

   ansys.geometry.core.designer.face.SurfaceType
   ansys.geometry.core.designer.face.FaceLoopType
   ansys.geometry.core.designer.face.FaceLoop
   ansys.geometry.core.designer.face.Face




.. py:class:: SurfaceType


   Bases: :py:obj:`enum.Enum`

   Provides values for the surface types supported by the Geometry service.

   .. py:attribute:: SURFACETYPE_UNKNOWN
      :value: 0



   .. py:attribute:: SURFACETYPE_PLANE
      :value: 1



   .. py:attribute:: SURFACETYPE_CYLINDER
      :value: 2



   .. py:attribute:: SURFACETYPE_CONE
      :value: 3



   .. py:attribute:: SURFACETYPE_TORUS
      :value: 4



   .. py:attribute:: SURFACETYPE_SPHERE
      :value: 5



   .. py:attribute:: SURFACETYPE_NURBS
      :value: 6



   .. py:attribute:: SURFACETYPE_PROCEDURAL
      :value: 7




.. py:class:: FaceLoopType


   Bases: :py:obj:`enum.Enum`

   Provides values for the face loop types supported by the Geometry service.

   .. py:attribute:: INNER_LOOP
      :value: 'INNER'



   .. py:attribute:: OUTER_LOOP
      :value: 'OUTER'




.. py:class:: FaceLoop(type: FaceLoopType, length: pint.Quantity, min_bbox: ansys.geometry.core.math.Point3D, max_bbox: ansys.geometry.core.math.Point3D, edges: beartype.typing.List[ansys.geometry.core.designer.edge.Edge])


   Provides an internal class holding the face loops defined on the server side.

   Notes
   -----
   This class is to be used only when parsing server side results. It is not
   intended to be instantiated by a user.

   Parameters
   ----------
   type : FaceLoopType
       Type of loop.
   length : Quantity
       Length of the loop.
   min_bbox : Point3D
       Minimum point of the bounding box containing the loop.
   max_bbox : Point3D
       Maximum point of the bounding box containing the loop.
   edges : List[Edge]
       Edges contained in the loop.

   .. py:property:: type
      :type: FaceLoopType

      Type of the loop.


   .. py:property:: length
      :type: pint.Quantity

      Length of the loop.


   .. py:property:: min_bbox
      :type: ansys.geometry.core.math.Point3D

      Minimum point of the bounding box containing the loop.


   .. py:property:: max_bbox
      :type: ansys.geometry.core.math.Point3D

      Maximum point of the bounding box containing the loop.


   .. py:property:: edges
      :type: beartype.typing.List[ansys.geometry.core.designer.edge.Edge]

      Edges contained in the loop.



.. py:class:: Face(id: str, surface_type: SurfaceType, body: ansys.geometry.core.designer.body.Body, grpc_client: ansys.geometry.core.connection.GrpcClient)


   Represents a single face of a body within the design assembly.

   This class synchronizes to a design within a supporting Geometry service instance.

   Parameters
   ----------
   id : str
       Server-defined ID for the body.
   surface_type : SurfaceType
       Type of surface that the face forms.
   body : Body
       Parent body that the face constructs.
   grpc_client : GrpcClient
       Active supporting Geometry service instance for design modeling.

   .. py:property:: id
      :type: str

      Face ID.


   .. py:property:: body
      :type: ansys.geometry.core.designer.body.Body

      Body that the face belongs to.


   .. py:property:: area
      :type: pint.Quantity

      Calculated area of the face.


   .. py:property:: surface_type
      :type: SurfaceType

      Surface type of the face.


   .. py:property:: edges
      :type: beartype.typing.List[ansys.geometry.core.designer.edge.Edge]

      List of all edges of the face.


   .. py:property:: loops
      :type: beartype.typing.List[FaceLoop]

      List of all loops of the face.


   .. py:method:: face_normal(u: float = 0.5, v: float = 0.5) -> ansys.geometry.core.math.UnitVector3D

      Get the normal direction to the face evaluated at certain UV coordinates.

      Notes
      -----
      To properly use this method, you must handle UV coordinates. Thus, you must
      know how these relate to the underlying Geometry service. It is an advanced
      method for Geometry experts only.

      Parameters
      ----------
      u : float, default: 0.5
          First coordinate of the 2D representation of a surface in UV space.
          The default is ``0.5``, which is the center of the surface.
      v : float, default: 0.5
          Second coordinate of the 2D representation of a surface in UV space.
          The default is ``0.5``, which is the center of the surface.

      Returns
      -------
      UnitVector3D
          :class:`UnitVector3D <ansys.geometry.core.math.vector.unitVector3D>`
          object evaluated at the given U and V coordinates.
          This :class:`UnitVector3D <ansys.geometry.core.math.vector.unitVector3D>`
          object is perpendicular to the surface at the given UV coordinates.


   .. py:method:: face_point(u: float = 0.5, v: float = 0.5) -> ansys.geometry.core.math.Point3D

      Get a point of the face evaluated at certain UV coordinates.

      Notes
      -----
      To properly use this method, you must handle UV coordinates. Thus, you must
      know how these relate to the underlying Geometry service. It is an advanced
      method for Geometry experts only.

      Parameters
      ----------
      u : float, default: 0.5
          First coordinate of the 2D representation of a surface in UV space.
          The default is ``0.5``, which is the center of the surface.
      v : float, default: 0.5
          Second coordinate of the 2D representation of a surface in UV space.
          The default is ``0.5``, which is the center of the surface.

      Returns
      -------
      Point
          :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
          object evaluated at the given UV coordinates.



