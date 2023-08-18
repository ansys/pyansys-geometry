


Module ``part``
===============



.. py:module:: ansys.geometry.core.designer.part



Description
-----------

Module providing fundamental data of an assembly.




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

   ansys.geometry.core.designer.part.Part
   ansys.geometry.core.designer.part.MasterComponent




.. py:class:: Part(id: str, name: str, components: beartype.typing.List[MasterComponent], bodies: beartype.typing.List[ansys.geometry.core.designer.body.MasterBody])


   Represents a part master.

   This class should not be accessed by users. The ``Part`` class holds fundamental
   data of an assembly.

   Parameters
   ----------
   id : str
       Unique identifier for the part.
   name : str
       Name of the part.
   components : List[MasterComponent]
       List of ``MasterComponent`` children that the part contains.
   bodies : List[MasterBody]
       List of ``MasterBody`` children that the part contains. These are master bodies.

   .. py:property:: id
      :type: str

      ID of the part.


   .. py:property:: name
      :type: str

      Name of the part.


   .. py:property:: components
      :type: beartype.typing.List[MasterComponent]

      ``MasterComponent`` children that the part contains.


   .. py:property:: bodies
      :type: beartype.typing.List[ansys.geometry.core.designer.body.MasterBody]

      ``MasterBody`` children that the part contains.

      These are master bodies.


   .. py:method:: __repr__() -> str

      Represent the part as a string.



.. py:class:: MasterComponent(id: str, name: str, part: Part, transform: ansys.geometry.core.math.Matrix44 = IDENTITY_MATRIX44)


   Represents a part occurrence.

   Notes
   -----
   This class should not be accessed by users. It holds the fundamental data of
   an assembly. Master components wrap parts by adding a transform matrix.

   Parameters
   ----------
   id : str
       Unique identifier for the transformed part.
   name : str
       Name of the transformed part.
   part : Part
       Reference to the transformed part's master part.
   transform : Matrix44
       4x4 transformation matrix from the master part.

   .. py:property:: id
      :type: str

      ID of the transformed part.


   .. py:property:: name
      :type: str

      Name of the transformed part.


   .. py:property:: occurrences
      :type: beartype.typing.List[ansys.geometry.core.designer.component.Component]

      List of all occurrences of the component.


   .. py:property:: part
      :type: Part

      Master part of the transformed part.


   .. py:property:: transform
      :type: ansys.geometry.core.math.Matrix44

      4x4 transformation matrix from the master part.


   .. py:method:: __repr__() -> str

      Represent the master component as a string.



