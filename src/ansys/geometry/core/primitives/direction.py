"""``Direction`` class module."""


class Direction:
    """
    Provides unit vector direction geometry primitive representation.

    Parameters
    ----------
    u: float
        U.
    v: float
        V.
    """

    def __init__(self, u: float, v: float):
        """Constructor method for ``Direction``."""
        self._u = u
        self._v = v
