"""``Sketch`` class module."""


from ansys.geometry.core.primitives.direction import Direction
from ansys.geometry.core.primitives.point3D import Point3D
from ansys.geometry.core.sketch.circle_sketch import CircleSketch
from ansys.geometry.core.sketch.line_sketch import LineSketch


class Sketch:
    """
    Provides Sketch class for building 2D sketch elements.
    """

    def __init__(self):
        """Constructor method for ``Sketch``."""
        self._sketch_curves = (
            []
        )  # SketchCurve[] maintaining reference to all sketch curves within the current sketch

    def circle(self, origin: Point3D, radius: float):
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

    def line(self, point_1: Point3D, point_2: Point3D):
        """
        Add a line segment sketch object to the sketch plane.

        Parameters
        ----------
        point_1 : Point3D
            Starting point of the segment.
        point_2 : Point3D
            Ending point of the segment.

        Returns
        -------
        Sketch
            Updated Sketch object.
        """
        line = LineSketch(point_1, point_2)

        self._sketch_curves.append(line)

        # TODO: save line creation to history tracking object

        # return the object created
        return self._sketch_curves[-1]
