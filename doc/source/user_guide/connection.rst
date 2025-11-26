Launching and connecting to a Modeler instance
**********************************************

PyAnsys Geometry provides the ability to launch and connect to a Modeler instance
either locally or remotely. A Modeler instance is a running instance of a
CAD service that the PyAnsys Geometry client can communicate with.

CAD services that are supported include:

- Ansys Geometry Service
- Ansys Discovery
- Ansys SpaceClaim

Connecting to a Modeler instance
--------------------------------

To connect to a Modeler instance, you can use the  :class:`Modeler() <ansys.geometry.core.modeler>` class,
which provides methods to connect to the desired CAD service. You can specify the connection parameters such
as the host, port, and authentication details.


.. code:: python

    from ansys.geometry.core import Modeler

    # Connect to a local Modeler instance
    modeler = Modeler(host="localhost", port=12345, transport_mode=...)

The ``transport_mode`` parameter can take several values depending on the type of connection you
want to establish. You can refer to the `Securing connections`_ section for more details on the
available transport modes.

.. warning:: Required transport_mode parameter

   Starting from PyAnsys Geometry 0.14, the ``transport_mode`` parameter is required when using
   the ``Modeler()`` class.

However, if you are using the :func:`launch_modeler() <ansys.geometry.core.connection.launcher>`
function to launch a local Modeler instance, the ``transport_mode`` parameter is optional and
will default to the appropriate mode based on the operating system and environment.

Connection types
----------------

PyAnsys Geometry supports different connection types to connect to a Modeler instance, which
differ in the environment in which the transport takes place:

- **Local connection**: The Modeler instance is running on the same machine as the PyAnsys
  Geometry client. This is typically used for development and testing purposes.
- **Remote connection**: The service instance is running on a different machine, and the
  Modeler client connects to it over the network. This is useful for accessing
  Modeler instances hosted on remote servers or cloud environments.

.. _user_guide_connection_securing:

Securing connections
--------------------

When connecting to a remote Modeler instance, it is important to ensure that the connection
is secure, not only to protect sensitive data but also to comply with organizational
security policies. These secure connections can be established using various methods, such as:

.. warning:: Secure connection compatibility

   Secure connections (mTLS, UDS, WNUA) are only available starting from Ansys release 24R2.
   However, some releases may require specific Service Packs to enable secure connection support.
   Starting from Ansys release 26R1, secure connections are available out-of-the-box without
   requiring additional Service Packs.

   If you are using an Ansys release prior to 24R2, you must use insecure connections.

- **mTLS**: Mutual Transport Layer Security (mTLS) is a security protocol that ensures both the client
  and server authenticate each other using digital certificates. This provides a high level of
  security for the connection. PyAnsys Geometry supports mTLS connections to Modeler instances. In that
  case, you need to provide the necessary certificates and keys when establishing the connection. More
  information on the certificates needed can be seen in
  `Generating certificates for mTLS <https://tools.docs.pyansys.com/version/stable/user_guide/secure_grpc.html#generating-certificates-for-mtls>`_.
  Make sure that the names of the files are in line with the previous link. An example of how to set up
  an mTLS connection is shown below:

  .. note::

     mTLS is the default transport mode when connecting to remote Modeler instances.

  .. code:: python

      from ansys.geometry.core import Modeler, launch_modeler

      # OPTION 1: Connect to a Modeler instance using mTLS
      modeler = Modeler(
          host="remote_host",
          port=12345,
          transport_mode="mtls",
          certs_dir="path/to/certs_directory",
      )

      # OPTION 2: Launch the Modeler instance locally using mTLS
      modeler = launch_modeler(
          transport_mode="mtls",
          certs_dir="path/to/certs_directory",
      )

- **UDS**: Unix Domain Sockets (UDS) provide a way to establish secure connections between
  processes on the same machine. UDS connections are faster and more secure than traditional
  network connections, as they do not require network protocols. PyAnsys Geometry supports UDS
  connections to local Modeler instances (**only on Linux-based services**). An example of how
  to set up a UDS connection is shown below:

  .. note::

     UDS is only supported when connecting to local Modeler instances on Linux-based services.
     It is also the default transport mode in such cases.

  .. code:: python

      from ansys.geometry.core import Modeler, launch_modeler

      # OPTION 1: Connect to a local Modeler instance using UDS
      modeler = Modeler(host="localhost", port=12345, transport_mode="uds")

      # OPTION 2: Launch the Modeler instance locally using UDS and specific directory and id for
      # the UDS socket
      modeler = Modeler(host="localhost", port=12345, transport_mode="uds", uds_dir="/path/to/uds_directory", uds_id="unique_id")

      # OPTION 3: Launch the Modeler instance locally using UDS
      modeler = launch_modeler(transport_mode="uds")

      # OPTION 4: Launch the Modeler instance locally using UDS and specific directory and id for
      # the UDS socket
      modeler = launch_modeler(transport_mode="uds", uds_dir="/path/to/uds_directory", uds_id="unique_id")

- **WNUA**: Windows Named User Authentication (WNUA) provides a way to establish secure connections
  between processes on the same Windows machine. WNUA connections use a built-in mechanism to verify
  that the owner of the service running is also the owner of the client connection established (similar
  to UDS). PyAnsys Geometry supports WNUA connections to local Modeler instances
  (**only on Windows-based services**). An example of how to set up a WNUA connection is shown below:

  .. note::

     WNUA is only supported when connecting to local Modeler instances on Windows-based services.
     It is also the default transport mode in such cases.

  .. code:: python

      from ansys.geometry.core import Modeler, launch_modeler

      # OPTION 1: Connect to a local Modeler instance using WNUA
      modeler = Modeler(host="localhost", port=12345, transport_mode="wnua")

      # OPTION 2: Launch the Modeler instance locally using WNUA
      modeler = launch_modeler(transport_mode="wnua")

- **Insecure**: Insecure connections do not provide any security measures to protect the data
  transmitted between the client and server. This mode is not recommended for production use,
  as it exposes the connection to potential security risks. However, it can be useful for
  development and testing purposes in trusted environments. An example of how to set up an
  insecure connection is shown below:

  .. code:: python

      from ansys.geometry.core import Modeler, launch_modeler

      # OPTION 1: Connect to a Modeler instance using an insecure connection
      modeler = Modeler(
          host="remote_host",
          port=12345,
          transport_mode="insecure",
      )

      # OPTION 2: Launch the Modeler instance locally using an insecure connection
      modeler = launch_modeler(
          transport_mode="insecure",
      )

For more information on secure connections and transport modes, see
`Securing gRPC connections <https://tools.docs.pyansys.com/version/stable/user_guide/secure_grpc.html>`_.
