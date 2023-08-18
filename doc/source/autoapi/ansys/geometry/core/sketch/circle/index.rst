


Module ``circle``
=================



.. py:module:: ansys.geometry.core.sketch.circle



Description
-----------

Provides for creating and managing a circle.




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

   ansys.geometry.core.sketch.circle.SketchCircle




.. py:class:: SketchCircle(center: ansys.geometry.core.math.Point2D, radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], plane: ansys.geometry.core.math.Plane = Plane())


   Bases: :py:obj:`ansys.geometry.core.sketch.face.SketchFace`, :py:obj:`ansys.geometry.core.primitives.Circle`

   Provides for modeling a circle.

   Parameters
   ----------
   center: Point2D
       Center point of the circle.
   radius : Union[Quantity, Distance, Real]
       Radius of the circle.
   plane : Plane, optional
       Plane containing the sketched circle, which is the global XY plane
       by default.

   .. py:property:: center
      :type: ansys.geometry.core.math.Point2D

      Center of the circle.


   .. py:property:: perimeter
      :type: pint.Quantity

      Perimeter of the circle.

      Notes
      -----
      This property resolves the dilemma between using the ``SkethFace.perimeter``
      property and the ``Circle.perimeter`` property.


   .. py:property:: visualization_polydata
      :type: pyvista.PolyData

      VTK polydata representation for PyVista visualization.

      The representation lies in the X/Y plane within
      the standard global Cartesian coordinate system.

      Returns
      -------
      pyvista.PolyData
          VTK pyvista.Polydata configuration.


   .. py:method:: plane_change(plane: ansys.geometry.core.math.Plane) -> None

      Redefine the plane containing the ``SketchCircle`` objects.

      Notes
      -----
      This implies that their 3D definition might suffer changes.

      Parameters
      ----------
      plane : Plane
          Desired new plane that is to contain the sketched circle.



