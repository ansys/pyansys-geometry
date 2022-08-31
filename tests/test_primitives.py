import pytest

from ansys.geometry.core.primitives import Point2D, Point3D


def test_point3d():
    """Simple test to create a ``Point3D``."""

    # Create two Point3D objects
    p_1 = Point3D([0, 1, 3])
    p_1_copy = Point3D([0, 1, 3])
    p_2 = Point3D([0, 4, 7])

    # Check that the equals operator works
    assert p_1 == p_1_copy
    assert p_1 != p_2

    # Check its X, Y, Z components
    assert p_1.x == 0
    assert p_1.y == 1
    assert p_1.z == 3

    # Check that the setter works properly in p_1_copy
    p_1_copy.x = 3
    p_1_copy.y = 3
    p_1_copy.z = 3

    # Check that the equals operator works (p_1 and p_1_copy should no longer be equal)
    assert p_1 != p_1_copy
    assert p_1 != p_2


def test_point2d():
    """Simple test to create a ``Point2D``."""

    # Create two Point2D objects
    p_1 = Point2D([0, 1])
    p_1_copy = Point2D([0, 1])
    p_2 = Point2D([0, 4])

    # Check that the equals operator works
    assert p_1 == p_1_copy
    assert p_1 != p_2

    # Check its X, Y, Z components
    assert p_1.x == 0
    assert p_1.y == 1

    # Check that the setter works properly in p_1_copy
    p_1_copy.x = 3
    p_1_copy.y = 3

    # Check that the equals operator works (p_1 and p_1_copy should no longer be equal)
    assert p_1 != p_1_copy
    assert p_1 != p_2


def test_point3d_errors():
    """Testing multiple ``Point3D`` errors."""

    with pytest.raises(ValueError, match="Point3D must have three coordinates."):
        Point3D([1, 4])

    with pytest.raises(ValueError, match="The input parameters should be integer or float."):
        Point3D(["a", "b", "c"])

    # Create a point
    point = Point3D([1, 4, 4])

    # Test setter error checks
    with pytest.raises(
        ValueError, match="The parameter 'x' should be a float or an integer value."
    ):
        point.x = "a"

    with pytest.raises(
        ValueError, match="The parameter 'y' should be a float or an integer value."
    ):
        point.y = "a"

    with pytest.raises(
        ValueError, match="The parameter 'z' should be a float or an integer value."
    ):
        point.z = "a"

    # Build a Point2D and try to compare against it
    with pytest.raises(ValueError, match="Comparison of"):
        point_2d = Point2D([1, 4])
        assert point == point_2d


def test_point2d_errors():
    """Testing multiple ``Point2D`` errors."""

    with pytest.raises(ValueError, match="Point2D must have two coordinates."):
        Point2D([1, 4, 4])

    with pytest.raises(ValueError, match="The input parameters should be integer or float."):
        Point2D(["a", "b"])

    # Create a point
    point = Point2D([1, 4])

    # Test setter error checks
    with pytest.raises(
        ValueError, match="The parameter 'x' should be a float or an integer value."
    ):
        point.x = "a"

    with pytest.raises(
        ValueError, match="The parameter 'y' should be a float or an integer value."
    ):
        point.y = "a"

    # Build a Point3D and try to compare against it
    with pytest.raises(ValueError, match="Comparison of"):
        point_3d = Point3D([1, 4, 4])
        assert point == point_3d
