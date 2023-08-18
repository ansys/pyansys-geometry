


Module ``cylinder``
===================



.. py:module:: ansys.geometry.core.primitives.cylinder



Description
-----------

Provides for creating and managing a cylinder.




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

   ansys.geometry.core.primitives.cylinder.Cylinder
   ansys.geometry.core.primitives.cylinder.CylinderEvaluation




.. py:class:: Cylinder(origin: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.Point3D], radius: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real], reference: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D] = UNITVECTOR3D_X, axis: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D] = UNITVECTOR3D_Z)


   Provides 3D cylinder representation.

   Parameters
   ----------
   origin : Union[~numpy.ndarray, RealSequence, Point3D]
       Origin of the cylinder.
   radius : Union[Quantity, Distance, Real]
       Radius of the cylinder.
   reference : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
       X-axis direction.
   axis : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
       Z-axis direction.

   .. py:property:: origin
      :type: ansys.geometry.core.math.Point3D

      Origin of the cylinder.


   .. py:property:: radius
      :type: pint.Quantity

      Radius of the cylinder.


   .. py:property:: dir_x
      :type: ansys.geometry.core.math.UnitVector3D

      X-direction of the cylinder.


   .. py:property:: dir_y
      :type: ansys.geometry.core.math.UnitVector3D

      Y-direction of the cylinder.


   .. py:property:: dir_z
      :type: ansys.geometry.core.math.UnitVector3D

      Z-direction of the cylinder.


   .. py:method:: surface_area(height: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real]) -> pint.Quantity

      Get the surface area of the cylinder.

      Notes
      -----
         By nature, a cylinder is infinite. If you want to get the surface area,
         you must bound it by a height. Normally a cylinder surface is not closed
         (does not have "caps" on the ends). This method assumes that the cylinder
         is closed for the purpose of getting the surface area.

      Parameters
      ----------
      height : Union[Quantity, Distance, Real]
          Height to bound the cylinder at.

      Returns
      -------
      Quantity
          Surface area of the temporarily bounded cylinder.


   .. py:method:: volume(height: beartype.typing.Union[pint.Quantity, ansys.geometry.core.misc.Distance, ansys.geometry.core.typing.Real]) -> pint.Quantity

      Get the volume of the cylinder.

      Notes
      -----
         By nature, a cylinder is infinite. If you want to get the surface area,
         you must bound it by a height. Normally a cylinder surface is not closed
         (does not have "caps" on the ends). This method assumes that the cylinder
         is closed for the purpose of getting the surface area.

      Parameters
      ----------
      height : Union[Quantity, Distance, Real]
          Height to bound the cylinder at.

      Returns
      -------
      Quantity
          Volume of the temporarily bounded cylinder.


   .. py:method:: transformed_copy(matrix: ansys.geometry.core.math.Matrix44) -> Cylinder

      Create a transformed copy of the cylinder based on a transformation matrix.

      Parameters
      ----------
      matrix : Matrix44
          4X4 transformation matrix to apply to the cylinder.

      Returns
      -------
      Cylinder
          New cylinder that is the transformed copy of the original cylinder.


   .. py:method:: mirrored_copy() -> Cylinder

      Create a mirrored copy of the cylinder along the y-axis.

      Returns
      -------
      Cylinder
          New cylinder that is a mirrored copy of the original cylinder.


   .. py:method:: __eq__(other: Cylinder) -> bool

      Equals operator for the ``Cylinder`` class.


   .. py:method:: evaluate(parameter: ansys.geometry.core.primitives.surface_evaluation.ParamUV) -> CylinderEvaluation

      Evaluate the cylinder at the given parameters.

      Parameters
      ----------
      parameter : ParamUV
          Parameters (u,v) to evaluate the cylinder at.

      Returns
      -------
      CylinderEvaluation
          Resulting evaluation.


   .. py:method:: project_point(point: ansys.geometry.core.math.Point3D) -> CylinderEvaluation

      Project a point onto the cylinder and evaluate the cylinder.

      Parameters
      ----------
      point : Point3D
          Point to project onto the cylinder.

      Returns
      -------
      CylinderEvaluation
          Resulting evaluation.


   .. py:method:: get_u_parameterization() -> ansys.geometry.core.primitives.parameterization.Parameterization

      Get the parametrization conditions for the U parameter.

      The U parameter specifies the clockwise angle around the axis (right-hand
      corkscrew law), with a zero parameter at ``dir_x`` and a period of 2*pi.

      Returns
      -------
      Parameterization
          Information about how the cylinder's U parameter is parameterized.


   .. py:method:: get_v_parameterization() -> ansys.geometry.core.primitives.parameterization.Parameterization

      Get the parametrization conditions for the V parameter.

      The V parameter specifies the distance along the axis, with a zero parameter at
      the XY plane of the cylinder.

      Returns
      -------
      Parameterization
          Information about how the cylinders's V parameter is parameterized.



.. py:class:: CylinderEvaluation(cylinder: Cylinder, parameter: ansys.geometry.core.primitives.surface_evaluation.ParamUV)


   Bases: :py:obj:`ansys.geometry.core.primitives.surface_evaluation.SurfaceEvaluation`

   Provides evaluation of a cylinder at given parameters.

   Parameters
   ----------
   cylinder: ~ansys.geometry.core.primitives.cylinder.Cylinder
       Cylinder to evaluate.
   parameter: ParamUV
       Parameters (u, v) to evaluate the cylinder at.

   .. py:property:: cylinder
      :type: Cylinder

      Cylinder being evaluated.


   .. py:property:: parameter
      :type: ansys.geometry.core.primitives.surface_evaluation.ParamUV

      Parameter that the evaluation is based upon.


   .. py:method:: position() -> ansys.geometry.core.math.Point3D

      Position of the evaluation.

      Returns
      -------
      Point3D
          Point that lies on the cylinder at this evaluation.


   .. py:method:: normal() -> ansys.geometry.core.math.UnitVector3D

      Normal to the surface.

      Returns
      -------
      UnitVector3D
          Normal unit vector to the cylinder at this evaluation.


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
          Second derivative with respect to the U and v parameters.


   .. py:method:: vv_derivative() -> ansys.geometry.core.math.Vector3D

      Second derivative with respect to the V parameter.

      Returns
      -------
      Vector3D
          Second derivative with respect to the V parameter.


   .. py:method:: min_curvature() -> ansys.geometry.core.typing.Real

      Minimum curvature of the cylinder.

      Returns
      -------
      Real
          Minimum curvature of the cylinder.


   .. py:method:: min_curvature_direction() -> ansys.geometry.core.math.UnitVector3D

      Minimum curvature direction.

      Returns
      -------
      UnitVector3D
          Mminimum curvature direction.


   .. py:method:: max_curvature() -> ansys.geometry.core.typing.Real

      Maximum curvature of the cylinder.

      Returns
      -------
      Real
          Maximum curvature of the cylinder.


   .. py:method:: max_curvature_direction() -> ansys.geometry.core.math.UnitVector3D

      Maximum curvature direction.

      Returns
      -------
      UnitVector3D
          Maximum curvature direction.



