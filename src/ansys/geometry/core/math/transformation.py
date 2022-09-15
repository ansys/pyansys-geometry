"""``Transformation`` module."""
from typing import Union

import numpy as np
from pint import Quantity
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math.matrix import Matrix
from ansys.geometry.core.math.point import Point
from ansys.geometry.core.math.vector import Vector
from ansys.geometry.core.misc import Angle, check_ndarray_is_float_int, check_type
from ansys.geometry.core.typing import RealSequence


def rotated_object(
    input: Union[np.ndarray, RealSequence, Point, Vector, Matrix],
    angle: Union[Quantity, Angle, RealSequence],
    axis: str,
) -> object:
    """Provides rotation for the object.

    Rotations in 3-D can be represented by a sequence
    of 3 rotations around a sequence of axes.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence, Point, Vector, Matrix]
        Input object for rotation.
    angle : Union[~numpy.ndarray, Real]
        Angle determining the rotation. It can be:

        * a single value
        * ``array_like`` with shape (N,), where each angle[i] corresponds to a single rotation

    axis : str
        The sequence of axes for rotations. Up to 3 characters. The order 'zyx' represents
        counterclockwise rotation.
    unit : Unit, optional
        Units employed to define the angle of rotation,
        by default ``UNIT_ANGLE``.
    """
    obj = np.asarray(input).view(np.ndarray)
    check_ndarray_is_float_int(obj)

    ang = np.asarray(angle).view(np.ndarray)
    if len(axis) > 3:
        raise ValueError(
            f"Expected axis specification to be a string of up to 3 characters, got {axis}"
        )
    if (ang.ndim == 0 and len(axis) != 1) or (ang.ndim == 1 and len(axis) != ang.shape[0]):
        raise ValueError("Axis and angle are not matching")
    if ang.ndim == 0:
        _angle = Angle(angle)._value
    else:
        _angle = [Angle(angs)._value for angs in angle]
    _axis = axis
    obj_type = type(input)
    rotated_obj = spatial_rotation.from_euler(_axis, _angle)
    obj_rot = rotated_obj.apply(obj)
    return obj_type(obj_rot)


def translated_object(
    input: Union[np.ndarray, RealSequence, Point, Vector, Matrix], vector: Vector
):
    """Provides a translation in a geometric transformation.

    Shifts every point of a figure, shape or space by the same distance in a
    given direction.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence, Point, Vector, Matrix]
        Input object for translation.
    vector : Vector
        A :class:`Vector` representing the translating direction.
    """
    obj = np.asarray(input).view(np.ndarray)
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


def scaled_object(input: Union[np.ndarray, RealSequence, Point, Vector, Matrix], vector: Vector):
    """Provides a scaling in a geometric transformation.

    enlarges (increases) or shrinks (diminishes)
    objects by a scale factor that is the same in all directions.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence, Point, Vector, Matrix]
        Input object for scaling.
    vector : Vector
        A :class:`Vector` representing the Scaling direction.
    """
    obj = np.asarray(input).view(np.ndarray)
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
