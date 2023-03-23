from beartype.typing import List

from ansys.geometry.core.designer.body import TemplateBody
from ansys.geometry.core.math import IDENTITY_MATRIX44, Matrix44


class Part:
    def __init__(
        self, id, name, parts: List["TransformedPart"], bodies: List[TemplateBody]
    ) -> None:
        self._id = id
        self._name = name
        self._parts = parts
        self._bodies = bodies

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def parts(self) -> List["TransformedPart"]:
        return self._parts

    @parts.setter
    def parts(self, parts: List["TransformedPart"]) -> None:
        self._parts = parts

    @property
    def bodies(self) -> List[TemplateBody]:
        return self._bodies

    @bodies.setter
    def bodies(self, bodies: List["TemplateBody"]) -> None:
        self._bodies = bodies

    def __repr__(self) -> str:
        return (
            f"Part(id={self.id}, "
            f"name={self.name}, "
            f"parts={[p.name for p in self.parts]}, "
            f"bodies={[b.name for b in self.bodies]})"
        )


class TransformedPart:
    def __init__(self, id, name, part: Part, transform: Matrix44 = IDENTITY_MATRIX44) -> None:
        self._id = id
        self._name = name
        self._part = part
        self._transform = transform

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def part(self) -> Part:
        return self._part

    @property
    def transform(self) -> Matrix44:
        return self._transform

    @transform.setter
    def transform(self, matrix: Matrix44) -> None:
        self._transform = matrix

    def __repr__(self) -> str:
        return (
            f"TransformedPart(id={self.id}, "
            f"name={self.name}, "
            f"template={self.part}, "
            f"transform={self.transform})"
        )
