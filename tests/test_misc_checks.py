# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.

import numpy as np
import pytest

from ansys.geometry.core.math import Point3D
from ansys.geometry.core.misc import (
    UNITS,
    check_is_float_int,
    check_ndarray_is_float_int,
    check_ndarray_is_non_zero,
    check_ndarray_is_not_none,
    check_pint_unit_compatibility,
    check_type,
    check_type_equivalence,
)


def test_check_type():
    """
    Test that the __eq__ check is working properly.

    Both objects must be of the same type to be compared.
    """
    a_2d = Point3D([1, 2, 0])

    check_type(a_2d, Point3D)

    with pytest.raises(TypeError, match="Provided type"):
        check_type(a_2d, int)

    with pytest.raises(TypeError, match="Provided type"):
        check_type(a_2d, (int, float))


def test_check_type_equivalence():
    """
    Test that the __eq__ check is working properly.

    Both objects must be of the same type to be compared.
    """
    a_2d = Point3D([1, 2, 0])
    b_2d = Point3D([3, 4, 0])

    # Check that a_2d and 3 are not the same
    with pytest.raises(TypeError, match="Provided type"):
        check_type_equivalence(3, a_2d)

    check_type_equivalence(a_2d, b_2d)


def test_check_pint_unit_compatibility():
    """
    Test that the :class:`pint.Unit` compatibility check is working properly.

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
    """
    Test that :class:`numpy.ndarray <numpy.ndarray>` object contains ``float`` or
    ``int`` values only.

    The object provided must be a :class:`numpy.ndarray <numpy.ndarray>`.
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
