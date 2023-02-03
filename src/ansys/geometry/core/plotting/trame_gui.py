"""Module for the trame visualizer."""
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout


class TrameVisualizer:
    """Trame visualizer class. It will define how the trame view layout will be."""

    def __init__(self) -> None:
        """Inits server and server related variables."""
        self.server = get_server()
        self.state, self.ctrl = self.server.state, self.server.controller

    def set_scene(self, plotter):
        """Sets the trame layout view and the mesh to show
        through the pyvista plotter.

        Parameters
        ----------
        plotter : pv.Plotter
            PyVista plotter with the mesh rendered.
        """
        self.state.trame__title = "PyGeometry Viewer"

        with SinglePageLayout(self.server) as layout:
            layout.icon.click = self.ctrl.view_reset_camera
            layout.title.set_text("PyGeometry")

            with layout.content:
                # Use PyVista UI template for Plotters
                view = plotter_ui(plotter.scene)
                self.ctrl.view_update = view.update

            # hide footer
            layout.footer.hide()

    def show(self):
        """Starts the server and shows the mesh."""
        self.server.start()
