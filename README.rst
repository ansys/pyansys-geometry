PyAnsys Geometry
================
|pyansys| |python| |pypi| |downloads| |GH-CI| |codecov| |MIT| |black| |pre-commit|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-geometry-core?logo=pypi
   :target: https://pypi.org/project/ansys-geometry-core/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-geometry-core.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-geometry-core
   :alt: PyPI

.. |downloads| image:: https://img.shields.io/pypi/dm/ansys-geometry-core.svg
   :target: https://pypi.org/project/ansys-geometry-core/
   :alt: PyPI Downloads

.. |codecov| image:: https://codecov.io/gh/ansys/pyansys-geometry/graph/badge.svg?token=UZIC7XT5WE
   :target: https://codecov.io/gh/ansys/pyansys-geometry
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/pyansys-geometry/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/pyansys-geometry/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/blog/license/mit
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black

.. |pre-commit| image:: https://results.pre-commit.ci/badge/github/ansys/pyansys-geometry/main.svg
   :target: https://results.pre-commit.ci/latest/github/ansys/pyansys-geometry/main
   :alt: pre-commit.ci

.. contents::

Overview
--------

PyAnsys Geometry is a Python client library for the Ansys Geometry service, as well as other CAD Ansys products
such as Ansys Discovery and Ansys SpaceClaim.

Installation
^^^^^^^^^^^^
You can use `pip <https://pypi.org/project/pip/>`_ to install PyAnsys Geometry.

.. code:: bash

    pip install ansys-geometry-core

To install the latest development version, run these commands:

.. code:: bash

   git clone https://github.com/ansys/pyansys-geometry
   cd pyansys-geometry
   pip install -e .

For more information, see `Getting Started`_.

Basic usage
^^^^^^^^^^^

This code shows how to import PyAnsys Geometry and use some basic capabilities:

.. code:: python

   from ansys.geometry.core import launch_modeler
   from ansys.geometry.core.designer import DesignFileFormat
   from ansys.geometry.core.math import Plane, Point3D, Point2D
   from ansys.geometry.core.misc import UNITS, Distance
   from ansys.geometry.core.sketch import Sketch

   # Define a sketch
   origin = Point3D([0, 0, 10])
   plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])

   # Create a sketch
   sketch = Sketch(plane)
   sketch.circle(Point2D([1, 1]), 30 * UNITS.m)
   sketch.plot()

   # Start a modeler session
   modeler = launch_modeler()

   # Create a design
   design = modeler.create_design("ModelingDemo")

   # Create a body directly on the design by extruding the sketch
   body = design.extrude_sketch(
       name="CylinderBody", sketch=sketch, distance=Distance(80, unit=UNITS.m)
   )

   # Plot the body
   design.plot()

   # Download the model
   design.download(file_location="file.scdocx", format=DesignFileFormat.SCDOCX)

For comprehensive usage information, see `Examples`_ in the `PyAnsys Geometry documentation`_.

Documentation and issues
^^^^^^^^^^^^^^^^^^^^^^^^
Documentation for the latest stable release of PyAnsys Geometry is hosted at `PyAnsys Geometry documentation`_.

In the upper right corner of the documentation's title bar, there is an option for switching from
viewing the documentation for the latest stable release to viewing the documentation for the
development version or previously released versions.

On the `PyAnsys Geometry Issues <https://github.com/ansys/pyansys-geometry/issues>`_ page,
you can create issues to report bugs and request new features. On the `PyAnsys Geometry Discussions
<https://github.com/ansys/pyansys-geometry/discussions>`_ page or the `Discussions <https://discuss.ansys.com/>`_
page on the Ansys Developer portal, you can post questions, share ideas, and get community feedback.

To reach the project support team, email `pyansys.core@ansys.com <mailto:pyansys.core@ansys.com>`_.


.. LINKS AND REFERENCES
.. _Getting Started: https://geometry.docs.pyansys.com/version/stable/getting_started/index.html
.. _Examples: https://geometry.docs.pyansys.com/version/stable/examples.html
.. _PyAnsys Geometry documentation: https://geometry.docs.pyansys.com/version/stable/index.html
