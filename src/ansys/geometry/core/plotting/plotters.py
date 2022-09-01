"""A module containing class definitions for plotting objects."""

from collections import namedtuple

import matplotlib.pyplot as plt

Drawable2D = namedtuple("Drawable2D", ["coordinates", "origin", "style", "label"])
"""An auxiliary class for containing plotting information of a ``SketchCurve``."""


class SketchPlotter:
    """A class for plotting sketches using matplotlib as backend."""

    def __init__(self, ax=None, show_grid=True):
        """Initialize the ``SketchPlotter`` instances.

        Parameters
        ----------
        ax : optional, ~matplotlib.Axes
            The axes where rendering the sketch.
        use_dark_theme : bool
            if ``True``, matplotlib dark theme is enabled.

        """
        # Create custom axes if no ones were provided
        self._ax = ax
        if not self._ax:
            _, self._ax = plt.subplots()
        self._ax.grid(show_grid)

        # Initialize the list of drawables
        drawables = []

    def _add_drawable(self, sketch_curve, color=None, label=None):
        """Adds the drawable to the list."""
        self._drawables.append(Drawable2D([sketch_curve.points, sketch_curve.origin, color, label]))

    def plot(
        self,
        sketch_curve,
        color=None,
        linestyle=None,
        linewidth=None,
        marker=None,
        markercolor=None,
        markersize=None,
        label=None,
    ):
        """Renders desired sketch instance in the scene axes."""
        self._ax.plot(
            sketch_curve.x_coords,
            sketch_curve.y_coords,
            color=color,
            linestyle=linestyle,
            lw=linewidth,
            marker=marker,
            ms=markersize,
            mfc=markercolor,
            label=label,
        )
        self._ax.set_aspect("equal")

    def show(self):
        plt.show()
