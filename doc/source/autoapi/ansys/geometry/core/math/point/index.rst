


Module ``point``
================



.. py:module:: ansys.geometry.core.math.point



Description
-----------

Provides geometry primitive representation for 2D and 3D points.




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

   ansys.geometry.core.math.point.Point2D
   ansys.geometry.core.math.point.Point3D




Attributes
~~~~~~~~~~

.. autoapisummary::

   ansys.geometry.core.math.point.DEFAULT_POINT2D_VALUES
   ansys.geometry.core.math.point.DEFAULT_POINT3D_VALUES
   ansys.geometry.core.math.point.BASE_UNIT_LENGTH


.. py:data:: DEFAULT_POINT2D_VALUES

   Default values for a 2D point.


.. py:data:: DEFAULT_POINT3D_VALUES

   Default values for a 3D point.


.. py:data:: BASE_UNIT_LENGTH

   Default value for the length of the base unit.


.. py:class:: Point2D(input: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence] = DEFAULT_POINT2D_VALUES, unit: beartype.typing.Optional[pint.Unit] = None)


   Bases: :py:obj:`numpy.ndarray`, :py:obj:`ansys.geometry.core.misc.PhysicalQuantity`

   Provides geometry primitive representation for a 2D point.

   Parameters
   ----------
   input : Union[~numpy.ndarray, RealSequence], default: DEFAULT_POINT2D_VALUES
       Direction arguments, either as a :class:`numpy.ndarray <numpy.ndarray>` class
       or as a ``RealSequence``.
   unit : ~pint.Unit, default: DEFAULT_UNITS.LENGTH
       Units for defining 2D point values.

   .. py:property:: x
      :type: pint.Quantity

      X plane component value.


   .. py:property:: y
      :type: pint.Quantity

      Y plane component value.


   .. py:method:: __eq__(other: Point2D) -> bool

      Equals operator for the ``Point2D`` class.


   .. py:method:: __ne__(other: Point2D) -> bool

      Not equals operator for the ``Point2D`` class.


   .. py:method:: __add__(other: beartype.typing.Union[Point2D, ansys.geometry.core.math.vector.Vector2D]) -> Point2D

      Add operation for the ``Point2D`` class.


   .. py:method:: __sub__(other: Point2D) -> Point2D

      Subtraction operation for the ``Point2D`` class.


   .. py:method:: unit() -> pint.Unit

      Get the unit of the object.


   .. py:method:: base_unit() -> pint.Unit

      Get the base unit of the object.



.. py:class:: Point3D(input: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence] = DEFAULT_POINT3D_VALUES, unit: beartype.typing.Optional[pint.Unit] = None)


   Bases: :py:obj:`numpy.ndarray`, :py:obj:`ansys.geometry.core.misc.PhysicalQuantity`

   Provides geometry primitive representation for a 3D point.

   Parameters
   ----------
   input : Union[~numpy.ndarray, RealSequence], default: DEFAULT_POINT3D_VALUES
       Direction arguments, either as a :class:`numpy.ndarray <numpy.ndarray>` class
       or as a ``RealSequence``.
   unit : ~pint.Unit, default: DEFAULT_UNITS.LENGTH
       Units for defining 3D point values.

   .. py:property:: x
      :type: pint.Quantity

      X plane component value.


   .. py:property:: y
      :type: pint.Quantity

      Y plane component value.


   .. py:property:: z
      :type: pint.Quantity

      Z plane component value.


   .. py:method:: __eq__(other: Point3D) -> bool

      Equals operator for the ``Point3D`` class.


   .. py:method:: __ne__(other: Point3D) -> bool

      Not equals operator for the ``Point3D`` class.


   .. py:method:: __add__(other: beartype.typing.Union[Point3D, ansys.geometry.core.math.vector.Vector3D]) -> Point3D

      Add operation for the ``Point3D`` class.


   .. py:method:: __sub__(other: beartype.typing.Union[Point3D, ansys.geometry.core.math.vector.Vector3D]) -> Point3D

      Subtraction operation for the ``Point3D`` class.


   .. py:method:: unit() -> pint.Unit

      Get the unit of the object.


   .. py:method:: base_unit() -> pint.Unit

      Get the base unit of the object.


   .. py:method:: transform(matrix: ansys.geometry.core.math.matrix.Matrix44) -> Point3D

      Transform the 3D point with a transformation matrix.

      Notes
      -----
      Transform the ``Point3D`` object by applying the specified 4x4
      transformation matrix and return a new ``Point3D`` object representing the
      transformed point.

      Parameters
      ----------
      matrix : Matrix44
          4x4 transformation matrix to apply to the point.

      Returns
      -------
      Point3D
          New 3D point that is the transformed copy of the original 3D point after applying
          the transformation matrix.



