


Module ``ellipse``
==================



.. py:module:: ansys.geometry.core.sketch.ellipse



Description
-----------

Provides for creating and managing an ellipse.




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

   ansys.geometry.core.sketch.ellipse.SketchEllipse




.. py:class:: SketchEllipse(center: ansys.geometry.core.math.Point2D, major_radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], minor_radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], angle: beartype.typing.Optional[beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real]] = 0, plane: ansys.geometry.core.math.Plane = Plane())


   Bases: :py:obj:`ansys.geometry.core.sketch.face.SketchFace`, :py:obj:`ansys.geometry.core.primitives.Ellipse`

   Provides for modeling an ellipse.

   Parameters
   ----------
   center: Point2D
       Center point of the ellipse.
   major_radius : Union[Quantity, Distance, Real]
       Major radius of the ellipse.
   minor_radius : Union[Quantity, Distance, Real]
       Minor radius of the ellipse.
   angle : Union[Quantity, Angle, Real], default: 0
       Placement angle for orientation alignment.
   plane : Plane, optional
       Plane containing the sketched ellipse, which is the global XY plane
       by default.

   .. py:property:: center
      :type: ansys.geometry.core.math.Point2D

      Center point of the ellipse.


   .. py:property:: angle
      :type: pint.Quantity

      Orientation angle of the ellipse.


   .. py:property:: perimeter
      :type: pint.Quantity

      Perimeter of the circle.

      Notes
      -----
      This property resolves the dilemma between using the ``SkethFace.perimeter``
      property and the ``Ellipse.perimeter`` property.


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

      Redefine the plane containing ``SketchEllipse`` objects.

      Notes
      -----
      This implies that their 3D definition might suffer changes.

      Parameters
      ----------
      plane : Plane
          Desired new plane that is to contain the sketched ellipse.



