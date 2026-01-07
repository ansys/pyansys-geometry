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
"""Provides tools for measurement."""

from typing import TYPE_CHECKING, Union

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import GeometryRuntimeError
from ansys.geometry.core.misc.checks import min_backend_version
from ansys.geometry.core.misc.measurements import Distance

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.edge import Edge
    from ansys.geometry.core.designer.face import Face


class Gap:
    """Represents a gap between two bodies.

    Parameters
    ----------
    distance : Distance
        Distance between two sides of the gap.
    """

    def __init__(self, distance: Distance):
        """Initialize ``Gap`` class."""
        self._distance = distance

    @property
    def distance(self) -> Distance:
        """Returns the closest distance between two bodies."""
        return self._distance


class MeasurementTools:
    """Measurement tools for PyAnsys Geometry.

    Parameters
    ----------
    grpc_client : GrpcClient
        gRPC client to use for the measurement tools.
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
    ``modeler.measurement_tools`` instead.
    """

    def __init__(self, grpc_client: GrpcClient, _internal_use: bool = False):
        """Initialize measurement tools class."""
        if not _internal_use:
            raise GeometryRuntimeError(
                "MeasurementTools should not be instantiated directly. "
                "Use 'modeler.measurement_tools' to access measurement tools."
            )
        self._grpc_client = grpc_client

    @min_backend_version(24, 2, 0)
    def min_distance_between_objects(
        self, object1: Union["Body", "Face", "Edge"], object2: Union["Body", "Face", "Edge"]
    ) -> Gap:
        """Find the gap between two bodies.

        Parameters
        ----------
        object1 : Union[Body, Face, Edge]
            First object to measure the gap.
        object2 : Union[Body, Face, Edge]
            Second object to measure the gap.

        Returns
        -------
        Gap
            Gap between two bodies.

        Warnings
        --------
        This method is only available starting on Ansys release 24R2.
        Also, using Face and Edge objects as inputs requires a minimum Ansys
        release of 25R2.
        """
        from ansys.geometry.core.designer.edge import Edge
        from ansys.geometry.core.designer.face import Face

        # Face and Edge objects are only accepted if the backend version is 25R2 or later.
        for obj in (object1, object2):
            if isinstance(obj, (Face, Edge)) and self._grpc_client.backend_version < (25, 2, 0):
                raise GeometryRuntimeError(
                    f"The method '{self.min_distance_between_objects.__name__}' using "
                    "Face and Edge objects as inputs requires a minimum Ansys release version of "
                    f"25.2.0, but the current version used is {self._grpc_client.backend_version}."
                )

        response = self._grpc_client.services.measurement_tools.min_distance_between_objects(
            selection=[object1.id, object2.id],
            backend_version=self._grpc_client.backend_version,
        )
        return Gap(response.get("distance"))
