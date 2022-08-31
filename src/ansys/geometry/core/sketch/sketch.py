"""``Sketch`` class module."""


from ansys.geometry.core.primitives.direction import Direction
from ansys.geometry.core.primitives.point3D import Point3D
from ansys.geometry.core.sketch.circle import CircleSketch
from ansys.geometry.core.sketch.line import LineSketch


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

        circle = CircleSketch(origin, Direction(0, 1), Direction(0, 1), radius)

        self._sketch_curves.append(circle)

        # TODO: save circle creation to history tracking object

        # return the object created
        return self._sketch_curves[-1]

    def line(self, point_1: Point3D, point_2: Point3D) -> LineSketch:
        """
        Add a line segment sketch object to the sketch plane.

        Parameters
        ----------
        point_1 : Point3D
            Start of the line segment.
        point_2 : Point3D
            End of the line segment.

        Returns
        -------
        LineSketch
            LineSketch object added to the sketch.
        """
        line = LineSketch(point_1, point_2)

        self._sketch_curves.append(line)

        # TODO: save line creation to history tracking object

        # return the object created
        return self._sketch_curves[-1]
