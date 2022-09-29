Contributing
############

Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with it and all `How-to <https://dev.docs.pyansys.com/how-to/index.html>`_ for 
guidelines and best practices. 
before attempting to
contribute to PyGeometry.
 
The following contribution information is specific to PyGeometry.

Cloning the PyGeometry repository
---------------------------------

Run this code to clone and install the latest version of PyGeometry in development mode:

.. code::

    git clone https://github.com/pyansys/pygeometry
    cd pygeometry
    python -m pip install --upgrade pip
    pip install -e .


Posting issues
--------------

Use the `PyGeometry Issues <https://github.com/pyansys/pygeometry/issues>`_
page to submit questions, report bugs, and request new features. When possible, it is
recommended that you use these issue templates:

* Bug report template
* Feature request template

If your issue does not fit into one of these categories, create your own issue.

To reach the project support team, email `pyansys.support@ansys.com <pyansys.support@ansys.com>`_.

Viewing PyGeometry documentation
---------------------------------

Documentation for the latest stable release of PyGeometry is hosted at
`PyGeometry Documentation <https://geometry.docs.pyansys.com>`_.

Documentation for the latest development version, which tracks the
``main`` branch, is hosted at `Development PyGeometry Documentation <https://dev.geometry.docs.pyansys.com/>`_.
This version is automatically kept up to date via GitHub actions.

Code style
----------

PyGeometry follows the PEP8 standard as outlined in the `PyAnsys Development Guide
<https://dev.docs.pyansys.com>`_ and implements style checking using
`pre-commit <https://pre-commit.com/>`_.

To ensure your code meets minimum code styling standards, run::

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook by running::

  pre-commit install

This way, it's not possible for you to push code that fails the style checks. For example::

  $ pre-commit install
  $ git commit -am "added my cool feature"
  black....................................................................Passed
  isort....................................................................Passed
  flake8...................................................................Passed
  codespell................................................................Passed
  check for merge conflicts................................................Passed
  debug statements (python)................................................Passed
  Validate GitHub Workflows................................................Passed