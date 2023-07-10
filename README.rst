PyGeometry
==========
|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-geometry-core?logo=pypi
   :target: https://pypi.org/project/ansys-geometry-core/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-geometry-core.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-geometry-core
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/ansys/ansys-geometry-core/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/pygeometry
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/pygeometry/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/pygeometry/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black


PyGeometry is a Python client library for the Ansys Geometry service.

.. contents::

Usage
-----

There are two different ways of getting started with the Geometry service and its client-library, PyGeometry.

Using PyGeometry launcher
^^^^^^^^^^^^^^^^^^^^^^^^^

PyGeometry is provided with an internal launcher that is capable of handling the specifics of
launching the Geometry service locally. The only requirements are that:

* Docker is installed on your machine.
* You have access to the PyAnsys GitHub container registry, where the Geometry service image is hosted.

.. caution::

   The Geometry service is currently available only as a Windows Docker image. The development
   team is working on getting the Linux Docker container available as soon as possible. In the meantime,
   make sure that your Docker engine is configured to run Windows Docker images.

First, bear in mind that you have to be `authenticated to ghcr.io
<https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry>`_.
Once authenticated, please proceed to download the Geometry service Docker image:

.. code:: bash

   docker pull ghcr.io/ansys/geometry:<tag>

The following OS-dependent tags are available:

* ``windows-latest``
* ``windows-latest-unstable``
* ``linux-latest``
* ``linux-latest-unstable``

Next, you will be ready to run the Geometry service directly from PyGeometry:

.. code:: python

   from ansys.geometry.core.connection import launch_modeler

   modeler = launch_modeler()

The previous ``launch_modeler()`` method will launch the Geometry service under the default
conditions. For more configurability, please use ``launch_local_modeler()``.

Manual service launch
^^^^^^^^^^^^^^^^^^^^^

First, start the Geometry service locally. If you have Docker installed and have
`authenticated to ghcr.io`_, you can start the service locally using Docker with:

.. code:: bash

   docker run --name ans_geo -e LICENSE_SERVER=<LICENSE-SERVER> -p 50051:50051 ghcr.io/ansys/geometry:<TAG>

The Geometry service has a set of environment variables that are **mandatory**:

* ``LICENSE_SERVER``: the license server (IP, DNS) to which the Geometry service shall connect. For example, ``127.0.0.1``.

Other optional environment variables are:

* ``ENABLE_TRACE``: whether to set up the trace level for debugging purposes. Expects either ``1`` or ``0``.
  By default, ``0`` (which means it is not activated).
* ``LOG_LEVEL``: sets the Geometry service logging level. By default, ``2``.

Next, connect to the service with:

.. code:: python

   from ansys.geometry.core import Modeler

   modeler = Modeler()

By default ``Modeler`` connects to ``127.0.0.1`` (``'localhost'``) on
port ``50051``. You can change this by modifying the ``host`` and ``port``
parameters of ``Modeler``, but note that you must also modify
your ``docker run`` command by changing ``<HOST-PORT>:50051``.

If you want to change the defaults, modify the following environment variables:

**On Linux/Mac OS**

.. code::

   export ANSRV_GEO_HOST=127.0.0.1
   export ANSRV_GEO_PORT=50051

**On Windows Powershell**

.. code::

   $env:ANSRV_GEO_HOST="127.0.0.1"
   $env:ANSRV_GEO_PORT=50051

**On Windows CMD**

.. code::

   SET ANSRV_GEO_HOST=127.0.0.1
   SET ANSRV_GEO_PORT=50051


Install the package
-------------------

PyGeometry has three installation modes: user, developer, and offline.

Install in user mode
^^^^^^^^^^^^^^^^^^^^

Before installing PyGeometry in user mode, make sure you have the latest version of
`pip`_ with:

.. code:: bash

   python -m pip install -U pip

Then, install PyGeometry with:

.. code:: bash

   python -m pip install ansys-geometry-core

.. caution::

    PyGeometry is currently hosted in a private PyPI repository. You must provide the index
    URL to the private PyPI repository:

    * Index URL: ``https://pkgs.dev.azure.com/pyansys/_packaging/pyansys/pypi/simple/``

    If access to this package registry is needed, email `pyansys.core@ansys.com <mailto:pyansys.core@ansys.com>`_
    to request access. The PyAnsys team can provide you a read-only token to be inserted in ``${PRIVATE_PYPI_ACCESS_TOKEN}``.
    Once you have it, run the following command:

    .. code:: bash

        pip install ansys-geometry-core --index-url=https://${PRIVATE_PYPI_ACCESS_TOKEN}@pkgs.dev.azure.com/pyansys/_packaging/pyansys/pypi/simple/

Install in developer mode
^^^^^^^^^^^^^^^^^^^^^^^^^

Installing PyGeometry in developer mode allows
you to modify the source and enhance it.

.. note::

    Before contributing to the project, ensure that you are thoroughly familiar
    with the `PyAnsys Developer's Guide`_.

To install PyGeometry in developer mode, perform these steps:

#. Clone the ``pygeometry`` repository:

   .. code:: bash

      git clone https://github.com/ansys/pygeometry

#. Access the ``pygeometry`` directory where the repository has been cloned:

   .. code:: bash

      cd pygeometry

#. Create a clean Python virtual environment and activate it:

   .. code:: bash

      # Create a virtual environment
      python -m venv .venv

      # Activate it in a POSIX system
      source .venv/bin/activate

      # Activate it in Windows CMD environment
      .venv\Scripts\activate.bat

      # Activate it in Windows Powershell
      .venv\Scripts\Activate.ps1

#. Make sure you have the latest required build system tools:

   .. code:: bash

      python -m pip install -U pip tox

#. Install the project in editable mode:

   .. code:: bash

      # Install the minimum requirements
      python -m pip install -e .

      # Install the minimum + tests requirements
      python -m pip install -e .[tests]

      # Install the minimum + doc requirements
      python -m pip install -e .[doc]

      # Install all requirements
      python -m pip install -e .[tests,doc]

Install in offline mode
^^^^^^^^^^^^^^^^^^^^^^^

If you lack an internet connection on your installation machine (or you do not have access to the
private Ansys PyPI packages repository), you should install PyGeometry by downloading the wheelhouse
archive from the `Releases Page <https://github.com/ansys/pygeometry/releases>`_ for your
corresponding machine architecture.

Each wheelhouse archive contains all the Python wheels necessary to install PyGeometry from scratch on Windows,
Linux, and MacOS from Python 3.8 to 3.11. You can install this on an isolated system with a fresh Python
installation or on a virtual environment.

For example, on Linux with Python 3.8, unzip the wheelhouse archive and install it with:

.. code:: bash

    unzip ansys-geometry-core-v0.2.10-wheelhouse-Linux-3.8.zip wheelhouse
    pip install ansys-geometry-core -f wheelhouse --no-index --upgrade --ignore-installed

If you're on Windows with Python 3.9, unzip to a wheelhouse directory and install using the preceding command.

Consider installing using a `virtual environment <https://docs.python.org/3/library/venv.html>`_.

Testing
-------

This project takes advantage of `tox`_. This tool automate common
development tasks (similar to Makefile), but it is oriented towards Python
development.

Using ``tox``
^^^^^^^^^^^^^

While Makefile has rules, `tox`_ has environments. In fact, ``tox`` creates its
own virtual environment so that anything being tested is isolated from the project
to guarantee the project's integrity.

The following environments commands are provided:

- **tox -e style**: Checks for coding style quality.
- **tox -e py**: Checks for unit tests.
- **tox -e py-coverage**: Checks for unit testing and code coverage.
- **tox -e doc**: Checks for documentation building process.

 .. admonition:: pyvista-pytest plugin

   This plugin facilitates the comparison of the images produced in PyGeometry for testing the plots.
   If you are changing the images, use flag ``--reset_image_cache`` which is not recommended except
   for testing or for potentially a major or minor release. For more information, see `pyvista-pytest`_.

Raw testing
^^^^^^^^^^^

If required, from the command line, you can call style commands, including
`black`_, `isort`_, and `flake8`_, and unit testing commands like `pytest`_.
However, this does not guarantee that your project is being tested in an isolated
environment, which is the reason why tools like `tox`_ exist.


Using ``pre-commit``
^^^^^^^^^^^^^^^^^^^^

The style checks take advantage of `pre-commit`_. Developers are not forced but
encouraged to install this tool with:

.. code:: bash

    python -m pip install pre-commit && pre-commit install


Documentation
-------------

For building documentation, you can run the usual rules provided in the
`Sphinx`_ Makefile, such as:

.. code:: bash

    make -C doc/ html && your_browser_name doc/html/index.html

However, the recommended way of checking documentation integrity is to use
``tox``:

.. code:: bash

    tox -e doc && your_browser_name .tox/doc_out/index.html


Distributing
------------

If you would like to create either source or wheel files, start by installing
the building requirements and then executing the build module:

.. code:: bash

    python -m pip install -U pip
    python -m build
    python -m twine check dist/*


.. LINKS AND REFERENCES
.. _black: https://github.com/psf/black
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _isort: https://github.com/PyCQA/isort
.. _pip: https://pypi.org/project/pip/
.. _pre-commit: https://pre-commit.com/
.. _PyAnsys Developer's Guide: https://dev.docs.pyansys.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/
.. _pyvista-pytest: https://github.com/pyvista/pytest-pyvista
