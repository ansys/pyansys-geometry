"""``Transformation`` module."""
from typing import Optional, Union

import numpy as np
from pint import Unit
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math import Vector
from ansys.geometry.core.misc import (
    UNIT_ANGLE,
    UNITS,
    check_ndarray_is_float_int,
    check_pint_unit_compatibility,
    check_type,
)
from ansys.geometry.core.misc.units import PhysicalQuantity
from ansys.geometry.core.typing import Real


class Rotation(np.ndarray, PhysicalQuantity):
    """Provides rotation for the object. Rotations in 3-D can be
    represented by a sequence of 3 rotations around a sequence of
    axes.

    Parameters
    ----------
    input : object
        Input object for rotation.
    angle : Union[~numpy.ndarray, Real]
        Angle determining the rotation
    axis : str
        The order of axis of rotation
    unit : Unit, optional
        Units employed to define the angle of rotation,
        by default ``UNIT_ANGLE``.
    """

    def __new__(
        cls,
        input: object,
        angle: Union[Real, np.ndarray],
        axis: str,
        unit: Optional[Unit] = UNIT_ANGLE,
    ) -> object:
        """Constructor for ``Rotation``."""
        obj = np.asarray(input).view(cls)
        check_ndarray_is_float_int(obj)

        check_type(unit, Unit)
        check_pint_unit_compatibility(unit, UNIT_ANGLE)

        obj._unit = unit
        _, obj._base_unit = UNITS.get_base_units(unit)

        ang = np.asarray(angle).view(cls)
        if len(axis) > 3:
            raise ValueError(
                f"Expected axis specification to be a string of up to 3 characters, got{axis}"
            )
        if ang.ndim == 0 and len(axis) != 1:
            raise ValueError("Axis and angle are not matching")
        if ang.ndim == 1 and len(axis) != ang.shape[0]:
            raise ValueError("Axis and angle are not matching")
        if ang.ndim >= 2 and len(axis) != ang.shape[1]:
            raise ValueError("Axis and angle are not matching")
        if ang.ndim == 0:
            obj._angle = (ang * unit).to_base_units().magnitude
        else:
            obj._angle = [(angs * unit).to_base_units().magnitude for angs in ang]

        obj._axis = axis
        obj_type = type(input)
        rotated_obj = spatial_rotation.from_euler(obj._axis, obj._angle)
        obj_rot = rotated_obj.apply(obj)
        return obj_type(obj_rot)


class Translation(np.ndarray):
    """Provides a translation in a geometric transformation that shifts
    every point of a figure, shape or space by the same distance in a
    given direction.

    Parameters
    ----------
    input : object
        Input object for translation.
    vector : Vector
        A :class:`Vector` representing the translating direction.
    """

    def __new__(cls, input: object, vector: Vector):
        obj = np.asarray(input).view(cls)
        obj = np.append(obj, [1])
        if vector._is_3d == True:
            translate = np.array(
                [
                    [1, 0, 0, vector.x],
                    [0, 1, 0, vector.y],
                    [0, 0, 1, vector.z],
                    [0, 0, 0, 1],
                ]
            )
        else:
            translate = np.array(
                [
                    [1, 0, vector.x],
                    [0, 1, vector.y],
                    [0, 0, 1],
                ]
            )
        return type(input)(np.matmul(translate, obj)[:-1])


class Scaling(np.ndarray):
    """Provides a scaling in a geometric transformation that
    enlarges (increases) or shrinks (diminishes)
    objects by a scale factor that is the same in all directions.

    Parameters
    ----------
    input : object
        Input object for scaling.
    vector : Vector
        A :class:`Vector` representing the Scaling direction.
    """

    def __new__(cls, input: object, vector: Vector):
        obj = np.asarray(input).view(cls)
        obj = np.append(obj, [1])
        if vector._is_3d == True:
            scalar_matrix = np.array(
                [
                    [vector.x, 0, 0, 0],
                    [0, vector.y, 0, 0],
                    [0, 0, vector.z, 0],
                    [0, 0, 0, 1],
                ]
            )
        else:
            scalar_matrix = np.array(
                [
                    [vector.x, 0, 0],
                    [0, vector.y, 0],
                    [0, 0, 1],
                ]
            )
        return type(input)(np.matmul(scalar_matrix, obj)[:-1])
