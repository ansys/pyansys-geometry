


Module ``displace_arrows``
==========================



.. py:module:: ansys.geometry.core.plotting.widgets.displace_arrows



Description
-----------

Provides the displacement arrows widget for the PyVista plotter.




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

   ansys.geometry.core.plotting.widgets.displace_arrows.CameraPanDirection
   ansys.geometry.core.plotting.widgets.displace_arrows.DisplacementArrow




.. py:class:: CameraPanDirection


   Bases: :py:obj:`enum.Enum`

   Provides an enum with the available movement directions of the camera.

   .. py:attribute:: XUP
      :value: (0, 'upxarrow.png', (5, 170))



   .. py:attribute:: XDOWN
      :value: (1, 'downarrow.png', (5, 130))



   .. py:attribute:: YUP
      :value: (2, 'upyarrow.png', (35, 170))



   .. py:attribute:: YDOWN
      :value: (3, 'downarrow.png', (35, 130))



   .. py:attribute:: ZUP
      :value: (4, 'upzarrow.png', (65, 170))



   .. py:attribute:: ZDOWN
      :value: (5, 'downarrow.png', (65, 130))




.. py:class:: DisplacementArrow(plotter: pyvista.Plotter, direction: CameraPanDirection)


   Bases: :py:obj:`ansys.geometry.core.plotting.widgets.button.Button`

   Defines the arrow to draw and what it is to do.

   Parameters
   ----------
   plotter : Plotter
       Plotter to draw the buttons on.
   direction : CameraPanDirection
       Direction that the camera is to move.

   .. py:method:: callback(state: bool) -> None

      Move the camera in the direction defined by the button.

      Parameters
      ----------
      state : bool
          State of the button, which is inherited from PyVista. The value is ``True``
          if the button is active. However, this parameter is unused by this ``callback``
          method.



