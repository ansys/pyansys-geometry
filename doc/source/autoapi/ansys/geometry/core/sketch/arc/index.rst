


Module ``arc``
==============



.. py:module:: ansys.geometry.core.sketch.arc



Description
-----------

Provides for creating and managing an arc.




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

   ansys.geometry.core.sketch.arc.Arc




.. py:class:: Arc(center: ansys.geometry.core.math.Point2D, start: ansys.geometry.core.math.Point2D, end: ansys.geometry.core.math.Point2D, clockwise: beartype.typing.Optional[bool] = False)


   Bases: :py:obj:`ansys.geometry.core.sketch.edge.SketchEdge`

   Provides for modeling an arc.

   Parameters
   ----------
   center : Point2D
       Center point of the arc.
   start : Point2D
       Starting point of the arc.
   end : Point2D
       Ending point of the arc.
   clockwise : bool, default: False
       Whether the arc spans the clockwise angle between the start and end points.
       When ``False`` (default), the arc spans the counter-clockwise angle. When
       ``True``, the arc spands the clockwise angle.

   .. py:property:: start
      :type: ansys.geometry.core.math.Point2D

      Starting point of the arc line.


   .. py:property:: end
      :type: ansys.geometry.core.math.Point2D

      Ending point of the arc line.


   .. py:property:: length
      :type: pint.Quantity

      Length of the arc.


   .. py:property:: radius
      :type: pint.Quantity

      Radius of the arc.


   .. py:property:: center
      :type: ansys.geometry.core.math.Point2D

      Center point of the arc.


   .. py:property:: angle
      :type: pint.Quantity

      Angle of the arc.


   .. py:property:: is_clockwise
      :type: bool

      Flag indicating whether the rotation of the angle is clockwise.

      Returns
      -------
      bool
          ``True`` if the sense of rotation is clockwise.
          ``False`` if the sense of rotation is counter-clockwise.


   .. py:property:: sector_area
      :type: pint.Quantity

      Area of the sector of the arc.


   .. py:property:: visualization_polydata
      :type: pyvista.PolyData

      VTK polydata representation for PyVista visualization.

      Notes
      -----
      The representation lies in the X/Y plane within
      the standard global Cartesian coordinate system.

      Returns
      -------
      pyvista.PolyData
          VTK pyvista.Polydata configuration.


   .. py:method:: __eq__(other: Arc) -> bool

      Equals operator for the ``Arc`` class.


   .. py:method:: __ne__(other: Arc) -> bool

      Not equals operator for the ``Arc`` class.


   .. py:method:: from_three_points(start: ansys.geometry.core.math.Point2D, inter: ansys.geometry.core.math.Point2D, end: ansys.geometry.core.math.Point2D)
      :classmethod:

      Create an arc from three given points.

      Parameters
      ----------
      start : Point2D
          Starting point of the arc.
      inter : Point2D
          Intermediate point (location) of the arc.
      end : Point2D
          Ending point of the arc.

      Returns
      -------
      Arc
          Arc generated from the three points.



