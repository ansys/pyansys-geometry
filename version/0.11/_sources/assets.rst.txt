Assets
######

In this section, users are able to download a set of assets related to PyAnsys Geometry.

Documentation
-------------

The following links provide users with downloadable documentation in various formats

* `Documentation in HTML format <_static/assets/download/documentation-html.zip>`_
* `Documentation in PDF format <_static/assets/download/ansys-geometry-core.pdf>`_

Wheelhouse
----------

If you lack an internet connection on your installation machine, you should install PyAnsys Geometry
by downloading the wheelhouse archive.

Each wheelhouse archive contains all the Python wheels necessary to install PyAnsys Geometry from scratch on Windows,
Linux, and MacOS from Python 3.10 to 3.13. You can install this on an isolated system with a fresh Python
installation or on a virtual environment.

For example, on Linux with Python 3.10, unzip the wheelhouse archive and install it with:

.. code:: bash

    unzip ansys-geometry-core-v0.11.0-all-wheelhouse-ubuntu-latest-3.10.zip wheelhouse
    pip install ansys-geometry-core -f wheelhouse --no-index --upgrade --ignore-installed

If you are on Windows with Python 3.10, unzip to a wheelhouse directory by running ``-d wheelhouse``
(this is required for unzipping to a directory on Windows) and install using the preceding command.

Consider installing using a `virtual environment <https://docs.python.org/3/library/venv.html>`_.

The following wheelhouse files are available for download:

.. jinja:: wheelhouse-assets

    {%- for os_name, download_links in assets.items() %}

    {{ os_name }}
    {{ "^" * os_name|length }}

    {%- for link in download_links %}
    * `{{ link.os }} wheelhouse for Python {{ link.python_versions }} <{{ link.prefix_url }}/ansys-geometry-core-{{ link.latest_released_version }}-all-wheelhouse-{{ link.runner }}-{{ link.python_versions }}.zip>`_
    {%- endfor %}

    {%- endfor %}

Geometry service Docker container assets
----------------------------------------

Build the latest Geometry service Docker container using the following assets. For
information on how to build the container, see :ref:`Docker containers <ref_docker>`.

Currently, the Geometry service backend is mainly delivered as a **Windows** Docker container.
However, these containers require a Windows machine to run them.

.. A Linux version of the Geometry service is also available but with limited capabilities,
.. meaning that certain operations are not available or fail.


Windows container
^^^^^^^^^^^^^^^^^

.. note::

   Only Ansys employees with access to
   https://github.com/ansys/pyansys-geometry-binaries can download these binaries.

* `Latest Geometry service binaries for Windows containers <https://github.com/ansys/pyansys-geometry-binaries>`_
* `Latest Geometry service Dockerfile for Windows containers <https://github.com/ansys/pyansys-geometry/releases/latest/download/windows-core-dockerfile.zip>`_

.. Linux container
.. ^^^^^^^^^^^^^^^

.. .. note::

..    Only users with access to https://github.com/ansys/pyansys-geometry-binaries can download these binaries.

.. * `Latest Geometry service binaries for Linux containers <https://github.com/ansys/pyansys-geometry-binaries>`_
.. * `Latest Geometry service Dockerfile for Linux containers <https://github.com/ansys/pyansys-geometry/releases/latest/download/linux-dockerfile.zip>`_
