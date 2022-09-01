"""Checking common functions."""

from typing import Optional, Union

from pint import Unit


def check_is_float_int(param: object, param_name: Optional[Union[str, None]]) -> None:
    """
    Method for checking if the parameter provided is
    a ``float`` or an ``int``.

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


def check_is_pint_unit(param: object, param_name: Optional[Union[str, None]]) -> None:
    """
    Method for checking if the parameter provided is
    a ``pint.Unit``.

    Parameters
    ----------
    param : object
        Object instance to be checked.
    param_name : str or None, optional
        The object instance name (if any). By default, ``None``.

    Raises
    ------
    TypeError
        In case the parameter is not a ``pint.Unit``.
    """
    if not isinstance(param, Unit):
        raise TypeError(
            "The parameter 'unit' should be a pint.Unit object."
            if param_name is None
            else f"The parameter '{param_name}' should be a pint.Unit object."
        )


def check_pint_unit_compatibility(input: Unit, expected: Unit) -> None:
    """
    Method for checking if the input ``pint.Unit`` provided is
    compatible with the expected ``pint.Unit``.

    Parameters
    ----------
    input : Unit
        The ``pint.Unit`` input.
    expected : Unit
        The ``pint.Unit`` expected dimensionality.

    Raises
    ------
    TypeError
        In case the input is not a compatible ``pint.Unit``.
    """
    if not input.is_compatible_with(expected):
        raise TypeError(
            f"The pint.Unit provided as input should be a {expected.dimensionality} Quantity."
        )


def check__eq__operation(input: object, expected: object) -> None:
    """
    Method for checking if the input object provided is
    of the same class as the expected one.

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
        raise TypeError(
            f"Comparison against {type(input)} is not possible. Should be of type {type(expected)}."
        )
