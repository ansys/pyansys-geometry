


Module ``torus``
================



.. py:module:: ansys.geometry.core.primitives.torus



Description
-----------

Provides for creating and managing a torus.




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

   ansys.geometry.core.primitives.torus.Torus
   ansys.geometry.core.primitives.torus.TorusEvaluation




.. py:class:: Torus(origin: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.Point3D], major_radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], minor_radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], reference: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D] = UNITVECTOR3D_X, axis: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D] = UNITVECTOR3D_Z)


   Provides 3D torus representation.

   Parameters
   ----------
   origin : Union[~numpy.ndarray, RealSequence, Point3D],
       Centered origin of the torus.
   direction_x : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
       X-axis direction.
   direction_y : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
       Y-axis direction.
   major_radius : Union[Quantity, Distance, Real]
       Major radius of the torus.
   minor_radius : Union[Quantity, Distance, Real]
       Minor radius of the torus.

   .. py:property:: origin
      :type: ansys.geometry.core.math.Point3D

      Origin of the torus.


   .. py:property:: major_radius
      :type: pint.Quantity

      Semi-major radius of the torus.


   .. py:property:: minor_radius
      :type: pint.Quantity

      Semi-minor radius of the torus.


   .. py:property:: dir_x
      :type: ansys.geometry.core.math.UnitVector3D

      X-direction of the torus.


   .. py:property:: dir_y
      :type: ansys.geometry.core.math.UnitVector3D

      Y-direction of the torus.


   .. py:property:: dir_z
      :type: ansys.geometry.core.math.UnitVector3D

      Z-direction of the torus.


   .. py:property:: volume
      :type: pint.Quantity

      Volume of the torus.


   .. py:property:: surface_area
      :type: pint.Quantity

      Surface_area of the torus.


   .. py:method:: __eq__(other: Torus) -> bool

      Equals operator for the ``Torus`` class.


   .. py:method:: transformed_copy(matrix: ansys.geometry.core.math.Matrix44) -> Torus

      Create a transformed copy of the torus based on a transformation matrix.

      Parameters
      ----------
      matrix : Matrix44
          4x4 transformation matrix to apply to the torus.

      Returns
      -------
      Torus
          New torus that is the transformed copy of the original torus.


   .. py:method:: mirrored_copy() -> Torus

      Create a mirrored copy of the torus along the y-axis.

      Returns
      -------
      Torus
          New torus that is a mirrored copy of the original torus.


   .. py:method:: evaluate(parameter: ansys.geometry.core.primitives.parameterization.ParamUV) -> TorusEvaluation

      Evaluate the torus at the given parameters.

      Parameters
      ----------
      parameter : ParamUV
          Parameters (u,v) to evaluate the torus at.

      Returns
      -------
      TorusEvaluation
          Resulting evaluation.


   .. py:method:: get_u_parameterization()

      Get the parametrization conditions for the U parameter.

      The U parameter specifies the longitude angle, increasing clockwise (east) about
      the axis (right-hand corkscrew law). It has a zero parameter at
      ``Geometry.Frame.DirX`` and a period of ``2*pi``.

      Returns
      -------
      Parameterization
          Information about how a sphere's U parameter is parameterized.


   .. py:method:: get_v_parameterization() -> ansys.geometry.core.primitives.parameterization.Parameterization

      Get the parametrization conditions of the V parameter.

      The V parameter specifies the latitude, increasing north, with a zero parameter
      at the equator. For the donut, where the ``Geometry.Torus.MajorRadius`` is greater
      than the ``Geometry.Torus.MinorRadius``, the range is ``[-pi, pi]`` and the
      parameterization is periodic. For a degenerate torus, the range is restricted
      accordingly and the parameterization is non-periodic.

      Returns
      -------
      Parameterization
          Information about how a torus's V parameter is parameterized.


   .. py:method:: project_point(point: ansys.geometry.core.math.Point3D) -> TorusEvaluation

      Project a point onto the torus and evaluate the torus.

      Parameters
      ----------
      point : Point3D
          Point to project onto the torus.

      Returns
      -------
      TorusEvaluation
          Resulting evaluation.



.. py:class:: TorusEvaluation(torus: Torus, parameter: ansys.geometry.core.primitives.parameterization.ParamUV)


   Bases: :py:obj:`ansys.geometry.core.primitives.surface_evaluation.SurfaceEvaluation`

   Evaluate the torus`` at given parameters.

   Parameters
   ----------
   Torus: ~ansys.geometry.core.primitives.torus.Torus
       Torust to evaluate.
   parameter: ParamUV
       Parameters (u, v) to evaluate the torus at.

   .. py:property:: torus
      :type: Torus

      Torus being evaluated.


   .. py:property:: parameter
      :type: ansys.geometry.core.primitives.parameterization.ParamUV

      Parameter that the evaluation is based upon.


   .. py:method:: position() -> ansys.geometry.core.math.Point3D

      Position of the evaluation.

      Returns
      -------
      Point3D
          Point that lies on the torus at this evaluation.


   .. py:method:: normal() -> ansys.geometry.core.math.UnitVector3D

      Normal to the surface.

      Returns
      -------
      UnitVector3D
          Normal unit vector to the torus at this evaluation.


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
          Second derivative with respect to the U and V parameters.


   .. py:method:: vv_derivative() -> ansys.geometry.core.math.Vector3D

      Second derivative with respect to the V parameter.

      Returns
      -------
      Vector3D
          Second derivative with respect to the V parameter.


   .. py:method:: curvature() -> Tuple[ansys.geometry.core.typing.Real, ansys.geometry.core.math.Vector3D, ansys.geometry.core.typing.Real, ansys.geometry.core.math.Vector3D]

      Curvature of the torus.

      Returns
      -------
      Tuple[Real, Vector3D, Real, Vector3D]
          Minimum and maximum curvature value and direction, respectively.


   .. py:method:: min_curvature() -> ansys.geometry.core.typing.Real

      Minimum curvature of the torus.

      Returns
      -------
      Real
          Minimum curvature of the torus.


   .. py:method:: min_curvature_direction() -> ansys.geometry.core.math.UnitVector3D

      Minimum curvature direction.

      Returns
      -------
      UnitVector3D
          Minimum curvature direction.


   .. py:method:: max_curvature() -> ansys.geometry.core.typing.Real

      Maximum curvature of the torus.

      Returns
      -------
      Real
          Maximum curvature of the torus.


   .. py:method:: max_curvature_direction() -> ansys.geometry.core.math.UnitVector3D

      Maximum curvature direction.

      Returns
      -------
      UnitVector3D
          Maximum curvature direction.



