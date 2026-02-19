# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # PyAnsys Geometry 101: Math
#
# The ``math`` module is the foundation of PyAnsys Geometry. This module is built on top of
# [NumPy](https://numpy.org/), one of the most renowned mathematical Python libraries.
#
# This example shows some of the main PyAnsys Geometry math objects and demonstrates
# why they are important prior to doing more exciting things in PyAnsys Geometry.

# ## Perform required imports
#
# Perform the required imports.

# +
import numpy as np

from ansys.geometry.core.math import Plane, Point2D, Point3D, Vector2D, Vector3D, UnitVector3D
# -

# ## Create points and vectors
#
# Everything starts with ``Point`` and ``Vector`` objects, which can each be defined in a 2D or 3D form.
# These objects inherit from NumPy's ``ndarray``, providing them with enhanced functionalities.
# When creating these objects, you must remember to pass in the arguments as a list (that is, with brackets ``[ ]``).
#
# Create 2D and 3D point and vectors.
#
# ```
# Point3D([x, y, z])
# Point2D([x, y])
#
# Vector3D([x, y, z])
# Vector2D([x, y])
# ```
#
# You can perform standard mathematical operations on points and vectors.
#
# Perform some standard operations on vectors.

# +
vec_1 = Vector3D([1,0,0]) # x-vector
vec_2 = Vector3D([0,1,0]) # y-vector

print("Sum of vectors [1, 0, 0] + [0, 1, 0]:")
print(vec_1 + vec_2) # sum

print("\nDot product of vectors [1, 0, 0] * [0, 1, 0]:")
print(vec_1 * vec_2) # dot

print("\nCross product of vectors [1, 0, 0] % [0, 1, 0]:")
print(vec_1 % vec_2) # cross
# -

# Create a vector from two points.

# +
p1 = Point3D([12.4, 532.3, 89])
p2 = Point3D([-5.7, -67.4, 46.6])

vec_3 = Vector3D.from_points(p1, p2)
vec_3
# -

# Normalize a vector to create a unit vector, which is also
# known as a *direction*.

# +
print("Magnitude of vec_3:")
print(vec_3.magnitude)

print("\nNormalized vec_3:")
print(vec_3.normalize())

print("\nNew magnitude:")
print(vec_3.normalize().magnitude)
# -

# Use the ``UnitVector`` class to automatically normalize the input
# for the unit vector.

uv = UnitVector3D([1,1,1])
uv

# Perform a few more mathematical operations on vectors.

# +
v1 = Vector3D([1, 0, 0])
v2 = Vector3D([0, 1, 0])

print("Vectors are perpendicular:")
print(v1.is_perpendicular_to(v2))

print("\nVectors are parallel:")
print(v1.is_parallel_to(v2))

print("\nVectors are opposite:")
print(v1.is_opposite(v2))

print("\nAngle between vectors:")
print(v1.get_angle_between(v2))
print(f"{np.pi / 2} == pi/2")
# -

# ## Create planes
#
# Once you begin creating sketches and bodies, ``Plane`` objects become very important. A plane
# is defined by these items:
#
# - An origin, which consists of a 3D point
# - Two directions (``direction_x`` and ``direction_y``), which are both ``UnitVector3D``objects
#
# If no direction vectors are provided, the plane defaults to the XY plane.
#
# Create two planes.

# +
plane = Plane(Point3D([0,0,0])) # XY plane

print("(1, 2, 0) is in XY plane:")
print(plane.is_point_contained(Point3D([1, 2, 0]))) # True

print("\n(0, 0, 5) is in XY plane:")
print(plane.is_point_contained(Point3D([0, 0, 5]))) # False
# -

# ## Perform parametric evaluations
#
# PyAnsys Geometry implements parametric evaluations for some curves and surfaces.
#
# Evaluate a sphere.

# +
from ansys.geometry.core.shapes import Sphere, SphereEvaluation
from ansys.geometry.core.math import Point3D
from ansys.geometry.core.misc import Distance

sphere = Sphere(Point3D([0,0,0]), Distance(1)) # radius = 1

eval = sphere.project_point(Point3D([1,1,1]))

print("U Parameter:")
print(eval.parameter.u)

print("\nV Parameter:")
print(eval.parameter.v)
# -

print("Point on the sphere:")
eval.position

print("Normal to the surface of the sphere at the evaluation position:")
eval.normal
