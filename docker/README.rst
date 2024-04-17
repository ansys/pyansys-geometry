Create your own Geometry service Docker container
=================================================

To learn how to build your own Geometry service Docker container,
see these topics:

.. * `Guide to building the Linux Docker container <https://geometry.docs.pyansys.com/version/dev/getting_started/docker/linux_container.html#build-the-geometry-service-linux-container>`_.
* `Guide to building the Windows Docker container <https://geometry.docs.pyansys.com/version/dev/getting_started/docker/windows_container.html#build-the-geometry-service-windows-container>`_.

If you have your own Ansys installation, you can build a Docker container
that uses your installation. In order to do this, download the
Python script `build_docker_windows.py <https://github.com/ansys/pyansys-geometry/blob/main/docker/build_docker_windows.py>`_
and run it from the command line:

.. code-block:: bash

    python build_docker_windows.py

If you have any problems, open a `GitHub Issue <https://github.com/ansys/pyansys-geometry/issues/new?assignees=&labels=bug&projects=&template=bug.yml&title=Bug+located+in+...>`_.