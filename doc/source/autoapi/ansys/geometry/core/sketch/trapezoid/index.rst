


Module ``trapezoid``
====================



.. py:module:: ansys.geometry.core.sketch.trapezoid



Description
-----------

Provides for creating and managing a trapezoid.




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

   ansys.geometry.core.sketch.trapezoid.Trapezoid




.. py:class:: Trapezoid(width: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], height: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], slant_angle: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real], nonsymmetrical_slant_angle: beartype.typing.Optional[beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real]] = None, center: beartype.typing.Optional[ansys.geometry.core.math.Point2D] = ZERO_POINT2D, angle: beartype.typing.Optional[beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real]] = 0)


   Bases: :py:obj:`ansys.geometry.core.sketch.face.SketchFace`

   Provides for modeling a 2D trapezoid.

   Parameters
   ----------
   width : Union[Quantity, Distance, Real]
       Width of the trapezoid.
   height : Union[Quantity, Distance, Real]
       Height of the trapezoid.
   slant_angle : Union[Quantity, Angle, Real]
       Angle for trapezoid generation.
   nonsymmetrical_slant_angle : Union[Quantity, Angle, Real], default: None
       Asymmetrical slant angles on each side of the trapezoid.
       The default is ``None``, in which case the trapezoid is symmetrical.
   center: Point2D, default: ZERO_POINT2D
       Center point of the trapezoid.
   angle : Union[Quantity, Angle, Real], default: 0
       Placement angle for orientation alignment.

   Notes
   -----
   If a nonsymmetrical slant angle is defined, the slant angle is
   applied to the left-most angle, and the nonsymmetrical slant angle
   is applied to the right-most angle.

   .. py:property:: center
      :type: ansys.geometry.core.math.Point2D

      Center of the trapezoid.


   .. py:property:: width
      :type: pint.Quantity

      Width of the trapezoid.


   .. py:property:: height
      :type: pint.Quantity

      Height of the trapezoid.


   .. py:property:: visualization_polydata
      :type: pyvista.PolyData

      VTK polydata representation for PyVista visualization.

      The representation lies in the X/Y plane within
      the standard global Cartesian coordinate system.

      Returns
      -------
      pyvista.PolyData
          VTK pyvista.Polydata configuration.



