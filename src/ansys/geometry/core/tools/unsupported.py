# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
"""Unsupported functions for the PyAnsys Geometry library."""

from dataclasses import dataclass
from enum import Enum, unique
from typing import TYPE_CHECKING

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import GeometryRuntimeError
from ansys.geometry.core.misc.auxiliary import get_all_bodies_from_design
from ansys.geometry.core.misc.checks import (
    min_backend_version,
)

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.edge import Edge
    from ansys.geometry.core.designer.face import Face
    from ansys.geometry.core.modeler import Modeler


@unique
class PersistentIdType(Enum):
    """Type of persistent id."""

    PNAME = 1
    PRIME_ID = 700


@dataclass
class ExportIdData:
    """Data for exporting persistent ids."""

    moniker: str
    id_type: PersistentIdType
    value: str


class UnsupportedCommands:
    """Provides unsupported commands for PyAnsys Geometry.

    Parameters
    ----------
    grpc_client : GrpcClient
        gRPC client to use for the geometry commands.
    modeler : Modeler
        Modeler instance to use for the geometry commands.
    _internal_use : bool, optional
        Internal flag to prevent direct instantiation by users.
        This parameter is for internal use only.

    Raises
    ------
    GeometryRuntimeError
        If the class is instantiated directly by users instead of through the modeler.

    Notes
    -----
    This class should not be instantiated directly. Use
    ``modeler.unsupported`` instead.

    """

    def __init__(self, grpc_client: GrpcClient, modeler: "Modeler", _internal_use: bool = False):
        """Initialize an instance of the ``UnsupportedCommands`` class."""
        if not _internal_use:
            raise GeometryRuntimeError(
                "UnsupportedCommands should not be instantiated directly. "
                "Use 'modeler.unsupported' to access unsupported commands."
            )
        self._grpc_client = grpc_client
        self.__id_map = {}
        self.__modeler = modeler
        self.__current_design = modeler.get_active_design()

    @min_backend_version(25, 2, 0)
    def __fill_imported_id_map(self, id_type: PersistentIdType) -> None:
        """Populate the persistent id map for caching.

        This cache should be cleared on design change.

        Parameters
        ----------
        id_type : PersistentIdType
            Type of id.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        result = self._grpc_client.services.unsupported.get_import_id_map(id_type=id_type)
        self.__id_map[id_type] = result.get("id_map", {})

    def __is_occurrence(self, master: str, occ: str) -> bool:
        """Determine if the master is the master of the occurrence.

        Parameters
        ----------
        master : str
            Master moniker.
        occ : str
            Occurrence moniker.

        Returns
        -------
        bool
            ``True`` if the master is the master of the occurrence.

        """
        master_id = occ.split("/")[-1]
        return master == master_id

    def __get_moniker_from_import_id(self, id_type: PersistentIdType, import_id: str) -> str | None:
        """Look up the moniker from the id map.

        Parameters
        ----------
        id_type : PersistentIdType
            Type of id.
        import_id : str
            Persistent id.

        Returns
        -------
        str | None
            Moniker associated with the id or None

        Notes
        -----
        This checks if the design has changed and clears the cache if it has.
        """
        if (
            self.__current_design != self.__modeler.get_active_design()
            or id_type not in self.__id_map
        ):
            self.__fill_imported_id_map(id_type)
        moniker = self.__id_map[id_type].get(import_id, None)
        return moniker

    @min_backend_version(25, 2, 0)
    def set_export_id(self, moniker: str, id_type: PersistentIdType, value: str) -> None:
        """Set the persistent id for the moniker.

        Parameters
        ----------
        moniker : str
            Moniker to set the id for.
        id_type : PersistentIdType
            Type of id.
        value : str
            Id to set.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        self._grpc_client.services.unsupported.set_export_ids(
            export_data=[ExportIdData(moniker=moniker, id_type=id_type, value=value)]
        )
        self.__id_map = {}

    @min_backend_version(26, 1, 0)
    def set_multiple_export_ids(
        self,
        export_data: list[ExportIdData],
    ) -> None:
        """Set multiple persistent ids for the monikers.

        Parameters
        ----------
        export_data : list[ExportIdData]
            List of export data containing monikers, id types, and values.

        Warnings
        --------
        This method is only available starting on Ansys release 26R1.
        """
        # Call the gRPC service
        _ = self._grpc_client.services.unsupported.set_export_ids(export_data=export_data)
        self.__id_map = {}

    def get_body_occurrences_from_import_id(
        self, import_id: str, id_type: PersistentIdType
    ) -> list["Body"]:
        """Get all body occurrences whose master has the given import id.

        Parameters
        ----------
        import_id : str
            Persistent id
        id_type : PersistentIdType
            Type of id

        Returns
        -------
        list[Body]
            List of body occurrences.
        """
        moniker = self.__get_moniker_from_import_id(id_type, import_id)

        if moniker is None:
            return []

        design = self.__modeler.get_active_design()
        return [
            body
            for body in get_all_bodies_from_design(design)
            if self.__is_occurrence(moniker, body.id)
        ]

    def get_face_occurrences_from_import_id(
        self, import_id: str, id_type: PersistentIdType
    ) -> list["Face"]:
        """Get all face occurrences whose master has the given import id.

        Parameters
        ----------
        import_id : str
            Persistent id.
        id_type : PersistentIdType
            Type of id.

        Returns
        -------
        list[Face]
            List of face occurrences.
        """
        moniker = self.__get_moniker_from_import_id(id_type, import_id)

        if moniker is None:
            return []

        design = self.__modeler.get_active_design()
        return [
            face
            for body in get_all_bodies_from_design(design)
            for face in body.faces
            if self.__is_occurrence(moniker, face.id)
        ]

    def get_edge_occurrences_from_import_id(
        self, import_id: str, id_type: PersistentIdType
    ) -> list["Edge"]:
        """Get all edge occurrences whose master has the given import id.

        Parameters
        ----------
        import_id : str
           Persistent id.
        id_type : PersistentIdType
           Type of id.

        Returns
        -------
        list[Edge]
           List of edge occurrences.
        """
        moniker = self.__get_moniker_from_import_id(id_type, import_id)

        if moniker is None:
            return []

        design = self.__modeler.get_active_design()
        return [
            edge
            for body in get_all_bodies_from_design(design)
            for edge in body.edges
            if self.__is_occurrence(moniker, edge.id)
        ]
