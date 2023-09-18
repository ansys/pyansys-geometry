Launch the Geometry service
---------------------------

There are methods for launching the Geometry service:

* You can use the PyAnsys Geometry launcher.
* You can manually launch the Geometry service.

Environment variables
^^^^^^^^^^^^^^^^^^^^^

The Geometry service requires this mandatory environment variable for its use:

* ``LICENSE_SERVER``: License server (IP address or DNS) that the Geometry service is to
  connect to. For example, ``127.0.0.1``.

You can also specify other optional environment variables:

* ``ENABLE_TRACE``: Whether to set up the trace level for debugging purposes. The default
  is ``0``, in which case the trace level is not set up. Options are ``1`` and ``0``.
* ``LOG_LEVEL``: Sets the Geometry service logging level. The default is ``2``, in which case
  the logging level is ``INFO``.

Other important information to keep in mind:

* The **host**: this is the machine that will host the Geometry Service. It will typically be
  on ``localhost`` but bare in mind that if you are deploying the service in a remote machine,
  you will need to pass in this machine's host IP when connecting. By default, PyAnsys Geometry
  will assume it is on ``localhost``.

* The **port**: this is the port that will expose the Geometry Service on the host machine. Its
  value is assumed to be ``50051``, but users can deploy the service on their preferred port.

Prior to using the PyAnsys Geometry launcher to launch the Geometry service, you must define
general environment variables required for your OS. You do not need to define these
environment variables prior to manually launching the Geometry service.

.. tab-set::

    .. tab-item:: Using PyAnsys Geometry launcher
       :sync: geometry

       Define the following general environment variables prior to using the PyAnsys Geometry
       launcher. Click the tab for your OS to see the appropriate commands.

       .. tab-set::

           .. tab-item:: Linux/Mac

               .. code-block:: bash

                   export ANSRV_GEO_LICENSE_SERVER=127.0.0.1
                   export ANSRV_GEO_ENABLE_TRACE=0
                   export ANSRV_GEO_LOG_LEVEL=2
                   export ANSRV_GEO_HOST=127.0.0.1
                   export ANSRV_GEO_PORT=50051

           .. tab-item:: Powershell

               .. code-block:: pwsh

                   $env:ANSRV_GEO_LICENSE_SERVER="127.0.0.1"
                   $env:ANSRV_GEO_ENABLE_TRACE=0
                   $env:ANSRV_GEO_LOG_LEVEL=2
                   $env:ANSRV_GEO_HOST="127.0.0.1"
                   $env:ANSRV_GEO_PORT=50051

           .. tab-item:: Windows CMD

               .. code-block:: bash

                   SET ANSRV_GEO_LICENSE_SERVER=127.0.0.1
                   SET ANSRV_GEO_ENABLE_TRACE=0
                   SET ANSRV_GEO_LOG_LEVEL=2
                   SET ANSRV_GEO_HOST=127.0.0.1
                   SET ANSRV_GEO_PORT=50051

       .. warning::

           When running a Windows Docker container, certain high-value ports might be restricted
           from its use. This means that the port exposed by the container will have to be set
           to lower values. It is recommended to change the value of ``ANSRV_GEO_PORT``
           to use a port such as ``700``, instead of ``50051``.

    .. tab-item:: Manual launch
       :sync: manual

       You do not need to define general environment variables prior to manually launching
       the Geometry service. They are directly passed to the Docker container itself.


Geometry service launcher
^^^^^^^^^^^^^^^^^^^^^^^^^

As mentioned earlier, you can launch the Geometry service locally in two different ways.
To see the commands for each method, click the following tabs.

.. tab-set::

    .. tab-item:: Using PyAnsys Geometry launcher
       :sync: geometry

       This method directly launches the Geometry service and
       provides a ``Modeler`` object.

       .. code:: python

          from ansys.geometry.core.connection import launch_modeler

          modeler = launch_modeler()

       The ``launch_modeler()`` method launches the Geometry service under the default
       conditions. For more configurability, use the ``launch_local_modeler()`` method.

    .. tab-item:: Manual launch
       :sync: manual

       This method requires that you manually launch the Geometry service. Remember to pass
       in the different environment variables that are needed. Afterwards, see the next section
       to understand how to connect to this service instance from PyAnsys Geometry.

       .. tab-set::

           .. tab-item:: Linux/Mac

               .. code-block:: bash

                   docker run \
                       --name ans_geo \
                       -e LICENSE_SERVER=<LICENSE_SERVER> \
                       -p 50051:50051 \
                       ghcr.io/ansys/geometry:<TAG>

           .. tab-item:: Powershell

               .. code-block:: pwsh

                   docker run `
                       --name ans_geo `
                       -e LICENSE_SERVER=<LICENSE_SERVER> `
                       -p 50051:50051 `
                       ghcr.io/ansys/geometry:<TAG>

           .. tab-item:: Windows CMD

               .. code-block:: bash

                   docker run ^
                       --name ans_geo ^
                       -e LICENSE_SERVER=<LICENSE_SERVER> ^
                       -p 50051:50051 ^
                       ghcr.io/ansys/geometry:<TAG>

       .. warning::

           When running a Windows Docker container, certain high-value ports might be restricted
           from its use. This means that the port exposed by the container will have to be set
           to lower values. It is recommended to change the value of ``-p 50051:50051``
           to use a port such as ``-p 700:50051``.

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

The following tabs show the commands that set the environment variables and ``Modeler``
function.

.. warning::

    When running a Windows Docker container, certain high-value ports might be restricted
    from its use. This means that the port exposed by the container will have to be set
    to lower values. It is recommended to change the value of ``ANSRV_GEO_PORT``
    to use a port such as ``700``, instead of ``50051``.

.. tab-set::

    .. tab-item:: Environment variables

        .. tab-set::

            .. tab-item:: Linux/Mac

                .. code-block:: bash

                    export ANSRV_GEO_HOST=127.0.0.1
                    export ANSRV_GEO_PORT=50051

            .. tab-item:: Powershell

                .. code-block:: pwsh

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
