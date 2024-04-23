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
from beartype.typing import TYPE_CHECKING, Union
import pyvista as pv

from ansys.geometry.core import LOG as logger
from ansys.geometry.core.plotting.plotter import Plotter

if TYPE_CHECKING:
    from ansys.geometry.core.plotting.plotter_helper import PlotterHelper

try:
    from pyvista.trame.ui import plotter_ui
    from trame.app import get_server
    from trame.ui import vuetify, vuetify3

    _HAS_TRAME = True

except ModuleNotFoundError:  # pragma: no cover
    _HAS_TRAME = False


class TrameVisualizer:
    """
    Defines the trame layout view.

    Parameters
    ----------
    client_type : str, optional
        Client type to use for the trame server. Options are 'vue2' and 'vue3'.
        Default is 'vue3'.
    """

    def __init__(self, client_type: str = "vue3") -> None:
        """Initialize the trame server and server-related variables."""
        if not _HAS_TRAME:  # pragma: no cover
            raise ModuleNotFoundError(
                "The package 'pyvista[trame]' is required to use this function."
            )
        self._client_type = client_type
        if client_type not in ["vue2", "vue3"]:
            self._client_type = "vue3"
            logger.warning("Invalid client type {}. Defaulting to 'vue3'.", client_type)

        self.server = get_server(client_type=client_type)
        self.state, self.ctrl = self.server.state, self.server.controller

    def set_scene(self, plotter: Union["pv.Plotter", Plotter, "PlotterHelper"]):
        """
        Set the trame layout view and the mesh to show through the PyVista plotter.

        Parameters
        ----------
        plotter : Union[~pyvista.Plotter, ~Plotter, ~PlotterHelper]
            PyVista plotter or PyAnsys plotter to render.
        """
        from ansys.geometry.core.plotting.plotter_helper import PlotterHelper

        if isinstance(plotter, PlotterHelper):
            pv_plotter = plotter._pl.scene
        elif isinstance(plotter, Plotter):
            pv_plotter = plotter.scene
        elif isinstance(plotter, pv.Plotter):
            pv_plotter = plotter
        else:
            logger.warning("Invalid plotter type. Expected PyVista plotter or PyAnsys plotter.")

        self.state.trame__title = "PyAnsys Geometry Viewer"
        if self._client_type == "vue3":
            page_layout = vuetify3.SinglePageLayout(self.server)
        else:
            page_layout = vuetify.SinglePageLayout(self.server)

        with page_layout as layout:
            layout.icon.click = self.ctrl.view_reset_camera
            layout.title.set_text("PyAnsys Geometry")

            with layout.content:
                # Use PyVista UI template for Plotters
                view = plotter_ui(pv_plotter)
                self.ctrl.view_update = view.update

            # hide footer with trame watermark
            layout.footer.hide()

    def show(self):
        """Start the trame server and show the mesh."""
        self.server.start()
