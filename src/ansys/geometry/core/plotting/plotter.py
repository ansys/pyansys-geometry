"""A module containing a class for plotting various PyGeometry objects."""

import numpy as np
import pyvista as pv


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
        scene.add_axes(box=True)

        # Show origin axes
        axes = pv.Axes(show_actor=True, actor_scale=2.0, line_width=5.0)
        axes.origin = (0, 0, 0)
        axes.actor.GetProperty().SetColor(0, 0, 0)
        scene.add_actor(axes.actor)

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
        axes = pv.Axes(show_actor=True, actor_scale=2.0, line_width=5.0)
        axes.actor.GetProperty().SetColor(0, 0, 0)

        # Transpose the frame matrix to fix rotation sense in VTK
        arr = np.vstack((frame.matrix, frame.origin)).T
        arr = np.vstack((arr, [0, 0, 0, 1]))

        # Apply matrix transformation to the actor
        axes.actor.SetUserMatrix(pv.vtkmatrix_from_array(arr))

        # Render the actor in the scene
        self.scene.add_actor(axes.actor)

    def plot_shape(self, shape):
        """Plot desired shape into the scene.

        Parameters
        ----------
        shape : Shape
            The ``Shape`` instance to be rendered in the scene.

        """
        # Generate the points and the lines
        try:
            points = shape.local_points(self._num_points)
        # Avoid error if a polygon shape is passed
        except TypeError:
            points = shape.local_points()
        lines = np.hstack([[2, ith, ith + 1] for ith in range(0, len(points) - 1)])

        # Plot those into the scene
        mesh_points = pv.PointSet(points)
        mesh_line = pv.PolyData(points, lines=lines)

        # Add those to the scene
        self.scene.add_mesh(mesh_points, color="red")
        self.scene.add_mesh(mesh_line, color="black", line_width=3, point_size=20)

    def plot_sketch(self, sketch):
        """Plot desired sktch into the scene.

        Parameters
        ----------
        sketch : Sketch
            The ``Sketch`` instance to be rendered in the scene.

        """
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
