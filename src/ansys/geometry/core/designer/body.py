"""``Body`` class module."""

from typing import TYPE_CHECKING

from ansys.geometry.core.connection.client import GrpcClient

if TYPE_CHECKING:
    from ansys.geometry.core.designer.component import Component


class Body:
    """
    Represents solids and surfaces organized within the design assembly.

    Synchronizes to a design within a supporting geometry service instance.

    Parameters
    ----------
    id : str
        A server defined identifier for the body.
    name : str
        A user-defined label for the body.
    parent_component : Component
        The parent component to nest the new component under within the design assembly.
    grpc_client : GrpcClient
        An active supporting geometry service instance for design modeling.
    """

    def __init__(self, id: str, name: str, parent_component: "Component", grpc_client: GrpcClient):
        """Constructor method for ``Body``."""

        self._id = id
        self._name = name
        self._parent_component = parent_component
        self._grpc_client = grpc_client
