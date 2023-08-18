


Module ``coordinate_system``
============================



.. py:module:: ansys.geometry.core.designer.coordinate_system



Description
-----------

Provides for managing a user-defined coordinate system.




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

   ansys.geometry.core.designer.coordinate_system.CoordinateSystem




.. py:class:: CoordinateSystem(name: str, frame: ansys.geometry.core.math.Frame, parent_component: ansys.geometry.core.designer.component.Component, grpc_client: ansys.geometry.core.connection.GrpcClient, preexisting_id: beartype.typing.Optional[str] = None)


   Represents a user-defined coordinate system within the design assembly.

   This class synchronizes to a design within a supporting Geometry
   service instance.

   Parameters
   ----------
   name : str
       User-defined label for the coordinate system.
   frame : Frame
       Frame defining the coordinate system bounds.
   parent_component : Component, default: Component
       Parent component the coordinate system is assigned against.
   grpc_client : GrpcClient
       Active supporting Geometry service instance for design modeling.

   .. py:property:: id
      :type: str

      ID of the coordinate system.


   .. py:property:: name
      :type: str

      Name of the coordinate system.


   .. py:property:: frame
      :type: ansys.geometry.core.math.Frame

      Frame of the coordinate system.


   .. py:property:: parent_component
      :type: ansys.geometry.core.designer.component.Component

      Parent component of the coordinate system.


   .. py:property:: is_alive
      :type: bool

      Flag indicating if coordinate system is still alive on the server side.


   .. py:method:: __repr__() -> str

      Represent the coordinate system as a string.



