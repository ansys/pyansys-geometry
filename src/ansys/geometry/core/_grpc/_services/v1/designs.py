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
"""Module containing the designs service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.designs import GRPCDesignsService
from .conversions import (
    build_grpc_id,
    from_grpc_curve_to_curve,
    from_grpc_frame_to_frame,
    from_grpc_material_to_material,
    from_grpc_matrix_to_matrix,
    from_grpc_plane_to_plane,
    from_grpc_point_to_point3d,
)


class GRPCDesignsServiceV1(GRPCDesignsService):
    """Designs service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    designs service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.commands.file_pb2_grpc import FileStub
        from ansys.api.discovery.v1.design.designdoc_pb2_grpc import DesignDocStub

        self.file_stub = FileStub(channel)
        self.designdoc_stub = DesignDocStub(channel)

    @protect_grpc
    def open(self, **kwargs) -> dict:  # noqa: D102
        from pathlib import Path
        from typing import TYPE_CHECKING, Generator

        from ansys.api.discovery.v1.commands.file_pb2 import OpenMode, OpenRequest

        import ansys.geometry.core.connection.defaults as pygeom_defaults

        from .conversions import from_import_options_definitions_to_grpc_import_options_definition

        if TYPE_CHECKING:  # pragma: no cover
            from ansys.geometry.core.misc.options import ImportOptions, ImportOptionsDefinitions

        def request_generator(
            file_path: Path,
            file_name: str,
            import_options: "ImportOptions",
            import_options_definitions: "ImportOptionsDefinitions",
            open_mode: OpenMode,
        ) -> Generator[OpenRequest, None, None]:
            """Generate requests for streaming file upload."""
            msg_buffer = 5 * 1024  # 5KB - for additional message data
            if pygeom_defaults.MAX_MESSAGE_LENGTH - msg_buffer < 0:  # pragma: no cover
                raise ValueError("MAX_MESSAGE_LENGTH is too small for file upload.")

            chunk_size = pygeom_defaults.MAX_MESSAGE_LENGTH - msg_buffer
            with Path.open(file_path, "rb") as file:
                while chunk := file.read(chunk_size):
                    test_req = OpenRequest(
                        data=chunk,
                        file_name=file_name,
                        open_mode=open_mode,
                        import_options=import_options.to_dict(),
                        import_options_definitions=from_import_options_definitions_to_grpc_import_options_definition(
                            import_options_definitions
                        ),
                    )
                    yield test_req

        # Get the open mode
        open_mode = kwargs["open_mode"]
        if open_mode == "new":
            open_mode = OpenMode.OPENMODE_NEW
        elif open_mode == "insert":
            open_mode = OpenMode.OPENMODE_INSERT

        # Call the gRPC service
        response = self.file_stub.Open(
            request_generator(
                file_path=kwargs["filepath"],
                file_name=kwargs["original_file_name"],
                import_options=kwargs["import_options"],
                import_options_definitions=kwargs["import_options_definitions"],
                open_mode=open_mode,
            )
        )

        # Return the response - formatted as a dictionary
        return {"file_path": response.design.path}

    @protect_grpc
    def new(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commands.file_pb2 import NewRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = NewRequest(name=kwargs["name"])

        # Call the gRPC service
        response = self.file_stub.New(request)

        # Return the response - formatted as a dictionary
        return {
            "design_id": response.design.id.id,
            "main_part_id": response.design.main_part_id.id,
        }

    @protect_grpc
    def get_assembly(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.designdoc_pb2 import GetAssemblyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = GetAssemblyRequest(id=build_grpc_id(kwargs["active_design"].get("design_id")))

        # Call the gRPC service
        response = self.designdoc_stub.GetAssembly(request)

        # Return the response - formatted as a dictionary
        serialized_response = self._serialize_assembly_response(response)
        return serialized_response

    @protect_grpc
    def close(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commands.file_pb2 import CloseRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CloseRequest(design_id=build_grpc_id(kwargs["design_id"]))

        # Call the gRPC service
        _ = self.file_stub.Close(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def put_active(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError(
            f"Method '{self.__class__.__name__}.put_active' is not "
            "implemented in this protofile version."
        )

    @protect_grpc
    def save_as(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commands.file_pb2 import SaveRequest

        from .conversions import (
            _check_write_body_facets_input,
            from_design_file_format_to_grpc_file_export_format,
        )

        _check_write_body_facets_input(kwargs["backend_version"], kwargs["write_body_facets"])

        # Create the request - assumes all inputs are valid and of the proper type
        request = SaveRequest(
            format=from_design_file_format_to_grpc_file_export_format(kwargs["format"]),
            write_body_facets=kwargs["write_body_facets"],
        )

        # Call the gRPC service
        response_stream = self.file_stub.Save(request)

        # Return the response - formatted as a dictionary
        data = bytes()
        for response in response_stream:
            data += response.data

        return {
            "data": data,
        }

    @protect_grpc
    def download_export(self, **kwargs) -> dict:  # noqa: D102
        return self.save_as(**kwargs)

    @protect_grpc
    def stream_download_export(self, **kwargs) -> dict:  # noqa: D102
        return self.save_as(**kwargs)

    @protect_grpc
    def insert(self, **kwargs) -> dict:  # noqa: D102
        # Route to open method
        return self.open(**kwargs, open_mode="insert")

    @protect_grpc
    def get_active(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import EntityRequest

        # Call the gRPC service
        response = self.designdoc_stub.Get(request=EntityRequest(id=build_grpc_id("")))

        # Return the response - formatted as a dictionary
        if response.design:
            return {
                "design_id": response.design.id.id,
                "main_part_id": response.design.main_part_id.id,
                "name": response.design.name,
            }

    @protect_grpc
    def upload_file(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError(
            f"Method '{self.__class__.__name__}.upload_file' is not "
            "implemented in this protofile version."
        )

    @protect_grpc
    def upload_file_stream(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError(
            f"Method '{self.__class__.__name__}.upload_file_stream' is not "
            "implemented in this protofile version."
        )

    @protect_grpc
    def stream_design_tessellation(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.designdoc_pb2 import DesignTessellationRequest

        from .conversions import (
            from_grpc_edge_tess_to_raw_data,
            from_grpc_tess_to_raw_data,
            from_tess_options_to_grpc_tess_options,
        )

        # If there are options, convert to gRPC options
        options = (
            from_tess_options_to_grpc_tess_options(kwargs["options"])
            if kwargs["options"] is not None
            else None
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = DesignTessellationRequest(
            options=options,
            include_faces=kwargs["include_faces"],
            include_edges=kwargs["include_edges"],
        )

        # Call the gRPC service
        response_stream = self.designdoc_stub.StreamDesignTessellation(request)

        # Return the response - formatted as a dictionary
        tess_map = {}
        for elem in response_stream:
            for body_id, body_tess in elem.body_tessellation.items():
                tess = {}
                for face_id, face_tess in body_tess.face_tessellation.items():
                    tess[face_id] = from_grpc_tess_to_raw_data(face_tess)
                for edge_id, edge_tess in body_tess.edge_tessellation.items():
                    tess[edge_id] = from_grpc_edge_tess_to_raw_data(edge_tess)
                tess_map[body_id] = tess

        return {
            "tessellation": tess_map,
        }

    @protect_grpc
    def download_file(self, **kwargs) -> dict:  # noqa: D102
        # This method is only accessed by __export_and_download_legacy,
        # which is only used for older versions of the server. Since this class
        # is only used for v1 of the protofiles, this method will not be implemented
        # here. If this method is called, it means there is a mismatch between the server
        # version and the protofiles version being used, and an error should be raised to
        # alert the user of this mismatch.
        raise NotImplementedError(  # pragma: no cover
            f"Method '{self.__class__.__name__}.download_file' is not "
            "implemented in this protofile version."
        )

    def _serialize_assembly_response(self, response):
        def serialize_body(body):
            return {
                "id": body.id.id,
                "name": body.name,
                "master_id": body.master_id.id,
                "parent_id": body.parent_id.id,
                "is_surface": body.is_surface,
            }

        def serialize_component(component):
            return {
                "id": component.id.id,
                "parent_id": component.parent_id.id,
                "master_id": component.master_id.id,
                "name": component.name,
                "placement": component.placement,
                "part_master": serialize_part(component.part_master),
            }

        def serialize_transformed_part(transformed_part):
            return {
                "id": transformed_part.id.id,
                "name": transformed_part.name,
                "placement": from_grpc_matrix_to_matrix(transformed_part.placement),
                "part_master": serialize_part(transformed_part.part_master),
            }

        def serialize_part(part):
            return {
                "id": part.id.id,
                "name": part.name,
            }

        def serialize_material_properties(material_property):
            return {
                "id": material_property.id.id,
                "display_name": material_property.display_name,
                "value": material_property.value,
                "units": material_property.units,
            }

        def serialize_material(material):
            material_properties = getattr(material, "material_properties", [])
            return {
                "name": material.name,
                "material_properties": [
                    serialize_material_properties(property) for property in material_properties
                ],
            }

        def serialize_named_selection(named_selection):
            return {"id": named_selection.id.id, "name": named_selection.name}

        def serialize_coordinate_systems(coordinate_systems):
            serialized_cs = []
            for cs in coordinate_systems.coordinate_systems:
                serialized_cs.append(
                    {
                        "id": cs.id.id,
                        "name": cs.name,
                        "frame": from_grpc_frame_to_frame(cs.frame),
                    }
                )

            return serialized_cs

        def serialize_component_coordinate_systems(component_coordinate_system):
            serialized_component_coordinate_systems = []
            for (
                component_coordinate_system_id,
                coordinate_systems,
            ) in component_coordinate_system.items():
                serialized_component_coordinate_systems.append(
                    {
                        "component_id": component_coordinate_system_id,
                        "coordinate_systems": serialize_coordinate_systems(coordinate_systems),
                    }
                )

            return serialized_component_coordinate_systems

        def serialize_component_shared_topologies(component_share_topology):
            serialized_share_topology = []
            for component_shared_topology_id, shared_topology in component_share_topology.items():
                serialized_share_topology.append(
                    {
                        "component_id": component_shared_topology_id,
                        "shared_topology_type": shared_topology,
                    }
                )
            return serialized_share_topology

        def serialize_beam_curve(curve):
            return {
                "curve": from_grpc_curve_to_curve(curve.curve),
                "start": from_grpc_point_to_point3d(curve.start),
                "end": from_grpc_point_to_point3d(curve.end),
                "interval_start": curve.interval_start,
                "interval_end": curve.interval_end,
                "length": curve.length,
            }

        def serialize_beam_curve_list(curve_list):
            return {"curves": [serialize_beam_curve(curve) for curve in curve_list.curves]}

        def serialize_beam_cross_section(cross_section):
            return {
                "section_anchor": cross_section.section_anchor,
                "section_angle": cross_section.section_angle.value_in_geometry_units,
                "section_frame": from_grpc_frame_to_frame(cross_section.section_frame),
                "section_profile": [
                    serialize_beam_curve_list(curve_list)
                    for curve_list in cross_section.section_profile
                ],
            }

        def serialize_beam_properties(properties):
            return {
                "area": properties.area.value_in_geometry_units,
                "centroid_x": properties.centroid_x.value_in_geometry_units,
                "centroid_y": properties.centroid_y.value_in_geometry_units,
                "warping_constant": properties.warping_constant.value_in_geometry_units,
                "ixx": properties.ixx.value_in_geometry_units,
                "ixy": properties.ixy.value_in_geometry_units,
                "iyy": properties.iyy.value_in_geometry_units,
                "shear_center_x": properties.shear_center_x.value_in_geometry_units,
                "shear_center_y": properties.shear_center_y.value_in_geometry_units,
                "torsional_constant": properties.torsional_constant.value_in_geometry_units,
            }

        def serialize_beam(beam):
            return {
                "id": beam.id.id,
                "parent_id": beam.parent.id,
                "start": from_grpc_point_to_point3d(beam.shape.start),
                "end": from_grpc_point_to_point3d(beam.shape.end),
                "name": beam.name,
                "is_deleted": beam.is_deleted,
                "is_reversed": beam.is_reversed,
                "is_rigid": beam.is_rigid,
                "material": from_grpc_material_to_material(beam.material),
                "type": beam.type,
                "properties": serialize_beam_properties(beam.properties),
                "cross_section": serialize_beam_cross_section(beam.cross_section),
            }

        def serialize_design_point(design_point):
            return {
                "id": design_point.id.id,
                "name": design_point.owner_name,
                "point": from_grpc_point_to_point3d(design_point.points[0]),
                "parent_id": design_point.parent_id.id,
            }
        
        def serialize_datum_plane(datum_plane):
            return {
                "id": datum_plane.id.id,
                "name": datum_plane.name,
                "plane": from_grpc_plane_to_plane(datum_plane.plane),
                "parent_id": datum_plane.parent_id.id,
            }

        parts = getattr(response, "parts", [])
        transformed_parts = getattr(response, "transformed_parts", [])
        bodies = getattr(response, "bodies", [])
        components = getattr(response, "components", [])
        materials = getattr(response, "materials", [])
        named_selections = getattr(response, "named_selections", [])
        component_coordinate_systems = getattr(response, "component_coord_systems", [])
        component_shared_topologies = getattr(response, "component_shared_topologies", [])
        beams = getattr(response, "beams", [])
        design_points = getattr(response, "design_points", [])
        datum_planes = getattr(response, "datum_planes", [])
        return {
            "parts": [serialize_part(part) for part in parts] if len(parts) > 0 else [],
            "transformed_parts": [serialize_transformed_part(tp) for tp in transformed_parts],
            "bodies": [serialize_body(body) for body in bodies] if len(bodies) > 0 else [],
            "components": [serialize_component(component) for component in components],
            "materials": [serialize_material(material) for material in materials],
            "named_selections": [serialize_named_selection(ns) for ns in named_selections],
            "component_coordinate_systems": serialize_component_coordinate_systems(
                component_coordinate_systems
            ),
            "component_shared_topologies": serialize_component_shared_topologies(
                component_shared_topologies
            ),
            "beams": [serialize_beam(beam) for beam in beams],
            "design_points": [serialize_design_point(dp) for dp in design_points],
            "datum_planes": [serialize_datum_plane(dp) for dp in datum_planes],
        }
