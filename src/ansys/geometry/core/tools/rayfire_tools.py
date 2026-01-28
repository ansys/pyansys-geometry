# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Provides tools for interacting with rayfire."""

from typing import TYPE_CHECKING

from pint import Quantity

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.errors import GeometryRuntimeError
from ansys.geometry.core.misc.checks import min_backend_version
from ansys.geometry.core.misc.measurements import Distance
from ansys.geometry.core.misc.options import RayfireOptions
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.face import Face
    from ansys.geometry.core.math.point import Point3D
    from ansys.geometry.core.math.vector import UnitVector3D
    from ansys.geometry.core.modeler import Modeler


class RayfireTools:
    """Rayfire tools for PyAnsys Geometry.
    
    Parameters
    ----------
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    modeler : Modeler
        The parent modeler instance.
    _internal_use : bool, optional
        Internal flag to prevent direct instantiation by users.
        This parameter is for internal use only.
    
    Raises
    ------
    GeometryRuntimeError
        If the class is instantiated directly by users instead
        of through the modeler.

    Notes
    -----
    This class should not be instantiated directly. Use
    ``modeler.rayfire_tools`` instead.   
    """

    def __init__(
        self, grpc_client: GrpcClient, modeler: "Modeler", _internal_use: bool = False
    ):
        """Initialize a new instance of the ``RepairTools`` class."""
        if not _internal_use:
            raise GeometryRuntimeError(
                "RayfireTools should not be instantiated directly. "
                "Use 'modeler.rayfire_tools' to access rayfire tools."
            )
        self._modeler = modeler
        self._grpc_client = grpc_client
    
    @min_backend_version(26, 1, 0)
    def rayfire(
        self,
        body: "Body",
        faces: list["Face"],
        direction: "UnitVector3D",
        points: list["Point3D"],
        max_distance: Distance | Quantity | Real,
    ) -> dict:
        """Perform rayfire operation.

        Parameters
        ----------
        body : Body
            Body to perform rayfire on.
        faces : list[Face]
            Faces to consider.
        direction : UnitVector3D
            Direction of the ray.
        points : list[Point3D]
            Starting points for rays.
        max_distance : Distance | Quantity | Real
            Maximum distance to check.

        Returns
        -------
        dict
            Rayfire results.
        """
        max_distance = (
            max_distance
            if isinstance(max_distance, Distance)
            else Distance(max_distance)
        )

        response = self._grpc_client.services.rayfire.rayfire(
            body_id=body.id,
            face_ids=[face.id for face in faces],
            direction=direction,
            points=points,
            max_distance=max_distance,
        )

        return response
    
    @min_backend_version(26, 1, 0)
    def rayfire_faces(
        self,
        body: "Body",
        faces: list["Face"],
        points: list["Point3D"],
        options: RayfireOptions | None = None,
    ) -> dict:
        """Perform the rayfire operation on faces.
        
        Parameters
        ----------
        body : Body
            Body to perform rayfire on.
        faces : list[Face]
            Faces to consider.
        points : list[Point3D]
            Starting points for rays.
        options : RayfireOptions, default: None
            Options for the rayfire operation.

        Returns
        -------
        dict
            Rayfire results.
        """
        response = self._grpc_client.services.rayfire.rayfire_faces(
            body_id=body.id,
            face_ids=[face.id for face in faces],
            points=points,
            options=options,
        )

        return response
    
    @min_backend_version(26, 1, 0)
    def rayfire_ordered(
        self,
        body: "Body",
        faces: list["Face"],
        direction: "UnitVector3D",
        ray_radius: Distance | Quantity | Real,
        points: list["Point3D"],
        max_distance: Distance | Quantity | Real,
        tight_tolerance: bool = False,
    ) -> dict:
        """Perform a rayfire ordered operation.
        
        Parameters
        ----------
        body : Body
            Body to perform rayfire on.
        faces : list[Face]
            Faces to consider.
        direction : UnitVector3D
            Direction of the ray.
        ray_radius : Distance | Quantity | Real
            The radius of the ray.
        points : list[Point3D]
            Starting points for rays.
        max_distance : Distance | Quantity | Real
            Maximum distance to check.
        tight_tolerance : bool, default: False
            Whether to use a tight tolerance for the ray fire operation.

        Returns
        -------
        dict
            Rayfire results.
        """
        ray_radius = ray_radius if isinstance(ray_radius, Distance) else Distance(ray_radius)
        max_distance = (
            max_distance
            if isinstance(max_distance, Distance)
            else Distance(max_distance)
        )

        response = self._grpc_client.services.rayfire.rayfire_ordered(
            body_id=body.id,
            face_ids=[face.id for face in faces],
            direction=direction,
            ray_radius=ray_radius,
            points=points,
            max_distance=max_distance,
            tight_tolerance=tight_tolerance,
        )

        return response
    
    @min_backend_version(26, 1, 0)
    def rayfire_ordered_uv(
        self,
        body: "Body",
        faces: list["Face"],
        direction: "UnitVector3D",
        ray_radius: Distance | Quantity | Real,
        points: list["Point3D"],
        max_distance: Distance | Quantity | Real,
        tight_tolerance: bool,
    ) -> dict:
        """Perform a rayfire ordered operation.
        
        Parameters
        ----------
        body : Body
            Body to perform rayfire on.
        faces : list[Face]
            Faces to consider.
        direction : UnitVector3D
            Direction of the ray.
        ray_radius : Distance | Quantity | Real
            The radius of the ray.
        points : list[Point3D]
            Starting points for rays.
        max_distance : Distance | Quantity | Real
            Maximum distance to check.
        tight_tolerance : bool
            Whether to use a tight tolerance for the ray fire operation.

        Returns
        -------
        dict
            Rayfire results.
        """
        ray_radius = ray_radius if isinstance(ray_radius, Distance) else Distance(ray_radius)
        max_distance = (
            max_distance
            if isinstance(max_distance, Distance)
            else Distance(max_distance)
        )

        response = self._grpc_client.services.rayfire.rayfire_ordered_uv(
            body_id=body.id,
            face_ids=[face.id for face in faces],
            direction=direction,
            ray_radius=ray_radius,
            points=points,
            max_distance=max_distance,
            tight_tolerance=tight_tolerance,
        )

        return response