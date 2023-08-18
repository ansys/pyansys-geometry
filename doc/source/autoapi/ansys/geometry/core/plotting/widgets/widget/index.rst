


Module ``widget``
=================



.. py:module:: ansys.geometry.core.plotting.widgets.widget



Description
-----------

Provides the abstract implementation of plotter widgets.




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

   ansys.geometry.core.plotting.widgets.widget.PlotterWidget




.. py:class:: PlotterWidget(plotter: pyvista.Plotter)


   Bases: :py:obj:`abc.ABC`

   Provides an abstract class for plotter widgets.

   Parameters
   ----------
   plotter : ~pyvista.Plotter
       Plotter instance to add the widget to.

   Notes
   -----
   These widgets are intended to be used with PyVista plotter objects.
   More specifically, the way in which this abstraction has been built
   ensures that these widgets are easily integrable with PyGeometry's
   own ``Plotter`` class.

   .. py:property:: plotter
      :type: pyvista.Plotter

      Plotter object the widget is assigned to.


   .. py:method:: callback(state) -> None
      :abstractmethod:

      General callback function for ``PlotterWidget`` objects.


   .. py:method:: update() -> None
      :abstractmethod:

      General update function for ``PlotterWidget`` objects.



