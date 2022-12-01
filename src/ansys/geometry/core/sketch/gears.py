"""Module for sketching gears."""

from beartype import beartype as check_input_types
import numpy as np
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import UNIT_ANGLE, Distance, check_pint_unit_compatibility
from ansys.geometry.core.sketch.arc import Arc
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.segment import Segment
from ansys.geometry.core.typing import Real


class Gear(SketchFace):
    """Base class for sketching gears."""

    def __init__(self):
        """Constructor method for gears."""
        super().__init__()

    @property
    def visualization_polydata(self) -> pv.PolyData:
        """
        VTK polydata representation for PyVista visualization.

        The representation lies in the X/Y plane within
        the standard global Cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            VTK pyvista.Polydata configuration.
        """
        return pv.merge([edge.visualization_polydata for edge in self._edges])


class DummyGear(Gear):
    """Dummy gear sketching class.

    Parameters
    ----------
    origin : Point2D
        Origin of the gear.
    outer_radius : Distance
        Outer radius of the gear.
    inner_radius : Distance
        Inner radius of the gear.
    n_teeth : int
        Number of teeth of the gear.
    """

    @check_input_types
    def __init__(
        self, origin: Point2D, outer_radius: Distance, inner_radius: Distance, n_teeth: int
    ):
        """Constructor method for a dummy gear."""
        # Call the parent ctor
        super().__init__()

        # Let's compute auxiliary variables
        repeat_angle = 2 * np.pi / n_teeth
        tooth_angle = 0.475 * repeat_angle
        gap_angle = repeat_angle - tooth_angle

        # Now, let's loop over all teeth to build the sketch
        for tooth_idx in range(n_teeth):
            # Three angles need to be computed: starting tooth angle,
            # ending tooth angle (==starting gap angle) and ending gap angle
            start_ang = tooth_idx * repeat_angle
            inter_ang = start_ang + tooth_angle
            end_ang = inter_ang + gap_angle

            # Let's compute the sin and cos values for these angles
            sin_inter = np.sin(inter_ang)
            cos_inter = np.cos(inter_ang)
            sin_end = np.sin(end_ang)
            cos_end = np.cos(end_ang)

            # Let's define the points for drawing the arcs and segments involved
            outer_arc_start = Point2D(
                [
                    outer_radius.value.m * np.cos(start_ang),
                    outer_radius.value.m * np.sin(start_ang),
                ],
                unit=outer_radius.unit,
            )
            outer_arc_end = Point2D(
                [outer_radius.value.m * cos_inter, outer_radius.value.m * sin_inter],
                unit=outer_radius.unit,
            )
            inner_arc_start = Point2D(
                [inner_radius.value.m * cos_inter, inner_radius.value.m * sin_inter],
                unit=inner_radius.unit,
            )
            inner_arc_end = Point2D(
                [inner_radius.value.m * cos_end, inner_radius.value.m * sin_end],
                unit=inner_radius.unit,
            )
            next_outer_arc_start = Point2D(
                [outer_radius.value.m * cos_end, outer_radius.value.m * sin_end],
                unit=outer_radius.unit,
            )

            # Now, let's proceed to draw the arcs and segments
            self._edges.append(
                Arc(center=origin, start=outer_arc_start + origin, end=outer_arc_end + origin)
            )
            self._edges.append(Segment(start=outer_arc_end + origin, end=inner_arc_start + origin))
            self._edges.append(
                Arc(center=origin, start=inner_arc_start + origin, end=inner_arc_end + origin)
            )
            self._edges.append(
                Segment(start=inner_arc_end + origin, end=next_outer_arc_start + origin)
            )


class SpurGear(Gear):
    """Class for sketching Spur gears.

    Parameters
    ----------
    origin : Point2D
        Origin of the spur gear.
    module : Real
        Module of the spur gear. This is also the ratio between the pitch circle
        in millimeters and the number of teeth.
    pressure_angle : Quantity
        Pressure angle of the spur gear.
    n_teeth : int
        Number of teeth of the spur gear.
    """

    @check_input_types
    def __init__(self, origin: Point2D, module: Real, pressure_angle: Quantity, n_teeth: int):
        """Constructor for Spur Gears."""
        # Call the parent ctor
        super().__init__()

        # Additional checks for inputs
        check_pint_unit_compatibility(pressure_angle.u, UNIT_ANGLE)

        # Store input parameters
        self._origin = origin
        self._module = module
        self._pressure_angle = pressure_angle.to(UNIT_ANGLE)
        self._n_teeth = n_teeth

        # Compute additional needed values
        self._ref_diameter = self.module * self.n_teeth
        self._base_diameter = self.ref_diameter * np.cos(self.pressure_angle)
        self._addendum = self.module
        self._dedendum = 1.25 * self.module
        self._tip_diameter = self.ref_diameter + 2 * self.module
        self._root_diameter = self.ref_diameter - 2.5 * self.module

        # TODO: To be properly implemented (sketching)...

    @property
    def origin(self) -> Point2D:
        """Origin of the spur gear."""
        return self._origin

    @property
    def module(self) -> Real:
        """Module of the spur gear."""
        return self._module

    @property
    def pressure_angle(self) -> Quantity:
        """Pressure angle of the spur gear."""
        return self._pressure_angle

    @property
    def n_teeth(self) -> int:
        """Number of teeth of the spur gear."""
        return self._n_teeth

    @property
    def ref_diameter(self) -> Real:
        """Reference diameter of the spur gear."""
        return self._ref_diameter

    @property
    def base_diameter(self) -> Real:
        """Base diameter of the spur gear."""
        return self._base_diameter

    @property
    def addendum(self) -> Real:
        """Addendum of the spur gear."""
        return self._addendum

    @property
    def dedendum(self) -> Real:
        """Dedendum of the spur gear."""
        return self._dedendum

    @property
    def tip_diameter(self) -> Real:
        """Tip diameter of the spur gear."""
        return self._tip_diameter

    @property
    def root_diameter(self) -> Real:
        """Root diameter of the spur gear."""
        return self._root_diameter
