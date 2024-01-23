PyAnsys Geometry documentation |version|
========================================

PyAnsys Geometry is a Python client library for the Ansys Geometry service.

.. grid:: 1 2 2 2
   :gutter: 4
   :padding: 2 2 0 0
   :class-container: sd-text-center

   .. grid-item-card:: :material-regular:`directions_run` Getting started

      Learn how to run the Windows Docker container, install the
      PyAnsys Geometry image, and launch and connect to the Geometry
      service.

   .. grid-item-card:: :material-regular:`book` User guide

      Understand key concepts and approaches for primitives,
      sketches, and model designs.


.. jinja:: main_toctree

   .. grid:: 1 2 2 2
      :gutter: 4
      :padding: 2 2 0 0
      :class-container: sd-text-center

       {% if build_api %}
      .. grid-item-card:: :material-regular:`code` API reference


         Understand PyAnsys Geometry API endpoints, their capabilities,
         and how to interact with them programmatically.

       {% endif %}

       {% if build_examples %}
      .. grid-item-card:: :material-regular:`terminal` Examples
         :class-card: intro-card

         Explore examples that show how to use PyAnsys Geometry to
         perform many different types of operations.

       {% endif %}

.. grid:: 1 2 2 2
   :gutter: 4
   :padding: 2 2 0 0
   :class-container: sd-text-center

   .. grid-item-card:: :material-regular:`diversity_3` Contribute

      Learn how to contribute to the PyAnsys Geometry codebase
      or documentation.

   .. grid-item-card:: :material-regular:`download` Assets

      Download different assets related to PyAnsys Geometry,
      such as documentation, package wheelhouse, and related files.


.. jinja:: main_toctree

    .. toctree::
       :hidden:
       :maxdepth: 3

       getting_started/index
       user_guide/index
       {% if build_api %}
       api/index
       {% endif %}
       {% if build_examples %}
       examples
       {% endif %}
       contributing
       assets
