"""Checking common functions."""

from typing import Optional, Union

import numpy as np
from pint import Unit


def check_is_float_int(param: object, param_name: Optional[Union[str, None]] = None) -> None:
    """
    Checks if the parameter provided is a ``float`` or an ``int``.

    Parameters
    ----------
    param : object
        Object instance to be checked.
    param_name : str or None, optional
        The object instance name (if any). By default, ``None``.

    Raises
    ------
    TypeError
        In case the parameter is not a ``float`` or an ``int``.
    """
    if not isinstance(param, (int, float)):
        raise TypeError(
            f"The parameter provided should be a float or an integer value."
            if param_name is None
            else f"The parameter '{param_name}' should be a float or an integer value."
        )


def check_is_point(
    param: object, param_name: Optional[Union[str, None]] = None, only_3d: bool = False
) -> None:
    """
    Checks if the parameter provided is a ``Point3D`` or ``Point2D``.

    Parameters
    ----------
    param : object
        Object instance to be checked.
    param_name : str or None, optional
        The object instance name (if any). By default, ``None``.
    only_3d : bool
        Only consider ``Point3D`` for checking.

    Raises
    ------
    TypeError
        In case the parameter is not a ``Point3D`` or a ``Point2D``.
    """
    from ansys.geometry.core.math.point import Point2D, Point3D

    consider = (Point3D) if only_3d else (Point2D, Point3D)
    point_type = "Point3D" if only_3d else "Point3D or Point2D"
    if not isinstance(param, consider):
        raise TypeError(
            f"The parameter provided should be a {point_type} object."
            if param_name is None
            else f"The parameter '{param_name}' should be a {point_type} object."
        )


def check_is_vector(
    param: object, param_name: Optional[Union[str, None]] = None, only_3d: bool = False
) -> None:
    """
    Checks if the parameter provided is a ``Vector3D`` or ``Vector2D``.

    Parameters
    ----------
    param : object
        Object instance to be checked.
    param_name : str or None, optional
        The object instance name (if any). By default, ``None``.
    only_3d : bool
        Only consider ``Vector3D`` for checking.

    Raises
    ------
    TypeError
        In case the parameter is not a ``Vector3D`` or a ``Vector2D``.
    """
    from ansys.geometry.core.math.vector import Vector2D, Vector3D

    consider = (Vector3D) if only_3d else (Vector2D, Vector3D)
    vector_type = "Vector3D" if only_3d else "Vector3D or Vector2D"
    if not isinstance(param, consider):
        raise TypeError(
            f"The parameter provided should be a {vector_type} object."
            if param_name is None
            else f"The parameter '{param_name}' should be a {vector_type} object."
        )


def check_is_unitvector(
    param: object, param_name: Optional[Union[str, None]] = None, only_3d: bool = False
) -> None:
    """
    Checks if the parameter provided is a ``UnitVector3D`` or ``UnitVector2D``.

    Parameters
    ----------
    param : object
        Object instance to be checked.
    param_name : str or None, optional
        The object instance name (if any). By default, ``None``.
    only_3d : bool
        Only consider ``UnitVector3D`` for checking.

    Raises
    ------
    TypeError
        In case the parameter is not a ``UnitVector3D`` or a ``UnitVector2D``.
    """
    from ansys.geometry.core.math.vector import UnitVector2D, UnitVector3D

    consider = (UnitVector3D) if only_3d else (UnitVector2D, UnitVector3D)
    unit_vector_type = "UnitVector3D" if only_3d else "UnitVector3D or UnitVector2D"
    if not isinstance(param, consider):
        raise TypeError(
            f"The parameter provided should be a {unit_vector_type} object."
            if param_name is None
            else f"The parameter '{param_name}' should be a {unit_vector_type} object."
        )


def check_is_quantityvector(
    param: object, param_name: Optional[Union[str, None]] = None, only_3d: bool = False
) -> None:
    """
    Checks if the parameter provided is a ``QuantityVector3D`` or ``QuantityVector2D``.

    Parameters
    ----------
    param : object
        Object instance to be checked.
    param_name : str or None, optional
        The object instance name (if any). By default, ``None``.
    only_3d : bool
        Only consider ``UnitVector3D`` for checking.

    Raises
    ------
    TypeError
        In case the parameter is not a ``QuantityVector3D`` or a ``QuantityVector2D``.
    """
    from ansys.geometry.core.math.vector import QuantityVector2D, QuantityVector3D

    consider = (QuantityVector3D) if only_3d else (QuantityVector2D, QuantityVector3D)
    quantity_vector_type = "QuantityVector3D" if only_3d else "QuantityVector3D or QuantityVector2D"
    if not isinstance(param, consider):
        raise TypeError(
            f"The parameter provided should be a {quantity_vector_type} object."
            if param_name is None
            else f"The parameter '{param_name}' should be a {quantity_vector_type} object."
        )


def check_ndarray_is_float_int(
    param: np.ndarray, param_name: Optional[Union[str, None]] = None
) -> None:
    """
    Checks if the :class:`numpy.ndarray` has ``float`` or ``int`` elements.

    Parameters
    ----------
    param : ~numpy.ndarray
        :class:`numpy.ndarray` instance to be checked.
    param_name : str or None, optional
        The :class:`numpy.ndarray` instance name (if any). By default, ``None``.

    Raises
    ------
    TypeError
        In case the parameter is not a ``float`` or an ``int``.
    """
    param_data = np.ravel(param)

    if not np.issubdtype(param.dtype, np.number) or not all(
        isinstance(data, (int, float)) for data in param_data.data
    ):
        raise TypeError(
            f"The numpy.ndarray provided should contain float or integer values."
            if param_name is None
            else f"The numpy.ndarray '{param_name}' should contain float or integer values."
        )


def check_ndarray_is_not_none(
    param: np.ndarray, param_name: Optional[Union[str, None]] = None
) -> None:
    """
    Checks if the :class:`numpy.ndarray` is not None-valued.

    Parameters
    ----------
    param : ~numpy.ndarray
        :class:`numpy.ndarray` instance to be checked.
    param_name : str or None, optional
        The :class:`numpy.ndarray` instance name (if any). By default, ``None``.

    Raises
    ------
    ValueError
        In case the :class:`numpy.ndarray` is None-valued.
    """
    param_data = np.ravel(param)
    if all(value is None for value in param_data):
        raise ValueError(
            f"The numpy.ndarray provided should not be a None numpy.ndarray."
            if param_name is None
            else f"The numpy.ndarray '{param_name}' should not be a None numpy.ndarray."
        )


def check_ndarray_is_non_zero(
    param: np.ndarray, param_name: Optional[Union[str, None]] = None
) -> None:
    """
    Checks if the :class:`numpy.ndarray` is not zero-valued.

    Parameters
    ----------
    param : ~numpy.ndarray
        :class:`numpy.ndarray` instance to be checked.
    param_name : str or None, optional
        The :class:`numpy.ndarray` instance name (if any). By default, ``None``.

    Raises
    ------
    ValueError
        In case the :class:`numpy.ndarray` is zero-valued.
    """
    param_data = np.ravel(param)
    if all(value == 0 for value in param_data):
        raise ValueError(
            f"The numpy.ndarray provided should not be a zeroes numpy.ndarray."
            if param_name is None
            else f"The numpy.ndarray '{param_name}' should not be a zeroes numpy.ndarray."
        )


def check_is_pint_unit(param: object, param_name: Optional[Union[str, None]] = None) -> None:
    """
    Checks if the parameter provided is a :class:`pint.Unit`.

    Parameters
    ----------
    param : object
        Object instance to be checked.
    param_name : str or None, optional
        The object instance name (if any). By default, ``None``.

    Raises
    ------
    TypeError
        In case the parameter is not a :class:`pint.Unit`.
    """
    if not isinstance(param, Unit):
        raise TypeError(
            "The parameter 'unit' should be a pint.Unit object."
            if param_name is None
            else f"The parameter '{param_name}' should be a pint.Unit object."
        )


def check_pint_unit_compatibility(input: Unit, expected: Unit) -> None:
    """
    Checks if the input :class:`pint.Unit` provided is compatible with the expected one.

    Parameters
    ----------
    input : ~pint.Unit
        The :class:`pint.Unit` input.
    expected : ~pint.Unit
        The :class:`pint.Unit` expected dimensionality.

    Raises
    ------
    TypeError
        In case the input is not a compatible :class:`pint.Unit`.
    """
    if not input.is_compatible_with(expected):
        raise TypeError(
            f"The pint.Unit provided as input should be a {expected.dimensionality} quantity."
        )


def check_type_equivalence(input: object, expected: object) -> None:
    """
    Checks if the input object provided is of the same class as the expected one.

    Parameters
    ----------
    input : object
        Input object's class to be evaluated.
    expected : object
        Expected object's class to be evaluated.

    Raises
    ------
    TypeError
        In case they are not of the same class.
    """

    if not isinstance(input, type(expected)):
        raise TypeError(f"Provided type {type(input)} is invalid, type {type(expected)} expected.")
