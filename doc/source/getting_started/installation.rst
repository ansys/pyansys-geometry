Installation
############

This page assumes that you want to install PyAnsys Geometry in developer mode so that
you can modify the source and enhance it. You can install PyAnsys Geometry from PyPI
or from the `PyAnsys Geometry repository <https://github.com/ansys/pyansys-geometry>`_ on GitHub.

Package dependencies
--------------------

PyAnsys Geometry is supported on Python version 3.8 and later. As indicated in the
`Moving to require Python 3 <https://python3statement.org/>`_ statement,
previous versions of Python are no longer supported.

PyAnsys Geometry dependencies are automatically checked when packages are installed.
These projects are required dependencies for PyAnsys Geometry:

* `ansys-api-geometry <https://pypi.org/project/ansys-api-geometry/>`_: Used for supplying
  gRPC code generated from Protobuf (PROTO) files
* `NumPy <https://pypi.org/project/numpy/>`_: Used for data array access
* `Pint <https://pypi.org/project/Pint/>`_: Used for measurement units
* `PyVista <https://pypi.org/project/pyvista/>`_: Used for interactive 3D plotting
* `SciPy <https://pypi.org/project/scipy/>`_: Used for geometric transformations

PyPI
----

Before installing PyAnsys Geometry, to ensure that you have the latest version of
`pip`_, run this command:

.. code:: bash

   python -m pip install -U pip

Then, to install PyAnsys Geometry, run this command:

.. code:: bash

   python -m pip install ansys-geometry-core

.. caution::

    PyAnsys Geometry is hosted in a private PyPI repository. You must provide the following
    index URL to the private PyPI repository:

    ``https://pkgs.dev.azure.com/pyansys/_packaging/pyansys/pypi/simple/``

    If access to this package registry is needed, email `pyansys.core@ansys.com <mailto:pyansys.core@ansys.com>`_
    to request a read-only token. Once you have obtained this token, run this command, replacing
    ``${PRIVATE_PYPI_ACCESS_TOKEN}`` with the token that you were sent:

    .. code:: bash

        pip install ansys-geometry-core --index-url=https://${PRIVATE_PYPI_ACCESS_TOKEN}@pkgs.dev.azure.com/pyansys/_packaging/pyansys/pypi/simple/


GitHub
------

To install the latest release from the `PyAnsys Geometry repository <https://github.com/ansys/pyansys-geometry>`_
on GitHub, run these commands:

.. code:: bash

   git clone https://github.com/ansys/pyansys-geometry
   cd pyansys-geometry
   pip install -e .

To verify your development installation, run this command:

.. code:: bash

   tox

Install in offline mode
-----------------------

If you lack an internet connection on your installation machine (or you do not have access to the
private Ansys PyPI packages repository), you should install PyAnsys Geometry by downloading the wheelhouse
archive for your corresponding machine architecture from the repository's `Releases page
<https://github.com/ansys/pyansys-geometry/releases>`_.

Each wheelhouse archive contains all the Python wheels necessary to install PyAnsys Geometry from scratch on Windows,
Linux, and MacOS from Python 3.8 to 3.11. You can install this on an isolated system with a fresh Python
installation or on a virtual environment.

For example, on Linux with Python 3.8, unzip the wheelhouse archive and install it with these commands:

.. code:: bash

    unzip ansys-geometry-core-v0.3.0-wheelhouse-Linux-3.8.zip wheelhouse
    pip install ansys-geometry-core -f wheelhouse --no-index --upgrade --ignore-installed

If you're on Windows with Python 3.9, unzip the wheelhouse archive to a wheelhouse directory
and then install using the same ``pip install`` command as in the preceding example.

Consider installing using a virtual environment. For more information, see `Creation of virtual
environments <https://docs.python.org/3/library/venv.html>`_ in the Python documentation.

Verify your installation
------------------------

Verify the :class:`Modeler() <ansys.geometry.core.modeler()>` connection with this code:

.. code:: pycon

    >>> from ansys.geometry.core import Modeler
    >>> modeler = Modeler()
    >>> print(modeler)

    Ansys Geometry Modeler (0x205c5c17d90)

    Ansys Geometry Modeler Client (0x205c5c16e00)
    Target:     localhost:652
    Connection: Healthy

If you see a response from the server, you can start using PyAnsys Geometry as a service.
For more information on PyAnsys Geometry usage, see :ref:`User guide <ref_user_guide>`.

.. LINKS AND REFERENCES
.. _pip: https://pypi.org/project/pip/
