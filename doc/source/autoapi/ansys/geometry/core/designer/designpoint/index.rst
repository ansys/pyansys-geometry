


Module ``designpoint``
======================



.. py:module:: ansys.geometry.core.designer.designpoint



Description
-----------

Module for creating and managing design points.




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

   ansys.geometry.core.designer.designpoint.DesignPoint




.. py:class:: DesignPoint(id: str, name: str, point: ansys.geometry.core.math.Point3D, parent_component: ansys.geometry.core.designer.component.Component)


   Provides for creating design points in components.

   Parameters
   ----------
   id : str
       Server-defined ID for the design points.
   name : str
       User-defined label for the design points.
   points : Point3D
       3D point constituting the design points.
   parent_component : Component
       Parent component to place the new design point under within the design assembly.

   .. py:property:: id
      :type: str

      ID of the design point.


   .. py:property:: name
      :type: str

      Name of the design point.


   .. py:property:: value
      :type: ansys.geometry.core.math.Point3D

      Value of the design point.


   .. py:property:: parent_component
      :type: beartype.typing.Union[ansys.geometry.core.designer.component.Component, None]

      Component node that the design point is under.


   .. py:method:: __repr__() -> str

      Represent the design points as a string.



