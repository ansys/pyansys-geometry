


Module ``circle``
=================



.. py:module:: ansys.geometry.core.primitives.circle



Description
-----------

Provides for creating and managing a circle.




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

   ansys.geometry.core.primitives.circle.Circle
   ansys.geometry.core.primitives.circle.CircleEvaluation




.. py:class:: Circle(origin: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.Point3D], radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], reference: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D] = UNITVECTOR3D_X, axis: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D] = UNITVECTOR3D_Z)


   Provides 3D circle representation.

   Parameters
   ----------
   origin : Union[~numpy.ndarray, RealSequence, Point3D]
       Origin of the circle.
   radius : Union[Quantity, Distance, Real]
       Radius of the circle.
   reference : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
       X-axis direction.
   axis : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
       Z-axis direction.

   .. py:property:: origin
      :type: ansys.geometry.core.math.Point3D

      Origin of the circle.


   .. py:property:: radius
      :type: pint.Quantity

      Radius of the circle.


   .. py:property:: diameter
      :type: pint.Quantity

      Diameter of the circle.


   .. py:property:: perimeter
      :type: pint.Quantity

      Perimeter of the circle.


   .. py:property:: area
      :type: pint.Quantity

      Area of the circle.


   .. py:property:: dir_x
      :type: ansys.geometry.core.math.UnitVector3D

      X-direction of the circle.


   .. py:property:: dir_y
      :type: ansys.geometry.core.math.UnitVector3D

      Y-direction of the circle.


   .. py:property:: dir_z
      :type: ansys.geometry.core.math.UnitVector3D

      Z-direction of the circle.


   .. py:method:: __eq__(other: Circle) -> bool

      Equals operator for the ``Circle`` class.


   .. py:method:: evaluate(parameter: ansys.geometry.core.typing.Real) -> CircleEvaluation

      Evaluate the circle at a given parameter.

      Parameters
      ----------
      parameter : Real
          Parameter to evaluate the circle at.

      Returns
      -------
      CircleEvaluation
          Resulting evaluation.


   .. py:method:: transformed_copy(matrix: ansys.geometry.core.math.Matrix44) -> Circle

      Create a transformed copy of the circle based on a transformation matrix.

      Parameters
      ----------
      matrix : Matrix44
          4x4 transformation matrix to apply to the circle.

      Returns
      -------
      Circle
          New circle that is the transformed copy of the original circle.


   .. py:method:: mirrored_copy() -> Circle

      Create a mirrored copy of the circle along the y-axis.

      Returns
      -------
      Circle
          A new circle that is a mirrored copy of the original circle.


   .. py:method:: project_point(point: ansys.geometry.core.math.Point3D) -> CircleEvaluation

      Project a point onto the circle and evauate the circle.

      Parameters
      ----------
      point : Point3D
          Point to project onto the circle.

      Returns
      -------
      CircleEvaluation
          Resulting evaluation.


   .. py:method:: is_coincident_circle(other: Circle) -> bool

      Determine if the circle is coincident with another.

      Parameters
      ----------
      other : Circle
          Circle to determine coincidence with.

      Returns
      -------
      bool
          ``True`` if this circle is coincident with the other, ``False`` otherwise.


   .. py:method:: get_parameterization() -> ansys.geometry.core.primitives.parameterization.Parameterization

      Get the parametrization of the circle.

      The parameter of a circle specifies the clockwise angle around the axis
      (right-hand corkscrew law), with a zero parameter at ``dir_x`` and a
      period of 2*pi.

      Returns
      -------
      Parameterization
          Information about how the circle is parameterized.



.. py:class:: CircleEvaluation(circle: Circle, parameter: ansys.geometry.core.typing.Real)


   Bases: :py:obj:`ansys.geometry.core.primitives.curve_evaluation.CurveEvaluation`

   Provides evaluation of a circle at a given parameter.

   Parameters
   ----------
   circle: ~ansys.geometry.core.primitives.circle.Circle
       Circle to evaluate.
   parameter: Real
       Parameter to evaluate the circle at.

   .. py:property:: circle
      :type: Circle

      Circle being evaluated.


   .. py:property:: parameter
      :type: ansys.geometry.core.typing.Real

      Parameter that the evaluation is based upon.


   .. py:method:: position() -> ansys.geometry.core.math.Point3D

      Position of the evaluation.

      Returns
      -------
      Point3D
          Point that lies on the circle at this evaluation.


   .. py:method:: tangent() -> ansys.geometry.core.math.UnitVector3D

      Tangent of the evaluation.

      Returns
      -------
      UnitVector3D
          Tangent unit vector to the circle at this evaluation.


   .. py:method:: normal() -> ansys.geometry.core.math.UnitVector3D

      Normal to the circle.

      Returns
      -------
      UnitVector3D
          Normal unit vector to the circle at this evaluation.


   .. py:method:: first_derivative() -> ansys.geometry.core.math.Vector3D

      First derivative of the evaluation.

      The first derivative is in the direction of the tangent and has a
      magnitude equal to the velocity (rate of change of position) at that
      point.

      Returns
      -------
      Vector3D
          First derivative of the evaluation.


   .. py:method:: second_derivative() -> ansys.geometry.core.math.Vector3D

      Second derivative of the evaluation.

      Returns
      -------
      Vector3D
          Second derivative of the evaluation.


   .. py:method:: curvature() -> ansys.geometry.core.typing.Real

      Curvature of the circle.

      Returns
      -------
      Real
          Curvature of the circle.



