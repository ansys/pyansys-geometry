


Module ``polygon``
==================



.. py:module:: ansys.geometry.core.sketch.polygon



Description
-----------

Provides for creating and managing a polygon.




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

   ansys.geometry.core.sketch.polygon.Polygon




.. py:class:: Polygon(center: ansys.geometry.core.math.Point2D, inner_radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], sides: int, angle: beartype.typing.Optional[beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real]] = 0)


   Bases: :py:obj:`ansys.geometry.core.sketch.face.SketchFace`

   Provides for modeling regular polygons.

   Parameters
   ----------
   center: Point2D
       Center point of the circle.
   inner_radius : Union[Quantity, Distance, Real]
       Inner radius (apothem) of the polygon.
   sides : int
       Number of sides of the polygon.
   angle : Union[Quantity, Angle, Real], default: 0
       Placement angle for orientation alignment.

   .. py:property:: center
      :type: ansys.geometry.core.math.Point2D

      Center point of the polygon.


   .. py:property:: inner_radius
      :type: pint.Quantity

      Inner radius (apothem) of the polygon.


   .. py:property:: n_sides
      :type: int

      Number of sides of the polygon.


   .. py:property:: angle
      :type: pint.Quantity

      Orientation angle of the polygon.


   .. py:property:: length
      :type: pint.Quantity

      Side length of the polygon.


   .. py:property:: outer_radius
      :type: pint.Quantity

      Outer radius of the polygon.


   .. py:property:: perimeter
      :type: pint.Quantity

      Perimeter of the polygon.


   .. py:property:: area
      :type: pint.Quantity

      Area of the polygon.


   .. py:property:: visualization_polydata
      :type: pyvista.PolyData

      VTK polydata representation for PyVista visualization.

      The representation lies in the X/Y plane within
      the standard global Cartesian coordinate system.

      Returns
      -------
      pyvista.PolyData
          VTK pyvista.Polydata configuration.



