


Module ``bbox``
===============



.. py:module:: ansys.geometry.core.math.bbox



Description
-----------

Provides for managing a bounding box.




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

   ansys.geometry.core.math.bbox.BoundingBox2D




.. py:class:: BoundingBox2D(x_min: ansys.geometry.core.typing.Real = sys.float_info.max, x_max: ansys.geometry.core.typing.Real = sys.float_info.min, y_min: ansys.geometry.core.typing.Real = sys.float_info.max, y_max: ansys.geometry.core.typing.Real = sys.float_info.min)


   Maintains the X and Y dimensions.

   Parameters
   ----------
   x_min : Real
       Minimum value for the x-dimensional bounds.
   x_max : Real
       Maximum value for the x-dimensional bounds.
   y_min : Real
       Minimum value for the y-dimensional bounds.
   y_max : Real
       Maximum value for the y-dimensional bounds.

   .. py:property:: x_min
      :type: ansys.geometry.core.typing.Real

      Minimum value of X-dimensional bounds.

      Returns
      -------
      Real
          Minimum value of the X-dimensional bounds.


   .. py:property:: x_max
      :type: ansys.geometry.core.typing.Real

      Maximum value of the X-dimensional bounds.

      Returns
      -------
      Real
          Maximum value of the X-dimensional bounds.


   .. py:property:: y_min
      :type: ansys.geometry.core.typing.Real

      Minimum value of Y-dimensional bounds.

      Returns
      -------
      Real
          Minimum value of Y-dimensional bounds.


   .. py:property:: y_max
      :type: ansys.geometry.core.typing.Real

      Maximum value of Y-dimensional bounds.

      Returns
      -------
      Real
          Maximum value of Y-dimensional bounds.


   .. py:method:: add_point(point: ansys.geometry.core.math.point.Point2D) -> None

      Extend the ranges of the bounding box to include a point.

      Notes
      -----
      This method is only applicable if the point components are outside
      the current bounds.

      Parameters
      ----------
      point : Point2D
          Point to include within the bounds.


   .. py:method:: add_point_components(x: ansys.geometry.core.typing.Real, y: ansys.geometry.core.typing.Real) -> None

      Extend the ranges of the bounding box to include the X and Y values.

      Notes
      -----
      This method is only applicable if the point components are outside
      the current bounds.

      Parameters
      ----------
      x : Real
          Point X component to include within the bounds.
      y : Real
          Point Y component to include within the bounds.


   .. py:method:: add_points(points: beartype.typing.List[ansys.geometry.core.math.point.Point2D]) -> None

      Extend the ranges of the bounding box to include given points.

      Parameters
      ----------
      points : List[Point2D]
          List of points to include within the bounds.


   .. py:method:: contains_point(point: ansys.geometry.core.math.point.Point2D) -> bool

      Evaluate whether a provided point lies within the X and Y ranges of the bounds.

      Parameters
      ----------
      point : Point2D
          Point to compare against the bounds.

      Returns
      -------
      bool
          ``True`` if the point is contained in the bounding box. Otherwise, ``False``.


   .. py:method:: contains_point_components(x: ansys.geometry.core.typing.Real, y: ansys.geometry.core.typing.Real) -> bool

      Check if point components are within current X and Y ranges of the bounds.

      Parameters
      ----------
      x : Real
          Point X component to compare against the bounds.
      y : Real
          Point Y component to compare against the bounds.

      Returns
      -------
      bool
          ``True`` if the components are contained in the bounding box. Otherwise, ``False``.


   .. py:method:: __eq__(other: BoundingBox2D) -> bool

      Equals operator for the ``BoundingBox2D`` class.


   .. py:method:: __ne__(other: BoundingBox2D) -> bool

      Not equals operator for the ``BoundingBox2D`` class.



