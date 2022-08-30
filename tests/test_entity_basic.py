import numpy as np
import pytest

from ansys.geometry.core.models import Direction, Matrix, Point3d


def test_geometry_points():
    """This test checks the creation of Point objects."""
    # Create 3D points.
    point_1 = Point3d(-1.5, 1.5, 99)
    point_2 = Point3d(1, 2, 3)

    # Check the first point.
    assert point_1.x == -1.5
    assert point_1.y == 1.5
    assert point_1.z == 99

    # Check the second point.
    assert point_2.x == 1.0
    assert point_2.y == 2.0
    assert point_2.z == 3.0

    # Change the value of x.
    point_1.x = 56
    assert point_1.x == 56

    # Change the value of y.
    point_1.y = 31
    assert point_1.y == 31

    # Change the value of z.
    point_1.x = 22
    assert point_1.x == 22

    # Check the second point remains constant.
    assert point_2.x == 1.0
    assert point_2.y == 2.0
    assert point_2.z == 3.0

    # Verify the point other than integer or float leads to an error.
    with pytest.raises(
        ValueError, match="The parameters 'x', 'y' and 'z' should be integer or float"
    ):
        Point3d(1, 2, "p")

    # Verify the update of point with x-coordinate other than integer or float leads to an error.
    with pytest.raises(ValueError, match="The parameter 'x' should be a float or an integer value"):
        point_2.x = "k"

    # Verify the update of point with y-coordinate other than integer or float leads to an error.
    with pytest.raises(ValueError, match="The parameter 'y' should be a float or an integer value"):
        point_2.y = "k"

    # Verify the update of point with z-coordinate other than integer or float leads to an error.
    with pytest.raises(ValueError, match="The parameter 'z' should be a float or an integer value"):
        point_2.z = "k"


def test_geometry_direction():
    """This test checks the creation of Direction objects and update the value of each
    direction coordinate."""

    # Create 3D direction.
    direction_1 = Direction(0, 1, 0)
    direction_2 = Direction(1, 0, 0)

    # Check the first direction.
    assert direction_1.x == 0.0
    assert direction_1.y == 1.0
    assert direction_1.z == 0.0

    # Check the second direction.
    assert direction_2.x == 1.0
    assert direction_2.y == 0.0
    assert direction_2.z == 0.0

    # Change the value of x-coordinate.
    direction_1.x = 1.0
    assert direction_1.x == 1.0

    # Change the value of y-coordinate.
    direction_1.y = 0.0
    assert direction_1.y == 0.0

    # Change the value of z-coordinate.
    direction_1.x = 1.0
    assert direction_1.x == 1.0

    # Check the second direction remains constant
    assert direction_2.x == 1.0
    assert direction_2.y == 0.0
    assert direction_2.z == 0.0

    # Verify the direction other than integer or float leads to an error.
    with pytest.raises(
        ValueError, match="The parameters 'x', 'y' and 'z' should be integer or float"
    ):
        Direction(1, 2, "p")

    # Verify the update of direction with x-axis other than integer or float leads to an error.
    with pytest.raises(ValueError, match="The parameter 'x' should be a float or an integer value"):
        direction_2.x = "k"

    # Verify the update of direction with y-axis other than integer or float leads to an error.
    with pytest.raises(ValueError, match="The parameter 'y' should be a float or an integer value"):
        direction_2.y = "k"

    # Verify the update of direction with z-axis other than integer or float leads to an error.
    with pytest.raises(ValueError, match="The parameter 'z' should be a float or an integer value"):
        direction_2.z = "k"


def test_geometry_matrix():
    """This test is to check if the ``Matrix`` object is created
    using 1D and 2D Numpy array of shape (16,) and (4, 4)
    respectively or with Numpy matrix of shape(4,4)
    """

    # Create a matrix using 1D np.ndarray.
    array_1d = np.array([0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 2])
    matrix_1 = Matrix(array_1d)

    # Create an 2D np.array with 1D array value.
    matrix_value = np.array([[0, 1, 1, 0], [1, 1, 0, 1], [0, 1, 1, 0], [1, 1, 1, 2]])

    # Check the matrix of Matrix object with np.matrix.
    assert (matrix_value == matrix_1.matrix).all()

    # create a matrix using 2D np.ndarray.
    array_2d = np.array([[0, 1, 1, 0], [1, 1, 0, 1], [0, 1, 1, 0], [1, 1, 1, 2]])
    matrix_2 = Matrix(array_2d)
    assert (matrix_2.matrix == array_2d).all()

    # Update the frame and check the new matrix values.
    new_value = np.array([[2, 6, 9, 1], [2, 1, 5, 1], [6, 2, 1, 1], [1, 1, 1, 5]])
    matrix_1.matrix = new_value
    assert (matrix_1.matrix == new_value).all()

    # Check the other matrix remains constant.
    assert (matrix_2.matrix == array_2d).all()

    # Replace 1st row and 2nd column with new value equals to 10.
    assert matrix_1.matrix[1, 2] == 5
    matrix_1.replace(1, 2, 10)
    assert matrix_1.matrix[1, 2] == 10

    # Verify the input to matrix other than 1D or 2D np.ndarray or np.matrix leads to an error.
    with pytest.raises(ValueError) as val:
        Matrix([45])
    assert (
        "The input to the Matrix should only be an 1D array of shape (16,) or a 2D array of shape (4,4)."  # noqa : E501
        in str(val.value)
    )

    # Verify the input to matrix with 1D np.ndarray other than  shape (16,) leads to an error.
    with pytest.raises(ValueError) as val:
        array_1d = np.array([0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1])
        Matrix(array_1d)
    assert (
        "The array input to the Matrix should only be an 1D array of shape (16,) or a 2D array of shape (4,4)."  # noqa : E501
        in str(val.value)
    )

    # Verify the input to matrix with 2D np.ndarray other than  shape (4, 4) leads to an error.
    with pytest.raises(ValueError) as val:
        array_2d = np.array([[0, 1, 1, 0]])
        Matrix(array_2d)
    assert (
        "The array input to the Matrix should only be an 1D array of shape (16,) or a 2D array of shape (4,4)."  # noqa : E501
        in str(val.value)
    )
