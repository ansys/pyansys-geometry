


Module ``trame_gui``
====================



.. py:module:: ansys.geometry.core.plotting.trame_gui



Description
-----------

Module for using trame <https://kitware.github.io/trame/index.html>`_ for visualization.




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

   ansys.geometry.core.plotting.trame_gui.TrameVisualizer




.. py:class:: TrameVisualizer


   Defines the trame layout view.

   .. py:method:: set_scene(plotter)

      Set the trame layout view and the mesh to show through the PyVista plotter.

      Parameters
      ----------
      plotter : pv.Plotter
          PyVista plotter with the rendered mesh.


   .. py:method:: show()

      Start the trame server and show the mesh.



