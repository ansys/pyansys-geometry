"""This module provides access and interaction with the PyGeometry Point object."""

from ansys.geometry.core.models.entities.core import BaseEntity


class Point3d(BaseEntity):
    """Provides for creating a point in Discovery or SpaceClaim.

    Parameters
    ----------
    x : float or int
        Coordinate values for the x axis.
    y : float or int
        Ccoordinate values for the y axis.
    z : float or int
        Coordinate values for the z axis.

    Examples
    --------
    Create a 3D point.

    >>> from ansys.geometry.core.models import Point3d
    >>> point = Point3d(1,2,3)
    >>> point
    <ansys.geometry.core.models.entities.basics.point3d.Point3d object at 0x00000216D05049A0>
    """

    def __init__(self, x, y, z):
        """Point constructor."""
        if not all(isinstance(value, (int, float)) for value in [x, y, z]):
            raise ValueError("The parameters 'x', 'y' and 'z' should be integer or float")

        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        """Return the x-coordinate value.

        Examples
        --------
        Create a 3D point.

        >>> from ansys.geometry.core.models import Point3d
        >>> point = Point3d(1,2,3)

        Change the x-coordinate value.

        >>> point.x = 5
        """
        return self._x

    @x.setter
    def x(self, x):
        """Set the x-coordinate value."""
        if not isinstance(x, (int, float)):
            raise ValueError("The parameter 'x' should be a float or an integer value")
        self._x = x

    @property
    def y(self):
        """Return the y-coordinate value.

        Examples
        --------
        Create a 3D point.

        >>> from ansys.geometry.core.models import Point3d
        >>> point = Point3d(1,2,3)

        Change the y-coordinate value.

        >>> point.y = 10
        """
        return self._y

    @y.setter
    def y(self, y):
        """Set the y-coordinate value."""
        if not isinstance(y, (int, float)):
            raise ValueError("The parameter 'y' should be a float or an integer value")
        self._y = y

    @property
    def z(self):
        """Return the x-coordinate value.

        Examples
        --------
        Create a 3D point.

        >>> from ansys.geometry.core.models import Point3d
        >>> point = Point3d(1,2,3)

        Change the z-coordinate value.

        >>> point.z = 55
        """
        return self._z

    @z.setter
    def z(self, z):
        """Set the z-ccordinate value."""
        if not isinstance(z, (int, float)):
            raise ValueError("The parameter 'z' should be a float or an integer value")
        self._z = z
