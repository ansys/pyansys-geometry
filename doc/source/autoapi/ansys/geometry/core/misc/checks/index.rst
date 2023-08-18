


Module ``checks``
=================



.. py:module:: ansys.geometry.core.misc.checks



Description
-----------

Provides functions for performing common checks.




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


Functions
~~~~~~~~~

.. autoapisummary::

   ansys.geometry.core.misc.checks.check_is_float_int
   ansys.geometry.core.misc.checks.check_ndarray_is_float_int
   ansys.geometry.core.misc.checks.check_ndarray_is_not_none
   ansys.geometry.core.misc.checks.check_ndarray_is_all_nan
   ansys.geometry.core.misc.checks.check_ndarray_is_non_zero
   ansys.geometry.core.misc.checks.check_pint_unit_compatibility
   ansys.geometry.core.misc.checks.check_type_equivalence
   ansys.geometry.core.misc.checks.check_type



.. py:function:: check_is_float_int(param: object, param_name: beartype.typing.Optional[beartype.typing.Union[str, None]] = None) -> None

   Check if a parameter has a float or integer value.

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


.. py:function:: check_ndarray_is_float_int(param: numpy.ndarray, param_name: beartype.typing.Optional[beartype.typing.Union[str, None]] = None) -> None

   Check if a :class:`numpy.ndarray <numpy.ndarray>` has float or integer values.

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


.. py:function:: check_ndarray_is_not_none(param: numpy.ndarray, param_name: beartype.typing.Optional[beartype.typing.Union[str, None]] = None) -> None

   Check if a :class:`numpy.ndarray <numpy.ndarray>` has all ``None`` values.

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


.. py:function:: check_ndarray_is_all_nan(param: numpy.ndarray, param_name: beartype.typing.Optional[beartype.typing.Union[str, None]] = None) -> None

   Check if a :class:`numpy.ndarray <numpy.ndarray>` is all nan-valued.

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


.. py:function:: check_ndarray_is_non_zero(param: numpy.ndarray, param_name: beartype.typing.Optional[beartype.typing.Union[str, None]] = None) -> None

   Check if a :class:`numpy.ndarray <numpy.ndarray>` is zero-valued.

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


.. py:function:: check_pint_unit_compatibility(input: pint.Unit, expected: pint.Unit) -> None

   Check if input for :class:`pint.Unit` is compatible with the expected input.

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


.. py:function:: check_type_equivalence(input: object, expected: object) -> None

   Check if an input object is of the same class as an expected object.

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


.. py:function:: check_type(input: object, expected_type: beartype.typing.Union[type, beartype.typing.Tuple[type, Ellipsis]]) -> None

   Check if an input object is of the same type as expected types.

   Parameters
   ----------
   input : object
       Input object.
   expected_type : Union[type, Tuple[type, ...]]
       One or more types to compare the input object against.

   Raises
   ------
   TypeError
       If the object does not match the one or more expected types.


