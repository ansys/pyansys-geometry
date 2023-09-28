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

What Ansys license do I need to run the Geometry service?
---------------------------------------------------------

.. note::

   Answered in https://github.com/ansys/pyansys-geometry/discussions/754

The Ansys Geometry service is a headless service developed on top of the
modelling libraries underneath Discovery and SpaceClaim.

Both in its standalone and dockerized versions, the Ansys Geometry Service
requires a **Discovery Modeling** license to run.

In order to run PyAnsys Geometry against other backends, such as Discovery
or SpaceClaim, users will need an Ansys license that allows them to run these
Ansys products.

The **Discovery Modeling** license is one of these licenses, but there are others
such as the Ansys Mechanical Enterprise license that would also allow users to run
these Ansys products. However, the Geometry service is not compatible with any other
license.

.. button-ref:: index
    :ref-type: doc
    :color: primary
    :shadow:
    :expand:

    Go to Getting started
