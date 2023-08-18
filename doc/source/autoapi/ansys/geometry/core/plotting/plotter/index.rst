


Module ``plotter``
==================



.. py:module:: ansys.geometry.core.plotting.plotter



Description
-----------

Provides for plotting various PyGeometry objects.




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

   ansys.geometry.core.plotting.plotter.Plotter
   ansys.geometry.core.plotting.plotter.PlotterHelper




.. py:class:: Plotter(scene: beartype.typing.Optional[pyvista.Plotter] = None, color_opts: beartype.typing.Optional[beartype.typing.Dict] = None, num_points: int = 100, enable_widgets: bool = True)


   Provides for plotting sketches and bodies.

   Parameters
   ----------
   scene : ~pyvista.Plotter, default: None
       ``Scene`` instance for rendering the objects.
   color_opts : dict, default: None
       Dictionary containing the background and top colors.
   num_points : int, default: 100
       Number of points to use to render the shapes.
   enable_widgets: bool, default: True
       Whether to enable widget buttons in the plotter window.
       Widget buttons must be disabled when using
       `trame <https://kitware.github.io/trame/index.html>`_
       for visualization.

   .. py:property:: scene
      :type: pyvista.Plotter

      Rendered scene object.

      Returns
      -------
      ~pvyista.Plotter
          Rendered scene object.


   .. py:method:: view_xy() -> None

      View the scene from the XY plane.


   .. py:method:: view_xz() -> None

      View the scene from the XZ plane.


   .. py:method:: view_yx() -> None

      View the scene from the YX plane.


   .. py:method:: view_yz() -> None

      View the scene from the YZ plane.


   .. py:method:: view_zx() -> None

      View the scene from the ZX plane.


   .. py:method:: view_zy() -> None

      View the scene from the ZY plane.


   .. py:method:: plot_frame(frame: ansys.geometry.core.math.Frame, plotting_options: beartype.typing.Optional[beartype.typing.Dict] = None) -> None

      Plot a frame in the scene.

      Parameters
      ----------
      frame : Frame
          Frame to render in the scene.
      plotting_options : dict, default: None
          Dictionary containing parameters accepted by the
          :class:`pyvista.plotting.tools.create_axes_marker` class for customizing
          the frame rendering in the scene.


   .. py:method:: plot_plane(plane: ansys.geometry.core.math.Plane, plane_options: beartype.typing.Optional[beartype.typing.Dict] = None, plotting_options: beartype.typing.Optional[beartype.typing.Dict] = None) -> None

      Plot a plane in the scene.

      Parameters
      ----------
      plane : Plane
          Plane to render in the scene.
      plane_options : dict, default: None
          Dictionary containing parameters accepted by the
          :class:`pyvista.Plane` instance for customizing the mesh
          representing the plane.
      plotting_options : dict, default: None
          Dictionary containing parameters accepted by the
          :class:`pyvista.Plotter.add_mesh` class for customizing the mesh
          rendering of the plane.


   .. py:method:: plot_sketch(sketch: ansys.geometry.core.sketch.Sketch, show_plane: bool = False, show_frame: bool = False, **plotting_options: beartype.typing.Optional[beartype.typing.Dict]) -> None

      Plot a sketch in the scene.

      Parameters
      ----------
      sketch : Sketch
          Sketch to render in the scene.
      show_plane : bool, default: False
          Whether to render the sketch plane in the scene.
      show_frame : bool, default: False
          Whether to show the frame in the scene.
      **plotting_options : dict, default: None
          Keyword arguments. For allowable keyword arguments, see the
          :func:`pyvista.Plotter.add_mesh` method.


   .. py:method:: add_body(body: ansys.geometry.core.designer.Body, merge: beartype.typing.Optional[bool] = False, **plotting_options: beartype.typing.Optional[beartype.typing.Dict]) -> str

      Add a body to the scene.

      Parameters
      ----------
      body : ansys.geometry.core.designer.Body
          Body to add.
      merge : bool, default: False
          Whether to merge the body into a single mesh. When ``True``, the
          individual faces of the tessellation are merged. This
          preserves the number of triangles and only merges the topology.
      **plotting_options : dict, default: None
          Keyword arguments. For allowable keyword arguments,
          see the :func:`pyvista.Plotter.add_mesh` method.

      Returns
      -------
      str
          Name of the added PyVista actor.


   .. py:method:: add_component(component: ansys.geometry.core.designer.Component, merge_component: bool = False, merge_bodies: bool = False, **plotting_options) -> str

      Add a component to the scene.

      Parameters
      ----------
      component : ansys.geometry.core.designer.Component
          Component to add.
      merge_component : bool, default: False
          Whether to merge the component into a single dataset. When
          ``True``, all the individual bodies are effectively combined
          into a single dataset without any hierarchy.
      merge_bodies : bool, default: False
          Whether to merge each body into a single dataset. When ``True``,
          all the faces of each individual body are effectively combined
          into a single dataset without separating faces.
      **plotting_options : dict, default: None
          Keyword arguments. For allowable keyword arguments, see the
          :func:`pyvista.Plotter.add_mesh` method.

      Returns
      -------
      str
          Name of the added PyVista actor.


   .. py:method:: add_sketch_polydata(polydata_entries: beartype.typing.List[pyvista.PolyData], **plotting_options) -> None

      Add sketches to the scene from PyVista polydata.

      Parameters
      ----------
      polydata : pyvista.PolyData
          Polydata to add.
      **plotting_options : dict, default: None
          Keyword arguments. For allowable keyword arguments, see the
          :func:`pyvista.Plotter.add_mesh` method.


   .. py:method:: add(object: Any, merge_bodies: bool = False, merge_components: bool = False, **plotting_options) -> beartype.typing.Dict[str, str]

      Add any type of object to the scene.

      These types of objects are supported: ``Body``, ``Component``, ``List[pv.PolyData]``,
      ``pv.MultiBlock``, and ``Sketch``.

      Parameters
      ----------
      plotting_list : List[Any]
          List of objects that you want to plot.
      merge_bodies : bool, default: False
          Whether to merge each body into a single dataset. When ``True``,
          all the faces of each individual body are effectively combined
          into a single dataset without separating faces.
      merge_component : bool, default: False
          Whether to merge the component into a single dataset. When
          ``True``, all the individual bodies are effectively combined
          into a single dataset without any hierarchy.
      **plotting_options : dict, default: None
          Keyword arguments. For allowable keyword arguments, see the
          :func:`pyvista.Plotter.add_mesh` method.

      Returns
      -------
      Mapping[str, str]
          Mapping between the pv.Actor and the PyGeometry object.


   .. py:method:: add_list(plotting_list: beartype.typing.List[Any], merge_bodies: bool = False, merge_components: bool = False, **plotting_options) -> beartype.typing.Dict[str, str]

      Add a list of any type of object to the scene.

      These types of objects are supported: ``Body``, ``Component``, ``List[pv.PolyData]``,
      ``pv.MultiBlock``, and ``Sketch``.

      Parameters
      ----------
      plotting_list : List[Any]
          List of objects you want to plot.
      merge_component : bool, default: False
          Whether to merge the component into a single dataset. When
          ``True``, all the individual bodies are effectively combined
          into a single dataset without any hierarchy.
      merge_bodies : bool, default: False
          Whether to merge each body into a single dataset. When ``True``,
          all the faces of each individual body are effectively combined
          into a single dataset without separating faces.
      **plotting_options : dict, default: None
          Keyword arguments. For allowable keyword arguments, see the
          :func:`pyvista.Plotter.add_mesh` method.

      Returns
      -------
      Mapping[str, str]
          Dictionary with the mapping between pv.Actor and PyGeometry objects.


   .. py:method:: show(show_axes_at_origin: bool = True, show_plane: bool = True, jupyter_backend: beartype.typing.Optional[str] = None, **kwargs: beartype.typing.Optional[beartype.typing.Dict]) -> None

      Show the rendered scene on the screen.

      Parameters
      ----------
      jupyter_backend : str, default: None
          PyVista Jupyter backend.
      **kwargs : dict, default: None
          Plotting keyword arguments. For allowable keyword arguments, see the
          :func:`pyvista.Plotter.show` method.

      Notes
      -----
      For more information on supported Jupyter backends, see
      `Jupyter Notebook Plotting <https://docs.pyvista.org/user-guide/jupyter/index.html>`_
      in the PyVista documentation.



.. py:class:: PlotterHelper(use_trame: beartype.typing.Optional[bool] = None, allow_picking: beartype.typing.Optional[bool] = False)


   Provides for simplifying the selection of trame in ``plot()`` functions.

   Parameters
   ----------
   use_trame : bool, default: None
       Whether to enable the use of `trame <https://kitware.github.io/trame/index.html>`_.
       The default is ``None``, in which case the ``USE_TRAME`` global setting
       is used.
   allow_picking: bool, default: False
       Enables/disables the picking capabilities in the PyVista plotter.

   .. py:method:: select_object(actor: pyvista.Actor, body_name: str, pt: numpy.Array) -> None

      Select an object in the plotter.

      Highlights the object edges and adds a label with the object name and adds
      it to the PyGeometry object selection.

      Parameters
      ----------
      actor : pv.Actor
          Actor on which to perform the operations.
      body_name : str
          Name of the Body to highlight.
      pt : np.Array
          Set of points to determine the label position.


   .. py:method:: unselect_object(actor: pyvista.Actor, body_name: str) -> None

      Unselect an object in the plotter.

      Removes edge highlighting and label from a plotter actor and removes it
      from the PyGeometry object selection.

      Parameters
      ----------
      actor : pv.Actor
          Actor that is currently highlighted
      body_name : str
          Body name to remove


   .. py:method:: picker_callback(actor: pyvista.Actor) -> None

      Define callback for the element picker.

      Parameters
      ----------
      actor : pv.Actor
          Actor that we are picking.


   .. py:method:: plot(object: Any, screenshot: beartype.typing.Optional[str] = None, merge_bodies: bool = False, merge_component: bool = False, view_2d: beartype.typing.Dict = None, **plotting_options) -> beartype.typing.List[any]

      Plot and show any PyGeometry object.

      These types of objects are supported: ``Body``, ``Component``, ``List[pv.PolyData]``,
      ``pv.MultiBlock``, and ``Sketch``.

      Parameters
      ----------
      object : any
          Any object or list of objects that you want to plot.
      screenshot : str, default: None
          Path for saving a screenshot of the image that is being represented.
      merge_bodies : bool, default: False
          Whether to merge each body into a single dataset. When ``True``,
          all the faces of each individual body are effectively combined
          into a single dataset without separating faces.
      merge_component : bool, default: False
          Whether to merge this component into a single dataset. When ``True``,
          all the individual bodies are effectively combined into a single
          dataset without any hierarchy.
      view_2d : Dict, default: None
          Dictionary with the plane and the viewup vectors of the 2D plane.
      **plotting_options : dict, default: None
          Keyword arguments. For allowable keyword arguments, see the
          :func:`pyvista.Plotter.add_mesh` method.

      Returns
      -------
      List[any]
          List with the picked bodies in the picked order.


   .. py:method:: show_plotter(screenshot: beartype.typing.Optional[str] = None) -> None

      Show the plotter or start the `trame <https://kitware.github.io/trame/index.html>`_ service.

      Parameters
      ----------
      plotter : Plotter
          PyGeometry plotter with the meshes added.
      screenshot : str, default: None
          Path for saving a screenshot of the image that is being represented.



