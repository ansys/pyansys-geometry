"""Provides common checks."""
from beartype.typing import Optional, Tuple, Union
import numpy as np
from pint import Unit


def check_is_float_int(param: object, param_name: Optional[Union[str, None]] = None) -> None:
    """
    Check if a parameter has a float or integer value.

    Parameters
    ----------
    param : object
        Object instance to check.
    param_name : str, default: None
        Parameter name (if any).

    Raises
    ------
    TypeError
        If the parameter does not have a float or integer value.
    """
    if not isinstance(param, (int, float)):
        raise TypeError(
            f"The parameter should have a float or integer value."
            if param_name is None
            else f"The parameter '{param_name}' should have a float or integer value."
        )


def check_ndarray_is_float_int(
    param: np.ndarray, param_name: Optional[Union[str, None]] = None
) -> None:
    """
    Check if a :class:`numpy.ndarray <numpy.ndarray>` has float/integer values.

    Parameters
    ----------
    param : ~numpy.ndarray
        :class:`numpy.ndarray <numpy.ndarray>` instance to check.
    param_name : str, default: None
        :class:`numpy.ndarray <numpy.ndarray>` instance name (if any).

    Raises
    ------
    TypeError
        If the :class:`numpy.ndarray <numpy.ndarray>` instance does not
        have float or integer values.
    """
    param_data = np.ravel(param)

    if not np.issubdtype(param.dtype, np.number) or not all(
        isinstance(data, (int, float)) for data in param_data.data
    ):
        raise TypeError(
            f"The numpy.ndarray should contain float or integer values."
            if param_name is None
            else f"The numpy.ndarray '{param_name}' should contain float or integer values."
        )


def check_ndarray_is_not_none(
    param: np.ndarray, param_name: Optional[Union[str, None]] = None
) -> None:
    """
    Check if a :class:`numpy.ndarray <numpy.ndarray>` has all ``None`` values.

    Parameters
    ----------
    param : ~numpy.ndarray
        :class:`numpy.ndarray <numpy.ndarray>` instance to check.
    param_name : str, default: None
        :class:`numpy.ndarray <numpy.ndarray>` instance name (if any).

    Raises
    ------
    ValueError
        If the :class:`numpy.ndarray <numpy.ndarray>` instance has a value
        of ``None`` for all parameters.
    """
    param_data = np.ravel(param)
    if all(value is None for value in param_data):
        raise ValueError(
            f"The numpy.ndarray should not have 'None' for all parameter values."
            if param_name is None
            else f"The numpy.ndarray '{param_name}' should not have 'None' for all parameter values."  # noqa: E501
        )


def check_ndarray_is_all_nan(
    param: np.ndarray, param_name: Optional[Union[str, None]] = None
) -> None:
    """
    Check if the :class:`numpy.ndarray <numpy.ndarray>` is all nan-valued.

    Parameters
    ----------
    param : ~numpy.ndarray
        :class:`numpy.ndarray <numpy.ndarray>` instance to check.
    param_name : str or None, default: None
        :class:`numpy.ndarray <numpy.ndarray>` instance name (if any).

    Raises
    ------
    ValueError
        If the :class:`numpy.ndarray <numpy.ndarray>` is all nan-valued.
    """
    if np.isnan(param).all():
        raise ValueError(
            f"The numpy.ndarray should not be a nan numpy.ndarray."
            if param_name is None
            else f"The numpy.ndarray '{param_name}' should not be a nan numpy.ndarray."
        )


def check_ndarray_is_non_zero(
    param: np.ndarray, param_name: Optional[Union[str, None]] = None
) -> None:
    """
    Check if the :class:`numpy.ndarray <numpy.ndarray>` is zero-valued.

    Parameters
    ----------
    param : ~numpy.ndarray
        :class:`numpy.ndarray <numpy.ndarray>` instance to check.
    param_name : str, default: None
        :class:`numpy.ndarray <numpy.ndarray>` instance name (if any).

    Raises
    ------
    ValueError
        If the :class:`numpy.ndarray <numpy.ndarray>` instance is zero-valued.
    """
    param_data = np.ravel(param)
    if all(value == 0 for value in param_data):
        raise ValueError(
            f"The numpy.ndarray should not be a numpy.ndarray of zeros."
            if param_name is None
            else f"The numpy.ndarray '{param_name}' should not be a numpy.ndarray of zeros."
        )


def check_pint_unit_compatibility(input: Unit, expected: Unit) -> None:
    """
    Check if the input for the :class:`pint.Unit` is compatible with the expected one.

    Parameters
    ----------
    input : ~pint.Unit
        :class:`pint.Unit` input.
    expected : ~pint.Unit
        :class:`pint.Unit` expected dimensionality.

    Raises
    ------
    TypeError
        If the input is not a compatible with the :class:`pint.Unit` class.
    """
    if not input.is_compatible_with(expected):
        raise TypeError(
            f"The pint.Unit provided as an input should be a {expected.dimensionality} quantity."
        )


def check_type_equivalence(input: object, expected: object) -> None:
    """
    Check if the input object provided is of the same class as the expected object.

    Parameters
    ----------
    input : object
        Input object.
    expected : object
        Expected object.

    Raises
    ------
    TypeError
        If they are not of the same class.
    """
    if not isinstance(input, type(expected)):
        raise TypeError(
            f"Provided type {type(input)} is invalid. Type {type(expected)} is expected."
        )


def check_type(input: object, expected_type: Union[type, Tuple[type, ...]]) -> None:
    """
    Check if the input object provided is of the same type as the expected types.

    Parameters
    ----------
    input : object
        Input object.
    expected_type : Union[type, Tuple[type, ...]]
        One or more types to compare against.

    Raises
    ------
    TypeError
        If the object does not match the one or more expected types.
    """
    if not isinstance(input, expected_type):
        raise TypeError(
            f"Provided type {type(input)} is invalid. Type {expected_type} is expected."
        )
