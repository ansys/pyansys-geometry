.. _ref_dev_mode:

Install package in development mode
###################################

This topic assumes that you want to install PyAnsys Geometry in developer mode so that
you can modify the source and enhance it. You can install PyAnsys Geometry from PyPI, Conda,
or from the `PyAnsys Geometry repository <https://github.com/ansys/pyansys-geometry>`_ on GitHub.

.. contents::
   :backlinks: none

Package dependencies
--------------------

PyAnsys Geometry is supported on Python version 3.10 and later. As indicated in the
`Moving to require Python 3 <https://python3statement.github.io/>`_ statement,
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


Conda
-----

You can also install PyAnsys Geometry using `conda`_. First, ensure that you have the latest version:

.. code:: bash

   conda update -n base -c defaults conda

Then, to install PyAnsys Geometry, run this command:

.. code:: bash

   conda install -c conda-forge ansys-geometry-core


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
Linux, and MacOS from Python 3.10 to 3.13. You can install this on an isolated system with a fresh Python
installation or on a virtual environment.

For example, on Linux with Python 3.10, unzip the wheelhouse archive and install it with these commands:

.. code:: bash

    unzip ansys-geometry-core-v0.11.0-all-wheelhouse-ubuntu-3.10.zip wheelhouse
    pip install ansys-geometry-core -f wheelhouse --no-index --upgrade --ignore-installed

If you are on Windows with Python 3.10, unzip the wheelhouse archive to a wheelhouse directory
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

.. button-ref:: index
    :ref-type: doc
    :color: primary
    :shadow:
    :expand:

    Go to Getting started

.. LINKS AND REFERENCES
.. _pip: https://pypi.org/project/pip/
.. _conda: https://conda.io/projects/conda/en/latest/user-guide/getting-started.html
