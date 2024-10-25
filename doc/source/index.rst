.. title:: PyAnsys Geometry

.. figure:: _static/logo/logo.png
    :align: center
    :width: 640px

PyAnsys Geometry is a Python client library for the Ansys Geometry service. You are looking at the documentation for version |version|.

.. grid:: 1 2 3 3
    :gutter: 1 2 3 3
    :padding: 1 2 3 3

    .. grid-item-card:: Getting started :fa:`person-running`
        :link: getting_started/index
        :link-type: doc

        Learn how to run the Windows Docker container, install the
        PyAnsys Geometry image, and launch and connect to the Geometry
        service.

    .. grid-item-card:: User guide :fa:`book-open-reader`
        :link: user_guide/index
        :link-type: doc

        Understand key concepts and approaches for primitives,
        sketches, and model designs.

    .. jinja:: main_toctree

        {% if build_api %}
        .. grid-item-card:: API reference :fa:`book-bookmark`
            :link: api/index
            :link-type: doc

            Understand PyAnsys Geometry API endpoints, their capabilities,
            and how to interact with them programmatically.
        {% endif %}

        {% if build_examples %}
        .. grid-item-card:: Examples :fa:`scroll`
            :link: examples
            :link-type: doc

            Explore examples that show how to use PyAnsys Geometry to
            perform many different types of operations.
        {% endif %}

    .. grid-item-card:: Contribute :fa:`people-group`
        :link: contributing
        :link-type: doc

        Learn how to contribute to the PyAnsys Geometry codebase
        or documentation.

    .. grid-item-card:: Assets :fa:`download`
        :link: assets
        :link-type: doc

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
       changelog
