from ansys.geometry.core.primitives import Point


def test_Point():
    """Simple test to create a ``Point``."""

    # Create two Point objects
    p_1 = Point(0, 1, 3)
    p_1_copy = Point(0, 1, 3)
    p_2 = Point(0, 4, 7)

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

    # Check that the equals operator works (p_1 and p_1_copy shouuld no longer be equal)
    assert p_1 != p_1_copy
    assert p_1 != p_2
