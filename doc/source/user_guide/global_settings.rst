.. _ref_global_settings:

===============
Global settings
===============

PyAnsys Geometry exposes a set of module-level boolean flags that control runtime
behavior. All flags live in the top-level :mod:`ansys.geometry.core` namespace and
can be toggled at any point during a Python session.

.. code:: python

    import ansys.geometry.core as pyansys_geometry

    # Inspect current value
    print(pyansys_geometry.ENABLE_RUNTIME_TYPECHECKING)

    # Toggle the flag
    pyansys_geometry.ENABLE_RUNTIME_TYPECHECKING = True


.. _ref_global_settings_overview:

Available flags
===============

The following table summarizes every flag, its default value, and its purpose.

.. list-table::
   :header-rows: 1
   :widths: 40 15 45

   * - Flag
     - Default
     - Purpose
   * - ``ENABLE_RUNTIME_TYPECHECKING``
     - ``False``
     - Enable runtime type checking for all public API methods and ``check_*`` helpers.
   * - ``USE_SERVICE_COLORS``
     - ``False``
     - Use the colors stored in the geometry service when plotting bodies and components.
   * - ``DISABLE_ACTIVE_DESIGN_CHECK``
     - ``False``
     - Skip the active-design guard that prevents operations on closed designs.
   * - ``USE_TRACKER_TO_UPDATE_DESIGN``
     - ``False``
     - Use the server-side tracker response to update the design after Boolean and combine
       operations instead of a full design refresh.


.. _ref_global_settings_runtime_typechecking:

``ENABLE_RUNTIME_TYPECHECKING``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, PyAnsys Geometry skips all runtime type validation to maximize performance.
Setting this flag to ``True`` activates two layers of checking:

1. **Decorator-based checking**: every public method decorated with ``@check_input_types``
   validates its arguments  using `beartype <https://beartype.readthedocs.io>`_,
   and raises a ``BeartypeCallHintParamViolation`` on a type mismatch.
2. **Helper-function checking**: all ``check_*`` helper functions (``check_type``,
   ``check_is_float_int``, and so on) execute their validation logic and raise ``TypeError``
   or ``ValueError`` on invalid inputs.

When the flag is ``False`` (default), both layers are bypassed entirely.

**When to enable it**

- During development and debugging to get immediate, descriptive type-error messages.
- In test suites that explicitly verify type-checking behavior.
- When integrating with external data sources where the input types are not guaranteed.

**When to leave it turned off (default)**

- In production workflows or performance-critical scripts where throughput matters.

.. code:: python

    import ansys.geometry.core as pyansys_geometry
    from ansys.geometry.core.math import Point3D
    from ansys.geometry.core.misc.checks import check_type

    # --- with runtime type checking turned off (default) ---
    check_type("not_a_point", Point3D)  # silently returns, no error raised

    # --- with runtime type checking enabled ---
    pyansys_geometry.ENABLE_RUNTIME_TYPECHECKING = True
    check_type("not_a_point", Point3D)  # raises TypeError


.. _ref_global_settings_use_service_colors:

``USE_SERVICE_COLORS``
~~~~~~~~~~~~~~~~~~~~~

When plotting bodies or components, PyAnsys Geometry can either use its own default
color cycle (fast, no server round-trip) or retrieve the exact colors stored for each
body in the geometry service.

Setting ``USE_SERVICE_COLORS = True`` enables the latter, causing the plotter to query
the service for per-body colors before rendering.

.. code:: python

    import ansys.geometry.core as pyansys_geometry

    pyansys_geometry.USE_SERVICE_COLORS = True

    # All subsequent plot() calls use service-side colors
    body.plot()
    component.plot()

.. note::

   Enabling service colors forces ``merge=False`` on every plot call, since individual
   body colors cannot be preserved after mesh merging. A performance warning is logged
   automatically when this combination is detected.


.. _ref_global_settings_disable_active_design_check:

``DISABLE_ACTIVE_DESIGN_CHECK``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every method that modifies the geometry model is guarded by an *active-design* check.
This guard verifies that the parent design has not been closed on the backend before
each operation, preventing cryptic gRPC errors.

In workflows where you are certain that all design objects remain valid for the lifetime
of your script (for example, inside a tightly controlled batch job), you can turn off
this check to eliminate its overhead.

.. warning::

   Only turn off this check if you are fully in control of the design lifecycle.
   Calling methods on objects that belong to a closed design results in
   unhandled gRPC errors.

.. code:: python

    import ansys.geometry.core as pyansys_geometry

    pyansys_geometry.DISABLE_ACTIVE_DESIGN_CHECK = True

    # Subsequent calls skip the active-design guard
    body.translate(direction, distance)


.. _ref_global_settings_use_tracker:

``USE_TRACKER_TO_UPDATE_DESIGN``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After boolean operations (``intersect``, ``subtract``, ``unite``), geometry commands and
combine operations, PyAnsys Geometry must synchronize the local design tree with the state
on the server. There are two strategies:

- **Full refresh** (default, ``False``): the entire design is re-fetched from the
  server and the local tree is rebuilt. This is the most robust approach.
- **Tracker-based update** (``True``): only the objects reported as changed by the
  server-side tracker are updated locally. This is faster for large assemblies, but
  requires server support.

.. note::

   The tracker-based approach relies on the Geometry service's ability to report which
   bodies and components were modified by an operation. Tracker support is only available
   in recent versions of the Geometry service (2026R1+).

.. code:: python

    import ansys.geometry.core as pyansys_geometry

    pyansys_geometry.USE_TRACKER_TO_UPDATE_DESIGN = True

    # Boolean operations now use incremental tracker updates
    body_a.subtract(body_b)
