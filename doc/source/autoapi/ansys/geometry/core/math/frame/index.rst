


Module ``frame``
================



.. py:module:: ansys.geometry.core.math.frame



Description
-----------

Provides for managing a frame.




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

   ansys.geometry.core.math.frame.Frame




.. py:class:: Frame(origin: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.point.Point3D] = ZERO_POINT3D, direction_x: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.vector.UnitVector3D, ansys.geometry.core.math.vector.Vector3D] = UNITVECTOR3D_X, direction_y: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.vector.UnitVector3D, ansys.geometry.core.math.vector.Vector3D] = UNITVECTOR3D_Y)


   Primitive representation of a frame (an origin and three fundamental directions).

   Parameters
   ----------
   origin : Union[~numpy.ndarray, RealSequence, Point3D], default: ZERO_POINT3D
       Centered origin of the`frame. The default is ``ZERO_POINT3D``, which is the
       Cartesian origin.
   direction_x : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D], default: UNITVECTOR3D_X
       X-axis direction.
   direction_y : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D], default: UNITVECTOR3D_Y
       Y-axis direction.

   .. py:property:: origin
      :type: ansys.geometry.core.math.point.Point3D

      Origin of the frame.


   .. py:property:: direction_x
      :type: ansys.geometry.core.math.vector.UnitVector3D

      X-axis direction of the frame.


   .. py:property:: direction_y
      :type: ansys.geometry.core.math.vector.UnitVector3D

      Y-axis direction of the frame.


   .. py:property:: direction_z
      :type: ansys.geometry.core.math.vector.UnitVector3D

      Z-axis direction of the frame.


   .. py:property:: global_to_local_rotation
      :type: ansys.geometry.core.math.matrix.Matrix33

      Global to local space transformation matrix.

      Returns
      -------
      Matrix33
          3x3 matrix representing the transformation from global to local
          coordinate space, excluding origin translation.


   .. py:property:: local_to_global_rotation
      :type: ansys.geometry.core.math.matrix.Matrix33

      Local to global space transformation matrix.

      Returns
      -------
      Matrix33
          3x3 matrix representing the transformation from local to global
          coordinate space.


   .. py:property:: transformation_matrix
      :type: ansys.geometry.core.math.matrix.Matrix44

      Full 4x4 transformation matrix.

      Returns
      -------
      Matrix44
          4x4 matrix representing the transformation from global to local
          coordinate space.


   .. py:method:: transform_point2d_local_to_global(point: ansys.geometry.core.math.point.Point2D) -> ansys.geometry.core.math.point.Point3D

      Transform a 2D point to a global 3D point.

      This method transforms a local, plane-contained ``Point2D`` object in the global
      coordinate system, thus representing it as a ``Point3D`` object.

      Parameters
      ----------
      point : Point2D
          ``Point2D`` local object to express in global coordinates.

      Returns
      -------
      Point3D
          Global coordinates for the 3D point.


   .. py:method:: __eq__(other: Frame) -> bool

      Equals operator for the ``Frame`` class.


   .. py:method:: __ne__(other: Frame) -> bool

      Not equals operator for the ``Frame`` class.



