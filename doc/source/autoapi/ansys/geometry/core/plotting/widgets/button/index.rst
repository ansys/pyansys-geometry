


Module ``button``
=================



.. py:module:: ansys.geometry.core.plotting.widgets.button



Description
-----------

Provides for implementing buttons in PyGeometry.




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

   ansys.geometry.core.plotting.widgets.button.Button




.. py:class:: Button(plotter: pyvista.Plotter, button_config: tuple)


   Bases: :py:obj:`ansys.geometry.core.plotting.widgets.widget.PlotterWidget`

   Provides the abstract class for implementing buttons in PyGeometry.

   Notes
   -----
   This class wraps the PyVista ``add_checkbox_button_widget()`` method.

   Parameters
   ----------
   plotter : Plotter
       Plotter to draw the buttons on.
   button_config : tuple
       Tuple containing the position and the path to the icon of the button.

   .. py:method:: callback(state: bool) -> None
      :abstractmethod:

      Get the functionality of the button, which is implemented by subclasses.

      Parameters
      ----------
      state : bool
          Whether the button is active.


   .. py:method:: update() -> None

      Assign the image that represents the button.



