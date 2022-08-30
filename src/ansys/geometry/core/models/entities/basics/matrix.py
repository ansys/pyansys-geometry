"""This module provides access and interaction with the PyDiscovery Matrix object."""
import numpy as np

from ansys.geometry.core.models.entities.core import BaseEntity


class Matrix(BaseEntity):
    """Provides access to create an homogeneous 3D transformation matrix.

        - The matrix is a pre-multiplication transformation.
        - The rotation is in m00->m22 and contains no scaling in its leading diagonal.
        - The translation is m03/m33, m13/m33, m23/m33.
        - The uniform scale is 1/m33.

    Provides the gRPC wrapper for matrices. The input to a Matrix should only be
    a 1D numpy array of shape (16,) or a 2D numpy array of shape (4,4).

    Parameters
    ----------
    matrix : np.ndarray
        1D numpy array of shape (16,) or 2D numpy array of
        shape (4,4).

    Examples
    --------
    Create a matrix from a 1D Numpy array.

    >>> from ansys.geometry.core.models import Matrix
    >>> value = np.array([0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 2])
    >>> matrix = Matrix(value)
    >>> matrix
    <ansys.geometry.core.models.entities.basics.matrix.Matrix object at 0x000002252CE6E050>
    >>> matrix.matrix
    array([[0, 1, 1, 0],
            [1, 1, 0, 1],
            [0, 1, 1, 0],
            [1, 1, 1, 2]])

    Create a Matrix from 2D Numpy array.

    >>> from ansys.geometry.core.models import Matrix
    >>> value = np.array([[0, 1, 1, 0], [1, 1, 0, 1], [0, 1, 1, 0], [1, 1, 1, 2]])
    >>> matrix = Matrix(value)
    >>> matrix
    <ansys.geometry.core.models.entities.basics.matrix.Matrix object at 0x000002252CE6E230>
    >>> matrix.matrix
    array([[0, 1, 1, 0],
            [1, 1, 0, 1],
            [0, 1, 1, 0],
            [1, 1, 1, 2]])
    """

    def __init__(self, matrix):
        """Matrix constructor."""
        self._matrix = self._check_input_matrix(matrix)

    @property
    def matrix(self):
        """Return the 3D transformation matrix.

        Examples
        --------
        Create a Matrix from Numpy matrix.

        >>> from ansys.discovery.models.geometry import Matrix
        >>> value = np.array([[0, 1, 1, 0], [1, 1, 0, 1], [0, 1, 1, 0], [1, 1, 1, 2]])
        >>> matrix = Matrix(value)
        >>> matrix
        <ansys.geometry.core.models.entities.basics.matrix.Matrix object at 0x000002252CE6E230>
        >>> matrix.matrix
        array([[0, 1, 1, 0],
                [1, 1, 0, 1],
                [0, 1, 1, 0],
                [1, 1, 1, 2]])

        Change the value of Matrix.

        >>> new_value = np.array([[0, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1], [1, 1, 1, 5]])
        >>> matrix.matrix = new_value
        >>> matrix.matrix
        array([[0, 0, 0, 1],
            [0, 1, 0, 1],
            [0, 0, 1, 1],
            [1, 1, 1, 5]])
        """
        return self._matrix

    @matrix.setter
    def matrix(self, matrix):
        """Set the 3D transformation matrix."""
        self._matrix = self._check_input_matrix(matrix)

    def replace(self, x, y, new_value):
        """Replace the single element in the matrix.

        Parameters
        ----------
        x : int
            The row value of the matrix to be change.

        y : int
            The column value of the matrix to be change.

        new_value : float
            The new value of the element in Matrix object.

        Examples
        --------
        Create a Matrix from Numpy matrix.

        >>> from ansys.discovery.models.geometry import Matrix
        >>> value = np.matrix([[0, 1, 1, 0], [1, 1, 0, 1], [0, 1, 1, 0], [1, 1, 1, 2]])
        >>> matrix = Matrix(value)
        >>> matrix
        <ansys.geometry.core.models.entities.basics.matrix.Matrix object at 0x000002252CE6E230>
        >>> matrix.matrix
        array([[0, 1, 1, 0],
            [1, 1, 0, 1],
            [0, 1, 1, 0],
            [1, 1, 1, 2]])

        Replace 1st row and 2nd column with new value equals to 10.

        >>> matrix.replace(1, 2, 10)
        >>> matrix.matrix
        array([[ 0,  0,  0,  1],
               [ 0,  1, 10,  1],
               [ 0,  0,  1,  1],
               [ 1,  1,  1,  5]])
        """
        if not all(isinstance(value, (int, float)) for value in [x, y]):
            raise ValueError("The parameters 'x' and 'y' should be an integer")
        if isinstance(new_value, float):
            raise ValueError("The parameter 'new_value' can only be a float")

        self._matrix[x, y] = new_value

    def _check_input_matrix(self, value):
        """Sanity check function to determine if the value passed to the Matrix is acceptable."""
        if isinstance(value, np.ndarray):

            if value.ndim == 1 and value.size == 16:
                return value.reshape(4, 4)

            elif value.ndim == 2 and value.shape == (4, 4):
                return value

            else:
                raise ValueError(
                    "The array input to the Matrix should only be an 1D array of shape (16,) or a 2D array of shape (4,4)."  # noqa : E501
                )

        else:
            raise ValueError(
                "The input to the Matrix should only be an 1D array of shape (16,) or a 2D array of shape (4,4)."  # noqa : E501
            )
