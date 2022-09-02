"""``Sketch`` class module."""


from ansys.geometry.core.sketch.curve import SketchCurve


class Sketch:
    """
    Provides Sketch class for building 2D sketch elements.
    """

    def __init__(self, curves=None):
        """Constructor method for ``Sketch``."""
        self._sketch_curves = [] if not curves else curves

    @property
    def sketch_curves(self) -> list[SketchCurve]:
        """Returns the sketched curves.

        Returns
        -------
        list[SketchCurve]
            A list of ``SketchCurve`` instances attached to the sketch.

        """
        return self._sketch_curves

    def draw(self, sketch_curve: SketchCurve) -> Sketch:
        """Draw desired ``SketchCurve`` into the sketch instance.

        Parameters
        ----------
        sketch_curve : SketchCurve
            An ``SketchCurve`` instance to be drawn in the sketch.

        Returns
        -------
        Sketch
            Returns the object itself to keep adding drawings.

        """
        self._sketch_curves.append(curve)
        return self
