


Module ``face``
===============



.. py:module:: ansys.geometry.core.sketch.face



Description
-----------

Provides for creating and managing a face (closed 2D sketch).




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

   ansys.geometry.core.sketch.face.SketchFace




.. py:class:: SketchFace


   Provides for modeling a face.

   .. py:property:: edges
      :type: beartype.typing.List[ansys.geometry.core.sketch.edge.SketchEdge]

      List of all component edges forming the face.


   .. py:property:: perimeter
      :type: pint.Quantity

      Perimeter of the face.


   .. py:property:: visualization_polydata
      :type: pyvista.PolyData

      VTK polydata representation for PyVista visualization.

      The representation lies in the X/Y plane within
      the standard global Cartesian coordinate system.

      Returns
      -------
      pyvista.PolyData
          VTK pyvista.Polydata configuration.


   .. py:method:: plane_change(plane: ansys.geometry.core.math.Plane) -> None

      Redefine the plane containing ``SketchFace`` objects.

      Notes
      -----
      This implies that their 3D definition might suffer changes. This method does
      nothing by default. It is required to be implemented in child ``SketchFace`` classes.

      Parameters
      ----------
      plane : Plane
          Desired new plane that is to contain the sketched face.



