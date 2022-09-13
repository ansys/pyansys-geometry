"""``Transformation`` module."""
from typing import Optional, Union

import numpy as np
from pint import Unit
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math.matrix import Matrix
from ansys.geometry.core.math.point import Point
from ansys.geometry.core.math.vector import Vector
from ansys.geometry.core.misc import (
    UNIT_ANGLE,
    UNITS,
    check_ndarray_is_float_int,
    check_pint_unit_compatibility,
    check_type,
)
from ansys.geometry.core.typing import Real, RealSequence


class Rotation(np.ndarray):
    """Provides rotation for the object.

    Rotations in 3-D can be represented by a sequence
    of 3 rotations around a sequence of axes.

    Parameters
    ----------
    input : object
        Input object for rotation.
    angle : Union[~numpy.ndarray, Real]
        Angle determining the rotation. It can be:

        * a single value
        * ``array_like`` with shape (N,), where each angle[i] corresponds to a single rotation
        * ``array_like`` with shape (N, 1), where each angle[i, 0]
          corresponds to a single rotation

    axis : str
        The sequence of axes for rotations. Up to 3 characters. The order 'zyx' represents
        counterclockwise rotation.
    unit : Unit, optional
        Units employed to define the angle of rotation,
        by default ``UNIT_ANGLE``.
    """

    def __new__(
        cls,
        input: Union[np.ndarray, RealSequence, Point, Vector, Matrix],
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
                f"Expected axis specification to be a string of up to 3 characters, got {axis}"
            )
        if ang.ndim == 0 and len(axis) != 1:
            raise ValueError("Axis and angle are not matching")
        if ang.ndim == 1 and len(axis) != ang.shape[0]:
            raise ValueError("Axis and angle are not matching")
        if ang.ndim >= 2 and len(axis) != ang.shape[1]:
            raise ValueError("Axis and angle are not matching")
        if ang.ndim == 0:
            obj._angle = (ang * obj._unit).to_base_units().magnitude
        else:
            obj._angle = [(angs * obj._unit).to_base_units().magnitude for angs in ang]

        obj._axis = axis
        obj_type = type(input)
        rotated_obj = spatial_rotation.from_euler(obj._axis, obj._angle)
        obj_rot = rotated_obj.apply(obj)
        return obj_type(obj_rot)


class Translation(np.ndarray):
    """Provides a translation in a geometric transformation.

    Shifts every point of a figure, shape or space by the same distance in a
    given direction.

    Parameters
    ----------
    input : object
        Input object for translation.
    vector : Vector
        A :class:`Vector` representing the translating direction.
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence, Point, Vector, Matrix], vector: Vector):
        """Constructor for ``Translation``."""
        obj = np.asarray(input).view(cls)
        check_ndarray_is_float_int(obj)
        if not isinstance(input, Matrix):
            obj = np.append(obj, [1])
        check_type(vector, Vector)
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
        if not isinstance(input, (Matrix)):
            return type(input)(np.matmul(translate, obj)[:-1])
        return type(input)(np.matmul(translate, obj))


class Scaling(np.ndarray):
    """Provides a scaling in a geometric transformation.

    enlarges (increases) or shrinks (diminishes)
    objects by a scale factor that is the same in all directions.

    Parameters
    ----------
    input : object
        Input object for scaling.
    vector : Vector
        A :class:`Vector` representing the Scaling direction.
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence, Point, Vector, Matrix], vector: Vector):
        """Constructor for ``Scaling``."""
        obj = np.asarray(input).view(cls)
        check_ndarray_is_float_int(obj)
        check_type(vector, Vector)
        if not isinstance(input, Matrix):
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
        if not isinstance(input, Matrix):
            return type(input)(np.matmul(scalar_matrix, obj)[:-1])
        return type(input)(np.matmul(scalar_matrix, obj))
