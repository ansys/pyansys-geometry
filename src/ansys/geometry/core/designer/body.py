"""``Body`` class module."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.geometry.core.designer.component import Component


class Body:
    """
    Provides class for 3D geometry.

    Synchronizes to a server.
    """

    def __init__(self, id: str, name: str, parent_component: "Component"):
        """Constructor method for ``Body``."""

        self._id = id
        self._name = name
        self._parent_component = parent_component
