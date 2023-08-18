


Module ``design``
=================



.. py:module:: ansys.geometry.core.designer.design



Description
-----------

Provides for managing designs.




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

   ansys.geometry.core.designer.design.DesignFileFormat
   ansys.geometry.core.designer.design.Design




.. py:class:: DesignFileFormat


   Bases: :py:obj:`enum.Enum`

   Provides supported file formats that can be downloaded for designs.

   .. py:attribute:: SCDOCX
      :value: ('SCDOCX', None)



   .. py:attribute:: PARASOLID_TEXT
      :value: ('PARASOLID_TEXT',)



   .. py:attribute:: PARASOLID_BIN
      :value: ('PARASOLID_BIN',)



   .. py:attribute:: FMD
      :value: ('FMD',)



   .. py:attribute:: STEP
      :value: ('STEP',)



   .. py:attribute:: IGES
      :value: ('IGES',)



   .. py:attribute:: INVALID
      :value: ('INVALID', None)




.. py:class:: Design(name: str, grpc_client: ansys.geometry.core.connection.GrpcClient, read_existing_design: bool = False)


   Bases: :py:obj:`ansys.geometry.core.designer.component.Component`

   Provides for organizing geometry assemblies.

   This class synchronizes to a supporting Geometry service instance.

   Parameters
   ----------
   name : str
       User-defined label for the design.
   grpc_client : GrpcClient
       Active supporting Geometry service instance for design modeling.
   read_existing_design : bool, default: False
       Whether an existing design on the service should be read. This parameter is
       only valid when connecting to an existing service session. Otherwise, avoid
       using this optional parameter.

   .. py:property:: materials
      :type: beartype.typing.List[ansys.geometry.core.materials.Material]

      List of materials available for the design.


   .. py:property:: named_selections
      :type: beartype.typing.List[ansys.geometry.core.designer.selection.NamedSelection]

      List of named selections available for the design.


   .. py:property:: beam_profiles
      :type: beartype.typing.List[ansys.geometry.core.designer.beam.BeamProfile]

      List of beam profile available for the design.


   .. py:method:: add_material(material: ansys.geometry.core.materials.Material) -> None

      Add a material to the design.

      Parameters
      ----------
      material : Material
          Material to add.


   .. py:method:: save(file_location: beartype.typing.Union[pathlib.Path, str]) -> None

      Save a design to disk on the active Geometry server instance.

      Parameters
      ----------
      file_location : Union[Path, str]
          Location on disk to save the file to.


   .. py:method:: download(file_location: beartype.typing.Union[pathlib.Path, str], format: beartype.typing.Optional[DesignFileFormat] = DesignFileFormat.SCDOCX) -> None

      Download a design from the active Geometry server instance.

      Parameters
      ----------
      file_location : Union[Path, str]
          Location on disk to save the file to.
      format :DesignFileFormat, default: DesignFileFormat.SCDOCX
          Format for the file to save to.


   .. py:method:: create_named_selection(name: str, bodies: beartype.typing.Optional[beartype.typing.List[ansys.geometry.core.designer.body.Body]] = None, faces: beartype.typing.Optional[beartype.typing.List[ansys.geometry.core.designer.face.Face]] = None, edges: beartype.typing.Optional[beartype.typing.List[ansys.geometry.core.designer.edge.Edge]] = None, beams: beartype.typing.Optional[beartype.typing.List[ansys.geometry.core.designer.beam.Beam]] = None, design_points: beartype.typing.Optional[beartype.typing.List[ansys.geometry.core.designer.designpoint.DesignPoint]] = None) -> ansys.geometry.core.designer.selection.NamedSelection

      Create a named selection on the active Geometry server instance.

      Parameters
      ----------
      name : str
          User-defined name for the named selection.
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

      Returns
      -------
      NamedSelection
          Newly created named selection that maintains references to all target entities.


   .. py:method:: delete_named_selection(named_selection: beartype.typing.Union[ansys.geometry.core.designer.selection.NamedSelection, str]) -> None

      Delete a named selection on the active Geometry server instance.

      Parameters
      ----------
      named_selection : Union[NamedSelection, str]
          Name of the named selection or instance.


   .. py:method:: delete_component(component: beartype.typing.Union[ansys.geometry.core.designer.component.Component, str]) -> None

      Delete a component (itself or its children).

      Notes
      -----
      If the component is not this component (or its children), it
      is not deleted.

      Parameters
      ----------
      id : Union[Component, str]
          Name of the component or instance to delete.

      Raises
      ------
      ValueError
          The design itself cannot be deleted.


   .. py:method:: set_shared_topology(share_type: ansys.geometry.core.designer.component.SharedTopologyType) -> None

      Set the shared topology to apply to the component.

      Parameters
      ----------
      share_type : SharedTopologyType
          Shared topology type to assign.

      Raises
      ------
      ValueError
          Shared topology does not apply to a design.


   .. py:method:: add_beam_circular_profile(name: str, radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance], center: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.Point3D] = ZERO_POINT3D, direction_x: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D] = UNITVECTOR3D_X, direction_y: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D] = UNITVECTOR3D_Y) -> ansys.geometry.core.designer.beam.BeamCircularProfile

      Add a new beam circular profile under the design for the creating beams.

      Parameters
      ----------
      name : str
          User-defined label for the new beam circular profile.
      radius : Real
          Radius of the beam circular profile.
      center : Union[~numpy.ndarray, RealSequence, Point3D]
          Center of the beam circular profile.
      direction_x : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
          X-plane direction.
      direction_y : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
          Y-plane direction.


   .. py:method:: add_midsurface_thickness(thickness: pint.Quantity, bodies: beartype.typing.List[ansys.geometry.core.designer.body.Body]) -> None

      Add a mid-surface thickness to a list of bodies.

      Parameters
      ----------
      thickness : Quantity
          Thickness to be assigned.
      bodies : List[Body]
          All bodies to include in the mid-surface thickness assignment.

      Notes
      -----
      Only surface bodies will be eligible for mid-surface thickness assignment.


   .. py:method:: add_midsurface_offset(offset_type: ansys.geometry.core.designer.body.MidSurfaceOffsetType, bodies: beartype.typing.List[ansys.geometry.core.designer.body.Body]) -> None

      Add a mid-surface offset type to a list of bodies.

      Parameters
      ----------
      offset_type : MidSurfaceOffsetType
          Surface offset to be assigned.
      bodies : List[Body]
          All bodies to include in the mid-surface offset assignment.

      Notes
      -----
      Only surface bodies will be eligible for mid-surface offset assignment.


   .. py:method:: delete_beam_profile(beam_profile: beartype.typing.Union[ansys.geometry.core.designer.beam.BeamProfile, str]) -> None

      Remove a beam profile on the active geometry server instance.

      Parameters
      ----------
      beam_profile : Union[BeamProfile, str]
          A beam profile name or instance that should be deleted.


   .. py:method:: __repr__() -> str

      Represent the ``Design`` as a string.



