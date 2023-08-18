


Module ``selection``
====================



.. py:module:: ansys.geometry.core.designer.selection



Description
-----------

Module for creating a named selection.




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

   ansys.geometry.core.designer.selection.NamedSelection




.. py:class:: NamedSelection(name: str, grpc_client: ansys.geometry.core.connection.GrpcClient, bodies: beartype.typing.Optional[beartype.typing.List[ansys.geometry.core.designer.body.Body]] = None, faces: beartype.typing.Optional[beartype.typing.List[ansys.geometry.core.designer.face.Face]] = None, edges: beartype.typing.Optional[beartype.typing.List[ansys.geometry.core.designer.edge.Edge]] = None, beams: beartype.typing.Optional[beartype.typing.List[ansys.geometry.core.designer.beam.Beam]] = None, design_points: beartype.typing.Optional[beartype.typing.List[ansys.geometry.core.designer.designpoint.DesignPoint]] = None, preexisting_id: beartype.typing.Optional[str] = None)


   Represents a single named selection within the design assembly.

   This class synchronizes to a design within a supporting Geometry service instance.

   A named selection organizes one or more design entities together for common actions
   against the entire group.

   Parameters
   ----------
   name : str
       User-defined name for the named selection.
   grpc_client : GrpcClient
       Active supporting Geometry service instance for design modeling.
   bodies : List[Body], default: None
       All bodies to include in the named selection.
   faces : List[Face], default: None
       All faces to include in the named selection.
   edges : List[Edge], default: None
       All edges to include in the named selection.
   beams : List[Beam], default: None
       All beams to include in the named selection.
   design_points : List[DesignPoints], default: None
       All design points to include in the named selection.

   .. py:property:: id
      :type: str

      ID of the named selection.


   .. py:property:: name
      :type: str

      Name of the named selection.



