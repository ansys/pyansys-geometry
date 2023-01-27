Geometry service using Docker
=============================

Install the PyGeometry image
----------------------------

#. Using your GitHub credentials, download the Docker image from the `pygeometry <https://github.com/pyansys/pygeometry>`_ repository.
#. If you have Docker installed, use a GitHub personal access token (PAT) with packages read permission to authorize Docker 
   to access this repository. For more information,
   see `creating a personal access token <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token>`_.

#. Save the token to a file:

   .. code:: bash

      echo XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX > GH_TOKEN.txt

#. Authorize Docker to access the repository:

   .. code:: bash

      GH_USERNAME=<my-github-username>
      cat GH_TOKEN.txt | docker login docker.pkg.github.com -u $GH_USERNAME --password-stdin

#. Pull the Geometry service locally using Docker with:


   .. code:: bash

      docker pull ghcr.io/pyansys/geometry:<tag>

   The following OS-dependent tags are available:

   * ``windows-latest``
   * ``windows-latest-unstable``

Launching the Geometry service
------------------------------

The Geometry service can be launched locally in two different ways:

.. tab-set:: 

    .. tab-item:: Using PyGeometry launcher

        This method will directly launch for you the Geometry Service and it
        will provide a ``Modeler`` object.

        .. code:: python

          from ansys.geometry.core.connection import launch_modeler

          modeler = launch_modeler()

        The previous ``launch_modeler()`` method will launch the Geometry Service under the default
        conditions. For more configurability, please use ``launch_local_modeler()``.

    .. tab-item:: Manual Geometry Service launch

       This method will involve the user manually launching the Geometry Service. Afterwards, please
       refer to the next section in order to understand how to connect to it from PyGeometry.

       .. code:: bash

          docker run --name ans_geo -p 50051:50051 ghcr.io/pyansys/geometry:windows-latest


Connect to the Geometry service
-------------------------------

After the service is launched, connect to it with:

.. code:: python

   from ansys.geometry.core import Modeler

   modeler = Modeler()

By default ``Modeler`` connects to ``127.0.0.1`` (``'localhost'``) on
port ``50051``. You can change this by modifying the ``host`` and ``port``
parameters of ``Modeler``, but note that you must also modify
your ``docker run`` command by changing ``<HOST-PORT>-50051``.

If you want to change the defaults, modify environment variables and the
``Modeler`` function:

.. tab-set:: 

    .. tab-item:: Environment variables

        .. tab-set::

            .. tab-item:: Linux/Mac

                .. code-block:: bash

                    export ANSRV_GEO_HOST=127.0.0.1
                    export ANSRV_GEO_PORT=50051

            .. tab-item:: Windows

                .. code-block:: bash

                    SET ANSRV_GEO_HOST=127.0.0.1
                    SET ANSRV_GEO_PORT=50051

    .. tab-item:: Modeler function

        .. code-block:: pycon

            >>> from ansys.geometry.core import Modeler
            >>> modeler = Modeler(host="127.0.0.1", port=50051)
