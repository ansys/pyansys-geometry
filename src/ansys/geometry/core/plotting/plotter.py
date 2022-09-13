"""A module containing a class for plotting various PyGeometry objects."""

import numpy as np
import pyvista as pv
from pyvista.plotting.tools import create_axes_marker


class Plotter:
    """A class devoted to plotting sketches and bodies."""

    def __init__(self, scene=None, background_opts=None, num_points=100):
        """Initializes the plotter.

        Parameters
        ----------
        scene : ~pyvista.Plotter, optional
            A scene for rendering the desired objects.

        """
        # Generate custom scene if none was provided
        if scene is None:
            scene = pv.Plotter()

        # If required, use a white background with no gradient
        if not background_opts:
            background_opts = dict(color="white")

        # Create the scene and assign the background
        self._scene = scene
        scene.set_background(**background_opts)
        view_box = scene.add_axes(line_width=5, box=True)

        # Show origin axes
        axes = create_axes_marker()
        axes.AxisLabelsOff()
        scene.add_actor(axes)

        # Create the fundamental XY plane
        plane = pv.Plane(i_size=10, j_size=10)
        scene.add_mesh(plane, color="white", show_edges=True, opacity=0.1)

        # Save the desired number of points
        self._num_points = num_points

    @property
    def scene(self):
        """Return the rendering scene object.

        Returns
        -------
        ~pvyista.Plotter
            The rendering scene object.

        """
        return self._scene

    def view_xy(self):
        """View the scene from the XY plane."""
        self.scene.view_xy()

    def view_xz(self):
        """View the scene from the XZ plane."""
        self.scene.view_xz()

    def view_yx(self):
        """View the scene from the YX plane."""
        self.scene.view_yx()

    def view_yz(self):
        """View the scene from the YZ plane."""
        self.scene.view_yz()

    def view_zx(self):
        """View the scene from the ZX plane."""
        self.scene.view_zx()

    def view_zy(self):
        """View the scene from the ZY plane."""
        self.scene.view_zy()

    def plot_frame(self, frame):
        """Plot desired frame into the scene.

        Parameters
        ----------
        frame : Frame
            The ``Frame`` instance to be rendered in the scene.

        """
        # Create an Axes actor
        axes = create_axes_marker()
        axes.AxisLabelsOff()
        axes.SetConeRadius(0.2)

        # Transpose the frame matrix to fix rotation sense in VTK
        arr = np.vstack((frame.global_to_local, frame.origin)).T
        arr = np.vstack((arr, [0, 0, 0, 1]))

        # Apply matrix transformation to the actor
        axes.SetUserMatrix(pv.vtkmatrix_from_array(arr))

        # Render the actor in the scene
        self.scene.add_actor(axes)

    def plot_plane(self, plane):
        """Plot desired plane into the scene.

        Parameters
        ----------
        plane : Plane
            The ``Plane`` instance to be rendered in the scene.

        """
        # Create a plane for showing the plane
        plane_mesh = pv.Plane(
            center=plane.origin, direction=plane.direction_z, i_size=10, j_size=10
        )
        self.scene.add_mesh(plane_mesh, color="blue", opacity=0.1)

    def plot_shape(self, shape):
        """Plot desired shape into the scene.

        Parameters
        ----------
        shape : Shape
            The ``Shape`` instance to be rendered in the scene.

        """
        # Generate the points and the lines
        try:
            points = shape.points(self._num_points)
        # Avoid error if a polygon shape is passed
        except TypeError:
            points = shape.points()
        lines = np.hstack([[2, ith, ith + 1] for ith in range(0, len(points) - 1)])

        # Plot those into the scene
        mesh_points = pv.PointSet(points)
        mesh_line = pv.PolyData(points, lines=lines)

        # Add those to the scene
        self.scene.add_mesh(mesh_points, color="red")
        self.scene.add_mesh(mesh_line, color="black", line_width=3, point_size=20)

    def plot_sketch(self, sketch, show_plane=False, show_frame=False):
        """Plot desired sktch into the scene.

        Parameters
        ----------
        sketch : Sketch
            The ``Sketch`` instance to be rendered in the scene.
        show_plane : bool
            If ``True``, it renders the sketch plane in the scene.
        show_frame : bool
            If ``Frame``, it renders the sketch plane in the scene.

        """
        # Show the sketch plane if required
        if show_plane:
            self.plot_plane(sketch._plane)

        # Show the sketch plane if required
        if show_frame:
            self.plot_frame(sketch._plane)

        # Draw each one of the shapes in the sketch
        for shape in sketch.shapes_list:
            self.plot_shape(shape)

    def plot_body(self):
        # Request data on server side
        # Body =(upon request)= vertices, faces and colors
        # Use PolyData
        raise NotImplementedError

    def show(self):
        """Display the rendered scene in the screen."""
        self.scene.show()
