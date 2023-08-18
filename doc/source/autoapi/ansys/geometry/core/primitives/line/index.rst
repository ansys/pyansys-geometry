


Module ``line``
===============



.. py:module:: ansys.geometry.core.primitives.line



Description
-----------

Provides for creating and managing a line.




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

   ansys.geometry.core.primitives.line.Line
   ansys.geometry.core.primitives.line.LineEvaluation




.. py:class:: Line(origin: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.Point3D], direction: beartype.typing.Union[numpy.ndarray, ansys.geometry.core.typing.RealSequence, ansys.geometry.core.math.UnitVector3D, ansys.geometry.core.math.Vector3D])


   Provides 3D line representation.

   Parameters
   ----------
   origin : Union[~numpy.ndarray, RealSequence, Point3D]
       Origin of the line.
   direction : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
       Direction of the line.

   .. py:property:: origin
      :type: ansys.geometry.core.math.Point3D

      Origin of the line.


   .. py:property:: direction
      :type: ansys.geometry.core.math.UnitVector3D

      Direction of the line.


   .. py:method:: __eq__(other: object) -> bool

      Equals operator for the ``Line`` class.


   .. py:method:: evaluate(parameter: float) -> LineEvaluation

      Evaluate the line at a given parameter.

      Parameters
      ----------
      parameter : Real
          Parameter to evaluate the line at.

      Returns
      -------
      LineEvaluation
          Resulting evaluation.


   .. py:method:: transformed_copy(matrix: ansys.geometry.core.math.Matrix44) -> Line

      Create a transformed copy of the line based on a transformation matrix.

      Parameters
      ----------
      matrix : Matrix44
          4X4 transformation matrix to apply to the line.

      Returns
      -------
      Line
         New line that is the transformed copy of the original line.


   .. py:method:: project_point(point: ansys.geometry.core.math.Point3D) -> LineEvaluation

      Project a point onto the line and evaluate the line.

      Parameters
      ----------
      point : Point3D
          Point to project onto the line.

      Returns
      -------
      LineEvaluation
          Resulting evaluation.


   .. py:method:: is_coincident_line(other: Line) -> bool

      Determine if the line is coincident with another line.

      Parameters
      ----------
      other : Line
          Line to determine coincidence with.

      Returns
      -------
      bool
          ``True`` if the line is coincident with another line, ``False`` otherwise.


   .. py:method:: is_opposite_line(other: Line) -> bool

      Determine if the line is opposite another line.

      Parameters
      ----------
      other : Line
          Line to determine opposition with.

      Returns
      -------
      bool
          ``True`` if the line is opposite to another line.


   .. py:method:: get_parameterization() -> ansys.geometry.core.primitives.parameterization.Parameterization

      Get the parametrization of the line.

      The parameter of a line specifies the distance from the `origin` in the
      direction of `direction`.

      Returns
      -------
      Parameterization
          Information about how the line is parameterized.



.. py:class:: LineEvaluation(line: Line, parameter: float = None)


   Bases: :py:obj:`ansys.geometry.core.primitives.curve_evaluation.CurveEvaluation`

   Evaluate a line.

   .. py:property:: line
      :type: Line

      Line being evaluated.


   .. py:property:: parameter
      :type: float

      Parameter that the evaluation is based upon.


   .. py:method:: position() -> ansys.geometry.core.math.Point3D

      Position of the evaluation.

      Returns
      -------
      Point3D
          Point that lies on the line at this evaluation.


   .. py:method:: tangent() -> ansys.geometry.core.math.UnitVector3D

      Tangent of the evaluation, which is always equal to the direction of the line.

      Returns
      -------
      UnitVector3D
          Tangent unit vector to the line at this evaluation.


   .. py:method:: first_derivative() -> ansys.geometry.core.math.Vector3D

      First derivative of the evaluation.

      The first derivative is always equal to the direction of the line.

      Returns
      -------
      Vector3D
          First derivative of the evaluation.


   .. py:method:: second_derivative() -> ansys.geometry.core.math.Vector3D

      Second derivative of the evaluation.

      The second derivative is always equal to a zero vector ``Vector3D([0, 0, 0])``.

      Returns
      -------
      Vector3D
          Second derivative of the evaluation, which is always ``Vector3D([0, 0, 0])``.


   .. py:method:: curvature() -> float

      Curvature of the line, which is always ``0``.

      Returns
      -------
      Real
          Curvature of the line, which is always ``0``.



