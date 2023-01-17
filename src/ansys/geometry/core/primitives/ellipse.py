""" Provides the ``Ellipse`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np
from pint import Quantity
from scipy.integrate import quad

from ansys.geometry.core.math import UNITVECTOR3D_X, UNITVECTOR3D_Z, Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import Accuracy, Distance
from ansys.geometry.core.primitives.curve_evaluation import CurveEvaluation
from ansys.geometry.core.typing import Real, RealSequence


class Ellipse:
    """
    Provides 3D ``Ellipse`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Origin of the ellipse.
    major_radius : Union[Quantity, Distance]
        Major radius of the ellipse.
    minor_radius : Union[Quantity, Distance]
        Minor radius of the ellipse.
    reference : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-plane direction.
    axis : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Z-plane direction.
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        major_radius: Union[Quantity, Distance],
        minor_radius: Union[Quantity, Distance],
        reference: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        axis: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Z,
    ):
        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin

        self._reference = (
            UnitVector3D(reference) if not isinstance(reference, UnitVector3D) else reference
        )
        self._axis = UnitVector3D(axis) if not isinstance(axis, UnitVector3D) else axis

        if not self._reference.is_perpendicular_to(self._axis):
            raise ValueError(
                "Ellipse reference (x-direction) and axis (z-direction) must be perpendicular."
            )

        self._major_radius = (
            major_radius if isinstance(major_radius, Distance) else Distance(major_radius)
        )
        self._minor_radius = (
            minor_radius if isinstance(minor_radius, Distance) else Distance(minor_radius)
        )

        if self._major_radius.value.m_as(self._major_radius.base_unit) <= 0:
            raise ValueError("Major radius must be a real positive value.")
        if self._minor_radius.value.m_as(self._minor_radius.base_unit) <= 0:
            raise ValueError("Minor radius must be a real positive value.")

        # Align both units if misaligned
        if self._major_radius.unit != self._minor_radius.unit:
            self._minor_radius.unit = self._major_radius.unit

        # Ensure that the major radius is equal or larger than the minor one
        if self._major_radius.value.m < self._minor_radius.value.m:
            raise ValueError("Major radius cannot be shorter than the minor radius.")

    @property
    def origin(self) -> Point3D:
        """Origin of the ellipse."""
        return self._origin

    @origin.setter
    @check_input_types
    def origin(self, origin: Point3D) -> None:
        """Set the origin of the ellipse."""
        self._origin = origin

    @property
    def major_radius(self) -> Quantity:
        """Major radius of the ellipse."""
        return self._major_radius.value

    @property
    def minor_radius(self) -> Quantity:
        """Minor radius of the ellipse."""
        return self._minor_radius.value

    @property
    def dir_x(self) -> UnitVector3D:
        """X-direction of the ellipse."""
        return self._reference

    @property
    def dir_y(self) -> UnitVector3D:
        """Y-direction of the ellipse."""
        return self.dir_z.cross(self.dir_x)

    @property
    def dir_z(self) -> UnitVector3D:
        """Z-direction of the ellipse."""
        return self._axis

    @check_input_types
    def __eq__(self, other: "Ellipse") -> bool:
        """Equals operator for the ``Ellipse`` class."""
        return (
            self._origin == other._origin
            and self._major_radius == other._major_radius
            and self._minor_radius == other._minor_radius
            and self._reference == other._reference
            and self._axis == other._axis
        )

    def evaluate(self, parameter: Real) -> "EllipseEvaluation":
        """Evaluate the ellipse at the given parameter."""
        return EllipseEvaluation(self, parameter)

    def project_point(self, point: Point3D) -> "EllipseEvaluation":
        """Project a point onto the ellipse and return its ``EllipseEvaluation``."""
        origin_to_point = point - self.origin
        dir_in_plane = UnitVector3D.from_points(
            Point3D([0, 0, 0]), origin_to_point - ((origin_to_point * self.dir_z) * self.dir_z)
        )
        if dir_in_plane.is_zero:
            return EllipseEvaluation(self, 0)

        t = np.arctan2(
            self.dir_y.dot(dir_in_plane) * self.major_radius.m,
            self.dir_x.dot(dir_in_plane) * self.minor_radius.m,
        )
        return EllipseEvaluation(self, t)

    def is_coincident_ellipse(self, other: "Ellipse") -> bool:
        """Determine if this ellipse is coincident with another."""
        return (
            Accuracy.length_is_equal(self.major_radius.m, other.major_radius.m)
            and Accuracy.length_is_equal(self.minor_radius.m, other.minor_radius.m)
            and self.origin == other.origin
            and self.dir_z == other.dir_z
        )

    @property
    def eccentricity(self) -> Real:
        """Eccentricity of the ellipse."""
        ecc = (self.major_radius.m**2 - self.minor_radius.m**2) ** 0.5 / self.major_radius.m
        if ecc == 1:
            raise ValueError("The curve defined is a parabola and not an ellipse.")
        elif ecc > 1:
            raise ValueError("The curve defined is an hyperbola and not an ellipse.")
        return ecc

    @property
    def linear_eccentricity(self) -> Quantity:
        """Linear eccentricity of the ellipse.

        Notes
        -----
        The linear eccentricity is the distance from the center to the focus.
        """
        return (self.major_radius**2 - self.minor_radius**2) ** 0.5

    @property
    def semi_latus_rectum(self) -> Quantity:
        """Return the semi-latus rectum of the ellipse."""
        return self.minor_radius**2 / self.major_radius

    @property
    def perimeter(self) -> Quantity:
        """Perimeter of the ellipse."""

        def integrand(theta, ecc):
            return np.sqrt(1 - (ecc * np.sin(theta)) ** 2)

        I, _ = quad(integrand, 0, np.pi / 2, args=(self.eccentricity,))
        return 4 * self.major_radius * I

    @property
    def area(self) -> Quantity:
        """Area of the ellipse."""
        return np.pi * self.major_radius * self.minor_radius


class EllipseEvaluation(CurveEvaluation):
    """
    Provides ``Ellipse`` evaluation at a certain parameter.

    Parameters
    ----------
    ellipse: ~ansys.geometry.core.primitives.ellipse.Ellipse
        The ``Ellipse`` object to be evaluated.
    parameter: float, int
        The parameter at which the ``Ellipse`` evaluation is requested.
    """

    def __init__(self, ellipse: Ellipse, parameter: Real) -> None:
        self._ellipse = ellipse
        self._parameter = parameter

    @property
    def ellipse(self) -> Ellipse:
        """The ellipse being evaluated."""
        return self._ellipse

    @property
    def parameter(self) -> Real:
        """The parameter that the evaluation is based upon."""
        return self._parameter

    def position(self) -> Point3D:
        """The position of the evaluation."""
        return (
            self.ellipse.origin
            + ((self.ellipse.major_radius * np.cos(self.parameter)) * self.ellipse.dir_x).m
            + ((self.ellipse.minor_radius * np.sin(self.parameter)) * self.ellipse.dir_y).m
        )

    def tangent(self) -> UnitVector3D:
        """The tangent of the evaluation."""
        return (
            (self.ellipse.minor_radius * np.cos(self.parameter) * self.ellipse.dir_y).m
            - (self.ellipse.major_radius * np.sin(self.parameter) * self.ellipse.dir_x).m
        ).normalize()

    def first_derivative(self) -> Vector3D:
        """The first derivative of the evaluation."""
        return (self.ellipse.minor_radius * np.cos(self.parameter) * self.ellipse.dir_y).m - (
            self.ellipse.major_radius * np.sin(self.parameter) * self.ellipse.dir_x
        ).m

    def second_derivative(self) -> Vector3D:
        """The second derivative of the evaluation."""
        return (
            -self.ellipse.major_radius * np.cos(self.parameter) * self.ellipse.dir_x
            - self.ellipse.minor_radius * np.sin(self.parameter) * self.ellipse.dir_y
        ).m

    def curvature(self) -> Real:
        """The curvature of the evaluation."""
        return self.second_derivative().magnitude / np.power(self.first_derivative().magnitude, 2)
