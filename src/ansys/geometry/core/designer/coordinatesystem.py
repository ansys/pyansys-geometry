"""``CoordinateSystem`` class module."""

from typing import TYPE_CHECKING

from ansys.api.geometry.v0.coordinatesystems_pb2 import CreateCoordinateSystemRequest
from ansys.api.geometry.v0.coordinatesystems_pb2_grpc import CoordinateSystemsStub
from ansys.api.geometry.v0.models_pb2 import CoordinateSystem as cs

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.connection.conversions import frame_to_grpc_frame
from ansys.geometry.core.math import Frame, Point, UnitVector
from ansys.geometry.core.misc import SERVER_UNIT_LENGTH

if TYPE_CHECKING:
    from ansys.geometry.core.designer.component import Component  # pragma: no cover


class CoordinateSystem:
    """
    Represents a user-defined coordinate system within the design assembly.

    Synchronizes to a design within a supporting geometry service instance.

    Parameters
    ----------
    name : str
        A user-defined label for the coordinate system.
    frame : Frame
        The frame defining the coordinate system bounds.
    parent_component : Component
        The parent component the coordinate system is assigned against.
    grpc_client : GrpcClient
        An active supporting geometry service instance for design modeling.
    """

    def __init__(
        self, name: str, frame: Frame, parent_component: "Component", grpc_client: GrpcClient
    ):
        """Constructor method for ``CoordinateSystem``."""

        self._parent_component = parent_component
        self._grpc_client = grpc_client
        self._coordinate_systems_stub = CoordinateSystemsStub(grpc_client.channel)

        new_coordinate_system = self._coordinate_systems_stub.CreateCoordinateSystem(
            CreateCoordinateSystemRequest(
                parent=parent_component.id,
                coordinate_system=cs(display_name=name, frame=frame_to_grpc_frame(frame)),
            )
        )

        self._id = new_coordinate_system.id
        self._name = new_coordinate_system.display_name
        self._frame = Frame(
            Point(
                [
                    new_coordinate_system.frame.origin.x,
                    new_coordinate_system.frame.origin.y,
                    new_coordinate_system.frame.origin.z,
                ],
                SERVER_UNIT_LENGTH,
            ),
            UnitVector(
                [
                    new_coordinate_system.frame.dir_x.x,
                    new_coordinate_system.frame.dir_x.y,
                    new_coordinate_system.frame.dir_x.z,
                ]
            ),
            UnitVector(
                [
                    new_coordinate_system.frame.dir_y.x,
                    new_coordinate_system.frame.dir_y.y,
                    new_coordinate_system.frame.dir_y.z,
                ]
            ),
        )

    @property
    def id(self) -> str:
        """ID of the coordinate system."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the coordinate system."""
        return self._name

    @property
    def frame(self) -> Frame:
        """Frame of the coordinate system."""
        return self._frame

    @property
    def parent_component(self) -> "Component":
        """Parent component of the coordinate system."""
        return self._parent_component
