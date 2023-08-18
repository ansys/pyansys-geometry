


Module ``edge``
===============



.. py:module:: ansys.geometry.core.sketch.edge



Description
-----------

Provides for creating and managing an edge.




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

   ansys.geometry.core.sketch.edge.SketchEdge




.. py:class:: SketchEdge


   Provides for modeling edges forming sketched shapes.

   .. py:property:: start
      :type: ansys.geometry.core.math.Point2D
      :abstractmethod:

      Starting point of the edge.


   .. py:property:: end
      :type: ansys.geometry.core.math.Point2D
      :abstractmethod:

      Ending point of the edge.


   .. py:property:: length
      :type: pint.Quantity
      :abstractmethod:

      Length of the edge.


   .. py:property:: visualization_polydata
      :type: pyvista.PolyData
      :abstractmethod:

      VTK polydata representation for PyVista visualization.

      The representation lies in the X/Y plane within
      the standard global Cartesian coordinate system.

      Returns
      -------
      pyvista.PolyData
          VTK pyvista.Polydata configuration.


   .. py:method:: plane_change(plane: ansys.geometry.core.math.Plane) -> None

      Redefine the plane containing ``SketchEdge`` objects.

      Notes
      -----
      This implies that their 3D definition might suffer changes. By default, this
      metho does nothing. It is required to be implemented in child ``SketchEdge``
      classes.

      Parameters
      ----------
      plane : Plane
          Desired new plane that is to contain the sketched edge.



