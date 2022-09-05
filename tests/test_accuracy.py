from ansys.geometry.core.accuracy import Accuracy


def test_length():
    """Determine effective length accuracy comparisons."""

    assert not Accuracy.length_is_zero(5)
    assert not Accuracy.length_is_zero(1e-7)
    assert Accuracy.length_is_zero(0)
    assert Accuracy.length_is_zero(1e-9)

    assert not Accuracy.length_is_negative(5)
    assert not Accuracy.length_is_negative(1e-10)
    assert not Accuracy.length_is_negative(1e-7)
    assert not Accuracy.length_is_negative(0)
    assert not Accuracy.length_is_negative(-1e-9)
    assert not Accuracy.length_is_negative(-1e-8)
    assert Accuracy.length_is_negative(-5)
    assert Accuracy.length_is_negative(-1e-7)

    assert not Accuracy.length_is_positive(-5)
    assert not Accuracy.length_is_positive(-1e-10)
    assert not Accuracy.length_is_positive(-1e-7)
    assert not Accuracy.length_is_positive(0)
    assert not Accuracy.length_is_positive(1e-9)
    assert not Accuracy.length_is_positive(1e-8)
    assert Accuracy.length_is_positive(5)
    assert Accuracy.length_is_positive(1e-7)


def test_angle():
    """Determine effective angle accuracy comparisons."""

    assert not Accuracy.angle_is_zero(5)
    assert not Accuracy.angle_is_zero(1e-6)
    assert Accuracy.angle_is_zero(0)
    assert Accuracy.angle_is_zero(1e-7)

    assert not Accuracy.angle_is_negative(5)
    assert not Accuracy.angle_is_negative(-1e-8)
    assert not Accuracy.angle_is_negative(1e-7)
    assert not Accuracy.angle_is_negative(0)
    assert Accuracy.angle_is_negative(-5)
    assert Accuracy.angle_is_negative(-1e-6)
    assert Accuracy.angle_is_negative(-1e-5)

    assert not Accuracy.angle_is_positive(-5)
    assert not Accuracy.angle_is_positive(1e-8)
    assert not Accuracy.angle_is_positive(1e-7)
    assert not Accuracy.angle_is_positive(0)
    assert Accuracy.angle_is_positive(5)
    assert Accuracy.angle_is_positive(1e-6)
    assert Accuracy.angle_is_positive(1e-5)


def test_within_tolerance():
    """Determine effective tolerance comparison."""

    # due to relative tolerance
    assert Accuracy.is_within_tolerance(5, 7, 0.4, 1.0)
    assert Accuracy.is_within_tolerance(5, 7, 1 / 3, 1.0)
    assert not Accuracy.is_within_tolerance(5, 7, 0.3, 1.0)

    # due to absolute tolerance
    assert not Accuracy.is_within_tolerance(5, 6, 0, 1)
    assert Accuracy.is_within_tolerance(5, 6, 0, 1.1)
