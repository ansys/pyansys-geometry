


Module ``component``
====================



.. py:module:: ansys.geometry.core.designer.component



Description
-----------

Provides for managing components.




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

   ansys.geometry.core.designer.component.SharedTopologyType
   ansys.geometry.core.designer.component.Component




.. py:class:: SharedTopologyType


   Bases: :py:obj:`enum.Enum`

   Enum for the component shared topologies available in the Geometry service.

   .. py:attribute:: SHARETYPE_NONE
      :value: 0



   .. py:attribute:: SHARETYPE_SHARE
      :value: 1



   .. py:attribute:: SHARETYPE_MERGE
      :value: 2



   .. py:attribute:: SHARETYPE_GROUPS
      :value: 3




.. py:class:: Component(name: str, parent_component: beartype.typing.Union[Component, None], grpc_client: ansys.geometry.core.connection.GrpcClient, template: beartype.typing.Optional[Component] = None, preexisting_id: beartype.typing.Optional[str] = None, master_component: beartype.typing.Optional[ansys.geometry.core.designer.part.MasterComponent] = None, read_existing_comp: bool = False)


   Provides for creating and managing a component.

   This class synchronizes to a design within a supporting Geometry service instance.

   Parameters
   ----------
   name : str
       User-defined label for the new component.
   parent_component : Component or None
       Parent component to place the new component under within the design assembly. The
       default is ``None`` only when dealing with a ``Design`` object.
   grpc_client : GrpcClient
       Active supporting Geometry service instance for design modeling.
   template : Component, default: None
       Template to create this component from. This creates an
       instance component that shares a master with the template component.
   preexisting_id : str, default: None
       ID of a component pre-existing on the server side to use to create the component
       on the client-side data model. If an ID is specified, a new component is not
       created on the server.
   master_component : MasterComponent, default: None
       Master component to use to create a nested component instance instead
       of creating a new conponent.
   read_existing_comp : bool, default: False
       Whether an existing component on the service should be read. This
       parameter is only valid when connecting to an existing service session.
       Otherwise, avoid using this optional parameter.

   .. py:property:: id
      :type: str

      ID of the component.


   .. py:property:: name
      :type: str

      Name of the component.


   .. py:property:: components
      :type: beartype.typing.List[Component]

      List of ``Component`` objects inside of the component.


   .. py:property:: bodies
      :type: beartype.typing.List[ansys.geometry.core.designer.body.Body]

      List of ``Body`` objects inside of the component.


   .. py:property:: beams
      :type: beartype.typing.List[ansys.geometry.core.designer.beam.Beam]

      List of ``Beam`` objects inside of the component.


   .. py:property:: design_points
      :type: beartype.typing.List[ansys.geometry.core.designer.designpoint.DesignPoint]

      List of ``DesignPoint`` objects inside of the component.


   .. py:property:: coordinate_systems
      :type: beartype.typing.List[ansys.geometry.core.designer.coordinate_system.CoordinateSystem]

      List of ``CoordinateSystem`` objects inside of the component.


   .. py:property:: parent_component
      :type: beartype.typing.Union[Component, None]

      Parent of the component.


   .. py:property:: is_alive
      :type: bool

      Whether the component is still alive on the server side.


   .. py:property:: shared_topology
      :type: beartype.typing.Union[SharedTopologyType, None]

      Shared topology type of the component (if any).

      Notes
      -----
      If no shared topology has been set, ``None`` is returned.


   .. py:method:: get_world_transform() -> ansys.geometry.core.math.Matrix44

      Get the full transformation matrix of the component in world space.

      Returns
      -------
      Matrix44
          4x4 transformation matrix of the component in world space.


   .. py:method:: modify_placement(translation: beartype.typing.Optional[ansys.geometry.core.math.Vector3D] = None, rotation_origin: beartype.typing.Optional[ansys.geometry.core.math.Point3D] = None, rotation_direction: beartype.typing.Optional[ansys.geometry.core.math.UnitVector3D] = None, rotation_angle: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real] = 0)

      Apply a translation and/or rotation to the existing placement matrix.

      Notes
      -----
      To reset a component's placement to an identity matrix, see
      :func:`reset_placement()` or call :func:`modify_placement()` with no arguments.

      Parameters
      ----------
      translation : Vector3D, default: None
          Vector that defines the desired translation to the component.
      rotation_origin : Point3D, default: None
          Origin that defines the axis to rotate the component about.
      rotation_direction : UnitVector3D, default: None
          Direction of the axis to rotate the component about.
      rotation_angle : Union[Quantity, Angle, Real], default: 0
          Angle to rotate the component around the axis.


   .. py:method:: reset_placement()

      Reset a component's placement matrix to an identity matrix.

      See :func:`modify_placement()`.


   .. py:method:: add_component(name: str, template: beartype.typing.Optional[Component] = None) -> Component

      Add a new component under this component within the design assembly.

      Parameters
      ----------
      name : str
          User-defined label for the new component.
      template : Component, default: None
          Template to create this component from. This creates an
          instance component that shares a master with the template component.

      Returns
      -------
      Component
          New component with no children in the design assembly.


   .. py:method:: set_shared_topology(share_type: SharedTopologyType) -> None

      Set the shared topology to apply to the component.

      Parameters
      ----------
      share_type : SharedTopologyType
          Shared topology type to assign to the component.


   .. py:method:: extrude_sketch(name: str, sketch: ansys.geometry.core.sketch.Sketch, distance: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real]) -> ansys.geometry.core.designer.body.Body

      Create a solid body by extruding the sketch profile up by a given distance.

      Notes
      -----
      The newly created body is placed under this component within the design assembly.

      Parameters
      ----------
      name : str
          User-defined label for the new solid body.
      sketch : Sketch
          Two-dimensional sketch source for the extrusion.
      distance : Union[Quantity, Distance, Real]
          Distance to extrude the solid body.

      Returns
      -------
      Body
          Extruded body from the given sketch.


   .. py:method:: extrude_face(name: str, face: ansys.geometry.core.designer.face.Face, distance: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance]) -> ansys.geometry.core.designer.body.Body

      Extrude the face profile by a given distance to create a solid body.

      There are no modifications against the body containing the source face.

      Notes
      -----
      The source face can be anywhere within the design component hierarchy.
      Therefore, there is no validation requiring that the face is placed under the
      target component where the body is to be created.

      Parameters
      ----------
      name : str
          User-defined label for the new solid body.
      face : Face
          Target face to use as the source for the new surface.
      distance : Union[Quantity, Distance]
          Distance to extrude the solid body.

      Returns
      -------
      Body
          Extruded solid body.


   .. py:method:: create_surface(name: str, sketch: ansys.geometry.core.sketch.Sketch) -> ansys.geometry.core.designer.body.Body

      Create a surface body with a sketch profile.

      The newly created body is placed under this component within the design assembly.

      Parameters
      ----------
      name : str
          User-defined label for the new surface body.
      sketch : Sketch
          Two-dimensional sketch source for the surface definition.

      Returns
      -------
      Body
          Body (as a planar surface) from the given sketch.


   .. py:method:: create_surface_from_face(name: str, face: ansys.geometry.core.designer.face.Face) -> ansys.geometry.core.designer.body.Body

      Create a surface body based on a face.

      Notes
      -----
      The source face can be anywhere within the design component hierarchy.
      Therefore, there is no validation requiring that the face is placed under the
      target component where the body is to be created.

      Parameters
      ----------
      name : str
          User-defined label for the new surface body.
      face : Face
          Target face to use as the source for the new surface.

      Returns
      -------
      Body
          Surface body.


   .. py:method:: create_coordinate_system(name: str, frame: ansys.geometry.core.math.Frame) -> ansys.geometry.core.designer.coordinate_system.CoordinateSystem

      Create a coordinate system.

      The newly created coordinate system is place under this component
      within the design assembly.

      Parameters
      ----------
      name : str
          User-defined label for the new coordinate system.
      frame : Frame
          Frame defining the coordinate system bounds.

      Returns
      -------
      CoordinateSystem


   .. py:method:: translate_bodies(bodies: beartype.typing.List[ansys.geometry.core.designer.body.Body], direction: ansys.geometry.core.math.UnitVector3D, distance: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real]) -> None

      Translate the geometry bodies in a specified direction by a given distance.

      Notes
      -----
      If the body does not belong to this component (or its children), it
      is not translated.

      Parameters
      ----------
      bodies: List[Body]
          List of bodies to translate by the same distance.
      direction: UnitVector3D
          Direction of the translation.
      distance: Union[Quantity, Distance, Real]
          Magnitude of the translation.

      Returns
      -------
      None


   .. py:method:: create_beams(segments: beartype.typing.List[beartype.typing.Tuple[ansys.geometry.core.math.Point3D, ansys.geometry.core.math.Point3D]], profile: ansys.geometry.core.designer.beam.BeamProfile) -> beartype.typing.List[ansys.geometry.core.designer.beam.Beam]

      Create beams under the component.

      Notes
      -----
      The newly created beams synchronize to a design within a supporting
      Geometry service instance.

      Parameters
      ----------
      segments : List[Tuple[Point3D, Point3D]]
          List of start and end pairs, each specifying a single line segment.
      profile : BeamProfile
          Beam profile to use to create the beams.


   .. py:method:: create_beam(start: ansys.geometry.core.math.Point3D, end: ansys.geometry.core.math.Point3D, profile: ansys.geometry.core.designer.beam.BeamProfile) -> ansys.geometry.core.designer.beam.Beam

      Create a beam under the component.

      The newly created beam synchronizes to a design within a supporting
      Geometry service instance.

      Parameters
      ----------
      start : Point3D
          Starting point of the beam line segment.
      end : Point3D
          Ending point of the beam line segment.
      profile : BeamProfile
          Beam profile to use to create the beam.


   .. py:method:: delete_component(component: beartype.typing.Union[Component, str]) -> None

      Delete a component (itself or its children).

      Notes
      -----
      If the component is not this component (or its children), it
      is not deleted.

      Parameters
      ----------
      component : Union[Component, str]
          ID of the component or instance to delete.


   .. py:method:: delete_body(body: beartype.typing.Union[ansys.geometry.core.designer.body.Body, str]) -> None

      Delete a body belonging to this component (or its children).

      Notes
      -----
      If the body does not belong to this component (or its children), it
      is not deleted.

      Parameters
      ----------
      body : Union[Body, str]
          ID of the body or instance to delete.


   .. py:method:: add_design_point(name: str, point: ansys.geometry.core.math.Point3D) -> ansys.geometry.core.designer.designpoint.DesignPoint

      Create a single design point.

      Parameters
      ----------
      name : str
          User-defined label for the design points.
      points : Point3D
          3D point constituting the design point.


   .. py:method:: add_design_points(name: str, points: beartype.typing.List[ansys.geometry.core.math.Point3D]) -> beartype.typing.List[ansys.geometry.core.designer.designpoint.DesignPoint]

      Create a list of design points.

      Parameters
      ----------
      name : str
          User-defined label for the list of design points.
      points : List[Point3D]
          List of the 3D points that constitute the list of design points.


   .. py:method:: delete_beam(beam: beartype.typing.Union[ansys.geometry.core.designer.beam.Beam, str]) -> None

      Delete an existing beam belonging to this component (or its children).

      Notes
      -----
      If the beam does not belong to this component (or its children), it
      is not deleted.

      Parameters
      ----------
      beam : Union[Beam, str]
          ID of the beam or instance to delete.


   .. py:method:: search_component(id: str) -> beartype.typing.Union[Component, None]

      Search nested components recursively for a component.

      Parameters
      ----------
      id : str
          ID of the component to search for.

      Returns
      -------
      Component
         Component with the requested ID. If this ID is not found, ``None`` is returned.


   .. py:method:: search_body(id: str) -> beartype.typing.Union[ansys.geometry.core.designer.body.Body, None]

      Search bodies in the component and nested components recursively for a body.

      Parameters
      ----------
      id : str
          ID of the body to search for.

      Returns
      -------
      Body
          Body with the requested ID. If the ID is not found, ``None`` is returned.


   .. py:method:: search_beam(id: str) -> beartype.typing.Union[ansys.geometry.core.designer.beam.Beam, None]

      Search beams in the component and nested components recursively for a beam.

      Parameters
      ----------
      id : str
          ID of the beam to search for.

      Returns
      -------
      Union[Beam, None]
          Beam with the requested ID. If the ID is not found, ``None`` is returned.


   .. py:method:: tessellate(merge_component: bool = False, merge_bodies: bool = False) -> beartype.typing.Union[pyvista.PolyData, pyvista.MultiBlock]

      Tessellate the component.

      Parameters
      ----------
      merge_component : bool, default: False
          Whether to merge this component into a single dataset. When ``True``,
          all the individual bodies are effectively combined into a single
          dataset without any hierarchy.
      merge_bodies : bool, default: False
          Whether to merge each body into a single dataset. When ``True``,
          all the faces of each individual body are effectively
          merged into a single dataset without separating faces.

      Returns
      -------
      ~pyvista.PolyData, ~pyvista.MultiBlock
          Merged :class:`pyvista.PolyData` if ``merge_component=True`` or a
          composite dataset.

      Examples
      --------
      Create two stacked bodies and return the tessellation as two merged bodies:

      >>> from ansys.geometry.core.sketch import Sketch
      >>> from ansys.geometry.core import Modeler
      >>> from ansys.geometry.core.math import Point2D, Point3D, Plane
      >>> from ansys.geometry.core.misc import UNITS
      >>> from ansys.geometry.core.plotting import Plotter
      >>> modeler = Modeler("10.54.0.72", "50051")
      >>> sketch_1 = Sketch()
      >>> box = sketch_1.box(
      >>>    Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(5, UNITS.m))
      >>> sketch_1.circle(Point2D([0, 0], UNITS.m), Quantity(25, UNITS.m))
      >>> design = modeler.create_design("MyDesign")
      >>> comp = design.add_component("MyComponent")
      >>> distance = Quantity(10, UNITS.m)
      >>> body = comp.extrude_sketch("Body", sketch=sketch_1, distance=distance)
      >>> sketch_2 = Sketch(Plane([0, 0, 10]))
      >>> box = sketch_2.box(
      >>>    Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(5, UNITS.m))
      >>> circle = sketch_2.circle(Point2D([0, 0], UNITS.m), Quantity(25, UNITS.m))
      >>> body = comp.extrude_sketch("Body", sketch=sketch_2, distance=distance)
      >>> dataset = comp.tessellate(merge_bodies=True)
      >>> dataset
      MultiBlock (0x7ff6bcb511e0)
        N Blocks:     2
        X Bounds:     -25.000, 25.000
        Y Bounds:     -24.991, 24.991
        Z Bounds:     0.000, 20.000


   .. py:method:: plot(merge_component: bool = False, merge_bodies: bool = False, screenshot: beartype.typing.Optional[str] = None, use_trame: beartype.typing.Optional[bool] = None, **plotting_options: beartype.typing.Optional[dict]) -> None

      Plot the component.

      Parameters
      ----------
      merge_component : bool, default: False
          Whether to merge the component into a single dataset. When ``True``,
          all the individual bodies are effectively merged into a single
          dataset without any hierarchy.
      merge_bodies : bool, default: False
          Whether to merge each body into a single dataset. When ``True``,
          all the faces of each individual body are effectively merged
          into a single dataset without separating faces.
      screenshot : str, default: None
          Path for saving a screenshot of the image being represented.
      use_trame : bool, default: None
          Whether to enable the use of `trame <https://kitware.github.io/trame/index.html>`_.
          The default is ``None``, in which case the ``USE_TRAME`` global setting
          is used.
      **plotting_options : dict, default: None
          Keyword arguments for plotting. For allowable keyword arguments, see the

      Examples
      --------
      Create 25 small cylinders in a grid-like pattern on the XY plane and
      plot them. Make the cylinders look metallic by enabling
      physically-based rendering with ``pbr=True``.

      >>> from ansys.geometry.core.misc.units import UNITS as u
      >>> from ansys.geometry.core.sketch import Sketch
      >>> from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
      >>> from ansys.geometry.core import Modeler
      >>> import numpy as np
      >>> modeler = Modeler()
      >>> origin = Point3D([0, 0, 0])
      >>> plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])
      >>> design = modeler.create_design("my-design")
      >>> mycomp = design.add_component("my-comp")
      >>> n = 5
      >>> xx, yy = np.meshgrid(
      ...     np.linspace(-4, 4, n),
      ...     np.linspace(-4, 4, n),
      ... )
      >>> for x, y in zip(xx.ravel(), yy.ravel()):
      ...     sketch = Sketch(plane)
      ...     sketch.circle(Point2D([x, y]), 0.2*u.m)
      ...     mycomp.extrude_sketch(f"body-{x}-{y}", sketch, 1 * u.m)
      >>> mycomp
      ansys.geometry.core.designer.Component 0x2203cc9ec50
          Name                 : my-comp
          Exists               : True
          Parent component     : my-design
          N Bodies             : 25
          N Components         : 0
          N Coordinate Systems : 0
      >>> mycomp.plot(pbr=True, metallic=1.0)


   .. py:method:: __repr__() -> str

      Represent the ``Component`` as a string.



