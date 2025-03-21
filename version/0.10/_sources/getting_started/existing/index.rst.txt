.. _ref_existing_session:

Use an existing session
=======================

If a session of Discovery, SpaceClaim, or the Geometry service is already
running, PyAnsys Geometry can be used to connect to it.

.. warning::

   Running a SpaceClaim or Discovery normal session does not suffice to be
   able to use it with PyAnsys Geometry. Both products need the ApiServer extension to be
   running. In this case, to ease the process, you should launch the products directly from the PyAnsys
   Geometry library as shown in :ref:`ref_creating_local_session`.

Establish the connection
------------------------

From Python, establish a connection to the existing client session by creating a ``Modeler`` object:

.. code:: python

    from ansys.geometry.core import Modeler

    modeler = Modeler(host="localhost", port=50051)

If no error messages are received, your connection is established successfully.
Note that your local port number might differ from the one shown in the preceding code.

Verify the connection
---------------------
If you want to verify that the connection is successful, request the status of the client
connection inside your ``Modeler`` object:

.. code:: pycon

   >>> modeler.client
   Ansys Geometry Modeler Client (...)
   Target:     localhost:50051
   Connection: Healthy

.. button-ref:: ../index
    :ref-type: doc
    :color: primary
    :shadow:
    :expand:

    Go to Getting started