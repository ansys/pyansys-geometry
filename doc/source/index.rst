PyAnsys Geometry documentation |version|
========================================

PyAnsys Geometry is a Python client library for the Ansys Geometry service.

.. grid:: 1 2 2 2
   :gutter: 4
   :padding: 2 2 0 0
   :class-container: sd-text-center

   .. grid-item-card:: Getting started
      :img-top: _static/assets/index_getting_started.png
      :class-card: intro-card

      Learn how to run the Windows Docker container, install the
      PyAnsys Geometry image, and launch and connect to the Geometry
      service.

      +++
      .. button-link:: getting_started/index.html
         :color: secondary
         :outline:
         :expand:
         :click-parent:

         Getting started

   .. grid-item-card::
      :img-top: _static/assets/index_user_guide.png

      User guide
      ^^^^^^^^^^

      Understand key concepts and approaches for primitives,
      sketches, and model designs.

      +++
      .. button-link:: user_guide/index.html
         :color: secondary
         :expand:
         :outline:
         :click-parent:

         User guide



.. jinja:: main_toctree

    .. grid:: 2
       :gutter: 2 2 3 3

       {% if build_api %}
       .. grid-item-card::
                :img-top: _static/assets/index_api.png

                API reference
                ^^^^^^^^^^^^^

                Understand PyAnsys Geometry API endpoints, their capabilities,
                and how to interact with them programmatically.

                +++
                .. button-link:: api/index.html
                   :color: secondary
                   :expand:
                   :outline:
                   :click-parent:

                      API reference
       {% endif %}

       {% if build_examples %}
       .. grid-item-card::
                :img-top: _static/assets/index_examples.png

                Examples
                ^^^^^^^^

                Explore examples that show how to use PyAnsys Geometry to
                perform many different types of operations.

                +++
                .. button-link:: examples.html
                   :color: secondary
                   :expand:
                   :outline:
                   :click-parent:

                      Examples
       {% endif %}

.. grid:: 2
    :gutter: 2 2 3 3

    .. grid-item-card::
            :img-top: _static/assets/index_contribute.png

            Contribute
            ^^^^^^^^^^
            Learn how to contribute to the PyAnsys Geometry codebase
            or documentation.

            +++
            .. button-link:: contributing.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  Contribute

    .. grid-item-card::
            :img-top: _static/assets/index_download.png

            Assets
            ^^^^^^
            Download different assets related to PyAnsys Geometry,
            such as documentation, package wheelhouse, and related files.

            +++
            .. button-link:: assets.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  Assets

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
