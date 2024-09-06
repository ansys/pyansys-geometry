# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Provides functions for performing common checks."""

from collections.abc import Iterable
from typing import TYPE_CHECKING
import warnings

import numpy as np
from pint import Unit
import semver

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.design import Design


def ensure_design_is_active(method):
    """Make sure that the design is active before executing a method.

    This function is necessary to be called whenever we do any operation
    on the design. If we are just accessing information of the class, it
    is not necessary to call this.
    """

    def wrapper(self, *args, **kwargs):
        import ansys.geometry.core as pyansys_geometry
        from ansys.geometry.core.errors import GeometryRuntimeError

        if pyansys_geometry.DISABLE_MULTIPLE_DESIGN_CHECK:
            # If the user has disabled the check, then we can skip it
            return method(self, *args, **kwargs)

        # Check if the current design is active... otherwise activate it
        def get_design_ref(obj) -> "Design":
            if hasattr(obj, "_modeler"):  # In case of a Design object
                return obj
            elif hasattr(
                obj, "_parent_component"
            ):  # In case of a Body, Component, DesignPoint, Beam
                # Recursive call
                return get_design_ref(obj._parent_component)
            elif hasattr(obj, "_body"):  # In case of a Face, Edge
                # Recursive call
                return get_design_ref(obj._body._parent_component)
            else:
                raise ValueError("Unable to find the design reference.")

        # Get the design reference
        design = get_design_ref(self)

        # Verify whether the Design has been closed on the backend
        if design.is_closed:
            raise GeometryRuntimeError(
                "The design has been closed on the backend. Cannot perform any operations on it."
            )

        # Activate the design if it is not active
        if not design.is_active:
            # First, check the backend allows for multiple documents
            if not design._grpc_client.multiple_designs_allowed:
                raise GeometryRuntimeError(
                    "The design is not active and multiple designs are "
                    "not allowed with the current backend."
                )
            else:
                design._activate()

        # Finally, call method
        return method(self, *args, **kwargs)

    return wrapper


def check_is_float_int(param: object, param_name: str | None = None) -> None:
    """Check if a parameter has a float or integer value.

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
            "The parameter should have a float or integer value."
            if param_name is None
            else f"The parameter '{param_name}' should have a float or integer value."
        )


def check_ndarray_is_float_int(param: np.ndarray, param_name: str | None = None) -> None:
    """Check if a :class:`numpy.ndarray <numpy.ndarray>` has float/integer types.

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
            "The numpy.ndarray should contain float or integer values."
            if param_name is None
            else f"The numpy.ndarray '{param_name}' should contain float or integer values."
        )


def check_ndarray_is_not_none(param: np.ndarray, param_name: str | None = None) -> None:
    """Check if a :class:`numpy.ndarray <numpy.ndarray>` is all ``None``.

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
            "The numpy.ndarray should not have 'None' for all parameter values."
            if param_name is None
            else f"The numpy.ndarray '{param_name}' should not have 'None' for all parameter values."  # noqa: E501
        )


def check_ndarray_is_all_nan(param: np.ndarray, param_name: str | None = None) -> None:
    """Check if a :class:`numpy.ndarray <numpy.ndarray>` is all nan-valued.

    Parameters
    ----------
    param : ~numpy.ndarray
        :class:`numpy.ndarray <numpy.ndarray>` instance to check.
    param_name : str or None, default: None
        :class:`numpy.ndarray <numpy.ndarray>` instance name (if any).

    Raises
    ------
    ValueError
        If the :class:`numpy.ndarray <numpy.ndarray>` instance is all nan-valued.
    """
    if np.isnan(param).all():
        raise ValueError(
            "The numpy.ndarray should not be a nan numpy.ndarray."
            if param_name is None
            else f"The numpy.ndarray '{param_name}' should not be a nan numpy.ndarray."
        )


def check_ndarray_is_non_zero(param: np.ndarray, param_name: str | None = None) -> None:
    """Check if a :class:`numpy.ndarray <numpy.ndarray>` is zero-valued.

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
            "The numpy.ndarray should not be a numpy.ndarray of zeros."
            if param_name is None
            else f"The numpy.ndarray '{param_name}' should not be a numpy.ndarray of zeros."
        )


def check_pint_unit_compatibility(input: Unit, expected: Unit) -> None:
    """Check if input :class:`pint.Unit` is compatible with the expected input.

    Parameters
    ----------
    input : ~pint.Unit
        :class:`pint.Unit` input.
    expected : ~pint.Unit
        :class:`pint.Unit` expected dimensionality.

    Raises
    ------
    TypeError
        If the input is not compatible with the :class:`pint.Unit` class.
    """
    if not input.is_compatible_with(expected):
        raise TypeError(
            f"The pint.Unit provided as an input should be a {expected.dimensionality} quantity."
        )


def check_type_equivalence(input: object, expected: object) -> None:
    """Check if an input object is of the same class as an expected object.

    Parameters
    ----------
    input : object
        Input object.
    expected : object
        Expected object.

    Raises
    ------
    TypeError
        If the objects are not of the same class.
    """
    if not isinstance(input, type(expected)):
        raise TypeError(
            f"Provided type {type(input)} is invalid. Type {type(expected)} is expected."
        )


def check_type(input: object, expected_type: type | tuple[type, ...]) -> None:
    """Check if an input object is of the same type as expected types.

    Parameters
    ----------
    input : object
        Input object.
    expected_type : type | tuple[type, ...]
        One or more types to compare the input object against.

    Raises
    ------
    TypeError
        If the object does not match the one or more expected types.
    """
    if not isinstance(input, expected_type):
        raise TypeError(
            f"Provided type {type(input)} is invalid. Type {expected_type} is expected."
        )


def check_type_all_elements_in_iterable(
    input: Iterable, expected_type: type | tuple[type, ...]
) -> None:
    """Check if all elements in an iterable are of the same type as expected.

    Parameters
    ----------
    input : Iterable
        Input iterable.
    expected_type : type | tuple[type, ...]
        One or more types to compare the input object against.

    Raises
    ------
    TypeError
        If one of the elements in the iterable does not match the one or more expected types.
    """
    for elem in input:
        check_type(elem, expected_type)


def min_backend_version(major: int, minor: int, service_pack: int):
    """Compare a minimum required version to the current backend version.

    Parameters
    ----------
    major : int
        Minimum major version required by the method.
    minor : int
        Minimum minor version required by the method.
    service_pack : int
        Minimum service pack version required by the method.

    Raises
    ------
    GeometryRuntimeError
        If the method version is higher than the backend version.
    GeometryRuntimeError
        If the client is not available.
    """
    # Lazy import to avoid circular imports
    from ansys.geometry.core.errors import GeometryRuntimeError
    from ansys.geometry.core.logger import LOG

    def backend_version_decorator(method):
        def wrapper(self, *args, **kwargs):
            method_version = semver.Version(major, minor, service_pack)
            if hasattr(self, "_grpc_client"):
                if self._grpc_client is None:
                    raise GeometryRuntimeError(
                        "The client is not available. You must initialize the client first."
                    )
                elif self._grpc_client.backend_version is not None:
                    comp = method_version.compare(self._grpc_client.backend_version)
                    # if comp is 1, method version is higher than backend version.
                    if comp == 1:
                        # Check if the version is "0.0.0" (i.e., the version is not available)
                        if str(self._grpc_client.backend_version) == "0.0.0":
                            raise GeometryRuntimeError(
                                f"The method '{method.__name__}' requires a minimum Ansys release version of "  # noqa: E501
                                + f"{method_version}, but the current version used is 24.1.0 or lower."  # noqa: E501
                            )
                        else:
                            raise GeometryRuntimeError(
                                f"The method '{method.__name__}' requires a minimum Ansys release version of "  # noqa: E501
                                + f"{method_version}, but the current version used is "
                                + f"{self._grpc_client.backend_version}."
                            )
                    else:
                        return method(self, *args, **kwargs)
            else:
                LOG.warning("This object does not have a connection with the backend.")

        return wrapper

    return backend_version_decorator


def deprecated_method(alternative: str | None = None, info: str | None = None):
    """Decorate a method as deprecated.

    Parameters
    ----------
    alternative : str, default: None
        Alternative method to use. If provided, the warning message will
        include the alternative method.
    info : str, default: None
        Additional information to include in the warning message.
    """

    def deprecated_decorator(method):
        def wrapper(*args, **kwargs):
            msg = f"The method '{method.__name__}' is deprecated."
            if alternative:
                msg += f" Use '{alternative}' instead."
            if info:
                msg += f" {info}"
            warnings.warn(msg, DeprecationWarning)
            return method(*args, **kwargs)

        return wrapper

    return deprecated_decorator


def deprecated_argument(arg: str, alternative: str | None = None, info: str | None = None):
    """Decorate a method argument as deprecated.

    Parameters
    ----------
    arg : str
        Argument to mark as deprecated.
    alternative : str, default: None
        Alternative argument to use. If provided, the warning message will
        include the alternative argument.
    info : str, default: None
        Additional information to include in the warning message.
    """

    def deprecated_decorator(method):
        def wrapper(*args, **kwargs):
            if arg in kwargs and kwargs[arg] is not None:
                msg = f"The argument '{arg}' in '{method.__name__}' is deprecated."
                if alternative:
                    msg += f" Use '{alternative}' instead."
                if info:
                    msg += f" {info}"
                warnings.warn(msg, DeprecationWarning)

            return method(*args, **kwargs)

        return wrapper

    return deprecated_decorator
