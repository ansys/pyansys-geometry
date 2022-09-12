"""Checking common functions."""
from typing import Any, Optional, Tuple, Union

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


def check_ndarray_is_all_nan(
    param: np.ndarray, param_name: Optional[Union[str, None]] = None
) -> None:
    """
    Checks if the :class:`numpy.ndarray` is all nan-valued.

    Parameters
    ----------
    param : ~numpy.ndarray
        :class:`numpy.ndarray` instance to be checked.
    param_name : str or None, optional
        The :class:`numpy.ndarray` instance name (if any). By default, ``None``.

    Raises
    ------
    ValueError
        In case the :class:`numpy.ndarray` is all nan-valued.
    """
    if np.isnan(param).all():
        raise ValueError(
            f"The numpy.ndarray provided should not be a nan numpy.ndarray."
            if param_name is None
            else f"The numpy.ndarray '{param_name}' should not be a nan numpy.ndarray."
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
            f"The numpy.ndarray provided should not be a numpy.ndarray of zeros."
            if param_name is None
            else f"The numpy.ndarray '{param_name}' should not be a numpy.ndarray of zeros."
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


def check_type(input: object, expected_type: Union[type, Tuple[type, ...]]) -> None:
    """
    Checks if the input object provided is of the same class as the expected one.

    Parameters
    ----------
    input : object
        Input object for class type evaluation.
    expected_type : Union[type, Tuple[type, ...]]
        One or more types to compare against.

    Raises
    ------
    TypeError
        In case object does not match expected type.
    """

    if not isinstance(input, expected_type):
        raise TypeError(f"Provided type {type(input)} is invalid, type {expected_type} expected.")


def only_for_3d(func):
    """Class decorator for checking if an object is 3D or not.

    Notes
    -----
    To use this decorator it is necessary to call it on top of a
    class method, and the class should have an ``is_3d`` property.
    """

    def wrapper(*args) -> Any:
        if not args[0].is_3d:
            raise ValueError("Instance is not 3D. Z component not accessible.")

        return func(*args)

    return wrapper
