


Module ``ellipse``
==================



.. py:module:: ansys.geometry.core.primitives.ellipse



Description
-----------

Provides for creating and managing an ellipse.




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

   ansys.geometry.core.primitives.ellipse.Ellipse
   ansys.geometry.core.primitives.ellipse.EllipseEvaluation




.. py:class:: Ellipse(origin: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.Point3D], major_radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], minor_radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], reference: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D] = UNITVECTOR3D_X, axis: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D] = UNITVECTOR3D_Z)


   Provides 3D ellipse representation.

   Parameters
   ----------
   origin : Union[~numpy.ndarray, RealSequence, Point3D]
       Origin of the ellipse.
   major_radius : Union[Quantity, Distance, Real]
       Major radius of the ellipse.
   minor_radius : Union[Quantity, Distance, Real]
       Minor radius of the ellipse.
   reference : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
       X-axis direction.
   axis : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
       Z-axis direction.

   .. py:property:: origin
      :type: ansys.geometry.core.math.Point3D

      Origin of the ellipse.


   .. py:property:: major_radius
      :type: pint.Quantity

      Major radius of the ellipse.


   .. py:property:: minor_radius
      :type: pint.Quantity

      Minor radius of the ellipse.


   .. py:property:: dir_x
      :type: ansys.geometry.core.math.UnitVector3D

      X-direction of the ellipse.


   .. py:property:: dir_y
      :type: ansys.geometry.core.math.UnitVector3D

      Y-direction of the ellipse.


   .. py:property:: dir_z
      :type: ansys.geometry.core.math.UnitVector3D

      Z-direction of the ellipse.


   .. py:property:: eccentricity
      :type: ansys.geometry.core.typing.Real

      Eccentricity of the ellipse.


   .. py:property:: linear_eccentricity
      :type: pint.Quantity

      Linear eccentricity of the ellipse.

      Notes
      -----
      The linear eccentricity is the distance from the center to the focus.


   .. py:property:: semi_latus_rectum
      :type: pint.Quantity

      Semi-latus rectum of the ellipse.


   .. py:property:: perimeter
      :type: pint.Quantity

      Perimeter of the ellipse.


   .. py:property:: area
      :type: pint.Quantity

      Area of the ellipse.


   .. py:method:: __eq__(other: Ellipse) -> bool

      Equals operator for the ``Ellipse`` class.


   .. py:method:: mirrored_copy() -> Ellipse

      Create a mirrored copy of the ellipse along the y-axis.

      Returns
      -------
      Ellipse
          New ellipse that is a mirrored copy of the original ellipse.


   .. py:method:: evaluate(parameter: ansys.geometry.core.typing.Real) -> EllipseEvaluation

      Evaluate the ellipse at the given parameter.

      Parameters
      ----------
      parameter : Real
          Parameter to evaluate the ellipse at.

      Returns
      -------
      EllipseEvaluation
          Resulting evaluation.


   .. py:method:: project_point(point: ansys.geometry.core.math.Point3D) -> EllipseEvaluation

      Project a point onto the ellipse and evaluate the ellipse.

      Parameters
      ----------
      point : Point3D
          Point to project onto the ellipse.

      Returns
      -------
      EllipseEvaluation
          Resulting evaluation.


   .. py:method:: is_coincident_ellipse(other: Ellipse) -> bool

      Determine if this ellipse is coincident with another.

      Parameters
      ----------
      other : Ellipse
          Ellipse to determine coincidence with.

      Returns
      -------
      bool
          ``True`` if this ellipse is coincident with the other, ``False`` otherwise.


   .. py:method:: transformed_copy(matrix: ansys.geometry.core.math.Matrix44) -> Ellipse

      Create a transformed copy of the ellipse based on a transformation matrix.

      Parameters
      ----------
      matrix : Matrix44
          4x4 transformation matrix to apply to the ellipse.

      Returns
      -------
      Ellipse
          New ellipse that is the transformed copy of the original ellipse.


   .. py:method:: get_parameterization() -> ansys.geometry.core.primitives.parameterization.Parameterization

      Get the parametrization of the ellipse.

      The parameter of an ellipse specifies the clockwise angle around the axis
      (right-hand corkscrew law), with a zero parameter at ``dir_x`` and a period of 2*pi.

      Returns
      -------
      Parameterization
          Information about how the ellipse is parameterized.



.. py:class:: EllipseEvaluation(ellipse: Ellipse, parameter: ansys.geometry.core.typing.Real)


   Bases: :py:obj:`ansys.geometry.core.primitives.curve_evaluation.CurveEvaluation`

   Evaluate an ellipse at a given parameter.

   Parameters
   ----------
   ellipse: ~ansys.geometry.core.primitives.ellipse.Ellipse
       Ellipse to evaluate.
   parameter: float, int
       Parameter to evaluate the ellipse at.

   .. py:property:: ellipse
      :type: Ellipse

      Ellipse being evaluated.


   .. py:property:: parameter
      :type: ansys.geometry.core.typing.Real

      Parameter that the evaluation is based upon.


   .. py:method:: position() -> ansys.geometry.core.math.Point3D

      Position of the evaluation.

      Returns
      -------
      Point3D
          Point that lies on the ellipse at this evaluation.


   .. py:method:: tangent() -> ansys.geometry.core.math.UnitVector3D

      Tangent of the evaluation.

      Returns
      -------
      UnitVector3D
          Tangent unit vector to the ellipse at this evaluation.


   .. py:method:: normal() -> ansys.geometry.core.math.UnitVector3D

      Normal of the evaluation.

      Returns
      -------
      UnitVector3D
          Normal unit vector to the ellipse at this evaluation.


   .. py:method:: first_derivative() -> ansys.geometry.core.math.Vector3D

      Girst derivative of the evaluation.

      The first derivative is in the direction of the tangent and has a magnitude
      equal to the velocity (rate of change of position) at that point.

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

      Curvature of the ellipse.

      Returns
      -------
      Real
          Curvature of the ellipse.



