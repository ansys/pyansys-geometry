


Module ``view_button``
======================



.. py:module:: ansys.geometry.core.plotting.widgets.view_button



Description
-----------

Provides the view button widget for changing the camera view.




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

   ansys.geometry.core.plotting.widgets.view_button.ViewDirection
   ansys.geometry.core.plotting.widgets.view_button.ViewButton




.. py:class:: ViewDirection


   Bases: :py:obj:`enum.Enum`

   Provides an enum with the available views.

   .. py:attribute:: XYPLUS
      :value: (0, '+xy.png', (5, 220))



   .. py:attribute:: XYMINUS
      :value: (1, '-xy.png', (5, 251))



   .. py:attribute:: XZPLUS
      :value: (2, '+xz.png', (5, 282))



   .. py:attribute:: XZMINUS
      :value: (3, '-xz.png', (5, 313))



   .. py:attribute:: YZPLUS
      :value: (4, '+yz.png', (5, 344))



   .. py:attribute:: YZMINUS
      :value: (5, '-yz.png', (5, 375))



   .. py:attribute:: ISOMETRIC
      :value: (6, 'isometric.png', (5, 406))




.. py:class:: ViewButton(plotter: pyvista.Plotter, direction: tuple)


   Bases: :py:obj:`ansys.geometry.core.plotting.widgets.button.Button`

   Provides for changing the view.

   Parameters
   ----------
   plotter : Plotter
       Plotter to draw the buttons on.
   direction : ViewDirection
       Direction of the view.

   .. py:method:: callback(state: bool) -> None

      Change the view depending on button interaction.

      Parameters
      ----------
      state : bool
          State of the button, which is inherited from PyVista. The value is ``True``
          if the button is active.

      Raises
      ------
      NotImplementedError
          Raised if the specified direction is not implemented.



