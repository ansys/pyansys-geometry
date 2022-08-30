"""This module provides access and interaction with the PyGeometry Direction object."""
from ansys.geometry.core.models.entities.core import BaseEntity


class Direction(BaseEntity):
    """Provides access to the 3D direction of the x, y, and z axes.

    Parameters
    ----------
    x : float or int
        Direction of the x axis.
    y : float or int
        Direction of the y axis.
    z : float or int
        Direction of the z axis.

    Examples
    --------
    Create a direction.

    >>> from ansys.geometry.core.models import Direction
    >>> x = Direction (1, 0, 0)
    >>> y = Direction (1, 1, 0)
    >>> z = Direction (0, 1, 1)
    >>> x
    <ansys.geometry.core.models.entities.basics.direction.Direction object at 0x000002252CE24D00>
    """

    def __init__(self, x, y, z):
        """Direction constructor."""
        if not all(isinstance(value, (int, float)) for value in [x, y, z]):
            raise ValueError("The parameters 'x', 'y' and 'z' should be integer or float")
        self._x = x
        self._y = y
        self._z = z
        self._msg = None

    @classmethod
    def _from_message(cls, value):
        """Provide constructor for obtaining the ``Direction`` object from its related gRPC message.

        Parameters
        ----------
        value : gRPC Point message.
            gRPC message to transform to a ``Direction`` object.

        Returns
        -------
        Direction : ansys.geometry.models.entities.basics.direction.Direction
            The Direction object.

        """
        return Direction(value.x, value.y, value.z)

    @property
    def x(self):
        """Return the x-axis direction value.

        Examples
        --------
        Create a direction.

        >>> from ansys.geometry.core.models import Direction
        >>> axis = Direction (1, 1, 0)

        Change the x-axis direction value.

        >>> axis.x = 0
        """
        return self._x

    @x.setter
    def x(self, x):
        """Set the x-axis direction."""
        if not isinstance(x, (int, float)):
            raise ValueError("The parameter 'x' should be a float or an integer value")
        self._x = x
        self._update_message()

    @property
    def y(self):
        """Return the y-axis direction value.

        Examples
        --------
        Create a direction.

        >>> from ansys.geometry.core.models import Direction
        >>> axis = Direction (1, 1, 0)

        Change the y-axis direction value.

        >>> axis.y = 0
        """
        return self._y

    @y.setter
    def y(self, y):
        """Set the y-axis direction."""
        if not isinstance(y, (int, float)):
            raise ValueError("The parameter 'y' should be a float or an integer value")
        self._y = y
        self._update_message()

    @property
    def z(self):
        """Return the z-axis direction value.

        Examples
        --------
        Create a direction.

        >>> from ansys.geometry.core.models import Direction
        >>> axis = Direction (1, 1, 0)

        Change the z-axis direction value

        >>> axis.z = 1
        """
        return self._z

    @z.setter
    def z(self, z):
        """Set the z-axis direction."""
        if not isinstance(z, (int, float)):
            raise ValueError("The parameter 'z' should be a float or an integer value")
        self._z = z
        self._update_message()

    def _update_message(self):
        """Update the gRPC Direction message."""
        self._msg = None
