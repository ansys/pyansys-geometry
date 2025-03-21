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
"""Auxiliary functions for the PyAnsys Geometry library."""

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.beam import Beam
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.component import Component
    from ansys.geometry.core.designer.design import Design
    from ansys.geometry.core.designer.edge import Edge
    from ansys.geometry.core.designer.face import Face

try:
    from ansys.tools.visualization_interface.utils.color import Color

    DEFAULT_COLOR = Color.DEFAULT.value
except ModuleNotFoundError:
    DEFAULT_COLOR = "#D6F7D1"


def get_design_from_component(component: "Component") -> "Design":
    """Get the ``Design`` of the given ``Component`` object.

    Parameters
    ----------
    component : Component
        The component object for which to find the ``Design``.

    Returns
    -------
    Design
        The ``Design`` of the provided component object.
    """
    # Get the design of the component
    while component.parent_component is not None:
        component = component.parent_component

    # Return the design
    return component


def get_design_from_body(body: "Body") -> "Design":
    """Get the ``Design`` of the given ``Body`` object.

    Parameters
    ----------
    body : Body
        The body object for which to find the ``Design``.

    Returns
    -------
    Design
        The ``Design`` of the provided body object.
    """
    # Get the parent component of the body
    component = body.parent_component

    # Get the design of the component
    return get_design_from_component(component)


def get_design_from_face(face: "Face") -> "Design":
    """Get the ``Design`` of the given ``Face`` object.

    Parameters
    ----------
    face : Face
        The face object for which to find the ``Design``.

    Returns
    -------
    Design
        The ``Design`` of the provided face object.
    """
    # Get the parent body of the face
    body = face.body

    # Get the design of the body
    return get_design_from_body(body)


def get_design_from_edge(edge: "Edge") -> "Design":
    """Get the ``Design`` of the given ``Edge`` object.

    Parameters
    ----------
    edge : Edge
        The edge object for which to find the ``Design``.

    Returns
    -------
    Design
        The ``Design`` of the provided edge object.
    """
    # Get the one of the bodies of the edge
    body = edge.faces[0].body

    # Get the design of the body
    return get_design_from_body(body)


def __traverse_component_elem(elem: str, comp: Union["Design", "Component"]) -> list:
    """Traverses all elements of a component or design, given its name."""
    elems = []
    comp_elems = getattr(comp, elem)
    elems.extend(comp_elems)
    for component in comp.components:
        elems.extend(__traverse_component_elem(elem, component))

    return elems


def __traverse_all_bodies(comp: Union["Design", "Component"]) -> list["Body"]:
    """Traverse all bodies in a design/component and all its subcomponents."""
    return __traverse_component_elem("bodies", comp)


def __traverse_all_beams(comp: Union["Design", "Component"]) -> list["Body"]:
    """Traverse all beams in a design/component and all its subcomponents."""
    return __traverse_component_elem("beams", comp)


def get_all_bodies_from_design(design: "Design") -> list["Body"]:
    """Find all the ``Body`` objects inside a ``Design``.

    Parameters
    ----------
    design : Design
        Parent design for the bodies.

    Returns
    -------
    list[Body]
        List of Body objects.

    Notes
    -----
    This method takes a design and gets the corresponding ``Body`` objects.
    """
    return __traverse_all_bodies(design)


def get_bodies_from_ids(design: "Design", body_ids: list[str]) -> list["Body"]:
    """Find the ``Body`` objects inside a ``Design`` from its ids.

    Parameters
    ----------
    design : Design
        Parent design for the faces.
    body_ids : list[str]
        List of body ids.

    Returns
    -------
    list[Body]
        List of Body objects.

    Notes
    -----
    This method takes a design and body ids, and gets their corresponding ``Body`` object.
    """
    return [body for body in __traverse_all_bodies(design) if body.id in body_ids]


def get_faces_from_ids(design: "Design", face_ids: list[str]) -> list["Face"]:
    """Find the ``Face`` objects inside a ``Design`` from its ids.

    Parameters
    ----------
    design : Design
        Parent design for the faces.
    face_ids : list[str]
        List of face ids.

    Returns
    -------
    list[Face]
        List of Face objects.

    Notes
    -----
    This method takes a design and face ids, and gets their corresponding ``Face`` object.
    """
    return [
        face for body in __traverse_all_bodies(design) for face in body.faces if face.id in face_ids
    ]  # noqa: E501


def get_edges_from_ids(design: "Design", edge_ids: list[str]) -> list["Edge"]:
    """Find the ``Edge`` objects inside a ``Design`` from its ids.

    Parameters
    ----------
    design : Design
        Parent design for the edges.
    edge_ids : list[str]
        List of edge ids.

    Returns
    -------
    list[Edge]
        List of Edge objects.

    Notes
    -----
    This method takes a design and edge ids, and gets their corresponding ``Edge`` objects.
    """
    return [
        edge for body in __traverse_all_bodies(design) for edge in body.edges if edge.id in edge_ids
    ]  # noqa: E501


def get_beams_from_ids(design: "Design", beam_ids: list[str]) -> list["Beam"]:
    """Find the ``Beam`` objects inside a ``Design`` from its ids.

    Parameters
    ----------
    design : Design
        Parent design for the beams.
    beam_ids : list[str]
        List of beam ids.

    Returns
    -------
    list[Beam]
        List of Beam objects.

    Notes
    -----
    This method takes a design and beam ids, and gets their corresponding ``Beam`` objects.
    """
    return [beam for beam in __traverse_all_beams(design) if beam.id in beam_ids]  # noqa: E501


def convert_color_to_hex(
    color: str | tuple[float, float, float] | tuple[float, float, float, float],
) -> str:
    """Get the hex string color from input formats.

    Parameters
    ----------
    color : str | tuple[float, float, float] | tuple[float, float, float, float]
        Color to set the body to. This can be a string representing a color name
        or a tuple of RGB values in the range [0, 1] (RGBA) or [0, 255] (pure RGB).

    Returns
    -------
    str
        The hex code string for the color, formatted #rrggbbaa.
    """
    import matplotlib.colors as mcolors

    try:
        if isinstance(color, tuple):
            # Ensure that all elements are within 0-1 or 0-255 range
            if all(0 <= c <= 1 for c in color):
                # Ensure they are floats if in 0-1 range
                if not all(isinstance(c, float) for c in color):
                    raise ValueError("RGB values in the 0-1 range must be floats.")
            elif all(0 <= c <= 255 for c in color):
                # Ensure they are integers if in 0-255 range
                if not all(isinstance(c, int) for c in color):
                    raise ValueError("RGB values in the 0-255 range must be integers.")
                # Normalize the 0-255 range to 0-1
                color = tuple(c / 255.0 for c in color)
            else:
                raise ValueError("RGB tuple contains mixed ranges or invalid values.")

            color = mcolors.to_hex(color, keep_alpha=True)
        elif isinstance(color, str):
            color = mcolors.to_hex(color, keep_alpha=True)
    except ValueError as err:
        raise ValueError(f"Invalid color value: {err}")

    return color


def convert_opacity_to_hex(opacity: float) -> str:
    """Get the hex string from an opacity value.

    Parameters
    ----------
    opacity : float
        Opacity to set body to. Must be in the range [0, 1].

    Returns
    -------
    The hex code for the opacity formatted #aa
    """
    try:
        # Ensure that the value is within 0-1 range
        if 0 <= opacity <= 1:
            return "{:02x}".format(int(opacity * 255))
        else:
            raise ValueError("Opacity value must be between 0 and 1.")
    except ValueError as err:
        raise ValueError(f"Invalid color value: {err}")
