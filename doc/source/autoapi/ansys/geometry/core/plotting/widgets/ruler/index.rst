


Module ``ruler``
================



.. py:module:: ansys.geometry.core.plotting.widgets.ruler



Description
-----------

Provides the ruler widget for the PyGeometry plotter.




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

   ansys.geometry.core.plotting.widgets.ruler.Ruler




.. py:class:: Ruler(plotter: pyvista.Plotter)


   Bases: :py:obj:`ansys.geometry.core.plotting.widgets.widget.PlotterWidget`

   Provides the ruler widget for the PyGeometry ``Plotter`` class.

   Parameters
   ----------
   plotter : ~pyvista.Plotter
       Provides the plotter to add the ruler widget to.

   .. py:method:: callback(state: bool) -> None

      Remove or add the ruler widget actor upon click.

      Notes
      -----
      This method provides a callback function for the ruler widet.
      It is called every time the ruler widget is clicked.

      Parameters
      ----------
      state : bool
          State of the button, which is inherited from PyVista. The value is ``True``
          if the button is active.


   .. py:method:: update() -> None

      Define the configuration and representation of the ruler widget button.



