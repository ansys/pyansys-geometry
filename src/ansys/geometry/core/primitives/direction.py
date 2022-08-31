"""``Direction2D`` and ``Direction3D`` class module."""
import numpy as np


class Direction3D(np.ndarray):
    """
    Provides 3D unit vector direction geometry primitive representation.

    Parameters
    ----------
    input : np.ndarray, List[int], List[float]
        The direction arguments, either as a np.ndarray, or as a list.
    """

    def __new__(cls, input):
        """Constructor for ``Direction3D``."""

        # TODO: Once Vector3D is available, just inherit from it
        #
        # obj = Vector3D(*args)
        #
        # But in the meantime...
        #
        obj = np.asarray(input).view(cls)

        if obj is None or len(obj) != 3:
            raise ValueError("Direction3D must have three coordinates.")

        if not np.issubdtype(obj.dtype, np.number) or not all(
            isinstance(value, (int, float)) for value in obj.data
        ):
            raise ValueError("The input parameters should be integer or float.")

        # Once we know we have a Vector3D... normalize!
        norm = np.linalg.norm(obj)

        if norm > 0:
            return obj / norm
        else:
            raise ValueError("The norm of the input Vector3D is not valid.")

    @property
    def ux(self):
        """Returns the X component of the direction."""
        return self[0]

    @property
    def uy(self):
        """Returns the Y component of the direction."""
        return self[1]

    @property
    def uz(self):
        """Returns the Z component of the direction."""
        return self[2]


class Direction2D(np.ndarray):
    """
    Provides 2D unit vector direction geometry primitive representation.

    Parameters
    ----------
    input : np.ndarray, List[int], List[float]
        The direction arguments, either as a np.ndarray, or as a list.
    """

    def __new__(cls, input):
        """Constructor for ``Direction2D``."""

        # TODO: Once Vector2D is available, just inherit from it
        #
        # obj = Vector2D(*args)
        #
        # But in the meantime...
        #
        obj = np.asarray(input).view(cls)

        if obj is None or len(obj) != 2:
            raise ValueError("Direction2D must have two coordinates.")

        if not np.issubdtype(obj.dtype, np.number) or not all(
            isinstance(value, (int, float)) for value in obj.data
        ):
            raise ValueError("The input parameters should be integer or float.")

        # Once we know we have a Vector2D... normalize!
        norm = np.linalg.norm(obj)

        if norm > 0:
            return obj / norm
        else:
            raise ValueError("The norm of the input Vector2D is not valid.")

    @property
    def ux(self):
        """Returns the X component of the direction."""
        return self[0]

    @property
    def uy(self):
        """Returns the Y component of the direction."""
        return self[1]
