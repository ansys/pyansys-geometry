"""Provides the ``Part`` class module."""
from beartype.typing import List

from ansys.geometry.core.designer.body import TemplateBody
from ansys.geometry.core.math import IDENTITY_MATRIX44, Matrix44


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
    parts : List[TransformedPart]
        List of TransformedPart children that this Part contains.
    bodies : List[TemplateBody]
        List of TemplateBody children that this Part contains. These are master bodies.
    """

    def __init__(
        self, id: str, name: str, parts: List["TransformedPart"], bodies: List[TemplateBody]
    ) -> None:
        """Initialize the ``Part`` class."""
        self._id: str = id
        self._name: str = name
        self._parts: List["TransformedPart"] = parts
        self._bodies: List[TemplateBody] = bodies

    @property
    def id(self) -> str:
        """ID of the part."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the part."""
        return self._name

    @property
    def parts(self) -> List["TransformedPart"]:
        """``TransformedPart`` children that this ``Part`` contains."""
        return self._parts

    @parts.setter
    def parts(self, parts: List["TransformedPart"]) -> None:
        self._parts = parts

    @property
    def bodies(self) -> List[TemplateBody]:
        """
        ``TemplateBody`` children that this ``Part`` contains.

        These are master bodies.
        """
        return self._bodies

    @bodies.setter
    def bodies(self, bodies: List["TemplateBody"]) -> None:
        self._bodies = bodies

    def __repr__(self) -> str:
        """Represent the ``Part`` as a string."""
        return (
            f"Part(id={self.id}, "
            f"name={self.name}, "
            f"parts={[p.name for p in self.parts]}, "
            f"bodies={[b.name for b in self.bodies]})"
        )


class TransformedPart:
    """
    Represents a Part Occurrence.

    Notes
    -----
    This class should not be accessed by users.
    TransformedParts hold fundamental data of an assembly. TransformedParts wrap Parts
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
        """Initialize ``TransformedPart`` class."""
        self._id: str = id
        self._name: str = name
        self._part: Part = part
        self._transform: Matrix44 = transform

    @property
    def id(self) -> str:
        """ID of the transformed part."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the transformed part."""
        return self._name

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
        """Represent the ``TransformedPart`` as a string."""
        return (
            f"TransformedPart(id={self.id}, "
            f"name={self.name}, "
            f"template={self.part}, "
            f"transform={self.transform})"
        )
