Contribute
##########

Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to PyAnsys Geometry.

The following contribution information is specific to PyAnsys Geometry.

Clone the repository
--------------------

To clone and install the latest PyAnsys Geometry release in development mode, run
these commands:

.. code::

    git clone https://github.com/ansys/pyansys-geometry
    cd pyansys-geometry
    python -m pip install --upgrade pip
    pip install -e .


Post issues
-----------

Use the `PyAnsys Geometry Issues <https://github.com/ansys/pyansys-geometry/issues>`_
page to submit questions, report bugs, and request new features. When possible, you
should use these issue templates:

* Bug, problem, error: For filing a bug report
* Documentation error: For requesting modifications to the documentation
* Adding an example: For proposing a new example
* New feature: For requesting enhancements to the code

If your issue does not fit into one of these template categories, you can click
the link for opening a blank issue.

To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

View documentation
------------------

Documentation for the latest stable release of PyAnsys Geometry is hosted at
`PyAnsys Geometry Documentation <https://geometry.docs.pyansys.com>`_.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

Adhere to code style
--------------------

PyAnsys Geometry follows the PEP8 standard as outlined in
`PEP 8 <https://dev.docs.pyansys.com/coding-style/pep8.html>`_ in
the *PyAnsys Developer's Guide* and implements style checking using
`pre-commit <https://pre-commit.com/>`_.

To ensure your code meets minimum code styling standards, run these commands::

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook by running this command::

  pre-commit install

This way, it's not possible for you to push code that fails the style checks::

  $ pre-commit install
  $ git commit -am "added my cool feature"
  ruff.....................................................................Passed
  codespell................................................................Passed
  check for merge conflicts................................................Passed
  debug statements (python)................................................Passed
  check yaml...............................................................Passed
  trim trailing whitespace.................................................Passed
  Validate GitHub Workflows................................................Passed
  check pre-commit.ci config...............................................Passed

Build the documentation
-----------------------

.. note::

  To build the documentation, you must have the Geometry Service
  installed and running on your machine because it is used to generate the
  examples in the documentation. It is also recommended that the
  service is running as a Docker container.

  If you do not have the Geometry Service installed, you can still build the
  documentation, but the examples are not generated. To build the
  documentation without the examples, define the following environment variable::

      # On Linux or macOS
      export BUILD_EXAMPLES=false

      # On Windows CMD
      set BUILD_EXAMPLES=false

      # On Windows PowerShell
      $env:BUILD_EXAMPLES="false"

To build the documentation locally, you must run this command to install the
documentation dependencies::

  pip install -e .[doc]

Then, navigate to the ``docs`` directory and run this command::

  # On Linux or macOS
  make html

  # On Windows
  ./make.bat html

The documentation is built in the ``docs/_build/html`` directory.

You can clean the documentation build by running this command::

  # On Linux or macOS
  make clean

  # On Windows
  ./make.bat clean

Adding examples
---------------

Users can collaborate with examples to this documentation by adding new examples. A reference
commit of the changes that adding an example requires is shown here:

https://github.com/ansys/pyansys-geometry/pull/1454/commits/7fcf02f86f05e0e5ce1c1071c3c5fcd274ec481c

To add a new example, follow these steps:

1. Create a new notebook in the ``doc/source/examples`` directory, under the appropriate
   folder for your example.
2. Use the ``doc\source\examples\99_misc\template.mystnb`` file as a reference for creating
   your example notebook. It contains the necessary metadata and structure for a
   PyAnsys Geometry example.
3. Add the new notebook to the ``doc/source/examples.rst`` file.
4. Store a thumbnail image of the example in the ``doc/source/_static/thumbnails`` directory.
5. Link the thumbnail image to your example file in the ``doc/source/conf.py`` file as shown in the reference commit.

You can also test the correct build process of a new example by performing the following steps:

1. Run the following command to install the documentation dependencies::

    pip install -e .[doc]

2. Navigate to the ``doc`` directory and run the following command::

    # On Linux or macOS
    make single-example examples/01_getting_started/01_math.mystnb

    # On Windows
    ./make.bat single-example examples/01_getting_started/01_math.mystnb

.. note::

  The example name must be the same as the notebook name, with its path
  starting at the ``examples`` directory.

3. Check the ``doc/source/_build/html`` directory for the generated documentation
   and open the ``index.html`` file in your browser.

Run tests
---------

PyAnsys Geometry uses `pytest <https://docs.pytest.org/en/stable/>`_ for testing.

Prerequisites
^^^^^^^^^^^^^

Prior to running the tests, you must run this command to install the test dependencies::

  pip install -e .[tests]

Make sure to define the port and host of the service using the following environment variables::

  # On Linux or macOS
  export ANSRV_GEO_PORT=5000
  export ANSRV_GEO_HOST=localhost

  # On Windows CMD
  set ANSRV_GEO_PORT=5000
  set ANSRV_GEO_HOST=localhost

  # On Windows PowerShell
  $env:ANSRV_GEO_PORT=5000
  $env:ANSRV_GEO_HOST="localhost"

Running the tests
^^^^^^^^^^^^^^^^^

To run the tests, navigate to the root directory of the repository and run this command::

  pytest

.. note::

  The tests require the Geometry Service to be installed and running on your machine.
  The tests fail if the service is not running. It is expected for the Geometry
  Service to be running as a Docker container.

  If you do not have the Geometry Service running as a Docker container, but you have it
  running on your machine, you can still run the tests with the following argument::

    pytest --use-existing-service=yes