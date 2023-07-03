"""Provides the ``Part`` class module."""
from beartype.typing import TYPE_CHECKING, List

from ansys.geometry.core.designer.body import MasterBody
from ansys.geometry.core.math import IDENTITY_MATRIX44, Matrix44

if TYPE_CHECKING:
    from ansys.geometry.core.designer.component import Component


class Part:
    """
    Represents a Part Master.

    This class should not be accessed by users. Parts hold fundamental data of an assembly.

    Parameters
    ----------
    id : str
        Unique identifier for this part.
    name : str
        Name of this part.
    components : List[MasterComponent]
        List of MasterComponent children that this Part contains.
    bodies : List[MasterBody]
        List of MasterBody children that this Part contains. These are master bodies.
    """

    def __init__(
        self, id: str, name: str, components: List["MasterComponent"], bodies: List[MasterBody]
    ) -> None:
        """Initialize the ``Part`` class."""
        self._id: str = id
        self._name: str = name
        self._components: List["MasterComponent"] = components
        self._bodies: List[MasterBody] = bodies

    @property
    def id(self) -> str:
        """ID of the part."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the part."""
        return self._name

    @property
    def components(self) -> List["MasterComponent"]:
        """``MasterComponent`` children that this ``Part`` contains."""
        return self._components

    @components.setter
    def components(self, components: List["MasterComponent"]) -> None:
        self._components = components

    @property
    def bodies(self) -> List[MasterBody]:
        """
        ``MasterBody`` children that this ``Part`` contains.

        These are master bodies.
        """
        return self._bodies

    @bodies.setter
    def bodies(self, bodies: List["MasterBody"]) -> None:
        self._bodies = bodies

    def __repr__(self) -> str:
        """Represent the ``Part`` as a string."""
        return (
            f"Part(id={self.id}, "
            f"name={self.name}, "
            f"parts={[p.name for p in self.components]}, "
            f"bodies={[b.name for b in self.bodies]})"
        )


class MasterComponent:
    """
    Represents a Part Occurrence.

    Notes
    -----
    This class should not be accessed by users.
    MasterComponents hold fundamental data of an assembly. MasterComponents wrap Parts
    by adding a transform matrix.

    Parameters
    ----------
    id : str
        Unique identifier for this transformed part.
    name : str
        Name of this transformed part.
    part : Part
        Reference to this transformed part's master part.
    transform : Matrix44
        4x4 transformation matrix from the master part.
    """

    def __init__(
        self, id: str, name: str, part: Part, transform: Matrix44 = IDENTITY_MATRIX44
    ) -> None:
        """Initialize ``MasterComponent`` class."""
        self._id: str = id
        self._name: str = name
        self._part: Part = part
        part.components.append(self)
        self._transform: Matrix44 = transform
        self._occurrences: List["Component"] = []

    @property
    def id(self) -> str:
        """ID of the transformed part."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the transformed part."""
        return self._name

    @property
    def occurrences(self) -> List["Component"]:
        """All occurrences of this component."""
        return self._occurrences

    @property
    def part(self) -> Part:
        """The master part of this transformed part."""
        return self._part

    @property
    def transform(self) -> Matrix44:
        """The 4x4 transformation matrix from the master part."""
        return self._transform

    @transform.setter
    def transform(self, matrix: Matrix44) -> None:
        self._transform = matrix

    def __repr__(self) -> str:
        """Represent the ``MasterComponent`` as a string."""
        return (
            f"MasterComponent(id={self.id}, "
            f"name={self.name}, "
            f"template={self.part}, "
            f"transform={self.transform})"
        )
