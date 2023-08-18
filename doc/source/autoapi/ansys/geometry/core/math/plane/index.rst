


Module ``plane``
================



.. py:module:: ansys.geometry.core.math.plane



Description
-----------

Provides primitive representation of a 2D plane in 3D space.




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

   ansys.geometry.core.math.plane.Plane




.. py:class:: Plane(origin: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.point.Point3D] = ZERO_POINT3D, direction_x: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.vector.UnitVector3D, ansys.geometry.core.math.vector.Vector3D] = UNITVECTOR3D_X, direction_y: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.vector.UnitVector3D, ansys.geometry.core.math.vector.Vector3D] = UNITVECTOR3D_Y)


   Bases: :py:obj:`ansys.geometry.core.math.frame.Frame`

   Provides primitive representation of a 2D plane in 3D space.

   Parameters
   ----------
   origin : Union[~numpy.ndarray, RealSequence, Point3D], default: ZERO_POINT3D
       Centered origin of the frame. The default is ``ZERO_POINT3D``, which is the
       Cartesian origin.
   direction_x : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D], default: UNITVECTOR3D_X
       X-axis direction.
   direction_y : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D], default: UNITVECTOR3D_Y
       Y-axis direction.

   .. py:method:: is_point_contained(point: ansys.geometry.core.math.point.Point3D) -> bool

      Check if a 3D point is contained in the plane.

      Parameters
      ----------
      point : Point3D
          :class:`Point3D <ansys.geometry.core.math.point.Point3D>` class to check.

      Returns
      -------
      bool
          ``True`` if the 3D point is contained in the plane, ``False`` otherwise.


   .. py:method:: __eq__(other: Plane) -> bool

      Equals operator for the ``Plane`` class.


   .. py:method:: __ne__(other: Plane) -> bool

      Not equals operator for the ``Plane`` class.



