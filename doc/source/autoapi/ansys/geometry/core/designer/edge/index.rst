


Module ``edge``
===============



.. py:module:: ansys.geometry.core.designer.edge



Description
-----------

Module for managing an edge.




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

   ansys.geometry.core.designer.edge.CurveType
   ansys.geometry.core.designer.edge.Edge




.. py:class:: CurveType


   Bases: :py:obj:`enum.Enum`

   Provides values for the curve types supported by the Geometry service.

   .. py:attribute:: CURVETYPE_UNKNOWN
      :value: 0



   .. py:attribute:: CURVETYPE_LINE
      :value: 1



   .. py:attribute:: CURVETYPE_CIRCLE
      :value: 2



   .. py:attribute:: CURVETYPE_ELLIPSE
      :value: 3



   .. py:attribute:: CURVETYPE_NURBS
      :value: 4



   .. py:attribute:: CURVETYPE_PROCEDURAL
      :value: 5




.. py:class:: Edge(id: str, curve_type: CurveType, body: ansys.geometry.core.designer.body.Body, grpc_client: ansys.geometry.core.connection.GrpcClient)


   Represents a single edge of a body within the design assembly.

   This class synchronizes to a design within a supporting Geometry service instance.

   Parameters
   ----------
   id : str
       Server-defined ID for the body.
   curve_type : CurveType
       Type of curve that the edge forms.
   body : Body
       Parent body that the edge constructs.
   grpc_client : GrpcClient
       Active supporting Geometry service instance for design modeling.

   .. py:property:: id
      :type: str

      ID of the edge.


   .. py:property:: length
      :type: pint.Quantity

      Calculated length of the edge.


   .. py:property:: curve_type
      :type: CurveType

      Curve type of the edge.


   .. py:property:: faces
      :type: beartype.typing.List[ansys.geometry.core.designer.face.Face]

      Faces that contain the edge.



