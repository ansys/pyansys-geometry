PyAnsys Geometry
================
|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |black| |pre-commit|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-geometry-core?logo=pypi
   :target: https://pypi.org/project/ansys-geometry-core/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-geometry-core.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-geometry-core
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/ansys/pyansys-geometry/graph/badge.svg?token=UZIC7XT5WE
   :target: https://codecov.io/gh/ansys/pyansys-geometry
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/pyansys-geometry/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/pyansys-geometry/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black

.. |pre-commit| image:: https://results.pre-commit.ci/badge/github/ansys/pyansys-geometry/main.svg
   :target: https://results.pre-commit.ci/latest/github/ansys/pyansys-geometry/main
   :alt: pre-commit.ci

PyAnsys Geometry is a Python client library for the Ansys Geometry service.

.. contents::

Usage
-----

There are different ways of getting started with using the Geometry service and its client library, PyAnsys Geometry.

For more information, see
`Getting Started <https://geometry.docs.pyansys.com/version/stable/getting_started/index.html>`_ documentation.

Installation
------------

PyAnsys Geometry has three installation modes: user, developer, and offline.

Install in user mode
^^^^^^^^^^^^^^^^^^^^

Before installing PyAnsys Geometry in user mode, make sure you have the latest version of
`pip`_ with:

.. code:: bash

   python -m pip install -U pip

Then, install PyAnsys Geometry with:

.. code:: bash

   python -m pip install ansys-geometry-core


Install in developer mode
^^^^^^^^^^^^^^^^^^^^^^^^^

Installing PyAnsys Geometry in developer mode allows
you to modify the source and enhance it.

.. note::

    Before contributing to the project, ensure that you are thoroughly familiar
    with the `PyAnsys Developer's Guide`_.

To install PyAnsys Geometry in developer mode, perform these steps:

#. Clone the ``pyansys-geometry`` repository:

   .. code:: bash

      git clone https://github.com/ansys/pyansys-geometry

#. Access the ``pyansys-geometry`` directory where the repository has been cloned:

   .. code:: bash

      cd pyansys-geometry

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

If you lack an internet connection on your installation machine, you should install PyAnsys Geometry
by downloading the wheelhouse archive from the `Releases <https://github.com/ansys/pyansys-geometry/releases>`_
page for your corresponding machine architecture.

Each wheelhouse archive contains all the Python wheels necessary to install PyAnsys Geometry from scratch on Windows,
Linux, and MacOS from Python 3.8 to 3.11. You can install this on an isolated system with a fresh Python
installation or on a virtual environment.

For example, on Linux with Python 3.8, unzip the wheelhouse archive and install it with:

.. code:: bash

    unzip ansys-geometry-core-v0.3.3-wheelhouse-Linux-3.8.zip wheelhouse
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

   This plugin facilitates the comparison of the images produced in PyAnsys Geometry for testing the plots.
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
