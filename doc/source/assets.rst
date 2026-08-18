Assets
######

In this section, users are able to download a set of assets related to PyAnsys Geometry.

Documentation
-------------

The following links provide users with downloadable documentation in various formats

.. jinja:: doc-assets

    * `Documentation in HTML format <{{ prefix_url }}/documentation-html.zip>`_
    * `Documentation in PDF format <{{ prefix_url }}/documentation-pdf.zip>`_

Wheelhouse
----------

If you lack an internet connection on your installation machine, you should install PyAnsys Geometry
by downloading the wheelhouse archive.

Each wheelhouse archive contains all the Python wheels necessary to install PyAnsys Geometry from scratch on Windows,
Linux, and MacOS from Python 3.12 to 3.14. You can install this on an isolated system with a fresh Python
installation or on a virtual environment.

For example, on Linux with Python 3.12, unzip the wheelhouse archive and install it with:

.. code:: bash

    unzip ansys_geometry_core-v0.17.0-all-wheelhouse-ubuntu-latest-3.12.zip wheelhouse
    pip install ansys-geometry-core -f wheelhouse --no-index --upgrade --ignore-installed

If you are on Windows with Python 3.12, unzip to a wheelhouse directory by running ``-d wheelhouse``
(this is required for unzipping to a directory on Windows) and install using the preceding command.

Consider installing using a `virtual environment <https://docs.python.org/3/library/venv.html>`_.

The following wheelhouse files are available for download:

.. jinja:: wheelhouse-assets

    {%- for os_name, download_links in assets.items() %}

    {{ os_name }}
    {{ "^" * os_name|length }}

    {%- for link in download_links %}
    * `{{ link.os }} wheelhouse for Python {{ link.python_versions }} <{{ link.prefix_url }}/ansys_geometry_core-{{ link.latest_released_version }}-all-wheelhouse-{{ link.runner }}-{{ link.python_versions }}.zip>`_
    {%- endfor %}

    {%- endfor %}

Geometry service Docker container assets
----------------------------------------

Build the latest Geometry service Docker container using the following assets. For
information on how to build the container, see :ref:`Docker containers <ref_docker>`.

The Geometry service backend can also be delivered as a Docker container. This is specially useful for
users who want to run the Geometry service on a containerized environment. The Geometry service Docker
container is available for both Windows and Linux.


Windows container
^^^^^^^^^^^^^^^^^

.. note::

   Only Ansys employees with access to
   https://github.com/ansys/pyansys-geometry-binaries can download these binaries.

* `Latest Geometry service binaries for Windows containers <https://github.com/ansys/pyansys-geometry-binaries>`_
* `Latest Geometry service Dockerfile for Windows containers <https://github.com/ansys/pyansys-geometry/releases/latest/download/windows-core-dockerfile.zip>`_

Linux container
^^^^^^^^^^^^^^^

.. note::

   Only Ansys employees with access to
   https://github.com/ansys/pyansys-geometry-binaries can download these binaries.

* `Latest Geometry service binaries for Linux containers <https://github.com/ansys/pyansys-geometry-binaries>`_
* `Latest Geometry service Dockerfile for Linux containers <https://github.com/ansys/pyansys-geometry/releases/latest/download/linux-core-dockerfile.zip>`_
