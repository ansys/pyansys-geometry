"""``Sketch`` class module."""


from ansys.geometry.core.primitives.point import Point3D
from ansys.geometry.core.primitives.vector import UnitVector2D
from ansys.geometry.core.sketch.circle import CircleSketch


class Sketch:
    """
    Provides Sketch class for building 2D sketch elements.
    """

    def __init__(self):
        """Constructor method for ``Sketch``."""
        self._sketch_curves = (
            []
        )  # SketchCurve[] maintaining reference to all sketch curves within the current sketch

    @property
    def sketch_curves(self):
        """Returns the sketched curves."""
        return self._sketch_curves

    def circle(self, origin: Point3D, radius: float) -> CircleSketch:
        """
        Add a circle sketch object to the sketch plane.

        Parameters
        ----------
        origin : Point3D
            Origin of the circle.
        radius : float
            Radius of the circle

        Returns
        -------
        CircleSketch
            CircleSketch object added to the sketch.
        """

        circle = CircleSketch(origin, UnitVector2D([0, 1]), UnitVector2D([0, 1]), radius)

        self._sketch_curves.append(circle)

        # TODO: save circle creation to history tracking object

        # return the object created
        return self._sketch_curves[-1]
