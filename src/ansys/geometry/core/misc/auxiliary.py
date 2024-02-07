"""Auxiliary functions for the PyAnsys Geometry library."""

from beartype.typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.geometry.core.designer.component import Component
    from ansys.geometry.core.designer.edge import Edge
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.face import Face
    from ansys.geometry.core.designer.design import Design


def get_design_from_component(component: "Component") -> "Design":
    """
    Get the ``Design`` of the given ``Component`` object.

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
    """
    Get the ``Design`` of the given ``Body`` object.

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
    """
    Get the ``Design`` of the given ``Face`` object.

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
    """
    Get the ``Design`` of the given ``Edge`` object.

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
