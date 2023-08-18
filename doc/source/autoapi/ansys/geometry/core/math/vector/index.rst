


Module ``vector``
=================



.. py:module:: ansys.geometry.core.math.vector



Description
-----------

Provides for creating and managing 2D and 3D vectors.




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

   ansys.geometry.core.math.vector.Vector3D
   ansys.geometry.core.math.vector.Vector2D
   ansys.geometry.core.math.vector.UnitVector3D
   ansys.geometry.core.math.vector.UnitVector2D




.. py:class:: Vector3D(shape, dtype=float, buffer=None, offset=0, strides=None, order=None)


   Bases: :py:obj:`numpy.ndarray`

   Provides for managing and creating a 3D vector.

   Parameters
   ----------
   input : Union[~numpy.ndarray, RealSequence]
       3D :class:`numpy.ndarray <numpy.ndarray>` class with shape(X,).

   .. py:property:: x
      :type: ansys.geometry.core.typing.Real

      X coordinate of the ``Vector3D`` class.


   .. py:property:: y
      :type: ansys.geometry.core.typing.Real

      Y coordinate of the ``Vector3D`` class.


   .. py:property:: z
      :type: ansys.geometry.core.typing.Real

      Z coordinate of the ``Vector3D`` class.


   .. py:property:: norm
      :type: float

      Norm of the vector.


   .. py:property:: magnitude
      :type: float

      Norm of the vector.


   .. py:property:: is_zero
      :type: bool

      Check if all components of the 3D vector are zero.


   .. py:method:: is_perpendicular_to(other_vector: Vector3D) -> bool

      Check if this vector and another vector are perpendicular.


   .. py:method:: is_parallel_to(other_vector: Vector3D) -> bool

      Check if this vector and another vector are parallel.


   .. py:method:: is_opposite(other_vector: Vector3D) -> bool

      Check if this vector and another vector are opposite.


   .. py:method:: normalize() -> Vector3D

      Return a normalized version of the 3D vector.


   .. py:method:: transform(matrix: ansys.geometry.core.math.matrix.Matrix44) -> Vector3D

      Transform the 3D vector3D with a transformation matrix.

      Notes
      -----
      Transform the ``Vector3D`` object by applying the specified 4x4
      transformation matrix and return a new ``Vector3D`` object representing the
      transformed vector.

      Parameters
      ----------
      matrix : Matrix44
          4x4 transformation matrix to apply to the vector.

      Returns
      -------
      Vector3D
          A new 3D vector that is the transformed copy of the original 3D vector after applying
          the transformation matrix.


   .. py:method:: get_angle_between(v: Vector3D) -> pint.Quantity

      Get the angle between this 3D vector and another 3D vector.

      Parameters
      ----------
      v : Vector3D
          Other 3D vector for computing the angle.

      Returns
      -------
      Quantity
          Angle between these two 3D vectors.


   .. py:method:: cross(v: Vector3D) -> Vector3D

      Get the cross product of ``Vector3D`` objects.


   .. py:method:: __eq__(other: Vector3D) -> bool

      Equals operator for the ``Vector3D`` class.


   .. py:method:: __ne__(other: Vector3D) -> bool

      Not equals operator for the ``Vector3D`` class.


   .. py:method:: __mul__(other: beartype.typing.Union[Vector3D, ansys.geometry.core.typing.Real]) -> beartype.typing.Union[Vector3D, ansys.geometry.core.typing.Real]

      Overload * operator with dot product.

      Notes
      -----
      This method also admits scalar multiplication.


   .. py:method:: __mod__(other: Vector3D) -> Vector3D

      Overload % operator with cross product.


   .. py:method:: __add__(other: beartype.typing.Union[Vector3D, ansys.geometry.core.math.point.Point3D]) -> beartype.typing.Union[Vector3D, ansys.geometry.core.math.point.Point3D]

      Addition operation overload for 3D vectors.


   .. py:method:: __sub__(other: Vector3D) -> Vector3D

      Subtraction operation overload for 3D vectors.


   .. py:method:: from_points(point_a: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.point.Point3D], point_b: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.point.Point3D])
      :classmethod:

      Create a 3D vector from two distinct 3D points.

      Parameters
      ----------
      point_a : Point3D
          :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
          class representing the first point.
      point_b : Point3D
          :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
          class representing the second point.

      Notes
      -----
      The resulting 3D vector is always expressed in ``Point3D``
      base units.

      Returns
      -------
      Vector3D
          3D vector from ``point_a`` to ``point_b``.



.. py:class:: Vector2D(shape, dtype=float, buffer=None, offset=0, strides=None, order=None)


   Bases: :py:obj:`numpy.ndarray`

   Provides for creating and managing a 2D vector.

   Parameters
   ----------
   input : Union[~numpy.ndarray, RealSequence]
       2D :class:`numpy.ndarray <numpy.ndarray>` class with shape(X,).

   .. py:property:: x
      :type: ansys.geometry.core.typing.Real

      X coordinate of the 2D vector.


   .. py:property:: y
      :type: ansys.geometry.core.typing.Real

      Y coordinate of the 2D vector.


   .. py:property:: norm
      :type: float

      Norm of the 2D vector.


   .. py:property:: magnitude
      :type: float

      Norm of the 2D vector.


   .. py:property:: is_zero
      :type: bool

      Check if values for all components of the 2D vector are zero.


   .. py:method:: cross(v: Vector2D)

      Return the cross product of ``Vector2D`` objects.


   .. py:method:: is_perpendicular_to(other_vector: Vector2D) -> bool

      Check if this 2D vector and another 2D vector are perpendicular.


   .. py:method:: is_parallel_to(other_vector: Vector2D) -> bool

      Check if this vector and another vector are parallel.


   .. py:method:: is_opposite(other_vector: Vector2D) -> bool

      Check if this vector and another vector are opposite.


   .. py:method:: normalize() -> Vector2D

      Return a normalized version of the 2D vector.


   .. py:method:: get_angle_between(v: Vector2D) -> pint.Quantity

      Get the angle between this 2D vector and another 2D vector.

      Parameters
      ----------
      v : Vector2D
          Other 2D vector to compute the angle with.

      Returns
      -------
      Quantity
          Angle between these two 2D vectors.


   .. py:method:: __eq__(other: Vector2D) -> bool

      Equals operator for the ``Vector2D`` class.


   .. py:method:: __ne__(other: Vector2D) -> bool

      Not equals operator for the ``Vector2D`` class.


   .. py:method:: __mul__(other: beartype.typing.Union[Vector2D, ansys.geometry.core.typing.Real]) -> beartype.typing.Union[Vector2D, ansys.geometry.core.typing.Real]

      Overload * operator with dot product.

      Notes
      -----
      This method also admits scalar multiplication.


   .. py:method:: __add__(other: beartype.typing.Union[Vector2D, ansys.geometry.core.math.point.Point2D]) -> beartype.typing.Union[Vector2D, ansys.geometry.core.math.point.Point2D]

      Addition operation overload for 2D vectors.


   .. py:method:: __sub__(other: Vector2D) -> Vector2D

      Subtraction operation overload for 2D vectors.


   .. py:method:: __mod__(other: Vector2D) -> Vector2D

      Overload % operator with cross product.


   .. py:method:: from_points(point_a: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.point.Point2D], point_b: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.point.Point2D])
      :classmethod:

      Create a 2D vector from two distinct 2D points.

      Parameters
      ----------
      point_a : Point2D
          :class:`Point2D <ansys.geometry.core.math.point.Point2D>`
          class representing the first point.
      point_b : Point2D
          :class:`Point2D <ansys.geometry.core.math.point.Point2D>`
          class representing the second point.

      Notes
      -----
      The resulting 2D vector is always expressed in ``Point2D``
      base units.

      Returns
      -------
      Vector2D
          2D vector from ``point_a`` to ``point_b``.



.. py:class:: UnitVector3D(shape, dtype=float, buffer=None, offset=0, strides=None, order=None)


   Bases: :py:obj:`Vector3D`

   Provides for creating and managing a 3D unit vector.

   Parameters
   ----------
   input : ~numpy.ndarray, ``Vector3D``
       * 1D :class:`numpy.ndarray <numpy.ndarray>` class with shape(X,)
       * Vector3D

   .. py:method:: from_points(point_a: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.point.Point3D], point_b: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.point.Point3D])
      :classmethod:

      Create a 3D unit vector from two distinct 3D points.

      Parameters
      ----------
      point_a : Point3D
          :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
          class representing the first point.
      point_b : Point3D
          :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
          class representing the second point.

      Returns
      -------
      UnitVector3D
          3D unit vector from ``point_a`` to ``point_b``.



.. py:class:: UnitVector2D(shape, dtype=float, buffer=None, offset=0, strides=None, order=None)


   Bases: :py:obj:`Vector2D`

   Provides for creating and managing a 3D unit vector.

   Parameters
   ----------
   input : ~numpy.ndarray, ``Vector2D``
       * 1D :class:`numpy.ndarray <numpy.ndarray>` class with shape(X,)
       * Vector2D

   .. py:method:: from_points(point_a: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.point.Point2D], point_b: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.point.Point2D])
      :classmethod:

      Create a 2D unit vector from two distinct 2D points.

      Parameters
      ----------
      point_a : Point2D
          :class:`Point2D <ansys.geometry.core.math.point.Point2D>`
          class representing the first point.
      point_b : Point2D
          :class:`Point2D <ansys.geometry.core.math.point.Point2D>`
          class representing the second point.

      Returns
      -------
      UnitVector2D
          2D unit vector from ``point_a`` to ``point_b``.



