.. _ref_faq:

Frequently asked questions
==========================

What is PyAnsys?
----------------
PyAnsys is a set of open source Python libraries that allow you to interface
with Ansys Electronics Desktop (AEDT), Ansys Mechanical, Ansys Parametric
Design Language (APDL), Ansys Fluent, and other Ansys products.

You can use PyAnsys libraries within a Python environment of your choice
in conjunction with external Python libraries.

How is the Ansys Geometry Service installed?
--------------------------------------------

.. note::

   This question is answered in https://github.com/ansys/pyansys-geometry/issues/1022 and
   https://github.com/ansys/pyansys-geometry/discussions/883

The Ansys Geometry service is available as a standalone service and it is installed
through the Ansys unified installer or the automated installer. Both are available
for download from the `Ansys Customer Portal <https://download.ansys.com/>`_.

When using the unified or automated installer, it is necessary to pass in the
``-geometryservice`` flag to install it.

Overall, the command to install the Ansys Geometry service with the unified installer is:

.. code-block:: bash

   setup.exe -silent -geometryservice

You can verify that the installation was successful by checking whether the
product has been installed on your file directory. If you are using the default
installation directory, the product is installed in the following directory:

.. code-block:: bash

   C:\Program Files\ANSYS Inc\vXXX\GeometryService

Where ``vXXX`` is the Ansys version that you have installed.

What Ansys license is needed to run the Geometry service?
---------------------------------------------------------

.. note::

   This question is answered in https://github.com/ansys/pyansys-geometry/discussions/754.

The Ansys Geometry service is a headless service developed on top of the
modeling libraries for Discovery and SpaceClaim.

Both in its standalone and Docker versions, the Ansys Geometry service
requires a **Discovery Modeling** license to run.

To run PyAnsys Geometry against other backends, such as Discovery
or SpaceClaim, users must have an Ansys license that allows them to run these
Ansys products.

The **Discovery Modeling** license is one of these licenses, but there are others,
such as the Ansys Mechanical Enterprise license, that also allow users to run
these Ansys products. However, the Geometry service is only compatible with
the **Discovery Modeling** license.

How to build the Docker image for the Ansys Geometry service?
-------------------------------------------------------------

.. note::

   This question is answered in https://github.com/ansys/pyansys-geometry/discussions/883

To build your own Docker image for the Ansys Geometry service, users should follow
the instructions provided in :ref:`ref_build_windows_docker_image_from_ansys_installation`. The
resulting image is a Windows-based Docker image that contains the Ansys Geometry
service.

How to access design objects in the design tree?
------------------------------------------------------

Design objects should not be stored in variables. Instead, they should be accessed through the
design tree. For example, if you have a design component called ``Design_Component``, you can
access it through the design tree as follows:

.. code-block:: python

   design.components[0]

This is strongly advised over storing the design component in a variable, such as:

.. code-block:: python

   comp = design.components[0]

Storing design objects in variables can lead to issues when the design tree is modified, such as
when new components are added or existing components are deleted. Accessing design objects through
the design tree ensures that you are always working with the most up-to-date version of the design.

.. button-ref:: index
    :ref-type: doc
    :color: primary
    :shadow:
    :expand:

    Go to Getting started