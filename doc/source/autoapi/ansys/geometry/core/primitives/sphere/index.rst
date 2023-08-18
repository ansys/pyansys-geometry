


Module ``sphere``
=================



.. py:module:: ansys.geometry.core.primitives.sphere



Description
-----------

Provides for creating and managing a sphere.




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

   ansys.geometry.core.primitives.sphere.Sphere
   ansys.geometry.core.primitives.sphere.SphereEvaluation




.. py:class:: Sphere(origin: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.Point3D], radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], reference: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D] = UNITVECTOR3D_X, axis: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D] = UNITVECTOR3D_Z)


   Provides 3D sphere representation.

   Parameters
   ----------
   origin : Union[~numpy.ndarray, RealSequence, Point3D]
       Origin of the sphere.
   radius : Union[Quantity, Distance, Real]
       Radius of the sphere.
   reference : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
       X-axis direction.
   axis : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
       Z-axis direction.

   .. py:property:: origin
      :type: ansys.geometry.core.math.Point3D

      Origin of the sphere.


   .. py:property:: radius
      :type: pint.Quantity

      Radius of the sphere.


   .. py:property:: dir_x
      :type: ansys.geometry.core.math.UnitVector3D

      X-direction of the sphere.


   .. py:property:: dir_y
      :type: ansys.geometry.core.math.UnitVector3D

      Y-direction of the sphere.


   .. py:property:: dir_z
      :type: ansys.geometry.core.math.UnitVector3D

      Z-direction of the sphere.


   .. py:property:: surface_area
      :type: pint.Quantity

      Surface area of the sphere.


   .. py:property:: volume
      :type: pint.Quantity

      Volume of the sphere.


   .. py:method:: __eq__(other: Sphere) -> bool

      Equals operator for the ``Sphere`` class.


   .. py:method:: transformed_copy(matrix: ansys.geometry.core.math.Matrix44) -> Sphere

      Create a transformed copy of the sphere based on a transformation matrix.

      Parameters
      ----------
      matrix : Matrix44
          4X4 transformation matrix to apply to the sphere.

      Returns
      -------
      Sphere
          New sphere that is the transformed copy of the original sphere.


   .. py:method:: mirrored_copy() -> Sphere

      Create a mirrored copy of the sphere along the y-axis.

      Returns
      -------
      Sphere
          New sphere that is a mirrored copy of the original sphere.


   .. py:method:: evaluate(parameter: ansys.geometry.core.primitives.parameterization.ParamUV) -> SphereEvaluation

      Evaluate the sphere at the given parameters.

      Parameters
      ----------
      parameter : ParamUV
          Parameters (u,v) to evaluate the sphere at.

      Returns
      -------
      SphereEvaluation
          Resulting evaluation.


   .. py:method:: project_point(point: ansys.geometry.core.math.Point3D) -> SphereEvaluation

      Project a point onto the sphere and evaluate the sphere.

      Parameters
      ----------
      point : Point3D
          Point to project onto the sphere.

      Returns
      -------
      SphereEvaluation
          Resulting evaluation.


   .. py:method:: get_u_parameterization() -> ansys.geometry.core.primitives.parameterization.Parameterization

      Get the parametrization conditions for the U parameter.

      The U parameter specifies the longitude angle, increasing clockwise (east) about
      ``dir_z`` (right-hand corkscrew law). It has a zero parameter at ``dir_x`` and a
      period of ``2*pi``.

      Returns
      -------
      Parameterization
          Information about how a sphere's U parameter is parameterized.


   .. py:method:: get_v_parameterization() -> ansys.geometry.core.primitives.parameterization.Parameterization

      Get the parametrization conditions for the V parameter.

      The V parameter specifies the latitude, increasing north, with a zero parameter
      at the equator and a range of ``[-pi/2, pi/2]``.

      Returns
      -------
      Parameterization
          Information about how a sphere's V parameter is parameterized.



.. py:class:: SphereEvaluation(sphere: Sphere, parameter: ansys.geometry.core.primitives.parameterization.ParamUV)


   Bases: :py:obj:`ansys.geometry.core.primitives.surface_evaluation.SurfaceEvaluation`

   Evaluate a sphere at given parameters.

   Parameters
   ----------
   sphere: ~ansys.geometry.core.primitives.sphere.Sphere
       Sphere to evaluate.
   parameter: ParamUV
       Parameters (u, v) to evaluate the sphere at.

   .. py:property:: sphere
      :type: Sphere

      Sphere being evaluated.


   .. py:property:: parameter
      :type: ansys.geometry.core.primitives.parameterization.ParamUV

      Parameter that the evaluation is based upon.


   .. py:method:: position() -> ansys.geometry.core.math.Point3D

      Position of the evaluation.

      Returns
      -------
      Point3D
          Point that lies on the sphere at this evaluation.


   .. py:method:: normal() -> ansys.geometry.core.math.UnitVector3D

      The normal to the surface.

      Returns
      -------
      UnitVector3D
          Normal unit vector to the sphere at this evaluation.


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
          The second derivative with respect to the U and V parameters.


   .. py:method:: vv_derivative() -> ansys.geometry.core.math.Vector3D

      Second derivative with respect to the V parameter.

      Returns
      -------
      Vector3D
          The second derivative with respect to the V parameter.


   .. py:method:: min_curvature() -> ansys.geometry.core.typing.Real

      Minimum curvature of the sphere.

      Returns
      -------
      Real
          Minimum curvature of the sphere.


   .. py:method:: min_curvature_direction() -> ansys.geometry.core.math.UnitVector3D

      Minimum curvature direction.

      Returns
      -------
      UnitVector3D
          Minimum curvature direction.


   .. py:method:: max_curvature() -> ansys.geometry.core.typing.Real

      Maximum curvature of the sphere.

      Returns
      -------
      Real
          Maximum curvature of the sphere.


   .. py:method:: max_curvature_direction() -> ansys.geometry.core.math.UnitVector3D

      Maximum curvature direction.

      Returns
      -------
      UnitVector3D
          Maximum curvature direction.



