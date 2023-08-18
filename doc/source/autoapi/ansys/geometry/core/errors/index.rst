


Module ``errors``
=================



.. py:module:: ansys.geometry.core.errors



Description
-----------

Provides PyGeometry-specific errors.




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

   ansys.geometry.core.errors.handler
   ansys.geometry.core.errors.protect_grpc



Attributes
~~~~~~~~~~

.. autoapisummary::

   ansys.geometry.core.errors.SIGINT_TRACKER


.. py:data:: SIGINT_TRACKER
   :value: []



.. py:exception:: GeometryRuntimeError


   Bases: :py:obj:`RuntimeError`

   Provides error message to raise when Geometry service passes a runtime error.


.. py:exception:: GeometryExitedError(msg='Geometry service has exited.')


   Bases: :py:obj:`RuntimeError`

   Provides error message to raise when Geometry service has exited.

   Parameters
   ----------
   msg : str, default: "Geometry service has exited."
       Message to raise.


.. py:function:: handler(sig, frame)

   Pass signal to the custom interrupt handler.


.. py:function:: protect_grpc(func)

   Capture gRPC exceptions and raise a more succinct error message.

   This method captures the ``KeyboardInterrupt`` exception to avoid
   segfaulting the Geometry service.

   While this works some of the time, it does not work all of the time. For some
   reason, gRPC still captures SIGINT.


