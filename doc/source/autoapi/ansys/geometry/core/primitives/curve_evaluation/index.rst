


Module ``curve_evaluation``
===========================



.. py:module:: ansys.geometry.core.primitives.curve_evaluation



Description
-----------

Provides for creating and managing a curve.




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

   ansys.geometry.core.primitives.curve_evaluation.CurveEvaluation




.. py:class:: CurveEvaluation(parameter: ansys.geometry.core.typing.Real = None)


   Provides for evaluating a curve.

   .. py:property:: parameter
      :type: ansys.geometry.core.typing.Real
      :abstractmethod:

      Parameter that the evaluation is based upon.


   .. py:method:: is_set() -> bool

      Determine if the parameter for the evaluation has been set.


   .. py:method:: position() -> ansys.geometry.core.math.Point3D
      :abstractmethod:

      Position of the evaluation.


   .. py:method:: first_derivative() -> ansys.geometry.core.math.Vector3D
      :abstractmethod:

      First derivative of the evaluation.


   .. py:method:: second_derivative() -> ansys.geometry.core.math.Vector3D
      :abstractmethod:

      Second derivative of the evaluation.


   .. py:method:: curvature() -> ansys.geometry.core.typing.Real
      :abstractmethod:

      Curvature of the evaluation.



