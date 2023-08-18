


Module ``triangle``
===================



.. py:module:: ansys.geometry.core.sketch.triangle



Description
-----------

Provides for creating and managing a triangle.




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

   ansys.geometry.core.sketch.triangle.Triangle




.. py:class:: Triangle(point1: ansys.geometry.core.math.Point2D, point2: ansys.geometry.core.math.Point2D, point3: ansys.geometry.core.math.Point2D)


   Bases: :py:obj:`ansys.geometry.core.sketch.face.SketchFace`

   Provides for modeling 2D triangles.

   Parameters
   ----------
   point1: Point2D
       Point that represents a triangle vertex.
   point2: Point2D
       Point that represents a triangle vertex.
   point3: Point2D
       Point that represents a triangle vertex.

   .. py:property:: point1
      :type: ansys.geometry.core.math.Point2D

      Triangle vertex 1.


   .. py:property:: point2
      :type: ansys.geometry.core.math.Point2D

      Triangle vertex 2.


   .. py:property:: point3
      :type: ansys.geometry.core.math.Point2D

      Triangle vertex 3.


   .. py:property:: visualization_polydata
      :type: pyvista.PolyData

      VTK polydata representation for PyVista visualization.

      The representation lies in the X/Y plane within
      the standard global Cartesian coordinate system.

      Returns
      -------
      pyvista.PolyData
          VTK pyvista.Polydata configuration.



