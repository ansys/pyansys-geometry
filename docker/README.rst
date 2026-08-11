Create your own Geometry service Docker container
=================================================

To learn how to build your own Geometry service Docker container,
see these topics:

.. * `Guide to building the Linux Docker container <https://geometry.docs.pyansys.com/version/dev/getting_started/docker/linux_container.html#build-the-geometry-service-linux-container>`_.
* `Guide to building the Windows Docker container <https://geometry.docs.pyansys.com/version/dev/getting_started/docker/windows_container.html#build-the-geometry-service-windows-container>`_.

If you have your own Ansys installation, you can build a Docker container
that uses your installation. Download the appropriate build script and run it
from the command line:

* **Windows** — `build_docker_windows.py <https://github.com/ansys/pyansys-geometry/blob/main/docker/build_docker_windows.py>`_

  .. code-block:: bash

      python build_docker_windows.py

* **Linux** — `build_docker_linux.py <https://github.com/ansys/pyansys-geometry/blob/main/docker/build_docker_linux.py>`_

  .. code-block:: bash

      python build_docker_linux.py

Both scripts automatically select the correct .NET runtime version based on
the targeted Ansys release: .NET 8 for releases up to 26.1 and .NET 10 for
27.1 and later.

If you have any problems, open a `GitHub Issue <https://github.com/ansys/pyansys-geometry/issues/new?assignees=&labels=bug&projects=&template=bug.yml&title=Bug+located+in+...>`_.