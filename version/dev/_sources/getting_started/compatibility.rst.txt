
.. _ref_ansys_comp:

Ansys version compatibility
===========================

The following table summarizes the compatibility matrix between the PyAnsys Geometry service
and the Ansys product versions.

+---------------------------+------------------------+-------------------------------+-------------------------------+------------------------------+------------------------------+
| PyAnsys Geometry versions | Ansys Product versions | Geometry Service (dockerized) | Geometry Service (standalone) |          Discovery           |          SpaceClaim          |
+===========================+========================+===============================+===============================+==============================+==============================+
|         ``0.2.X``         |          23R2          | :octicon:`check-circle-fill`  | :octicon:`check-circle-fill`  |      :octicon:`x-circle`     | :octicon:`check-circle-fill` |
+---------------------------+------------------------+-------------------------------+-------------------------------+------------------------------+------------------------------+
|         ``0.3.X``         |    23R2 (partially)    | :octicon:`check-circle-fill`  | :octicon:`check-circle-fill`  |      :octicon:`x-circle`     | :octicon:`check-circle-fill` |
+---------------------------+------------------------+-------------------------------+-------------------------------+------------------------------+------------------------------+
|         ``0.4.X``         |      24R1 onward       | :octicon:`check-circle-fill`  | :octicon:`check-circle-fill`  | :octicon:`check-circle-fill` | :octicon:`check-circle-fill` |
+---------------------------+------------------------+-------------------------------+-------------------------------+------------------------------+------------------------------+
|         ``0.5.X``         |      24R1 onward       | :octicon:`check-circle-fill`  | :octicon:`check-circle-fill`  | :octicon:`check-circle-fill` | :octicon:`check-circle-fill` |
+---------------------------+------------------------+-------------------------------+-------------------------------+------------------------------+------------------------------+

.. tip:: Forth- and back-compatibility mechanism

    Starting on version ``0.5.X`` and onward, PyAnsys Geometry has implemented a forth- and back-compatibility mechanism to
    ensure that the Python library can be used with different versions of the Ansys products.

    Methods are now decorated with the ``@min_backend_version`` decorator to indicate the compatibility with the Ansys product versions.
    If an unsupported method is called, a ``GeometryRuntimeError`` is raised when attempting to use the method. Users are informed of the
    minimum Ansys product version required to use the method.


Access to the documentation for the preceding versions is found at the `Versions <https://geometry.docs.pyansys.com/version/index.html>`_ page.

.. button-ref:: index
    :ref-type: doc
    :color: primary
    :shadow:
    :expand:

    Go to Getting started
