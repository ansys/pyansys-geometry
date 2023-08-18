


Module ``defaults``
===================



.. py:module:: ansys.geometry.core.connection.defaults



Description
-----------

Module providing default connection parameters.




Summary
-------

.. tab-set::




    .. tab-item:: Classes

        Content 2

    .. tab-item:: Functions

        Content 2

    .. tab-item:: Enumerations

        Content 2

    .. tab-item:: Attributes

        Content 2






Contents
--------

.. py:data:: DEFAULT_HOST

   Default for the HOST name.

   By default, PyGeometry searches for the environment variable ``ANSRV_GEO_HOST``,
   and if this variable does not exist, PyGeometry uses ``127.0.0.1`` as the host.


.. py:data:: DEFAULT_PORT
   :type: int

   Default for the HOST port.

   By default, PyGeometry searches for the environment variable ``ANSRV_GEO_PORT``,
   and if this variable does not exist, PyGeometry uses ``50051`` as the port.


.. py:data:: MAX_MESSAGE_LENGTH

   Default for the gRPC maximum message length.

   By default, PyGeometry searches for the environment variable ``PYGEOMETRY_MAX_MESSAGE_LENGTH``,
   and if this variable does not exist, PyGeometry uses ``256Mb`` as the maximum message length.


.. py:data:: GEOMETRY_SERVICE_DOCKER_IMAGE
   :value: 'ghcr.io/ansys/geometry'

   Default for the Geometry service Docker image location.

   Tag is dependent on what OS service is requested.


.. py:data:: DEFAULT_PIM_CONFIG

   Default for the PIM configuration when running PIM Light.

   This parameter is only to be used when PIM Light is being run.


