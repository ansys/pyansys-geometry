


Module ``gears``
================



.. py:module:: ansys.geometry.core.sketch.gears



Description
-----------

Module for creating and managing gears.




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

   ansys.geometry.core.sketch.gears.Gear
   ansys.geometry.core.sketch.gears.DummyGear
   ansys.geometry.core.sketch.gears.SpurGear




.. py:class:: Gear


   Bases: :py:obj:`ansys.geometry.core.sketch.face.SketchFace`

   Provides the base class for sketching gears.

   .. py:property:: visualization_polydata
      :type: pyvista.PolyData

      VTK polydata representation for PyVista visualization.

      The representation lies in the X/Y plane within
      the standard global Cartesian coordinate system.

      Returns
      -------
      pyvista.PolyData
          VTK pyvista.Polydata configuration.



.. py:class:: DummyGear(origin: ansys.geometry.core.math.Point2D, outer_radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], inner_radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], n_teeth: int)


   Bases: :py:obj:`Gear`

   Provides the dummy class for sketching gears.

   Parameters
   ----------
   origin : Point2D
       Origin of the gear.
   outer_radius : Union[Quantity, Distance, Real]
       Outer radius of the gear.
   inner_radius : Union[Quantity, Distance, Real]
       Inner radius of the gear.
   n_teeth : int
       Number of teeth of the gear.


.. py:class:: SpurGear(origin: ansys.geometry.core.math.Point2D, module: ansys.geometry.core.typing.Real, pressure_angle: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real], n_teeth: int)


   Bases: :py:obj:`Gear`

   Provides the class for sketching spur gears.

   Parameters
   ----------
   origin : Point2D
       Origin of the spur gear.
   module : Real
       Module of the spur gear. This is also the ratio between the pitch circle
       diameter in millimeters and the number of teeth.
   pressure_angle : Union[Quantity, Angle, Real]
       Pressure angle of the spur gear.
   n_teeth : int
       Number of teeth of the spur gear.

   .. py:property:: origin
      :type: ansys.geometry.core.math.Point2D

      Origin of the spur gear.


   .. py:property:: module
      :type: ansys.geometry.core.typing.Real

      Module of the spur gear.


   .. py:property:: pressure_angle
      :type: pint.Quantity

      Pressure angle of the spur gear.


   .. py:property:: n_teeth
      :type: int

      Number of teeth of the spur gear.


   .. py:property:: ref_diameter
      :type: ansys.geometry.core.typing.Real

      Reference diameter of the spur gear.


   .. py:property:: base_diameter
      :type: ansys.geometry.core.typing.Real

      Base diameter of the spur gear.


   .. py:property:: addendum
      :type: ansys.geometry.core.typing.Real

      Addendum of the spur gear.


   .. py:property:: dedendum
      :type: ansys.geometry.core.typing.Real

      Dedendum of the spur gear.


   .. py:property:: tip_diameter
      :type: ansys.geometry.core.typing.Real

      Tip diameter of the spur gear.


   .. py:property:: root_diameter
      :type: ansys.geometry.core.typing.Real

      Root diameter of the spur gear.



