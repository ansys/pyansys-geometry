


Module ``parameterization``
===========================



.. py:module:: ansys.geometry.core.primitives.parameterization



Description
-----------

Provides the parametrization-related classes.




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

   ansys.geometry.core.primitives.parameterization.ParamUV
   ansys.geometry.core.primitives.parameterization.Interval
   ansys.geometry.core.primitives.parameterization.ParamForm
   ansys.geometry.core.primitives.parameterization.ParamType
   ansys.geometry.core.primitives.parameterization.Parameterization




.. py:class:: ParamUV(u: ansys.geometry.core.typing.Real, v: ansys.geometry.core.typing.Real)


   Parameter class containing 2 parameters: (u, v).

   Notes
   -----
   Likened to a 2D point in UV space Used as an argument in parametric
   surface evaluations. This matches the service implementation for the
   Geometry service.

   Parameters
   ----------
   u : Real
       u-parameter.
   v : Real
       v-parameter.

   .. py:property:: u
      :type: ansys.geometry.core.typing.Real

      u-parameter.


   .. py:property:: v
      :type: ansys.geometry.core.typing.Real

      v-parameter.


   .. py:method:: __add__(other: ParamUV) -> ParamUV

      Add the u and v components of the other ParamUV to this ParamUV.

      Parameters
      ----------
      other : ParamUV
          The parameters to add these parameters.

      Returns
      -------
      ParamUV
          The sum of the parameters.


   .. py:method:: __sub__(other: ParamUV) -> ParamUV

      Subtract the u and v components of the other ParamUV from this ParamUV.

      Parameters
      ----------
      other : ParamUV
          The parameters to subtract from these parameters.

      Returns
      -------
      ParamUV
          The difference of the parameters.


   .. py:method:: __mul__(other: ParamUV) -> ParamUV

      Multiplies the u and v components of this ParamUV by the other ParamUV.

      Parameters
      ----------
      other : ParamUV
          The parameters to multiply by these parameters.

      Returns
      -------
      ParamUV
          The product of the parameters.


   .. py:method:: __truediv__(other: ParamUV) -> ParamUV

      Divides the u and v components of this ParamUV by the other ParamUV.

      Parameters
      ----------
      other : ParamUV
          The parameters to divide these parameters by.

      Returns
      -------
      ParamUV
          The quotient of the parameters.


   .. py:method:: __repr__() -> str

      Represent the ``ParamUV`` as a string.



.. py:class:: Interval(start: ansys.geometry.core.typing.Real, end: ansys.geometry.core.typing.Real)


   Interval class that defines a range of values.

   Parameters
   ----------
   start : Real
       Start value of the interval.
   end : Real
       End value of the interval.

   .. py:property:: start
      :type: ansys.geometry.core.typing.Real

      Start value of the interval.


   .. py:property:: end
      :type: ansys.geometry.core.typing.Real

      End value of the interval.


   .. py:method:: is_open() -> bool

      If the interval is open (-inf, inf).

      Returns
      -------
      bool
          True if both ends of the interval are negative and positive infinity respectively.


   .. py:method:: is_closed() -> bool

      If the interval is closed. Neither value is inf or -inf.

      Returns
      -------
      bool
          True if neither bound of the interval is infinite.


   .. py:method:: get_span() -> ansys.geometry.core.typing.Real

      Return the quantity contained by the interval. Interval must be closed.

      Returns
      -------
      Real
          The difference between the end and start of the interval.


   .. py:method:: __repr__() -> str

      Represent the ``Interval`` as a string.



.. py:class:: ParamForm


   Bases: :py:obj:`enum.Enum`

   ParamForm enum class that defines the form of a Parameterization.

   .. py:attribute:: OPEN
      :value: 1



   .. py:attribute:: CLOSED
      :value: 2



   .. py:attribute:: PERIODIC
      :value: 3



   .. py:attribute:: OTHER
      :value: 4




.. py:class:: ParamType


   Bases: :py:obj:`enum.Enum`

   ParamType enum class that defines the type of a Parameterization.

   .. py:attribute:: LINEAR
      :value: 1



   .. py:attribute:: CIRCULAR
      :value: 2



   .. py:attribute:: OTHER
      :value: 3




.. py:class:: Parameterization(form: ParamForm, type: ParamType, interval: Interval)


   Parameterization class describes the parameters of a specific geometry.

   Parameters
   ----------
   form : ParamForm
       Form of the parameterization.
   type : ParamType
       Type of the parameterization.
   interval : Interval
       Interval of the parameterization.

   .. py:property:: form
      :type: ParamForm

      The form of the parameterization.


   .. py:property:: type
      :type: ParamType

      The type of the parameterization.


   .. py:property:: interval
      :type: Interval

      The interval of the parameterization.


   .. py:method:: __repr__() -> str

      Represent the ``Parameterization`` as a string.



