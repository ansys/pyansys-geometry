


Module ``matrix``
=================



.. py:module:: ansys.geometry.core.math.matrix



Description
-----------

Provides matrix primitive representations.




Summary
-------

.. tab-set::




    .. tab-item:: Classes

        Content 2

    .. tab-item:: Functions

        Content 2

    .. tab-item:: Enumerations

        Content 2

    .. tab-item:: Attributes

        Content 2






Contents
--------

Classes
~~~~~~~

.. autoapisummary::

   ansys.geometry.core.math.matrix.Matrix
   ansys.geometry.core.math.matrix.Matrix33
   ansys.geometry.core.math.matrix.Matrix44




Attributes
~~~~~~~~~~

.. autoapisummary::

   ansys.geometry.core.math.matrix.DEFAULT_MATRIX33
   ansys.geometry.core.math.matrix.DEFAULT_MATRIX44


.. py:data:: DEFAULT_MATRIX33

   Default value of the 3x3 identity matrix for the ``Matrix33`` class.


.. py:data:: DEFAULT_MATRIX44

   Default value of the 4x4 identity matrix for the ``Matrix44`` class.


.. py:class:: Matrix(shape, dtype=float, buffer=None, offset=0, strides=None, order=None)


   Bases: :py:obj:`numpy.ndarray`

   Provides matrix primitive representation.

   Parameters
   ----------
   input : Union[~numpy.ndarray, RealSequence]
       Matrix arguments as a :class:`np.ndarray <numpy.ndarray>` class.

   .. py:method:: determinant() -> ansys.geometry.core.typing.Real

      Get the determinant of the matrix.


   .. py:method:: inverse() -> Matrix

      Provide the inverse of the matrix.


   .. py:method:: __mul__(other: beartype.typing.Union[Matrix, numpy.ndarray]) -> Matrix

      Get the multiplication of the matrix.


   .. py:method:: __eq__(other: Matrix) -> bool

      Equals operator for the ``Matrix`` class.


   .. py:method:: __ne__(other: Matrix) -> bool

      Not equals operator for the ``Matrix`` class.



.. py:class:: Matrix33(shape, dtype=float, buffer=None, offset=0, strides=None, order=None)


   Bases: :py:obj:`Matrix`

   Provides 3x3 matrix primitive representation.

   Parameters
   ----------
   input : Union[~numpy.ndarray, RealSequence, Matrix], default: DEFAULT_MATRIX33
       Matrix arguments as a :class:`np.ndarray <numpy.ndarray>` class.


.. py:class:: Matrix44(shape, dtype=float, buffer=None, offset=0, strides=None, order=None)


   Bases: :py:obj:`Matrix`

   Provides 4x4 matrix primitive representation.

   Parameters
   ----------
   input : Union[~numpy.ndarray, RealSequence, Matrix], default: DEFAULT_MATRIX44
       Matrix arguments as a :class:`np.ndarray <numpy.ndarray>` class.


