"""Provides the ``Ellipse`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import numpy as np
from pint import Quantity
import pyvista as pv
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math import Matrix33, Matrix44, Plane, Point2D, Point3D, Vector3D
from ansys.geometry.core.misc import UNIT_ANGLE, UNIT_LENGTH, Angle, Distance
from ansys.geometry.core.primitives import Ellipse
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.typing import Real


class SketchEllipse(SketchFace, Ellipse):
    """Provides for modeling ellipses.

    Parameters
    ----------
    center: Point2D
        Point representing the center of the ellipse.
    semi_major_axis : Union[Quantity, Distance]
        Semi-major axis of the ellipse.
    semi_minor_axis : Union[Quantity, Distance]
        Semi-minor axis of the ellipse.
    angle : Union[Quantity, Angle, Real], default: 0
        Placement angle for orientation alignment.
    """

    @check_input_types
    def __init__(
        self,
        center: Point2D,
        semi_major_axis: Union[Quantity, Distance],
        semi_minor_axis: Union[Quantity, Distance],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
        plane: Plane = Plane(),
    ):
        """Initialize the ellipse."""
        # Call SketchFace init method
        SketchFace.__init__(self)

        # Store the 2D center of the ellipse
        self._center = center

        self._semi_major_axis = (
            semi_major_axis if isinstance(semi_major_axis, Distance) else Distance(semi_major_axis)
        )
        self._semi_minor_axis = (
            semi_minor_axis if isinstance(semi_minor_axis, Distance) else Distance(semi_minor_axis)
        )

        if self._semi_major_axis.value.m_as(self._semi_major_axis.base_unit) <= 0:
            raise ValueError("Semi-major axis must be a real positive value.")
        if self._semi_minor_axis.value.m_as(self._semi_minor_axis.base_unit) <= 0:
            raise ValueError("Semi-minor axis must be a real positive value.")

        if isinstance(angle, (int, float)):
            angle = Angle(angle, UNIT_ANGLE)
        self._angle_offset = angle if isinstance(angle, Angle) else Angle(angle, angle.units)

        # Align both units if misaligned
        if self._semi_major_axis.unit != self._semi_minor_axis.unit:
            self._semi_minor_axis.unit = self._semi_major_axis.unit

        # Ensure that the semi-major axis is equal or larger than the minor one
        if self._semi_major_axis.value.m < self._semi_minor_axis.value.m:
            raise ValueError("Semi-major axis cannot be shorter than the semi-minor axis.")

        # Call Circle init method
        self._init_primitive_ellipse_from_plane(plane, semi_major_axis, semi_minor_axis, angle)

    def _init_primitive_ellipse_from_plane(
        self,
        plane: Plane,
        major_radius: Optional[Union[Quantity, Distance]] = None,
        minor_radius: Optional[Union[Quantity, Distance]] = None,
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ) -> None:
        """
        Method in charge of initializing correctly the underlying
        primitive ``Ellipse`` class.

        Parameters
        ----------
        plane : Plane
            Plane containing the sketched ellipse.
        major_radius : Optional[Union[Quantity, Distance]], optional
            Major radius of the ellipse (if any), by default None.
        minor_radius : Optional[Union[Quantity, Distance]], optional
            Minor radius of the ellipse (if any), by default None.
        angle : Union[Quantity, Angle, Real], default: 0
            Placement angle for orientation alignment.
        """

        # Use the radius given (if any)
        maj_radius = major_radius if major_radius else self.semi_major_axis
        min_radius = minor_radius if minor_radius else self.semi_minor_axis

        # Call Ellipse init method
        center_global = plane.origin + Point3D(
            self.center[0] * plane.direction_x + self.center[1] * plane.direction_y,
            unit=self.center.base_unit,
        )

        angle_rad = angle.value.m_as(UNIT_ANGLE)
        # import pdb; pdb.set_trace()
        new_rotated_dir_x = Vector3D(
            [
                np.cos(angle_rad) * plane.direction_x.x - np.sin(angle_rad) * plane.direction_x.y,
                np.sin(angle_rad) * plane.direction_x.x + np.cos(angle_rad) * plane.direction_x.y,
                plane.direction_x.z,
            ]
        )

        Ellipse.__init__(
            self, center_global, maj_radius, min_radius, new_rotated_dir_x, plane.direction_z
        )

    @property
    def center(self) -> Point2D:
        """Point that is the center of the ellipse."""
        return self._center

    @property
    def semi_major_axis(self) -> Quantity:
        """Semi-major axis of the ellipse."""
        return self._semi_major_axis.value

    @property
    def semi_minor_axis(self) -> Quantity:
        """Semi-minor axis of the ellipse."""
        return self._semi_minor_axis.value

    @property
    def angle(self) -> Angle:
        """Orientation angle of the ellipse."""
        return self._angle_offset

    @property
    def perimeter(self) -> Quantity:
        """Perimeter of the circle.

        Notes
        -----
        This property resolves the dilemma between using the ``SkethFace.perimeter``
        property and the ``Circle.perimeter`` property.
        """
        return Ellipse.perimeter.fget(self)

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
        rotation = Matrix33(
            spatial_rotation.from_euler(
                "xyz", [0, 0, self._angle_offset.value.m_as(UNIT_ANGLE)], degrees=False
            ).as_matrix()
        )

        transformation_matrix = Matrix44(
            [
                [
                    rotation[0, 0],
                    rotation[0, 1],
                    rotation[0, 2],
                    self.center.x.m_as(UNIT_LENGTH),
                ],
                [
                    rotation[1, 0],
                    rotation[1, 1],
                    rotation[1, 2],
                    self.center.y.m_as(UNIT_LENGTH),
                ],
                [
                    rotation[2, 0],
                    rotation[2, 1],
                    rotation[2, 2],
                    0,
                ],
                [0, 0, 0, 1],
            ]
        )

        return pv.Ellipse(
            semi_major_axis=self.semi_major_axis.m_as(UNIT_LENGTH),
            semi_minor_axis=self.semi_minor_axis.m_as(UNIT_LENGTH),
        ).transform(transformation_matrix)
