# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.component import Component
    from ansys.geometry.core.designer.design import Design
    from ansys.geometry.core.designer.edge import Edge
    from ansys.geometry.core.designer.face import Face


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


def __traverse_all_bodies(comp: Union["Design", "Component"]) -> list["Body"]:
    """Traverse all bodies in a design and all its subcomponents.

    This is a private method. Do not use it directly.

    Notes
    -----
    This method is a recursive helper function to traverse all bodies in a
    design and all its subcomponents.

    Parameters
    ----------
    design : Design
        Design object to traverse.

    Returns
    -------
    list[Body]
        List of all bodies in the design or component.
    """
    bodies = []
    bodies.extend(comp.bodies)
    for component in comp.components:
        bodies.extend(__traverse_all_bodies(component))

    return bodies


def get_bodies_from_ids(design: "Design", body_ids: list[str]) -> list["Body"]:
    """Find the ``Body`` objects inside a ``Design`` from its ids.

    Notes
    -----
    This method takes a design and body ids, and gets their corresponding ``Body`` object.

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
    """
    return [body for body in __traverse_all_bodies(design) if body.id in body_ids]


def get_faces_from_ids(design: "Design", face_ids: list[str]) -> list["Face"]:
    """Find the ``Face`` objects inside a ``Design`` from its ids.

    Notes
    -----
    This method takes a design and face ids, and gets their corresponding ``Face`` object.

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
    """
    return [
        face for body in __traverse_all_bodies(design) for face in body.faces if face.id in face_ids
    ]  # noqa: E501


def get_edges_from_ids(design: "Design", edge_ids: list[str]) -> list["Edge"]:
    """Find the ``Edge`` objects inside a ``Design`` from its ids.

    Notes
    -----
    This method takes a design and edge ids, and gets their corresponding ``Edge`` objects.

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
    """
    return [
        edge for body in __traverse_all_bodies(design) for edge in body.edges if edge.id in edge_ids
    ]  # noqa: E501
