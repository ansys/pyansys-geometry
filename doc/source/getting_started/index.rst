Getting started
###############

To use PyGeometry, you need to have a local installation of `docker <https://docs.docker.com/engine/install/>`_. 
To start the service locally, have  to `authenticated to ghcr.io
<https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry>`_,
Now you can start the geometry service locally using ``docker`` with:

.. code:: bash

   docker run --name ans_geo -e -p 50051:50051 ghcr.io/pyansys/pygeometry:latest

Next, connect to the service with:

.. code:: python
   
   >>> from ansys.geometry.core import Modeler
   >>> modeler = Modeler()

By default ``Modeler`` will connect to ``127.0.0.1`` (``'localhost'``) at the
port 50051. You can change this by modifying the ``host`` and ``port``
parameters of ``Modeler``, but note that you will have to also modify this in
your ``docker run`` command by changing ``<HOST-PORT>-50051``.

If you wish to modify the defaults, modify the following environment variables:

If on Linux/Mac OS:

.. code::

   export ANSRV_GEO_HOST=127.0.0.1
   export ANSRV_GEO_PORT=50051

Or Windows:

.. code::

   SET ANSRV_GEO_HOST=127.0.0.1
   SET ANSRV_GEO_PORT=50051

Installation
============

Python module
^^^^^^^^^^^^^

In order to install PyGeometry, make sure you have the latest version of
`pip`_. To do so, run:

.. code:: bash

   python -m pip install -U pip

Then, you can simply execute:

.. code:: bash

   poetry run python -m pip install ansys-geometry-core

Alternatively, install the latest from `PyGeometry <https://github.com/pyansys/pygeometry>` GitHub via:

   .. code:: bash

      git clone https://github.com/pyansys/pygeometry
      cd pygeometry
      pip install -e .
        
You can verify your development installation by running:

   .. code:: bash
        
      tox

Offline mode installation
^^^^^^^^^^^^^^^^^^^^^^^^^

If you lack an internet connection on your installation machine (or you do not have access to the
private PyPi package), the recommended way of installing PyGeometry is downloading the wheelhouse
archive from the `Releases Page <https://github.com/pyansys/pygeometry/releases>`_ for your
corresponding machine architecture.

Each wheelhouse archive contains all the Python wheels necessary to install PyGeometry from scratch on Windows,
Linux, and MacOS from Python 3.7 to 3.10. You can install this on an isolated system with a fresh Python
installation or on a virtual environment.

For example, on Linux with Python 3.7, unzip the wheelhouse archive and install it with the following:

.. code:: bash

    unzip ansys-geometry-core-v0.1.dev0-wheelhouse-Linux-3.7.zip wheelhouse
    pip install ansys-geometry-core -f wheelhouse --no-index --upgrade --ignore-installed

If you're on Windows with Python 3.9, unzip to a wheelhouse directory and install using the same command as above.

Consider installing using a `virtual environment <https://docs.python.org/3/library/venv.html>`_.

Verify your installation
========================

Check the Modelar() connection by:

.. code:: python

    >>> from ansys.geometry.core import Modeler
    >>> modeler = Modeler()
    >>> print(modeler)
    
    Ansys Geometry Modeler (0x205c5c17d90)

    Ansys Geometry Modeler Client (0x205c5c16e00)
    Target:     localhost:652
    Connection: Healthy

.. LINKS AND REFERENCES
.. _pip: https://pypi.org/project/pip/
.. _pre-commit: https://pre-commit.com/
.. _PyAnsys Developer's guide: https://dev.docs.pyansys.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/