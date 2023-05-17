.. _ref_docker:

Geometry service using Docker
=============================

Docker
------

Ensure that the machine in which the Geometry service should run has Docker installed. Otherwise,
please install `Docker Engine <https://docs.docker.com/engine/install/>`_ from the previous link.

.. caution::
    At the moment, the Geometry service backend is only delivered as a Windows Docker container.
    As such, this container only runs on a Windows machine. Furthermore, it has also been observed
    that certain Docker Desktop versions for Windows are not properly configured for running Windows
    Docker containers. Refer to
    :ref:`Running the Geometry service Windows Docker container <ref_docker_windows>` for further details.

.. _ref_docker_windows:

Running the Geometry service Windows Docker container
-----------------------------------------------------

For running the Windows Docker container of the Geometry service, please ensure that
you follow the upcoming steps when installing Docker:

#. Install `Docker Desktop 4.13.1 <https://docs.docker.com/desktop/release-notes/#4131>`_ **or below**.
   It has been observed that newer versions present problems when running Windows Docker containers.

#. When prompted for ``Use WSL2 instead of Hyper-V (recommended)``, **deselect this option**.

#. Once the installation process finishes, open up Docker Desktop.

#. On ``Settings >> Software updates``, deselect ``Automatically check for updates``. Then, ``Apply & restart``.

#. On the Windows taskbar, go to the ``Show hidden icons`` section, right click in the Docker Desktop app and
   select ``Switch to Windows containers...``.

At this point, your Docker engine supports running Windows Docker containers. Next step involves downloading
the Geometry service Windows Docker image.

Install the PyGeometry image
----------------------------

Once you have Docker installed on your machine, the next steps involve pulling down the Geometry service
Docker container.

#. Using your GitHub credentials, download the Docker image from the `pygeometry <https://github.com/ansys/pygeometry>`_ repository.

#. If you have Docker installed, use a GitHub personal access token (PAT) with packages read permission to authorize Docker
   to access this repository. For more information,
   see `creating a personal access token <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token>`_.

#. Save the token to a file:

   .. code-block:: bash

       echo XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX > GH_TOKEN.txt

#. Authorize Docker to access the repository:

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


#. Pull the Geometry service locally using Docker with:

   .. code:: bash

      docker pull ghcr.io/ansys/geometry:<tag>

   The following OS-dependent tags are available:

   * ``windows-latest``
   * ``windows-latest-unstable``
   * ``linux-latest``
   * ``linux-latest-unstable``

Launching the Geometry service
------------------------------

In this section there are two mechanisms for launching the Geometry service: either **using the PyGeometry launcher**
or **manually launching the service**.

Environment variables
^^^^^^^^^^^^^^^^^^^^^

The Geometry service has a set of environment variables that are **mandatory** for its use:

* ``LICENSE_SERVER``: the license server (IP, DNS) to which the Geometry service shall connect. For example, ``127.0.0.1``.

Other optional environment variables are:

* ``ENABLE_TRACE``: whether to set up the trace level for debugging purposes. Expects either ``1`` or ``0``.
  By default, ``0`` (which means it is not activated).
* ``LOG_LEVEL``: sets the Geometry service logging level. By default, ``2``.

Depending on the mechanism chosen to launch the Geometry service, you can set them as follows:

.. tab-set::

    .. tab-item:: Using PyGeometry launcher

        In this case, users will have to define the following general environment variables prior
        to launching it. Bare in mind that the naming of the variables is not the same:

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

    .. tab-item:: Manual Geometry service launch

        In this case, there is no prior environment variable definition needed. They can
        directly be passed to the Docker container itself.


Geometry service launcher
^^^^^^^^^^^^^^^^^^^^^^^^^

The Geometry service can be launched locally in two different ways:

.. tab-set::

    .. tab-item:: Using PyGeometry launcher

        This method will directly launch for you the Geometry service and it
        will provide a ``Modeler`` object.

        .. code:: python

          from ansys.geometry.core.connection import launch_modeler

          modeler = launch_modeler()

        The previous ``launch_modeler()`` method will launch the Geometry service under the default
        conditions. For more configurability, please use ``launch_local_modeler()``.

    .. tab-item:: Manual Geometry service launch

       This method will involve the user manually launching the Geometry service. Remember to pass
       in the different environment variables needed. Afterwards, please refer to the next section in
       order to understand how to connect to it from PyGeometry.

       .. code:: bash

          docker run --name ans_geo -e LICENSE_SERVER=<LICENSE_SERVER> -p 50051:50051 ghcr.io/ansys/geometry:<TAG>


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
