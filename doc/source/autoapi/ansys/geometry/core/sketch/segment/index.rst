


Module ``segment``
==================



.. py:module:: ansys.geometry.core.sketch.segment



Description
-----------

Provides for creating and managing a segment.




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

   ansys.geometry.core.sketch.segment.SketchSegment




.. py:class:: SketchSegment(start: ansys.geometry.core.math.Point2D, end: ansys.geometry.core.math.Point2D, plane: ansys.geometry.core.math.Plane = Plane())


   Bases: :py:obj:`ansys.geometry.core.sketch.edge.SketchEdge`, :py:obj:`ansys.geometry.core.primitives.Line`

   Provides segment representation of a line.

   Parameters
   ----------
   start : Point2D
       Starting point of the line segment.
   end : Point2D
       Ending point of the line segment.
   plane : Plane, optional
       Plane containing the sketched circle, which is the global XY plane
       by default.

   .. py:property:: start
      :type: ansys.geometry.core.math.Point2D

      Starting point of the segment.


   .. py:property:: end
      :type: ansys.geometry.core.math.Point2D

      Ending point of the segment.


   .. py:property:: length
      :type: pint.Quantity

      Length of the segment.


   .. py:property:: visualization_polydata
      :type: pyvista.PolyData

      VTK polydata representation for PyVista visualization.

      The representation lies in the X/Y plane within
      the standard global Cartesian coordinate system.

      Returns
      -------
      pyvista.PolyData
          VTK pyvista.Polydata configuration.


   .. py:method:: __eq__(other: SketchSegment) -> bool

      Equals operator for the ``SketchSegment`` class.


   .. py:method:: __ne__(other: SketchSegment) -> bool

      Not equals operator for the ``SketchSegment`` class.


   .. py:method:: plane_change(plane: ansys.geometry.core.math.Plane) -> None

      Redefine the plane containing ``SketchSegment`` objects.

      Notes
      -----
      This implies that their 3D definition might suffer changes.

      Parameters
      ----------
      plane : Plane
          Desired new plane that is to contain the sketched segment.



