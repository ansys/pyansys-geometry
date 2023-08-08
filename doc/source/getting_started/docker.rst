.. _ref_docker:

Geometry service using Docker
=============================

Docker
------

Ensure that the machine that the Geometry service is to run on has Docker installed. Otherwise,
see `Install Docker Engine <https://docs.docker.com/engine/install/>`_ in the Docker documentation.

.. caution::
    Currently, the Geometry service backend is only delivered as a Windows Docker container.
    As such, this container only runs on a Windows machine. Furthermore, certain Docker Desktop
    versions for Windows are not properly configured for running Windows Docker containers. For
    more information, see :ref:`Running the Geometry service Windows Docker container <ref_docker_windows>`.

.. _ref_docker_windows:

Run the Windows Docker container
--------------------------------

To run the Windows Docker container for the Geometry service, ensure that you follow
these steps when installing Docker:

#. Install Docker Desktop 4.13.1. To download this version, use the Windows download link
   in the `4.13.1 <https://docs.docker.com/desktop/release-notes/#4131>`_ section of the
   Docker release notes. Newer Docker Desktop versions present problems when running
   Windows Docker containers.

#. When prompted for **Use WSL2 instead of Hyper-V (recommended)**, clear this checkbox.

#. Once the installation process finishes, start Docker Desktop.

#. Select **Settings >> Software updates**, clear the **Automatically check for updates** checkbox, and
   click **Apply & restart**.

#. On the Windows taskbar, go to the **Show hidden icons** section, right-click in the Docker Desktop app, and
   select **Switch to Windows containers**.

Now that your Docker engine supports running Windows Docker containers, you can install the PyGeometry image.

Install the PyGeometry image
----------------------------

Once Docker is installed on your machine, follow these steps to download the Docker container for the
PyGeometry service and install this image.

#. Using your GitHub credentials, download the Docker image from the `pygeometry repository <https://github.com/ansys/pygeometry>`_
   on GitHub.

#. Use a GitHub personal access token (PAT) with permission for reading packages to authorize Docker
   to access this repository. For more information, see `Managing your personal access tokens
   <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens>`_
   in the GitHub documentation.

#. Save the token to a file with this command:

   .. code-block:: bash

       echo XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX > GH_TOKEN.txt

#. Authorize Docker to access the repository. To see the appropriate commands, click the tab for your OS.

   .. tab-set::

       .. tab-item:: Linux/Mac

           .. code-block:: bash

               GH_USERNAME=<my-github-username>
               cat GH_TOKEN.txt | docker login ghcr.io -u $GH_USERNAME --password-stdin

       .. tab-item:: Powershell

           .. code-block:: bash

               $env:GH_USERNAME=<my-github-username>
               cat GH_TOKEN.txt | docker login ghcr.io -u $env:GH_USERNAME --password-stdin

       .. tab-item:: Windows CMD

           .. code-block:: bash

               SET GH_USERNAME=<my-github-username>
               type GH_TOKEN.txt | docker login ghcr.io -u %GH_USERNAME% --password-stdin


#. Pull the Geometry service locally using Docker with a command like this:

   .. code:: bash

      docker pull ghcr.io/ansys/geometry:<tag>

   For ``<tag>``, use one of these available OS-dependent tags:

   * ``windows-latest``
   * ``windows-latest-unstable``
   * ``linux-latest``
   * ``linux-latest-unstable``

Launch the Geometry service
---------------------------

There are methods for launching the Geometry service:

* You can use the PyGeometry launcher.
* You can manually launch the Geometry service.

Environment variables
^^^^^^^^^^^^^^^^^^^^^

The Geometry service requires this mandatory environment variable for its use:

* ``LICENSE_SERVER``: License server (IP address or DNS) that the Geometry service is to
  connect to. For example, ``127.0.0.1``.

You can also specify other optional environment variables:

* ``ENABLE_TRACE``: Whether to set up the trace level for debugging purposes. The default
  is ``0``, in which case the trace level is not to be set up. Options are ``1`` and ``0``. 
* ``LOG_LEVEL``: Sets the Geometry service logging level. The default is ``2``, in which case
  the logging level is ``INFO``.

Depending on how you choose to launch the Geometry service, you can set environment
variables as shown on the tab for your OS:

.. tab-set::

    .. tab-item:: Using PyGeometry launcher

        In this case, you must define the following general environment variables prior
        to launching PyGeometry. Bare in mind that the naming of the variables is not the same.

        .. tab-set::

            .. tab-item:: Linux/Mac

                .. code-block:: bash

                    export ANSRV_GEO_LICENSE_SERVER=127.0.0.1
                    export ANSRV_GEO_ENABLE_TRACE=0
                    export ANSRV_GEO_LOG_LEVEL=2

            .. tab-item:: Powershell

                .. code-block:: bash

                    $env:ANSRV_GEO_LICENSE_SERVER="127.0.0.1"
                    $env:ANSRV_GEO_ENABLE_TRACE=0
                    $env:ANSRV_GEO_LOG_LEVEL=2

            .. tab-item:: Windows CMD

                .. code-block:: bash

                    SET ANSRV_GEO_LICENSE_SERVER=127.0.0.1
                    SET ANSRV_GEO_ENABLE_TRACE=0
                    SET ANSRV_GEO_LOG_LEVEL=2

    .. tab-item:: Manually launching Geometry service

        In this case, no prior environment variable definition is needed. They are
        directly passed to the Docker container itself.


Geometry service launcher
^^^^^^^^^^^^^^^^^^^^^^^^^

As already mentioned, you can launch the Geometry service locally in two different ways.
To see the commands for each method, click the following tabs.

.. tab-set::

    .. tab-item:: Using PyGeometry launcher

        This method directly launches the Geometry service and
        provides a ``Modeler`` object.

        .. code:: python

          from ansys.geometry.core.connection import launch_modeler

          modeler = launch_modeler()

        The ``launch_modeler()`` method launches the Geometry service under the default
        conditions. For more configurability, use the ``launch_local_modeler()`` method.

    .. tab-item:: Manual Geometry service launch

       This method requires that you manually launch the Geometry service. Remember to pass
       in the different environment variables that are needed. Afterwards, see the next section
       to understand how to connect to this service instance from PyGeometry.

       .. code:: bash

          docker run --name ans_geo -e LICENSE_SERVER=<LICENSE_SERVER> -p 50051:50051 ghcr.io/ansys/geometry:<TAG>


Connect to the Geometry service
-------------------------------

After the Geometry service is launched, connect to it with these commands:

.. code:: python

   from ansys.geometry.core import Modeler

   modeler = Modeler()

By default, the ``Modeler`` instance connects to ``127.0.0.1`` (``"localhost"``) on
port ``50051``. You can change this by modifying the ``host`` and ``port``
parameters of the ``Modeler`` object, but note that you must also modify
your ``docker run`` command by changing the ``<HOST-PORT>-50051`` argument.

The following tabs show the code that sets the environment variables and ``Modeler`` function.

.. tab-set::

    .. tab-item:: Environment variables

        .. tab-set::

            .. tab-item:: Linux/Mac

                .. code-block:: bash

                    export ANSRV_GEO_HOST=127.0.0.1
                    export ANSRV_GEO_PORT=50051

            .. tab-item:: Powershell

                .. code-block:: bash

                    $env:ANSRV_GEO_HOST="127.0.0.1"
                    $env:ANSRV_GEO_PORT=50051

            .. tab-item:: Windows CMD

                .. code-block:: bash

                    SET ANSRV_GEO_HOST=127.0.0.1
                    SET ANSRV_GEO_PORT=50051

    .. tab-item:: Modeler function

        .. code-block:: pycon

            >>> from ansys.geometry.core import Modeler
            >>> modeler = Modeler(host="127.0.0.1", port=50051)
