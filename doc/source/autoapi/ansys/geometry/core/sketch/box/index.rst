


Module ``box``
==============



.. py:module:: ansys.geometry.core.sketch.box



Description
-----------

Provides for creating and managing a box (quadrilateral).




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

   ansys.geometry.core.sketch.box.Box




.. py:class:: Box(center: ansys.geometry.core.math.Point2D, width: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], height: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], angle: beartype.typing.Optional[beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real]] = 0)


   Bases: :py:obj:`ansys.geometry.core.sketch.face.SketchFace`

   Provides for modeling a box.

   Parameters
   ----------
   center: Point2D
       Center point of the box.
   width : Union[Quantity, Distance, Real]
       Width of the box.
   height : Union[Quantity, Distance, Real]
       Height of the box.
   angle : Union[Quantity, Angle, Real], default: 0
       Placement angle for orientation alignment.

   .. py:property:: center
      :type: ansys.geometry.core.math.Point2D

      Center point of the box.


   .. py:property:: width
      :type: pint.Quantity

      Width of the box.


   .. py:property:: height
      :type: pint.Quantity

      Height of the box.


   .. py:property:: perimeter
      :type: pint.Quantity

      Perimeter of the box.


   .. py:property:: area
      :type: pint.Quantity

      Area of the box.


   .. py:property:: visualization_polydata
      :type: pyvista.PolyData

      VTK polydata representation for PyVista visualization.

      The representation lies in the X/Y plane within
      the standard global cartesian coordinate system.

      Returns
      -------
      pyvista.PolyData
          VTK pyvista.Polydata configuration.



