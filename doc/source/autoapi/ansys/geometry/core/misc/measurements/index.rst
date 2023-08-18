


Module ``measurements``
=======================



.. py:module:: ansys.geometry.core.misc.measurements



Description
-----------

Provides various measurement-related classes.




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

   ansys.geometry.core.misc.measurements.SingletonMeta
   ansys.geometry.core.misc.measurements.DefaultUnitsClass
   ansys.geometry.core.misc.measurements.Measurement
   ansys.geometry.core.misc.measurements.Distance
   ansys.geometry.core.misc.measurements.Angle




Attributes
~~~~~~~~~~

.. autoapisummary::

   ansys.geometry.core.misc.measurements.DEFAULT_UNITS


.. py:class:: SingletonMeta


   Bases: :py:obj:`type`

   Provides a thread-safe implementation of a singleton design pattern.

   .. py:method:: __call__(*args, **kwargs)

      Return a single instance of the class.

      Possible changes to the value of the ``__init__`` argument do not affect the
      returned instance.



.. py:class:: DefaultUnitsClass


   Provides default units for the PyGeometry singleton design pattern.

   .. py:property:: LENGTH
      :type: pint.Unit

      Default length unit for PyGeometry.


   .. py:property:: ANGLE
      :type: pint.Unit

      Default angle unit for PyGeometry.


   .. py:property:: SERVER_LENGTH
      :type: pint.Unit

      Default length unit for supporting Geometry services for gRPC messages.

      Notes
      -----
      The default units on the server side are not modifiable yet.


   .. py:property:: SERVER_AREA
      :type: pint.Unit

      Default area unit for supporting Geometry services for gRPC messages.

      Notes
      -----
      The default units on the server side are not modifiable yet.


   .. py:property:: SERVER_VOLUME
      :type: pint.Unit

      Default volume unit for supporting Geometry services for gRPC messages.

      Notes
      -----
      The default units on the server side are not modifiable yet.


   .. py:property:: SERVER_ANGLE
      :type: pint.Unit

      Default angle unit for supporting Geometry services for gRPC messages.

      Notes
      -----
      The default units on the server side are not modifiable yet.



.. py:data:: DEFAULT_UNITS

   PyGeometry default units object.


.. py:class:: Measurement(value: beartype.typing.Union[ansys.geometry.core.typing.Real, pint.Quantity], unit: pint.Unit, dimensions: pint.Unit)


   Bases: :py:obj:`ansys.geometry.core.misc.units.PhysicalQuantity`

   Provides the ``PhysicalQuantity`` subclass for holding a measurement.

   Parameters
   ----------
   value : Union[Real, Quantity]
       Value of the measurement.
   unit : ~pint.Unit
       Units for the measurement.
   dimensions : ~pint.Unit
       Units for extracting the dimensions of the measurement.
       If ``~pint.Unit.meter`` is given, the dimension extracted is ``[length]``.

   .. py:property:: value
      :type: pint.Quantity

      Value of the measurement.


   .. py:method:: __eq__(other: Measurement) -> bool

      Equals operator for the ``Measurement`` class.



.. py:class:: Distance(value: beartype.typing.Union[ansys.geometry.core.typing.Real, pint.Quantity], unit: beartype.typing.Optional[pint.Unit] = None)


   Bases: :py:obj:`Measurement`

   Provides the ``Measurement`` subclass for holding a distance.

   Parameters
   ----------
   value : Union[Real, Quantity]
       Value of the distance.
   unit : ~pint.Unit, default: DEFAULT_UNITS.LENGTH
       Units for the distance.


.. py:class:: Angle(value: beartype.typing.Union[ansys.geometry.core.typing.Real, pint.Quantity], unit: beartype.typing.Optional[pint.Unit] = None)


   Bases: :py:obj:`Measurement`

   Provides the ``Measurement`` subclass for holding an angle.

   Parameters
   ----------
   value : Union[Real, Quantity]
       Value of the angle.
   unit : ~pint.Unit, default: DEFAULT_UNITS.ANGLE
       Units for the distance.


