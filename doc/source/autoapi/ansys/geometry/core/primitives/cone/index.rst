


Module ``cone``
===============



.. py:module:: ansys.geometry.core.primitives.cone



Description
-----------

Provides for creating and managing a cone.




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

   ansys.geometry.core.primitives.cone.Cone
   ansys.geometry.core.primitives.cone.ConeEvaluation




.. py:class:: Cone(origin: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.Point3D], radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], half_angle: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Angle, ansys.geometry.core.typing.Real], reference: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D] = UNITVECTOR3D_X, axis: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D] = UNITVECTOR3D_Z)


   Provides 3D cone representation.

   Parameters
   ----------
   origin : Union[~numpy.ndarray, RealSequence, Point3D]
       Origin of the cone.
   radius : Union[Quantity, Distance, Real]
       Radius of the cone.
   half_angle : Union[Quantity, Angle, Real]
       Half angle of the apex, determining the upward angle.
   reference : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
       X-axis direction.
   axis : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
       Z-axis direction.

   .. py:property:: origin
      :type: ansys.geometry.core.math.Point3D

      Origin of the cone.


   .. py:property:: radius
      :type: pint.Quantity

      Radius of the cone.


   .. py:property:: half_angle
      :type: pint.Quantity

      Half angle of the apex.


   .. py:property:: dir_x
      :type: ansys.geometry.core.math.UnitVector3D

      X-direction of the cone.


   .. py:property:: dir_y
      :type: ansys.geometry.core.math.UnitVector3D

      Y-direction of the cone.


   .. py:property:: dir_z
      :type: ansys.geometry.core.math.UnitVector3D

      Z-direction of the cone.


   .. py:property:: height
      :type: pint.Quantity

      Height of the cone.


   .. py:property:: surface_area
      :type: pint.Quantity

      Surface area of the cone.


   .. py:property:: volume
      :type: pint.Quantity

      Volume of the cone.


   .. py:property:: apex
      :type: ansys.geometry.core.math.Point3D

      Apex point of the cone.


   .. py:property:: apex_param
      :type: ansys.geometry.core.typing.Real

      Apex parameter of the cone.


   .. py:method:: transformed_copy(matrix: ansys.geometry.core.math.Matrix44) -> Cone

      Create a transformed copy of the cone based on a transformation matrix.

      Parameters
      ----------
      matrix : Matrix44
          4x4 transformation matrix to apply to the cone.

      Returns
      -------
      Cone
          New cone that is the transformed copy of the original cone.


   .. py:method:: mirrored_copy() -> Cone

      Create a mirrored copy of the cone along the y-axis.

      Returns
      -------
      Cone
          New cone that is a mirrored copy of the original cone.


   .. py:method:: __eq__(other: Cone) -> bool

      Equals operator for the ``Cone`` class.


   .. py:method:: evaluate(parameter: ansys.geometry.core.primitives.parameterization.ParamUV) -> ConeEvaluation

      Evaluate the cone at given parameters.

      Parameters
      ----------
      parameter : ParamUV
          Parameters (u,v) to evaluate the cone at.

      Returns
      -------
      ConeEvaluation
          Resulting evaluation.


   .. py:method:: project_point(point: ansys.geometry.core.math.Point3D) -> ConeEvaluation

      Project a point onto the cone and evaluate the cone.

      Parameters
      ----------
      point : Point3D
          Point to project onto the cone.

      Returns
      -------
      ConeEvaluation
          Resulting evaluation.


   .. py:method:: get_u_parameterization() -> ansys.geometry.core.primitives.parameterization.Parameterization

      Get the parametrization conditions for the U parameter.

      The U parameter specifies the clockwise angle around the axis (right-hand
      corkscrew law), with a zero parameter at ``dir_x`` and a period of 2*pi.

      Returns
      -------
      Parameterization
          Information about how a cone's U parameter is parameterized.


   .. py:method:: get_v_parameterization() -> ansys.geometry.core.primitives.parameterization.Parameterization

      Get the parametrization conditions for the V parameter.

      The V parameter specifies the distance along the axis, with a zero parameter at
      the XY plane of the cone.

      Returns
      -------
      Parameterization
          Information about how a cone's V parameter is parameterized.



.. py:class:: ConeEvaluation(cone: Cone, parameter: ansys.geometry.core.primitives.parameterization.ParamUV)


   Bases: :py:obj:`ansys.geometry.core.primitives.surface_evaluation.SurfaceEvaluation`

   Evaluate the cone at given parameters.

   Parameters
   ----------
   cone: ~ansys.geometry.core.primitives.cone.Cone
       Cone to evaluate.
   parameter: ParamUV
       Pparameters (u, v) to evaluate the cone at.

   .. py:property:: cone
      :type: Cone

      Cone being evaluated.


   .. py:property:: parameter
      :type: ansys.geometry.core.primitives.parameterization.ParamUV

      Parameter that the evaluation is based upon.


   .. py:method:: position() -> ansys.geometry.core.math.Point3D

      Position of the evaluation.

      Returns
      -------
      Point3D
          Point that lies on the cone at this evaluation.


   .. py:method:: normal() -> ansys.geometry.core.math.UnitVector3D

      Normal to the surface.

      Returns
      -------
      UnitVector3D
          Normal unit vector to the cone at this evaluation.


   .. py:method:: u_derivative() -> ansys.geometry.core.math.Vector3D

      First derivative with respect to the U parameter.

      Returns
      -------
      Vector3D
          First derivative with respect to the U parameter.


   .. py:method:: v_derivative() -> ansys.geometry.core.math.Vector3D

      First derivative with respect to the V parameter.

      Returns
      -------
      Vector3D
          First derivative with respect to the V parameter.


   .. py:method:: uu_derivative() -> ansys.geometry.core.math.Vector3D

      Second derivative with respect to the U parameter.

      Returns
      -------
      Vector3D
          Second derivative with respect to the U parameter.


   .. py:method:: uv_derivative() -> ansys.geometry.core.math.Vector3D

      Second derivative with respect to the U and V parameters.

      Returns
      -------
      Vector3D
          Second derivative with respect to U and V parameters.


   .. py:method:: vv_derivative() -> ansys.geometry.core.math.Vector3D

      Second derivative with respect to the V parameter.

      Returns
      -------
      Vector3D
          Second derivative with respect to the V parameter.


   .. py:method:: min_curvature() -> ansys.geometry.core.typing.Real

      Minimum curvature of the cone.

      Returns
      -------
      Real
          Minimum curvature of the cone.


   .. py:method:: min_curvature_direction() -> ansys.geometry.core.math.UnitVector3D

      Minimum curvature direction.

      Returns
      -------
      UnitVector3D
          Minimum curvature direction.


   .. py:method:: max_curvature() -> ansys.geometry.core.typing.Real

      Maximum curvature of the cone.

      Returns
      -------
      Real
          Maximum curvature of the cone.


   .. py:method:: max_curvature_direction() -> ansys.geometry.core.math.UnitVector3D

      Maximum curvature direction.

      Returns
      -------
      UnitVector3D
          Maximum curvature direction.



