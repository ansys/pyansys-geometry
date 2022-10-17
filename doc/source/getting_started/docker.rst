PyGeometry service using docker
===============================

Install the PyGeometry image
----------------------------

#. Using your GitHub credentials, download the docker image in the `PyGeometry <https://github.com/pyansys/pygeometry>`_ repository.
#. If you have docker installed, use a GitHub personal access token (PAT) with packages read permission to authorize docker 
   to access this repository. For more information,
   see `creating a personal access token <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token>`_.

#. Save the token to a file:

   .. code:: bash

      echo XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX > GH_TOKEN.txt

#. Authorize Docker to access the repository:
   
   .. code:: bash

      GH_USERNAME=<my-github-username>
      cat GH_TOKEN.txt | docker login docker.pkg.github.com -u $GH_USERNAME --password-stdin

#. Launch the Geometry Service locally using ``docker`` with:

.. code:: bash

   docker run --name ans_geo -e -p 50051:50051 ghcr.io/pyansys/pygeometry:latest

Connect to the PyGeometry Service
---------------------------------

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