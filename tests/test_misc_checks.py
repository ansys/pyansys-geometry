# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

import warnings

import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core.errors import GeometryRuntimeError
from ansys.geometry.core.math import Point3D
from ansys.geometry.core.misc import (
    UNITS,
    TessellationOptions,
    auxiliary,
    check_is_float_int,
    check_ndarray_is_float_int,
    check_ndarray_is_non_zero,
    check_ndarray_is_not_none,
    check_pint_unit_compatibility,
    check_type,
    check_type_equivalence,
    deprecated_argument,
    deprecated_method,
    kwargs_passed_not_accepted,
    min_backend_version,
)
from ansys.geometry.core.misc.measurements import Angle, Distance


def test_tessellation_options():
    # Testing tessellation options with Real values
    tessellation_options = TessellationOptions(
        surface_deviation=0.01,
        angle_deviation=0.1,
        max_aspect_ratio=2.0,
        max_edge_length=5.0,
        watertight=True,
    )
    assert isinstance(tessellation_options.surface_deviation, Distance)
    assert isinstance(tessellation_options.angle_deviation, Angle)
    assert isinstance(tessellation_options.max_edge_length, Distance)
    assert tessellation_options.surface_deviation.value.m_as("m") == 0.01
    assert tessellation_options.angle_deviation.value.m_as("rad") == 0.1
    assert tessellation_options.max_aspect_ratio == 2.0
    assert tessellation_options.max_edge_length.value.m_as("m") == 5.0
    assert tessellation_options.watertight is True

    # Testing tessellation options with Distance and Angle objects
    tessellation_options_with_measurements = TessellationOptions(
        surface_deviation=Distance(0.02, UNITS.meter),
        angle_deviation=Angle(0.2, UNITS.radian),
        max_aspect_ratio=3.0,
        max_edge_length=Distance(10.0, UNITS.meter),
        watertight=False,
    )
    assert isinstance(tessellation_options_with_measurements.surface_deviation, Distance)
    assert isinstance(tessellation_options_with_measurements.angle_deviation, Angle)
    assert isinstance(tessellation_options_with_measurements.max_edge_length, Distance)
    assert tessellation_options_with_measurements.surface_deviation.value.m_as(UNITS.m) == 0.02
    assert tessellation_options_with_measurements.angle_deviation.value.m_as(UNITS.rad) == 0.2
    assert tessellation_options_with_measurements.max_aspect_ratio == 3.0
    assert tessellation_options_with_measurements.max_edge_length.value.m_as(UNITS.m) == 10.0
    assert tessellation_options_with_measurements.watertight is False

    # Testing tessellation options with Quantity objects
    tessellation_options_with_quantities = TessellationOptions(
        surface_deviation=Quantity(0.03, UNITS.meter),
        angle_deviation=Quantity(0.3, UNITS.radian),
        max_aspect_ratio=4.0,
        max_edge_length=Quantity(15.0, UNITS.meter),
        watertight=True,
    )
    assert isinstance(tessellation_options_with_quantities.surface_deviation, Distance)
    assert isinstance(tessellation_options_with_quantities.angle_deviation, Angle)
    assert isinstance(tessellation_options_with_quantities.max_edge_length, Distance)
    assert tessellation_options_with_quantities.surface_deviation.value.m_as(UNITS.m) == 0.03
    assert tessellation_options_with_quantities.angle_deviation.value.m_as(UNITS.rad) == 0.3
    assert tessellation_options_with_quantities.max_aspect_ratio == 4.0
    assert tessellation_options_with_quantities.max_edge_length.value.m_as(UNITS.m) == 15.0
    assert tessellation_options_with_quantities.watertight is True

    # Testing tessellation options with unit conversions (Distance and Angle)
    tessellation_options_with_conversions = TessellationOptions(
        surface_deviation=Distance(10, UNITS.millimeter),  # 10mm = 0.01m
        angle_deviation=Angle(180, UNITS.degree),  # 180 degrees = π radians
        max_edge_length=Distance(5, UNITS.centimeter),  # 5cm = 0.05m
    )
    import math

    assert isinstance(tessellation_options_with_conversions.surface_deviation, Distance)
    assert isinstance(tessellation_options_with_conversions.angle_deviation, Angle)
    assert isinstance(tessellation_options_with_conversions.max_edge_length, Distance)
    assert (
        abs(tessellation_options_with_conversions.surface_deviation.value.m_as(UNITS.m) - 0.01)
        < 1e-9
    )
    assert (
        abs(tessellation_options_with_conversions.angle_deviation.value.m_as(UNITS.rad) - math.pi)
        < 1e-9
    )
    assert (
        abs(tessellation_options_with_conversions.max_edge_length.value.m_as(UNITS.m) - 0.05) < 1e-9
    )

    # Testing tessellation options with unit conversions (Quantity)
    tessellation_options_with_qty_conversions = TessellationOptions(
        surface_deviation=Quantity(20, UNITS.millimeter),  # 20mm = 0.02m
        angle_deviation=Quantity(90, UNITS.degree),  # 90 degrees = π/2 radians
        max_edge_length=Quantity(10, UNITS.centimeter),  # 10cm = 0.1m
    )
    assert isinstance(tessellation_options_with_qty_conversions.surface_deviation, Distance)
    assert isinstance(tessellation_options_with_qty_conversions.angle_deviation, Angle)
    assert isinstance(tessellation_options_with_qty_conversions.max_edge_length, Distance)
    assert (
        abs(tessellation_options_with_qty_conversions.surface_deviation.value.m_as(UNITS.m) - 0.02)
        < 1e-9
    )
    assert (
        abs(
            tessellation_options_with_qty_conversions.angle_deviation.value.m_as(UNITS.rad)
            - math.pi / 2
        )
        < 1e-9
    )
    assert (
        abs(tessellation_options_with_qty_conversions.max_edge_length.value.m_as(UNITS.m) - 0.1)
        < 1e-9
    )


def test_misc_checks():
    # Testing backend_version_decorator for log warning
    @min_backend_version(25, 2, 0)
    def fake_temp_operation(obj):
        print("Performing operation...")

    invalid_object = {"key": "value"}
    fake_temp_operation(invalid_object)


def test_check_auxiliary():
    """Test the auxiliary functions for checking color conversion."""
    with pytest.raises(ValueError, match="RGB values in the 0-1 range must be floats."):
        auxiliary.convert_color_to_hex(tuple([0, 1, 0]))
    with pytest.raises(ValueError, match="RGB values in the 0-255 range must be integers."):
        auxiliary.convert_color_to_hex(tuple([1.1, 1.1, 1.1, 1.1]))
    with pytest.raises(ValueError, match="RGB tuple contains mixed ranges or invalid values."):
        auxiliary.convert_color_to_hex(tuple([256, 11, 1.1]))
    with pytest.raises(ValueError, match="Invalid color value:."):
        auxiliary.convert_color_to_hex((125, 128))


def test_check_type():
    """Test that the __eq__ check is working properly.

    Both objects must be of the same type to be compared.
    """
    a_2d = Point3D([1, 2, 0])

    check_type(a_2d, Point3D)

    with pytest.raises(TypeError, match="Provided type"):
        check_type(a_2d, int)

    with pytest.raises(TypeError, match="Provided type"):
        check_type(a_2d, (int, float))


def test_check_type_equivalence():
    """Test that the __eq__ check is working properly.

    Both objects must be of the same type to be compared.
    """
    a_2d = Point3D([1, 2, 0])
    b_2d = Point3D([3, 4, 0])

    # Check that a_2d and 3 are not the same
    with pytest.raises(TypeError, match="Provided type"):
        check_type_equivalence(3, a_2d)

    check_type_equivalence(a_2d, b_2d)


def test_check_pint_unit_compatibility():
    """Test that the :class:`pint.Unit` compatibility check is working
    properly.

    Both objects must be of the same dimensionality to be compared.
    """
    length_1 = UNITS.meter
    length_2 = UNITS.mm
    time_1 = UNITS.sec

    # Check that length_1 and time_1 are not of the same dimensionality
    with pytest.raises(TypeError, match="The pint.Unit provided as an input should be a"):
        check_pint_unit_compatibility(length_1, time_1)

    # Check that length_1 and length_2 are not of the same dimensionality
    check_pint_unit_compatibility(length_1, length_2)


def test_check_ndarray_is_float_int():
    """Test that :class:`numpy.ndarray <numpy.ndarray>` object contains
    ``float`` or ``int`` values only.

    The object provided must be a :class:`numpy.ndarray
    <numpy.ndarray>`.
    """
    # Create several arrays
    arr_strs = np.asarray(["a", "b", "c"])
    arr_num = np.asarray([1, 2, 3])
    arr_num_with_strs = np.asarray([1, 2, "a"])

    with pytest.raises(
        TypeError, match="The numpy.ndarray should contain float or integer values."
    ):
        check_ndarray_is_float_int(arr_strs)

    with pytest.raises(
        TypeError, match="The numpy.ndarray 'arr_strs' should contain float or integer values."
    ):
        check_ndarray_is_float_int(arr_strs, "arr_strs")

    with pytest.raises(
        TypeError, match="The numpy.ndarray should contain float or integer values."
    ):
        check_ndarray_is_float_int(arr_num_with_strs)

    # This raises no error
    check_ndarray_is_float_int(arr_num)


def test_check_is_float_int():
    """Test that the input object is a ``float`` or ``int``."""
    # Create several inputs
    str = "a"
    num_int = 1
    num_float = 1.5345
    num_complex = 1 + 2j

    with pytest.raises(TypeError, match="The parameter should have a float or integer value."):
        check_is_float_int(str)

    with pytest.raises(
        TypeError, match="The parameter 'str' should have a float or integer value."
    ):
        check_is_float_int(str, "str")

    with pytest.raises(
        TypeError, match="The parameter 'num_complex' should have a float or integer value."
    ):
        check_is_float_int(num_complex, "num_complex")

    # This raises no error
    check_is_float_int(num_int)
    check_is_float_int(num_float)


def test_check_ndarray_is_non_zero():
    # Create several arrays
    arr_strs = np.asarray(["a", "b", "c"])
    arr_num = np.asarray([1, 2, 3])
    arr_1d = np.asarray([0, 0, 0])
    arr_2d = np.asarray([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    with pytest.raises(
        ValueError, match="The numpy.ndarray should not be a numpy.ndarray of zeros."
    ):
        check_ndarray_is_non_zero(arr_1d)

    with pytest.raises(
        ValueError, match="The numpy.ndarray 'arr_1d' should not be a numpy.ndarray of zeros."
    ):
        check_ndarray_is_non_zero(arr_1d, "arr_1d")

    with pytest.raises(
        ValueError, match="The numpy.ndarray should not be a numpy.ndarray of zeros."
    ):
        check_ndarray_is_non_zero(arr_2d)

    # This raises no error
    check_ndarray_is_non_zero(arr_num)
    check_ndarray_is_non_zero(arr_strs)


def test_check_ndarray_is_not_none():
    # Create several arrays
    arr_strs = np.asarray(["a", "b", "c"])
    arr_num = np.asarray([1, 2, 3])
    arr_1d = np.asarray([None, None, None])
    arr_2d = np.asarray([[None, None, None], [None, None, None], [None, None, None]])

    with pytest.raises(
        ValueError, match="The numpy.ndarray should not have 'None' for all parameter values."
    ):
        check_ndarray_is_not_none(arr_1d)

    with pytest.raises(
        ValueError,
        match="The numpy.ndarray 'arr_1d' should not have 'None' for all parameter values.",
    ):
        check_ndarray_is_not_none(arr_1d, "arr_1d")

    with pytest.raises(
        ValueError, match="The numpy.ndarray should not have 'None' for all parameter values."
    ):
        check_ndarray_is_not_none(arr_2d)

    # This raises no error
    check_ndarray_is_not_none(arr_num)
    check_ndarray_is_not_none(arr_strs)


def test_min_version_backend():
    """Test the minimum backend version checker decorator."""

    class MockClient:
        def __init__(self):
            self.backend_version = "24.1.0"

    class MockObject:
        def __init__(self):
            self._grpc_client = MockClient()

    mock_object = MockObject()

    # Ensure that lower and matching versions do not raise an error
    @min_backend_version(24, 0, 0)
    def case_lower(mock_object):
        return True

    assert case_lower(mock_object)

    @min_backend_version(24, 1, 0)
    def case_match(mock_object):
        return True

    assert case_match(mock_object)

    # Higher version than backend should raise an error
    @min_backend_version(24, 2, 0)
    def case_higher(mock_object):
        return True

    with pytest.raises(
        GeometryRuntimeError,
        match="The method 'case_higher' requires a minimum Ansys release version of 24.2.0, but the current version used is 24.1.0.",  # noqa: E501
    ):
        case_higher(mock_object)

    # If client is not initialized, an error should be raised
    mock_object._grpc_client = None

    @min_backend_version(24, 1, 0)
    def case_no_client(mock_object):
        return True

    with pytest.raises(
        GeometryRuntimeError,
        match="The client is not available. You must initialize the client first.",
    ):
        case_no_client(mock_object)

    # If the client has no backend version, an error should be raised
    mock_object._grpc_client = MockClient()
    mock_object._grpc_client.backend_version = "0.0.0"

    @min_backend_version(24, 2, 0)
    def case_no_version(mock_object):
        return True

    with pytest.raises(
        GeometryRuntimeError,
        match="The method 'case_no_version' requires a minimum Ansys release version of 24.2.0, but the current version used is 24.1.0 or lower.",  # noqa: E501
    ):
        case_no_version(mock_object)


def test_deprecated_method_decorator():
    """Test the deprecated method decorator."""

    class MockObject:
        def __init__(self):
            self._grpc_client = None

        @staticmethod
        @deprecated_method()
        def deprecated_method_no_input():
            return True

        @staticmethod
        @deprecated_method(info="This is some extra info.")
        def deprecated_method_with_info():
            return True

        @staticmethod
        @deprecated_method(
            info="This is some extra info.",
            alternative="new_method",
            version="1.0.0",
            remove="2.0.0",
        )
        def deprecated_method_with_info_and_alternate_and_versions():
            return True

    mock_object = MockObject()

    # Ensure that the method is deprecated
    with pytest.deprecated_call(match="The method 'deprecated_method_no_input' is deprecated."):
        mock_object.deprecated_method_no_input()

    with pytest.deprecated_call(
        match="The method 'deprecated_method_with_info' is deprecated. This is some extra info."
    ):
        mock_object.deprecated_method_with_info()

    with pytest.deprecated_call(
        match="The method 'deprecated_method_with_info_and_alternate_and_versions' is deprecated."
        " Use 'new_method' instead. This is some extra info."
        " This method was deprecated in version 1.0.0."
        " This method will be removed in version 2.0.0."
    ):
        mock_object.deprecated_method_with_info_and_alternate_and_versions()


def test_deprecated_argument_decorator():
    """Test the deprecated argument decorator."""

    class MockObject:
        def __init__(self):
            self._grpc_client = None

        @staticmethod
        @deprecated_argument("dep_arg")
        def deprecated_argument_no_input(dep_arg: str = None):
            return True

        @staticmethod
        @deprecated_argument("dep_arg", info="This is some extra info.")
        def deprecated_argument_with_info(dep_arg: str = None):
            return True

        @staticmethod
        @deprecated_argument(
            "dep_arg",
            info="This is some extra info.",
            alternative="alt_arg",
            version="1.0.0",
            remove="2.0.0",
        )
        def deprecated_argument_with_info_and_alternate_and_versions(
            dep_arg: str = None, alt_arg: str = None
        ):
            return True

    mock_object = MockObject()

    # Ensure that the argument is deprecated
    with pytest.deprecated_call(
        match="The argument 'dep_arg' in 'deprecated_argument_no_input' is deprecated."
    ):
        mock_object.deprecated_argument_no_input(dep_arg="test")

    with pytest.deprecated_call(
        match="The argument 'dep_arg' in 'deprecated_argument_with_info' is deprecated."
        " This is some extra info."
    ):
        mock_object.deprecated_argument_with_info(dep_arg="test")

    with pytest.deprecated_call(
        match="The argument 'dep_arg' in 'deprecated_argument_with_info_and_alternate_and_versions'"
        " is deprecated. Use 'alt_arg' instead. This is some extra info."
        " This argument was deprecated in version 1.0.0."
        " This argument will be removed in version 2.0.0."
    ):
        mock_object.deprecated_argument_with_info_and_alternate_and_versions(dep_arg="test")

    # Check that if we use the alternative argument, no warning is raised
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        mock_object.deprecated_argument_with_info_and_alternate_and_versions(alt_arg="test")


def test_kwargs_passed_not_accepted():
    """Test the kwargs_passed_not_accepted decorator."""

    @kwargs_passed_not_accepted
    def my_method(arg1, arg2, **kwargs):
        """A method that accepts no keyword arguments."""
        return arg1 + arg2

    # Call the method without kwargs - should not raise an error
    assert my_method(1, 2) == 3
    assert my_method(arg1=1, arg2=2) == 3

    # Call the method with kwargs - should raise an error
    with pytest.raises(
        TypeError,
        match="The following keyword arguments are not accepted in the"
        " method 'my_method': unexpected_arg, another_one.",
    ):
        my_method(1, 2, unexpected_arg=3, another_one="test")

    with pytest.raises(
        TypeError,
        match="The following keyword arguments are not accepted in the method 'my_method': arg3.",
    ):
        my_method(arg1=1, arg2=2, arg3=3)


def test_kwargs_passed_not_accepted_decorator_order():
    """Test the kwargs_passed_not_accepted decorator."""

    @deprecated_argument("arg3")
    @kwargs_passed_not_accepted
    def my_method(arg1, arg2, **kwargs):
        """A method that accepts no keyword arguments."""
        return arg1 + arg2

    # Call the method without kwargs - should not raise an error
    assert my_method(1, 2) == 3
    assert my_method(arg1=1, arg2=2) == 3

    # Call the method with kwargs - should raise an error
    with pytest.raises(
        TypeError,
        match="The following keyword arguments are not accepted in the"
        " method 'my_method': unexpected_arg, another_one.",
    ):
        my_method(1, 2, unexpected_arg=3, another_one="test")

    with pytest.raises(
        TypeError,
        match="The following keyword arguments are not accepted in the method 'my_method': arg3.",
    ):
        my_method(arg1=1, arg2=2, arg3=3)

    @kwargs_passed_not_accepted
    @deprecated_argument("arg3")
    def my_method_diff_order(arg1, arg2, **kwargs):
        """A method that accepts no keyword arguments."""
        return arg1 + arg2

    # Call the method without kwargs - should not raise an error
    assert my_method_diff_order(1, 2) == 3
    assert my_method_diff_order(arg1=1, arg2=2) == 3

    # Call the method with kwargs - should raise an error
    with pytest.raises(
        TypeError,
        match="The following keyword arguments are not accepted in the "
        "method 'my_method_diff_order': unexpected_arg, another_one.",
    ):
        my_method_diff_order(1, 2, unexpected_arg=3, another_one="test")

    with pytest.raises(
        TypeError,
        match="The following keyword arguments are not accepted in the "
        "method 'my_method_diff_order': arg3.",
    ):
        my_method_diff_order(arg1=1, arg2=2, arg3=3)
