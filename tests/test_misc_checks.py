import numpy as np
import pytest

from ansys.geometry.core import UNITS
from ansys.geometry.core.math import Point2D, Point3D
from ansys.geometry.core.math.vector import (
    QuantityVector2D,
    QuantityVector3D,
    UnitVector2D,
    UnitVector3D,
    Vector2D,
    Vector3D,
)
from ansys.geometry.core.misc import (
    check_is_float_int,
    check_is_pint_unit,
    check_is_point,
    check_is_quantityvector,
    check_is_unitvector,
    check_is_vector,
    check_ndarray_is_float_int,
    check_ndarray_is_non_zero,
    check_ndarray_is_not_none,
    check_pint_unit_compatibility,
    check_type_equivalence,
)


def test_check_type_equivalence():
    """
    Test that the __eq__ check is working properly.

    Both objects must be of the same type to be compared.
    """
    a_2d = Point2D([1, 2])
    a_3d = Point3D([1, 2, 0])
    b_2d = Point2D([3, 4])

    # Check that a_2d and a_3d are not the same
    with pytest.raises(TypeError, match="Provided type"):
        check_type_equivalence(a_2d, a_3d)

    # Check that a_2d and a_3d are not the same
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
    with pytest.raises(TypeError, match="The pint.Unit provided as input should be a"):
        check_pint_unit_compatibility(length_1, time_1)

    # Check that length_1 and length_2 are not of the same dimensionality
    check_pint_unit_compatibility(length_1, length_2)


def test_check_is_pint_unit():
    """
    Test that the :class:`pint.Unit` type check is working properly.

    The object provided must be a :class:`pint.Unit`.
    """
    pint_unit = UNITS.meter
    not_a_pint_unit = "myUnit"

    # Check that not_a_pint_unit is not a pint.Unit object
    with pytest.raises(TypeError, match="The parameter 'unit' should be a pint.Unit object."):
        check_is_pint_unit(not_a_pint_unit)

    with pytest.raises(
        TypeError, match="The parameter 'not_a_pint_unit' should be a pint.Unit object."
    ):
        check_is_pint_unit(not_a_pint_unit, "not_a_pint_unit")

    # Check that pint_unit is indeed a pint.Unit
    check_is_pint_unit(pint_unit)


def test_check_ndarray_is_float_int():
    """
    Test that :class:`numpy.ndarray` object contains ``float`` or ``int`` values only.

    The object provided must be a :class:`numpy.ndarray`.
    """

    # Create several arrays
    arr_strs = np.asarray(["a", "b", "c"])
    arr_num = np.asarray([1, 2, 3])
    arr_num_with_strs = np.asarray([1, 2, "a"])

    with pytest.raises(
        TypeError, match="The numpy.ndarray provided should contain float or integer values."
    ):
        check_ndarray_is_float_int(arr_strs)

    with pytest.raises(
        TypeError, match="The numpy.ndarray 'arr_strs' should contain float or integer values."
    ):
        check_ndarray_is_float_int(arr_strs, "arr_strs")

    with pytest.raises(
        TypeError, match="The numpy.ndarray provided should contain float or integer values."
    ):
        check_ndarray_is_float_int(arr_num_with_strs)

    # This raises no error
    check_ndarray_is_float_int(arr_num)


def test_check_is_float_int():
    """
    Test that the input object is a ``float`` or ``int``.
    """

    # Create several inputs
    str = "a"
    num_int = 1
    num_float = 1.5345
    num_complex = 1 + 2j

    with pytest.raises(
        TypeError, match="The parameter provided should be a float or an integer value."
    ):
        check_is_float_int(str)

    with pytest.raises(
        TypeError, match="The parameter 'str' should be a float or an integer value."
    ):
        check_is_float_int(str, "str")

    with pytest.raises(
        TypeError, match="The parameter 'num_complex' should be a float or an integer value."
    ):
        check_is_float_int(num_complex, "num_complex")

    # This raises no error
    check_is_float_int(num_int)
    check_is_float_int(num_float)


def test_check_is_point():
    """
    Test that the input object is a ``Point2D`` or ``Point3D``.
    """

    # Create several arrays
    arr_strs = np.asarray(["a", "b", "c"])
    arr_num = np.asarray([1, 2, 3])
    vector_2d = Vector2D([1, 2])

    with pytest.raises(
        TypeError, match="The parameter provided should be a Point3D or Point2D object."
    ):
        check_is_point(arr_strs)

    with pytest.raises(TypeError, match="The parameter 'arr_num' should be a Point3D object."):
        check_is_point(arr_num, "arr_num", only_3d=True)

    with pytest.raises(
        TypeError, match="The parameter provided should be a Point3D or Point2D object."
    ):
        check_is_point(vector_2d)

    with pytest.raises(TypeError, match="The parameter provided should be a Point3D object."):
        check_is_point(Point2D(), only_3d=True)

    # This raises no error
    check_is_point(Point3D())
    check_is_point(Point2D())
    check_is_point(Point3D([1, 2, 3]))
    check_is_point(Point2D([1, 2]))


def test_check_is_vector():
    """
    Test that the input object is a ``Vector2D`` or ``Vector3D``.
    """

    # Create several arrays
    arr_strs = np.asarray(["a", "b", "c"])
    arr_num = np.asarray([1, 2, 3])
    point_2d = Point2D([1, 2])

    with pytest.raises(
        TypeError, match="The parameter provided should be a Vector3D or Vector2D object."
    ):
        check_is_vector(arr_strs)

    with pytest.raises(TypeError, match="The parameter 'arr_num' should be a Vector3D object."):
        check_is_vector(arr_num, "arr_num", only_3d=True)

    with pytest.raises(
        TypeError, match="The parameter provided should be a Vector3D or Vector2D object."
    ):
        check_is_vector(point_2d)

    with pytest.raises(TypeError, match="The parameter provided should be a Vector3D object."):
        check_is_vector(Vector2D([1, 0]), only_3d=True)

    # This raises no error
    check_is_vector(Vector2D([1, 2]))
    check_is_vector(UnitVector2D([1, 2]))
    check_is_vector(QuantityVector2D([1, 2], UNITS.mm))
    check_is_vector(Vector3D([1, 2, 3]))
    check_is_vector(UnitVector3D([1, 2, 3]))
    check_is_vector(QuantityVector3D([1, 2, 3], UNITS.mm))


def test_check_is_quantityvector():
    """
    Test that the input object is a ``QuantityVector2D`` or ``QuantityVector3D``.
    """

    # Create several arrays
    arr_strs = np.asarray(["a", "b", "c"])
    arr_num = np.asarray([1, 2, 3])
    point_2d = Point2D([1, 2])

    with pytest.raises(
        TypeError,
        match="The parameter provided should be a QuantityVector3D or QuantityVector2D object.",
    ):
        check_is_quantityvector(arr_strs)

    with pytest.raises(
        TypeError, match="The parameter 'arr_num' should be a QuantityVector3D object."
    ):
        check_is_quantityvector(arr_num, "arr_num", only_3d=True)

    with pytest.raises(
        TypeError,
        match="The parameter provided should be a QuantityVector3D or QuantityVector2D object.",
    ):
        check_is_quantityvector(point_2d)

    with pytest.raises(
        TypeError, match="The parameter provided should be a QuantityVector3D object."
    ):
        check_is_quantityvector(QuantityVector2D([1, 0], UNITS.mm), only_3d=True)

    with pytest.raises(
        TypeError,
        match="The parameter provided should be a QuantityVector3D or QuantityVector2D object.",
    ):
        check_is_quantityvector(Vector2D([1, 2]))

    with pytest.raises(
        TypeError,
        match="The parameter provided should be a QuantityVector3D or QuantityVector2D object.",
    ):
        check_is_quantityvector(UnitVector2D([1, 2]))

    with pytest.raises(
        TypeError,
        match="The parameter provided should be a QuantityVector3D or QuantityVector2D object.",
    ):
        check_is_quantityvector(Vector3D([1, 2, 3]))

    with pytest.raises(
        TypeError,
        match="The parameter provided should be a QuantityVector3D or QuantityVector2D object.",
    ):
        check_is_quantityvector(UnitVector3D([1, 2, 3]))

    # This raises no error
    check_is_quantityvector(QuantityVector2D([1, 2], UNITS.mm))
    check_is_quantityvector(QuantityVector3D([1, 2, 3], UNITS.mm))


def test_check_is_unitvector():
    """
    Test that the input object is a ``UnitVector2D`` or ``UnitVector3D``.
    """

    # Create several arrays
    arr_strs = np.asarray(["a", "b", "c"])
    arr_num = np.asarray([1, 2, 3])
    point_2d = Point2D([1, 2])

    with pytest.raises(
        TypeError, match="The parameter provided should be a UnitVector3D or UnitVector2D object."
    ):
        check_is_unitvector(arr_strs)

    with pytest.raises(TypeError, match="The parameter 'arr_num' should be a UnitVector3D object."):
        check_is_unitvector(arr_num, "arr_num", only_3d=True)

    with pytest.raises(
        TypeError, match="The parameter provided should be a UnitVector3D or UnitVector2D object."
    ):
        check_is_unitvector(point_2d)

    with pytest.raises(TypeError, match="The parameter provided should be a UnitVector3D object."):
        check_is_unitvector(UnitVector2D([1, 0]), only_3d=True)

    with pytest.raises(
        TypeError, match="The parameter provided should be a UnitVector3D or UnitVector2D object."
    ):
        check_is_unitvector(Vector2D([1, 2]))

    with pytest.raises(
        TypeError, match="The parameter provided should be a UnitVector3D or UnitVector2D object."
    ):
        check_is_unitvector(QuantityVector2D([1, 2], UNITS.mm))

    with pytest.raises(
        TypeError, match="The parameter provided should be a UnitVector3D or UnitVector2D object."
    ):
        check_is_unitvector(Vector3D([1, 2, 3]))

    with pytest.raises(
        TypeError, match="The parameter provided should be a UnitVector3D or UnitVector2D object."
    ):
        check_is_unitvector(QuantityVector3D([1, 2, 3], UNITS.mm))

    # This raises no error
    check_is_unitvector(UnitVector2D([1, 2]))
    check_is_unitvector(UnitVector3D([1, 2, 3]))


def test_check_ndarray_is_non_zero():
    # Create several arrays
    arr_strs = np.asarray(["a", "b", "c"])
    arr_num = np.asarray([1, 2, 3])
    arr_1d = np.asarray([0, 0, 0])
    arr_2d = np.asarray([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    with pytest.raises(
        ValueError, match="The numpy.ndarray provided should not be a numpy.ndarray of zeros."
    ):
        check_ndarray_is_non_zero(arr_1d)

    with pytest.raises(
        ValueError, match="The numpy.ndarray 'arr_1d' should not be a numpy.ndarray of zeros."
    ):
        check_ndarray_is_non_zero(arr_1d, "arr_1d")

    with pytest.raises(
        ValueError, match="The numpy.ndarray provided should not be a numpy.ndarray of zeros."
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
        ValueError, match="The numpy.ndarray provided should not be a None numpy.ndarray."
    ):
        check_ndarray_is_not_none(arr_1d)

    with pytest.raises(
        ValueError, match="The numpy.ndarray 'arr_1d' should not be a None numpy.ndarray."
    ):
        check_ndarray_is_not_none(arr_1d, "arr_1d")

    with pytest.raises(
        ValueError, match="The numpy.ndarray provided should not be a None numpy.ndarray."
    ):
        check_ndarray_is_not_none(arr_2d)

    # This raises no error
    check_ndarray_is_not_none(arr_num)
    check_ndarray_is_not_none(arr_strs)
