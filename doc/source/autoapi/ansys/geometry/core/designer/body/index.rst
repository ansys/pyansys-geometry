


Module ``body``
===============



.. py:module:: ansys.geometry.core.designer.body



Description
-----------

Provides for managing a body.




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

   ansys.geometry.core.designer.body.MidSurfaceOffsetType
   ansys.geometry.core.designer.body.IBody
   ansys.geometry.core.designer.body.MasterBody
   ansys.geometry.core.designer.body.Body




.. py:class:: MidSurfaceOffsetType


   Bases: :py:obj:`enum.Enum`

   Provides values for mid-surface offsets supported by the Geometry service.

   .. py:attribute:: MIDDLE
      :value: 0



   .. py:attribute:: TOP
      :value: 1



   .. py:attribute:: BOTTOM
      :value: 2



   .. py:attribute:: VARIABLE
      :value: 3



   .. py:attribute:: CUSTOM
      :value: 4




.. py:class:: IBody


   Bases: :py:obj:`abc.ABC`

   Defines the common methods for a body, providing the abstract body interface.

   Both the ``MasterBody`` class and ``Body`` class both inherit from the ``IBody``
   class. All child classes must implement all abstract methods.

   .. py:method:: id() -> str
      :abstractmethod:

      Get the ID of the body as a string.


   .. py:method:: name() -> str
      :abstractmethod:

      Get the name of the body.


   .. py:method:: faces() -> beartype.typing.List[ansys.geometry.core.designer.face.Face]
      :abstractmethod:

      Get a list of all faces within the body.

      Returns
      -------
      List[Face]


   .. py:method:: edges() -> beartype.typing.List[ansys.geometry.core.designer.edge.Edge]
      :abstractmethod:

      Get a list of all edges within the body.

      Returns
      -------
      List[Edge]


   .. py:method:: is_alive() -> bool
      :abstractmethod:

      Check if the body is still alive and has not been deleted.


   .. py:method:: is_surface() -> bool
      :abstractmethod:

      Check if the body is a planar body.


   .. py:method:: surface_thickness() -> beartype.typing.Union[pint.Quantity, None]
      :abstractmethod:

      Get the surface thickness of a surface body.

      Notes
      -----
      This method is only for surface-type bodies that have been assigned a surface thickness.


   .. py:method:: surface_offset() -> beartype.typing.Union[ansys.geometry.core.designer.design.MidSurfaceOffsetType, None]
      :abstractmethod:

      Get the surface offset type of a surface body.

      Notes
      -----
      This method is only for surface-type bodies that have been assigned a surface offset.


   .. py:method:: volume() -> pint.Quantity
      :abstractmethod:

      Calculate the volume of the body.

      Notes
      -----
      When dealing with a planar surface, a value of ``0`` is returned as a volume.


   .. py:method:: assign_material(material: ansys.geometry.core.materials.Material) -> None
      :abstractmethod:

      Assign a material against the design in the active Geometry service instance.

      Parameters
      ----------
      material : Material
          Source material data.


   .. py:method:: add_midsurface_thickness(thickness: pint.Quantity) -> None
      :abstractmethod:

      Add a mid-surface thickness to a surface body.

      Parameters
      ----------
      thickness : Quantity
          Thickness to assign.

      Notes
      -----
      Only surface bodies are eligible for mid-surface thickness assignment.


   .. py:method:: add_midsurface_offset(offset: ansys.geometry.core.designer.design.MidSurfaceOffsetType) -> None
      :abstractmethod:

      Add a mid-surface offset to a surface body.

      Parameters
      ----------
      offset_type : MidSurfaceOffsetType
          Surface offset to assign.

      Notes
      -----
      Only surface bodies are eligible for mid-surface offset assignment.


   .. py:method:: imprint_curves(faces: beartype.typing.List[ansys.geometry.core.designer.face.Face], sketch: ansys.geometry.core.sketch.Sketch) -> beartype.typing.Tuple[beartype.typing.List[ansys.geometry.core.designer.edge.Edge], beartype.typing.List[ansys.geometry.core.designer.face.Face]]
      :abstractmethod:

      Imprint all specified geometries onto specified faces of the body.

      Parameters
      ----------
      faces: List[Face]
          List of faces to imprint the curves of the sketch onto.
      sketch: Sketch
          All curves to imprint on the faces.

      Returns
      -------
      Tuple[List[Edge], List[Face]]
          All impacted edges and faces from the imprint operation.


   .. py:method:: project_curves(direction: ansys.geometry.core.math.UnitVector3D, sketch: ansys.geometry.core.sketch.Sketch, closest_face: bool, only_one_curve: beartype.typing.Optional[bool] = False) -> beartype.typing.List[ansys.geometry.core.designer.face.Face]
      :abstractmethod:

      Project all specified geometries onto the body.

      Parameters
      ----------
      direction: UnitVector3D
          Direction of the projection.
      sketch: Sketch
          All curves to project on the body.
      closest_face: bool
          Whether to target the closest face with the projection.
      only_one_curve: bool, default: False
          Whether to project only one curve of the entire sketch. When
          ``True``, only one curve is projected.

      Notes
      -----
      The ``only_one_curve`` parameter allows you to optimize the server call because
      projecting curves is an expensive operation. This reduces the workload on the
      server side.

      Returns
      -------
      List[Face]
          All faces from the project curves operation.


   .. py:method:: imprint_projected_curves(direction: ansys.geometry.core.math.UnitVector3D, sketch: ansys.geometry.core.sketch.Sketch, closest_face: bool, only_one_curve: beartype.typing.Optional[bool] = False) -> beartype.typing.List[ansys.geometry.core.designer.face.Face]
      :abstractmethod:

      Project and imprint specified geometries onto the body.

      This method combines the ``project_curves()`` and ``imprint_curves()`` method into
      one method. It is much more performant than calling them back-to-back when dealing
      with many curves. Because it is a specialized function, this method only returns
      the faces (and not the edges) from the imprint operation.

      Parameters
      ----------
      direction: UnitVector3D
          Direction of the projection.
      sketch: Sketch
          All curves to project on the body.
      closest_face: bool
          Whether to target the closest face with the projection.
      only_one_curve: bool, default: False
          Whether to project only one curve of the entire sketch. When
          ``True``, only one curve is projected.

      Notes
      -----
      The ``only_one_curve`` parameter allows you to optimize the server call because
      projecting curves is an expensive operation. This reduces the workload on the
      server side.

      Returns
      -------
      List[Face]
          All imprinted faces from the operation.


   .. py:method:: translate(direction: ansys.geometry.core.math.UnitVector3D, distance: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real]) -> None
      :abstractmethod:

      Translate the geometry body in the specified direction by a given distance.

      Parameters
      ----------
      direction: UnitVector3D
          Direction of the translation.
      distance: Union[Quantity, Distance, Real]
          Distance (magnitude) of the translation.

      Returns
      -------
      None


   .. py:method:: copy(parent: ansys.geometry.core.designer.component.Component, name: str = None) -> Body
      :abstractmethod:

      Create a copy of the body and place it under the specified parent component.

      Parameters
      ----------
      parent: Component
          Parent component to place the new body under within the design assembly.
      name: str
          Name to give the new body.

      Returns
      -------
      Body
          Copy of the body.


   .. py:method:: tessellate(merge: beartype.typing.Optional[bool] = False) -> beartype.typing.Union[pyvista.PolyData, pyvista.MultiBlock]
      :abstractmethod:

      Tessellate the body and return the geometry as triangles.

      Parameters
      ----------
      merge : bool, default: False
          Whether to merge the body into a single mesh. When ``False`` (default), the
          number of triangles are preserved and only the topology is merged.
          When ``True``, the individual faces of the tessellation are merged.

      Returns
      -------
      ~pyvista.PolyData, ~pyvista.MultiBlock
          Merged :class:`pyvista.PolyData` if ``merge=True`` or a composite dataset.

      Examples
      --------
      Extrude a box centered at the origin to create a rectangular body and
      tessellate it:

      >>> from ansys.geometry.core.misc.units import UNITS as u
      >>> from ansys.geometry.core.sketch import Sketch
      >>> from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
      >>> from ansys.geometry.core import Modeler
      >>> modeler = Modeler()
      >>> origin = Point3D([0, 0, 0])
      >>> plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 0, 1])
      >>> sketch = Sketch(plane)
      >>> box = sketch.box(Point2D([2, 0]), 4, 4)
      >>> design = modeler.create_design("my-design")
      >>> my_comp = design.add_component("my-comp")
      >>> body = my_comp.extrude_sketch("my-sketch", sketch, 1 * u.m)
      >>> blocks = body.tessellate()
      >>> blocks
      >>> MultiBlock (0x7f94ec757460)
           N Blocks:  6
           X Bounds:  0.000, 4.000
           Y Bounds:  -1.000, 0.000
           Z Bounds:  -0.500, 4.500

      Merge the body:

      >>> mesh = body.tessellate(merge=True)
      >>> mesh
      PolyData (0x7f94ec75f3a0)
        N Cells:      12
        N Points:     24
        X Bounds:     0.000e+00, 4.000e+00
        Y Bounds:     -1.000e+00, 0.000e+00
        Z Bounds:     -5.000e-01, 4.500e+00
        N Arrays:     0


   .. py:method:: plot(merge: bool = False, screenshot: beartype.typing.Optional[str] = None, use_trame: beartype.typing.Optional[bool] = None, **plotting_options: beartype.typing.Optional[dict]) -> None
      :abstractmethod:

      Plot the body.

      Parameters
      ----------
      merge : bool, default: False
          Whether to merge the body into a single mesh. When ``False`` (default),
          the number of triangles are preserved and only the topology is merged.
          When ``True``, the individual faces of the tessellation are merged.
      screenshot : str, default: None
          Path for saving a screenshot of the image that is being represented.
      use_trame : bool, default: None
          Whether to enable the use of `trame <https://kitware.github.io/trame/index.html>`_.
          The default is ``None``, in which case the ``USE_TRAME`` global setting
          is used.
      **plotting_options : dict, default: None
          Keyword arguments for plotting. For allowable keyword arguments, see the
          :func:`pyvista.Plotter.add_mesh` method.

      Examples
      --------
      Extrude a box centered at the origin to create rectangular body and
      plot it:

      >>> from ansys.geometry.core.misc.units import UNITS as u
      >>> from ansys.geometry.core.sketch import Sketch
      >>> from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
      >>> from ansys.geometry.core import Modeler
      >>> modeler = Modeler()
      >>> origin = Point3D([0, 0, 0])
      >>> plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 0, 1])
      >>> sketch = Sketch(plane)
      >>> box = sketch.box(Point2D([2, 0]), 4, 4)
      >>> design = modeler.create_design("my-design")
      >>> mycomp = design.add_component("my-comp")
      >>> body = mycomp.extrude_sketch("my-sketch", sketch, 1 * u.m)
      >>> body.plot()

      Plot the body and color each face individually:

      >>> body.plot(multi_colors=True)


   .. py:method:: intersect(other: Body) -> None

      Intersect two bodies.

      Notes
      -----
      The ``self`` parameter is directly modified with the result, and
      the ``other`` parameter is consumed. Thus, it is important to make
      copies if needed.

      Parameters
      ----------
      other : Body
          Body to intersect with.

      Raises
      ------
      ValueError
          If the bodies do not intersect.


   .. py:method:: subtract(other: Body) -> None

      Subtract two bodies.

      Notes
      -----
      The ``self`` parameter is directly modified with the result, and
      the ``other`` parameter is consumed. Thus, it is important to make
      copies if needed.

      Parameters
      ----------
      other : Body
          Body to subtract from the ``self`` parameter.

      Raises
      ------
      ValueError
          If the subtraction results in an empty (complete) subtraction.


   .. py:method:: unite(other: Body) -> None

      Unite two bodies.

      Notes
      -----
      The ``self`` parameter is directly modified with the result, and
      the ``other`` parameter is consumed. Thus, it is important to make
      copies if needed.

      Parameters
      ----------
      other : Body
          Body to unite with the ``self`` parameter.



.. py:class:: MasterBody(id: str, name: str, grpc_client: ansys.geometry.core.connection.GrpcClient, is_surface: bool = False)


   Bases: :py:obj:`IBody`

   Represents solids and surfaces organized within the design assembly.

   Solids and surfaces synchronize to a design within a supporting Geometry service instance.

   Parameters
   ----------
   id : str
       Server-defined ID for the body.
   name : str
       User-defined label for the body.
   parent_component : Component
       Parent component to place the new component under within the design assembly.
   grpc_client : GrpcClient
       Active supporting geometry service instance for design modeling.
   is_surface : bool, default: False
       Whether the master body is a surface or an 3D object (with volume). The default
       is ``False``, in which case the master body is a surface. When ``True``, the
       master body is a 3D object (with volume).

   .. py:property:: id
      :type: str

      Get the ID of the body as a string.


   .. py:property:: name
      :type: str

      Get the name of the body.


   .. py:property:: is_surface
      :type: bool

      Check if the body is a planar body.


   .. py:property:: surface_thickness
      :type: beartype.typing.Union[pint.Quantity, None]

      Get the surface thickness of a surface body.

      Notes
      -----
      This method is only for surface-type bodies that have been assigned a surface thickness.


   .. py:property:: surface_offset
      :type: beartype.typing.Union[ansys.geometry.core.designer.design.MidSurfaceOffsetType, None]

      Get the surface offset type of a surface body.

      Notes
      -----
      This method is only for surface-type bodies that have been assigned a surface offset.


   .. py:property:: faces
      :type: beartype.typing.List[ansys.geometry.core.designer.face.Face]

      Get a list of all faces within the body.

      Returns
      -------
      List[Face]


   .. py:property:: edges
      :type: beartype.typing.List[ansys.geometry.core.designer.edge.Edge]

      Get a list of all edges within the body.

      Returns
      -------
      List[Edge]


   .. py:property:: is_alive
      :type: bool

      Check if the body is still alive and has not been deleted.


   .. py:property:: volume
      :type: pint.Quantity

      Calculate the volume of the body.

      Notes
      -----
      When dealing with a planar surface, a value of ``0`` is returned as a volume.


   .. py:method:: reset_tessellation_cache()

      Decorate ``MasterBody`` methods that require a tessellation cache update.

      Parameters
      ----------
      func : method
          Method to call.

      Returns
      -------
      Any
          Output of the method, if any.


   .. py:method:: assign_material(material: ansys.geometry.core.materials.Material) -> None

      Assign a material against the design in the active Geometry service instance.

      Parameters
      ----------
      material : Material
          Source material data.


   .. py:method:: add_midsurface_thickness(thickness: pint.Quantity) -> None

      Add a mid-surface thickness to a surface body.

      Parameters
      ----------
      thickness : Quantity
          Thickness to assign.

      Notes
      -----
      Only surface bodies are eligible for mid-surface thickness assignment.


   .. py:method:: add_midsurface_offset(offset: ansys.geometry.core.designer.design.MidSurfaceOffsetType) -> None

      Add a mid-surface offset to a surface body.

      Parameters
      ----------
      offset_type : MidSurfaceOffsetType
          Surface offset to assign.

      Notes
      -----
      Only surface bodies are eligible for mid-surface offset assignment.


   .. py:method:: imprint_curves(faces: beartype.typing.List[ansys.geometry.core.designer.face.Face], sketch: ansys.geometry.core.sketch.Sketch) -> beartype.typing.Tuple[beartype.typing.List[ansys.geometry.core.designer.edge.Edge], beartype.typing.List[ansys.geometry.core.designer.face.Face]]
      :abstractmethod:

      Imprint all specified geometries onto specified faces of the body.

      Parameters
      ----------
      faces: List[Face]
          List of faces to imprint the curves of the sketch onto.
      sketch: Sketch
          All curves to imprint on the faces.

      Returns
      -------
      Tuple[List[Edge], List[Face]]
          All impacted edges and faces from the imprint operation.


   .. py:method:: project_curves(direction: ansys.geometry.core.math.UnitVector3D, sketch: ansys.geometry.core.sketch.Sketch, closest_face: bool, only_one_curve: beartype.typing.Optional[bool] = False) -> beartype.typing.List[ansys.geometry.core.designer.face.Face]
      :abstractmethod:

      Project all specified geometries onto the body.

      Parameters
      ----------
      direction: UnitVector3D
          Direction of the projection.
      sketch: Sketch
          All curves to project on the body.
      closest_face: bool
          Whether to target the closest face with the projection.
      only_one_curve: bool, default: False
          Whether to project only one curve of the entire sketch. When
          ``True``, only one curve is projected.

      Notes
      -----
      The ``only_one_curve`` parameter allows you to optimize the server call because
      projecting curves is an expensive operation. This reduces the workload on the
      server side.

      Returns
      -------
      List[Face]
          All faces from the project curves operation.


   .. py:method:: imprint_projected_curves(direction: ansys.geometry.core.math.UnitVector3D, sketch: ansys.geometry.core.sketch.Sketch, closest_face: bool, only_one_curve: beartype.typing.Optional[bool] = False) -> beartype.typing.List[ansys.geometry.core.designer.face.Face]
      :abstractmethod:

      Project and imprint specified geometries onto the body.

      This method combines the ``project_curves()`` and ``imprint_curves()`` method into
      one method. It is much more performant than calling them back-to-back when dealing
      with many curves. Because it is a specialized function, this method only returns
      the faces (and not the edges) from the imprint operation.

      Parameters
      ----------
      direction: UnitVector3D
          Direction of the projection.
      sketch: Sketch
          All curves to project on the body.
      closest_face: bool
          Whether to target the closest face with the projection.
      only_one_curve: bool, default: False
          Whether to project only one curve of the entire sketch. When
          ``True``, only one curve is projected.

      Notes
      -----
      The ``only_one_curve`` parameter allows you to optimize the server call because
      projecting curves is an expensive operation. This reduces the workload on the
      server side.

      Returns
      -------
      List[Face]
          All imprinted faces from the operation.


   .. py:method:: translate(direction: ansys.geometry.core.math.UnitVector3D, distance: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real]) -> None

      Translate the geometry body in the specified direction by a given distance.

      Parameters
      ----------
      direction: UnitVector3D
          Direction of the translation.
      distance: Union[Quantity, Distance, Real]
          Distance (magnitude) of the translation.

      Returns
      -------
      None


   .. py:method:: copy(parent: ansys.geometry.core.designer.component.Component, name: str = None) -> Body

      Create a copy of the body and place it under the specified parent component.

      Parameters
      ----------
      parent: Component
          Parent component to place the new body under within the design assembly.
      name: str
          Name to give the new body.

      Returns
      -------
      Body
          Copy of the body.


   .. py:method:: tessellate(merge: beartype.typing.Optional[bool] = False, transform: ansys.geometry.core.math.Matrix44 = IDENTITY_MATRIX44) -> beartype.typing.Union[pyvista.PolyData, pyvista.MultiBlock]

      Tessellate the body and return the geometry as triangles.

      Parameters
      ----------
      merge : bool, default: False
          Whether to merge the body into a single mesh. When ``False`` (default), the
          number of triangles are preserved and only the topology is merged.
          When ``True``, the individual faces of the tessellation are merged.

      Returns
      -------
      ~pyvista.PolyData, ~pyvista.MultiBlock
          Merged :class:`pyvista.PolyData` if ``merge=True`` or a composite dataset.

      Examples
      --------
      Extrude a box centered at the origin to create a rectangular body and
      tessellate it:

      >>> from ansys.geometry.core.misc.units import UNITS as u
      >>> from ansys.geometry.core.sketch import Sketch
      >>> from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
      >>> from ansys.geometry.core import Modeler
      >>> modeler = Modeler()
      >>> origin = Point3D([0, 0, 0])
      >>> plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 0, 1])
      >>> sketch = Sketch(plane)
      >>> box = sketch.box(Point2D([2, 0]), 4, 4)
      >>> design = modeler.create_design("my-design")
      >>> my_comp = design.add_component("my-comp")
      >>> body = my_comp.extrude_sketch("my-sketch", sketch, 1 * u.m)
      >>> blocks = body.tessellate()
      >>> blocks
      >>> MultiBlock (0x7f94ec757460)
           N Blocks:  6
           X Bounds:  0.000, 4.000
           Y Bounds:  -1.000, 0.000
           Z Bounds:  -0.500, 4.500

      Merge the body:

      >>> mesh = body.tessellate(merge=True)
      >>> mesh
      PolyData (0x7f94ec75f3a0)
        N Cells:      12
        N Points:     24
        X Bounds:     0.000e+00, 4.000e+00
        Y Bounds:     -1.000e+00, 0.000e+00
        Z Bounds:     -5.000e-01, 4.500e+00
        N Arrays:     0


   .. py:method:: plot(merge: bool = False, screenshot: beartype.typing.Optional[str] = None, use_trame: beartype.typing.Optional[bool] = None, **plotting_options: beartype.typing.Optional[dict]) -> None

      Plot the body.

      Parameters
      ----------
      merge : bool, default: False
          Whether to merge the body into a single mesh. When ``False`` (default),
          the number of triangles are preserved and only the topology is merged.
          When ``True``, the individual faces of the tessellation are merged.
      screenshot : str, default: None
          Path for saving a screenshot of the image that is being represented.
      use_trame : bool, default: None
          Whether to enable the use of `trame <https://kitware.github.io/trame/index.html>`_.
          The default is ``None``, in which case the ``USE_TRAME`` global setting
          is used.
      **plotting_options : dict, default: None
          Keyword arguments for plotting. For allowable keyword arguments, see the
          :func:`pyvista.Plotter.add_mesh` method.

      Examples
      --------
      Extrude a box centered at the origin to create rectangular body and
      plot it:

      >>> from ansys.geometry.core.misc.units import UNITS as u
      >>> from ansys.geometry.core.sketch import Sketch
      >>> from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
      >>> from ansys.geometry.core import Modeler
      >>> modeler = Modeler()
      >>> origin = Point3D([0, 0, 0])
      >>> plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 0, 1])
      >>> sketch = Sketch(plane)
      >>> box = sketch.box(Point2D([2, 0]), 4, 4)
      >>> design = modeler.create_design("my-design")
      >>> mycomp = design.add_component("my-comp")
      >>> body = mycomp.extrude_sketch("my-sketch", sketch, 1 * u.m)
      >>> body.plot()

      Plot the body and color each face individually:

      >>> body.plot(multi_colors=True)


   .. py:method:: intersect(other: Body) -> None
      :abstractmethod:

      Intersect two bodies.

      Notes
      -----
      The ``self`` parameter is directly modified with the result, and
      the ``other`` parameter is consumed. Thus, it is important to make
      copies if needed.

      Parameters
      ----------
      other : Body
          Body to intersect with.

      Raises
      ------
      ValueError
          If the bodies do not intersect.


   .. py:method:: subtract(other: Body) -> None
      :abstractmethod:

      Subtract two bodies.

      Notes
      -----
      The ``self`` parameter is directly modified with the result, and
      the ``other`` parameter is consumed. Thus, it is important to make
      copies if needed.

      Parameters
      ----------
      other : Body
          Body to subtract from the ``self`` parameter.

      Raises
      ------
      ValueError
          If the subtraction results in an empty (complete) subtraction.


   .. py:method:: unite(other: Body) -> None
      :abstractmethod:

      Unite two bodies.

      Notes
      -----
      The ``self`` parameter is directly modified with the result, and
      the ``other`` parameter is consumed. Thus, it is important to make
      copies if needed.

      Parameters
      ----------
      other : Body
          Body to unite with the ``self`` parameter.


   .. py:method:: __repr__() -> str

      Represent the master body as a string.



.. py:class:: Body(id, name, parent: ansys.geometry.core.designer.component.Component, template: MasterBody)


   Bases: :py:obj:`IBody`

   Represents solids and surfaces organized within the design assembly.

   Solids and surfaces synchronize to a design within a supporting Geometry service instance.

   Parameters
   ----------
   id : str
       Server-defined ID for the body.
   name : str
       User-defined label for the body.
   parent : Component
       Parent component to place the new component under within the design assembly.
   template : MasterBody
       Master body that this body is an occurrence of.

   .. py:property:: id
      :type: str

      Get the ID of the body as a string.


   .. py:property:: name
      :type: str

      Get the name of the body.


   .. py:property:: parent
      :type: ansys.geometry.core.designer.component.Component


   .. py:property:: faces
      :type: beartype.typing.List[ansys.geometry.core.designer.face.Face]

      Get a list of all faces within the body.

      Returns
      -------
      List[Face]


   .. py:property:: edges
      :type: beartype.typing.List[ansys.geometry.core.designer.edge.Edge]

      Get a list of all edges within the body.

      Returns
      -------
      List[Edge]


   .. py:property:: is_alive
      :type: bool

      Check if the body is still alive and has not been deleted.


   .. py:property:: is_surface
      :type: bool

      Check if the body is a planar body.


   .. py:property:: surface_thickness
      :type: beartype.typing.Union[pint.Quantity, None]

      Get the surface thickness of a surface body.

      Notes
      -----
      This method is only for surface-type bodies that have been assigned a surface thickness.


   .. py:property:: surface_offset
      :type: beartype.typing.Union[ansys.geometry.core.designer.design.MidSurfaceOffsetType, None]

      Get the surface offset type of a surface body.

      Notes
      -----
      This method is only for surface-type bodies that have been assigned a surface offset.


   .. py:property:: volume
      :type: pint.Quantity

      Calculate the volume of the body.

      Notes
      -----
      When dealing with a planar surface, a value of ``0`` is returned as a volume.


   .. py:method:: reset_tessellation_cache()

      Decorate ``Body`` methods that require a tessellation cache update.

      Parameters
      ----------
      func : method
          Method to call.

      Returns
      -------
      Any
          Output of the method, if any.


   .. py:method:: assign_material(material: ansys.geometry.core.materials.Material) -> None

      Assign a material against the design in the active Geometry service instance.

      Parameters
      ----------
      material : Material
          Source material data.


   .. py:method:: add_midsurface_thickness(thickness: pint.Quantity) -> None

      Add a mid-surface thickness to a surface body.

      Parameters
      ----------
      thickness : Quantity
          Thickness to assign.

      Notes
      -----
      Only surface bodies are eligible for mid-surface thickness assignment.


   .. py:method:: add_midsurface_offset(offset: ansys.geometry.core.designer.design.MidSurfaceOffsetType) -> None

      Add a mid-surface offset to a surface body.

      Parameters
      ----------
      offset_type : MidSurfaceOffsetType
          Surface offset to assign.

      Notes
      -----
      Only surface bodies are eligible for mid-surface offset assignment.


   .. py:method:: imprint_curves(faces: beartype.typing.List[ansys.geometry.core.designer.face.Face], sketch: ansys.geometry.core.sketch.Sketch) -> beartype.typing.Tuple[beartype.typing.List[ansys.geometry.core.designer.edge.Edge], beartype.typing.List[ansys.geometry.core.designer.face.Face]]

      Imprint all specified geometries onto specified faces of the body.

      Parameters
      ----------
      faces: List[Face]
          List of faces to imprint the curves of the sketch onto.
      sketch: Sketch
          All curves to imprint on the faces.

      Returns
      -------
      Tuple[List[Edge], List[Face]]
          All impacted edges and faces from the imprint operation.


   .. py:method:: project_curves(direction: ansys.geometry.core.math.UnitVector3D, sketch: ansys.geometry.core.sketch.Sketch, closest_face: bool, only_one_curve: beartype.typing.Optional[bool] = False) -> beartype.typing.List[ansys.geometry.core.designer.face.Face]

      Project all specified geometries onto the body.

      Parameters
      ----------
      direction: UnitVector3D
          Direction of the projection.
      sketch: Sketch
          All curves to project on the body.
      closest_face: bool
          Whether to target the closest face with the projection.
      only_one_curve: bool, default: False
          Whether to project only one curve of the entire sketch. When
          ``True``, only one curve is projected.

      Notes
      -----
      The ``only_one_curve`` parameter allows you to optimize the server call because
      projecting curves is an expensive operation. This reduces the workload on the
      server side.

      Returns
      -------
      List[Face]
          All faces from the project curves operation.


   .. py:method:: imprint_projected_curves(direction: ansys.geometry.core.math.UnitVector3D, sketch: ansys.geometry.core.sketch.Sketch, closest_face: bool, only_one_curve: beartype.typing.Optional[bool] = False) -> beartype.typing.List[ansys.geometry.core.designer.face.Face]

      Project and imprint specified geometries onto the body.

      This method combines the ``project_curves()`` and ``imprint_curves()`` method into
      one method. It is much more performant than calling them back-to-back when dealing
      with many curves. Because it is a specialized function, this method only returns
      the faces (and not the edges) from the imprint operation.

      Parameters
      ----------
      direction: UnitVector3D
          Direction of the projection.
      sketch: Sketch
          All curves to project on the body.
      closest_face: bool
          Whether to target the closest face with the projection.
      only_one_curve: bool, default: False
          Whether to project only one curve of the entire sketch. When
          ``True``, only one curve is projected.

      Notes
      -----
      The ``only_one_curve`` parameter allows you to optimize the server call because
      projecting curves is an expensive operation. This reduces the workload on the
      server side.

      Returns
      -------
      List[Face]
          All imprinted faces from the operation.


   .. py:method:: translate(direction: ansys.geometry.core.math.UnitVector3D, distance: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real]) -> None

      Translate the geometry body in the specified direction by a given distance.

      Parameters
      ----------
      direction: UnitVector3D
          Direction of the translation.
      distance: Union[Quantity, Distance, Real]
          Distance (magnitude) of the translation.

      Returns
      -------
      None


   .. py:method:: copy(parent: ansys.geometry.core.designer.component.Component, name: str = None) -> Body

      Create a copy of the body and place it under the specified parent component.

      Parameters
      ----------
      parent: Component
          Parent component to place the new body under within the design assembly.
      name: str
          Name to give the new body.

      Returns
      -------
      Body
          Copy of the body.


   .. py:method:: tessellate(merge: beartype.typing.Optional[bool] = False) -> beartype.typing.Union[pyvista.PolyData, pyvista.MultiBlock]

      Tessellate the body and return the geometry as triangles.

      Parameters
      ----------
      merge : bool, default: False
          Whether to merge the body into a single mesh. When ``False`` (default), the
          number of triangles are preserved and only the topology is merged.
          When ``True``, the individual faces of the tessellation are merged.

      Returns
      -------
      ~pyvista.PolyData, ~pyvista.MultiBlock
          Merged :class:`pyvista.PolyData` if ``merge=True`` or a composite dataset.

      Examples
      --------
      Extrude a box centered at the origin to create a rectangular body and
      tessellate it:

      >>> from ansys.geometry.core.misc.units import UNITS as u
      >>> from ansys.geometry.core.sketch import Sketch
      >>> from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
      >>> from ansys.geometry.core import Modeler
      >>> modeler = Modeler()
      >>> origin = Point3D([0, 0, 0])
      >>> plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 0, 1])
      >>> sketch = Sketch(plane)
      >>> box = sketch.box(Point2D([2, 0]), 4, 4)
      >>> design = modeler.create_design("my-design")
      >>> my_comp = design.add_component("my-comp")
      >>> body = my_comp.extrude_sketch("my-sketch", sketch, 1 * u.m)
      >>> blocks = body.tessellate()
      >>> blocks
      >>> MultiBlock (0x7f94ec757460)
           N Blocks:  6
           X Bounds:  0.000, 4.000
           Y Bounds:  -1.000, 0.000
           Z Bounds:  -0.500, 4.500

      Merge the body:

      >>> mesh = body.tessellate(merge=True)
      >>> mesh
      PolyData (0x7f94ec75f3a0)
        N Cells:      12
        N Points:     24
        X Bounds:     0.000e+00, 4.000e+00
        Y Bounds:     -1.000e+00, 0.000e+00
        Z Bounds:     -5.000e-01, 4.500e+00
        N Arrays:     0


   .. py:method:: plot(merge: bool = False, screenshot: beartype.typing.Optional[str] = None, use_trame: beartype.typing.Optional[bool] = None, **plotting_options: beartype.typing.Optional[dict]) -> None

      Plot the body.

      Parameters
      ----------
      merge : bool, default: False
          Whether to merge the body into a single mesh. When ``False`` (default),
          the number of triangles are preserved and only the topology is merged.
          When ``True``, the individual faces of the tessellation are merged.
      screenshot : str, default: None
          Path for saving a screenshot of the image that is being represented.
      use_trame : bool, default: None
          Whether to enable the use of `trame <https://kitware.github.io/trame/index.html>`_.
          The default is ``None``, in which case the ``USE_TRAME`` global setting
          is used.
      **plotting_options : dict, default: None
          Keyword arguments for plotting. For allowable keyword arguments, see the
          :func:`pyvista.Plotter.add_mesh` method.

      Examples
      --------
      Extrude a box centered at the origin to create rectangular body and
      plot it:

      >>> from ansys.geometry.core.misc.units import UNITS as u
      >>> from ansys.geometry.core.sketch import Sketch
      >>> from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
      >>> from ansys.geometry.core import Modeler
      >>> modeler = Modeler()
      >>> origin = Point3D([0, 0, 0])
      >>> plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 0, 1])
      >>> sketch = Sketch(plane)
      >>> box = sketch.box(Point2D([2, 0]), 4, 4)
      >>> design = modeler.create_design("my-design")
      >>> mycomp = design.add_component("my-comp")
      >>> body = mycomp.extrude_sketch("my-sketch", sketch, 1 * u.m)
      >>> body.plot()

      Plot the body and color each face individually:

      >>> body.plot(multi_colors=True)


   .. py:method:: intersect(other: Body) -> None

      Intersect two bodies.

      Notes
      -----
      The ``self`` parameter is directly modified with the result, and
      the ``other`` parameter is consumed. Thus, it is important to make
      copies if needed.

      Parameters
      ----------
      other : Body
          Body to intersect with.

      Raises
      ------
      ValueError
          If the bodies do not intersect.


   .. py:method:: subtract(other: Body) -> None

      Subtract two bodies.

      Notes
      -----
      The ``self`` parameter is directly modified with the result, and
      the ``other`` parameter is consumed. Thus, it is important to make
      copies if needed.

      Parameters
      ----------
      other : Body
          Body to subtract from the ``self`` parameter.

      Raises
      ------
      ValueError
          If the subtraction results in an empty (complete) subtraction.


   .. py:method:: unite(other: Body) -> None

      Unite two bodies.

      Notes
      -----
      The ``self`` parameter is directly modified with the result, and
      the ``other`` parameter is consumed. Thus, it is important to make
      copies if needed.

      Parameters
      ----------
      other : Body
          Body to unite with the ``self`` parameter.


   .. py:method:: __repr__() -> str

      Represent the ``Body`` as a string.



