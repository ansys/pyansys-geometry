


Module ``beam``
===============



.. py:module:: ansys.geometry.core.designer.beam



Description
-----------

Provides for creating and managing a beam.




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

   ansys.geometry.core.designer.beam.BeamProfile
   ansys.geometry.core.designer.beam.BeamCircularProfile
   ansys.geometry.core.designer.beam.Beam




.. py:class:: BeamProfile(id: str, name: str)


   Represents a single beam profile organized within the design assembly.

   This profile synchronizes to a design within a supporting Geometry service instance.

   Parameters
   ----------
   id : str
       Server-defined ID for the beam profile.
   name : str
       User-defined label for the beam profile.

   Notes
   -----
   ``BeamProfile`` objects are expected to be created from the ``Design`` object.
   This means that you are not expected to instantiate your own ``BeamProfile``
   object. You should call the specific ``Design`` API for the ``BeamProfile`` desired.

   .. py:property:: id
      :type: str

      ID of the beam profile.


   .. py:property:: name
      :type: str

      Name of the beam profile.



.. py:class:: BeamCircularProfile(id: str, name: str, radius: ansys.geometry.core.misc.Distance, center: ansys.geometry.core.math.Point3D, direction_x: ansys.geometry.core.math.UnitVector3D, direction_y: ansys.geometry.core.math.UnitVector3D)


   Bases: :py:obj:`BeamProfile`

   Represents a single circular beam profile organized within the design assembly.

   This profile synchronizes to a design within a supporting Geometry service instance.

   Parameters
   ----------
   id : str
       Server-defined ID for the beam profile.
   name : str
       User-defined label for the beam profile.
   radius : Distance
       Radius of the circle.
   center: Point3D
       3D point representing the center of the circle.
   direction_x: UnitVector3D
       X-axis direction.
   direction_y: UnitVector3D
       Y-axis direction.

   Notes
   -----
   ``BeamProfile`` objects are expected to be created from the ``Design`` object.
   This means that you are not expected to instantiate your own ``BeamProfile``
   object. You should call the specific ``Design`` API for the ``BeamProfile`` desired.

   .. py:property:: radius
      :type: ansys.geometry.core.misc.Distance

      Radius of the circular beam profile.


   .. py:property:: center
      :type: ansys.geometry.core.math.Point3D

      Center of the circular beam profile.


   .. py:property:: direction_x
      :type: ansys.geometry.core.math.UnitVector3D

      X-axis direction of the circular beam profile.


   .. py:property:: direction_y
      :type: ansys.geometry.core.math.UnitVector3D

      Y-axis direction of the circular beam profile.


   .. py:method:: __repr__() -> str

      Represent the ``BeamCircularProfile`` as a string.



.. py:class:: Beam(id: str, start: ansys.geometry.core.math.Point3D, end: ansys.geometry.core.math.Point3D, profile: BeamProfile, parent_component: ansys.geometry.core.designer.component.Component)


   Represents a simplified solid body with an assigned 2D cross-section.

   This body synchronizes to a design within a supporting Geometry service instance.

   Parameters
   ----------
   id : str
       Server-defined ID for the body.
   name : str
       User-defined label for the body.
   start : Point3D
       Start of the beam line segment.
   end : Point3D
       End of the beam line segment.
   profile : BeamProfile
       Beam profile to use to create the beam.
   parent_component : Component
       Parent component to nest the new beam under within the design assembly.

   .. py:property:: id
      :type: str

      Service-defined ID of the beam.


   .. py:property:: start
      :type: ansys.geometry.core.math.Point3D

      Start of the beam line segment.


   .. py:property:: end
      :type: ansys.geometry.core.math.Point3D

      End of the beam line segment.


   .. py:property:: profile
      :type: BeamProfile

      Beam profile of the beam line segment.


   .. py:property:: parent_component
      :type: beartype.typing.Union[ansys.geometry.core.designer.component.Component, None]

      Component node that the beam is under.


   .. py:property:: is_alive
      :type: bool

      Flag indicating whether the beam is still alive on the server side.


   .. py:method:: __repr__() -> str

      Represent the beam as a string.



