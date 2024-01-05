# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Module for using `trame <https://kitware.github.io/trame/index.html>`_ for visualization."""
try:
    from pyvista.trame.ui import plotter_ui
    from trame.app import get_server
    from trame.ui.vuetify import SinglePageLayout

    _HAS_TRAME = True

except ModuleNotFoundError:  # pragma: no cover
    _HAS_TRAME = False


class TrameVisualizer:
    """Defines the trame layout view."""

    def __init__(self) -> None:
        """Initialize the trame server and server-related variables."""
        if not _HAS_TRAME:  # pragma: no cover
            raise ModuleNotFoundError(
                "The package 'pyvista[trame]' is required to use this function."
            )

        self.server = get_server()
        self.state, self.ctrl = self.server.state, self.server.controller

    def set_scene(self, plotter):
        """
        Set the trame layout view and the mesh to show through the PyVista plotter.

        Parameters
        ----------
        plotter : ~pyvista.Plotter
            PyVista plotter with the rendered mesh.
        """
        self.state.trame__title = "PyAnsys Geometry Viewer"

        with SinglePageLayout(self.server) as layout:
            layout.icon.click = self.ctrl.view_reset_camera
            layout.title.set_text("PyAnsys Geometry")

            with layout.content:
                # Use PyVista UI template for Plotters
                view = plotter_ui(plotter.scene)
                self.ctrl.view_update = view.update

            # hide footer with trame watermark
            layout.footer.hide()

    def show(self):
        """Start the trame server and show the mesh."""
        self.server.start()
