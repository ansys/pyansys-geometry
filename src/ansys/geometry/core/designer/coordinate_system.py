"""Provides the ``CoordinateSystem`` class module."""

from ansys.api.geometry.v0.coordinatesystems_pb2 import CreateRequest
from ansys.api.geometry.v0.coordinatesystems_pb2_grpc import CoordinateSystemsStub
from beartype.typing import TYPE_CHECKING, Optional

from ansys.geometry.core.connection import GrpcClient, frame_to_grpc_frame
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.math import Frame, Point3D, UnitVector3D
from ansys.geometry.core.misc import DEFAULT_UNITS

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.component import Component


class CoordinateSystem:
    """
    Represents a user-defined coordinate system within the design assembly.

    This coordinate system synchronizes to a design within a supporting Geometry service instance.

    Parameters
    ----------
    name : str
        User-defined label for the coordinate system.
    frame : Frame
        Frame defining the coordinate system bounds.
    parent_component : Component, default: Component
        Parent component the coordinate system is assigned against.
    grpc_client : GrpcClient
        Active supporting Geometry service instance for design modeling.
    """

    @protect_grpc
    def __init__(
        self,
        name: str,
        frame: Frame,
        parent_component: "Component",
        grpc_client: GrpcClient,
        preexisting_id: Optional[str] = None,
    ):
        """Initialize ``CoordinateSystem`` class."""
        self._parent_component = parent_component
        self._grpc_client = grpc_client
        self._coordinate_systems_stub = CoordinateSystemsStub(grpc_client.channel)
        self._is_alive = True

        # Create without going to server
        if preexisting_id:
            self._name = name
            self._frame = frame
            self._id = preexisting_id
            return

        self._grpc_client.log.debug("Requesting creation of Coordinate System.")
        new_coordinate_system = self._coordinate_systems_stub.Create(
            CreateRequest(
                parent=parent_component.id,
                name=name,
                frame=frame_to_grpc_frame(frame),
            )
        )

        self._id = new_coordinate_system.id
        self._name = new_coordinate_system.name
        self._frame = Frame(
            Point3D(
                [
                    new_coordinate_system.frame.origin.x,
                    new_coordinate_system.frame.origin.y,
                    new_coordinate_system.frame.origin.z,
                ],
                DEFAULT_UNITS.SERVER_LENGTH,
            ),
            UnitVector3D(
                [
                    new_coordinate_system.frame.dir_x.x,
                    new_coordinate_system.frame.dir_x.y,
                    new_coordinate_system.frame.dir_x.z,
                ]
            ),
            UnitVector3D(
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

    @property
    def is_alive(self) -> bool:
        """If the CoordinateSystem is still alive on the server side."""
        return self._is_alive

    def __repr__(self) -> str:
        """Represent the ``CoordinateSystem`` as a string."""
        lines = [f"ansys.geometry.core.designer.CoordinateSystem {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Exists               : {self.is_alive}")
        lines.append(f"  Parent component     : {self.parent_component.name}")
        lines.append(
            f"  Frame origin         : [{','.join([str(x) for x in self.frame.origin])}] in meters"
        )
        lines.append(
            f"  Frame X-direction    : [{','.join([str(x) for x in self.frame.direction_x])}]"
        )
        lines.append(
            f"  Frame Y-direction    : [{','.join([str(x) for x in self.frame.direction_y])}]"
        )
        lines.append(
            f"  Frame Z-direction    : [{','.join([str(x) for x in self.frame.direction_z])}]"
        )
        return "\n".join(lines)
