# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # PyAnsys Geometry 101: Units
#
# To handle units inside the source code, PyAnsys Geometry uses [Pint](https://pint.readthedocs.io/en/stable/),
# a third-party open source software that other PyAnsys libraries also use.
#
# The following code examples show how to operate with units inside
# the PyAnsys Geometry codebase and create objects with different units.

# ## Import units handler
#
# The following line of code imports the units handler: ``pint.util.UnitRegistry``.
# For more information on the ``UnitRegistry`` class in the ``pint`` API, see
# [Most important classes](https://pint.readthedocs.io/en/stable/api/base.html#most-important-classes)
# in the Pint documentation.

from ansys.geometry.core.misc import UNITS


# ## Create and work with ``Quantity`` objects
#
# With the ``UnitRegistry`` object called ``UNITS``, you can create ``Quantity``
# objects. A ``Quantity`` object is simply a container class with two core elements:
#
# - A number
# - A unit
#
# ``Quantity`` objects have convenience methods, including those for transforming to
# different units and comparing magnitudes, values, and units. For more information on the
# ``Quantity`` class in the ``pint`` API, see
# [Most important classes](https://pint.readthedocs.io/en/stable/api/base.html#most-important-classes)
# in the Pint documentation. You can also step through this
# [Pint tutorial](https://pint.readthedocs.io/en/stable/getting/tutorial.html).

# +
from pint import Quantity

a = Quantity(10, UNITS.mm)

print(f"Object a is a pint.Quantity: {a}")

print("Request its magnitude in different ways (accessor methods):")
print(f"Magnitude: {a.m}.")
print(f"Also magnitude: {a.magnitude}.")

print("Request its units in different ways (accessor methods):")
print(f"Units: {a.u}.")
print(f"Also units: {a.units}.")

# Quantities can be compared between different units
# You can also build Quantity objects as follows:
a2 = 10 * UNITS.mm
print(f"Compare quantities built differently: {a == a2}")

# Quantities can be compared between different units
a2_diff_units = 1 * UNITS.cm
print(f"Compare quantities with different units: {a == a2_diff_units}")
# -

# PyAnsys Geometry objects work by returning ``Quantity`` objects whenever the
# property requested has a physical meaning.
#
# Return ``Quantity`` objects for ``Point3D`` objects.

# +
from ansys.geometry.core.math import Point3D

point_a = Point3D([1,2,4])
print("========================= Point3D([1,2,4]) ========================")
print(f"Point3D is a numpy.ndarray in SI units: {point_a}.")
print(f"However, request each of the coordinates individually...\n")
print(f"X Coordinate: {point_a.x}")
print(f"Y Coordinate: {point_a.y}")
print(f"Z Coordinate: {point_a.z}\n")

# Now, store the information with different units...
point_a_km = Point3D([1,2,4], unit=UNITS.km)
print("================= Point3D([1,2,4], unit=UNITS.km) =================")
print(f"Point3D is a numpy.ndarray in SI units: {point_a_km}.")
print(f"However, request each of the coordinates individually...\n")
print(f"X Coordinate: {point_a_km.x}")
print(f"Y Coordinate: {point_a_km.y}")
print(f"Z Coordinate: {point_a_km.z}\n")

# These points, although they are in different units, can be added together.
res = point_a + point_a_km

print("=================== res = point_a + point_a_km ====================")
print(f"numpy.ndarray: {res}")
print(f"X Coordinate: {res.x}")
print(f"Y Coordinate: {res.y}")
print(f"Z Coordinate: {res.z}")
# -

# ## Use default units
#
# PyAnsys Geometry implements the concept of *default units*.

# +
from ansys.geometry.core.misc import DEFAULT_UNITS

print("=== Default unit length ===")
print(DEFAULT_UNITS.LENGTH)

print("=== Default unit angle ===")
print(DEFAULT_UNITS.ANGLE)
# -

# It is important to differentiate between *client-side* default units
# and *server-side* default units. You are able to control both of them.
#
# Print the default server unit length.

print("=== Default server unit length ===")
print(DEFAULT_UNITS.SERVER_LENGTH)

# Use default units.

# +
from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import DEFAULT_UNITS

DEFAULT_UNITS.LENGTH = UNITS.mm

point_2d_default_units = Point2D([3, 4])
print("This is a Point2D with default units")
print(f"X Coordinate: {point_2d_default_units.x}")
print(f"Y Coordinate: {point_2d_default_units.y}")
print(f"numpy.ndarray value: {point_2d_default_units}")

# Revert back to original default units
DEFAULT_UNITS.LENGTH = UNITS.m
# -

# PyAnsys Geometry has certain auxiliary classes implemented that provide proper
# unit checking when assigning values. Although they are basically intended for
# internal use of the library, you can define them for use.

from ansys.geometry.core.misc import Angle, Distance

# Start with ``Distance``. The main difference between a ``Quantity`` object
# (that is, ``from pint import Quantity``) and a ``Distance`` is that there
# is an active check on the units passed (in case they are not the default ones).
# Here are some examples.

# +
radius = Distance(4)
print(f"The radius is {radius.value}.")

# Reassign the value of the distance
radius.value = 7 * UNITS.cm
print(f"After reassignment, the radius is {radius.value}.")


# Change the units if desired
radius.unit = UNITS.cm
print(f"After changing its units, the radius is {radius.value}.")
# -

# The next two code examples show how unreasonable operations raise errors.

try:
    radius.value = 3 * UNITS.degrees
except TypeError as err:
    print(f"Error raised: {err}")

try:
    radius.unit = UNITS.fahrenheit
except TypeError as err:
    print(f"Error raised: {err}")

# The same behavior applies to the ``Angle`` object. Here are some examples.

# +
import numpy as np

rotation_angle = Angle(np.pi / 2)
print(f"The rotation angle is {rotation_angle.value}.")

# Try reassigning the value of the distance
rotation_angle.value = 7 * UNITS.degrees
print(f"After reassignment, the rotation angle is {rotation_angle.value}.")

# You could also change its units if desired
rotation_angle.unit = UNITS.degrees
print(f"After changing its units, the rotation angle is {rotation_angle.value}.")
