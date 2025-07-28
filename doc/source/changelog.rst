.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the PyAnsys Geometry project.

.. vale off

.. towncrier release notes start

`0.11.0 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.11.0>`_ - July 15, 2025
==========================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update with delta
          - `#1922 <https://github.com/ansys/pyansys-geometry/pull/1922>`_

        * - Find and fix stitch/missing/small faces enhancements
          - `#1953 <https://github.com/ansys/pyansys-geometry/pull/1953>`_

        * - Nurbs and trimmedcurve enhancements
          - `#1994 <https://github.com/ansys/pyansys-geometry/pull/1994>`_

        * - Allow logos linux 26 1
          - `#2048 <https://github.com/ansys/pyansys-geometry/pull/2048>`_

        * - Nurbscurve conversions
          - `#2053 <https://github.com/ansys/pyansys-geometry/pull/2053>`_

        * - Add components to ns
          - `#2068 <https://github.com/ansys/pyansys-geometry/pull/2068>`_

        * - Add mating conditions (align, tangent, orient)
          - `#2069 <https://github.com/ansys/pyansys-geometry/pull/2069>`_

        * - Vertex references
          - `#2083 <https://github.com/ansys/pyansys-geometry/pull/2083>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump jupytext from 1.17.1 to 1.17.2 in the docs-deps group
          - `#2024 <https://github.com/ansys/pyansys-geometry/pull/2024>`_

        * - Bump ansys-tools-visualization-interface from 0.9.1 to 0.9.2
          - `#2027 <https://github.com/ansys/pyansys-geometry/pull/2027>`_

        * - Bump trame-vtk from 2.8.15 to 2.8.17
          - `#2028 <https://github.com/ansys/pyansys-geometry/pull/2028>`_

        * - Bump pytest from 8.3.5 to 8.4.0
          - `#2034 <https://github.com/ansys/pyansys-geometry/pull/2034>`_

        * - Bump requests from 2.32.3 to 2.32.4
          - `#2040 <https://github.com/ansys/pyansys-geometry/pull/2040>`_

        * - Bump beartype from 0.20.2 to 0.21.0
          - `#2042 <https://github.com/ansys/pyansys-geometry/pull/2042>`_

        * - Bump panel from 1.6.1 to 1.7.1
          - `#2043 <https://github.com/ansys/pyansys-geometry/pull/2043>`_

        * - Bump ansys-tools-path from 0.7.1 to 0.7.2
          - `#2044 <https://github.com/ansys/pyansys-geometry/pull/2044>`_

        * - Bump quarto-cli from 1.7.31 to 1.7.32
          - `#2050 <https://github.com/ansys/pyansys-geometry/pull/2050>`_

        * - Bump ansys-tools-path from 0.7.2 to 0.7.3
          - `#2051 <https://github.com/ansys/pyansys-geometry/pull/2051>`_

        * - Bump pytest-cov from 6.1.1 to 6.2.1
          - `#2052 <https://github.com/ansys/pyansys-geometry/pull/2052>`_

        * - Limiting ansys-tools-visualization-interface
          - `#2054 <https://github.com/ansys/pyansys-geometry/pull/2054>`_

        * - Bump pytest from 8.4.0 to 8.4.1
          - `#2065 <https://github.com/ansys/pyansys-geometry/pull/2065>`_

        * - Bump panel from 1.7.1 to 1.7.2
          - `#2077 <https://github.com/ansys/pyansys-geometry/pull/2077>`_

        * - Bump trame-vtk from 2.8.17 to 2.9.0
          - `#2078 <https://github.com/ansys/pyansys-geometry/pull/2078>`_

        * - Bump numpydoc from 1.8.0 to 1.9.0 in the docs-deps group
          - `#2080 <https://github.com/ansys/pyansys-geometry/pull/2080>`_

        * - Bump ansys-api-geometry from 0.4.62 to 0.4.64
          - `#2081 <https://github.com/ansys/pyansys-geometry/pull/2081>`_

        * - Bump ansys-api-geometry from 0.4.64 to 0.4.65
          - `#2085 <https://github.com/ansys/pyansys-geometry/pull/2085>`_

        * - Bump notebook from 7.4.3 to 7.4.4 in the docs-deps group
          - `#2086 <https://github.com/ansys/pyansys-geometry/pull/2086>`_

        * - Bump ansys-sphinx-theme[autoapi] from 1.5.2 to 1.5.3 in the docs-deps group
          - `#2089 <https://github.com/ansys/pyansys-geometry/pull/2089>`_

        * - Bump panel from 1.7.2 to 1.7.4
          - `#2112 <https://github.com/ansys/pyansys-geometry/pull/2112>`_

        * - Bump pytest-pyvista from 0.1.9 to 0.2.0
          - `#2113 <https://github.com/ansys/pyansys-geometry/pull/2113>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Adding extra line
          - `#2026 <https://github.com/ansys/pyansys-geometry/pull/2026>`_

        * - Add proper disclaimer to binaries repository
          - `#2060 <https://github.com/ansys/pyansys-geometry/pull/2060>`_

        * - Add warning section for minimum version on methods
          - `#2062 <https://github.com/ansys/pyansys-geometry/pull/2062>`_

        * - Add deepwiki link
          - `#2073 <https://github.com/ansys/pyansys-geometry/pull/2073>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Make sure export_glb is handling a single polydata object
          - `#2032 <https://github.com/ansys/pyansys-geometry/pull/2032>`_

        * - Prevent the creation of empty named selections
          - `#2063 <https://github.com/ansys/pyansys-geometry/pull/2063>`_

        * - Revert visualization changes
          - `#2084 <https://github.com/ansys/pyansys-geometry/pull/2084>`_

        * - Internalize document after insert: update test
          - `#2092 <https://github.com/ansys/pyansys-geometry/pull/2092>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update changelog for v0.10.9
          - `#2023 <https://github.com/ansys/pyansys-geometry/pull/2023>`_

        * - Bump ansys/actions from 10.0.4 to 10.0.6 in the actions group
          - `#2025 <https://github.com/ansys/pyansys-geometry/pull/2025>`_

        * - Bump ansys/actions from 10.0.6 to 10.0.8 in the actions group
          - `#2029 <https://github.com/ansys/pyansys-geometry/pull/2029>`_

        * - Pre-commit automatic update
          - `#2033 <https://github.com/ansys/pyansys-geometry/pull/2033>`_, `#2066 <https://github.com/ansys/pyansys-geometry/pull/2066>`_, `#2076 <https://github.com/ansys/pyansys-geometry/pull/2076>`_, `#2090 <https://github.com/ansys/pyansys-geometry/pull/2090>`_, `#2111 <https://github.com/ansys/pyansys-geometry/pull/2111>`_

        * - Bump ansys/actions from 10.0.8 to 10.0.9 in the actions group
          - `#2035 <https://github.com/ansys/pyansys-geometry/pull/2035>`_

        * - Bump ansys/actions from 10.0.9 to 10.0.10 in the actions group
          - `#2038 <https://github.com/ansys/pyansys-geometry/pull/2038>`_

        * - Bump the actions group with 2 updates
          - `#2041 <https://github.com/ansys/pyansys-geometry/pull/2041>`_

        * - Upload code coverage on linux
          - `#2049 <https://github.com/ansys/pyansys-geometry/pull/2049>`_

        * - Bump ansys/actions from 10.0.11 to 10.0.12 in the actions group
          - `#2071 <https://github.com/ansys/pyansys-geometry/pull/2071>`_

        * - Bump github/codeql-action from 3.29.0 to 3.29.1 in the actions group
          - `#2075 <https://github.com/ansys/pyansys-geometry/pull/2075>`_

        * - Bump github/codeql-action from 3.29.1 to 3.29.2 in the actions group
          - `#2079 <https://github.com/ansys/pyansys-geometry/pull/2079>`_

        * - Using proper artifactory location
          - `#2114 <https://github.com/ansys/pyansys-geometry/pull/2114>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Expand code coverage and fix a few things
          - `#2039 <https://github.com/ansys/pyansys-geometry/pull/2039>`_

        * - Add more tests and update some tests
          - `#2046 <https://github.com/ansys/pyansys-geometry/pull/2046>`_

        * - Expanding test coverage for sketch
          - `#2047 <https://github.com/ansys/pyansys-geometry/pull/2047>`_

        * - Expanding test coverage for designer and math
          - `#2061 <https://github.com/ansys/pyansys-geometry/pull/2061>`_

        * - Adding test coverage for designer, sketch, misc
          - `#2070 <https://github.com/ansys/pyansys-geometry/pull/2070>`_

        * - Add more tests to expand coverage
          - `#2087 <https://github.com/ansys/pyansys-geometry/pull/2087>`_

        * - Add stride named selection import test
          - `#2088 <https://github.com/ansys/pyansys-geometry/pull/2088>`_

        * - Add more code coverage
          - `#2096 <https://github.com/ansys/pyansys-geometry/pull/2096>`_

        * - Logo removal should work on linux now
          - `#2098 <https://github.com/ansys/pyansys-geometry/pull/2098>`_

        * - Expand coverage and add bug fix test
          - `#2103 <https://github.com/ansys/pyansys-geometry/pull/2103>`_

        * - Bug fix test and round trip open file tests
          - `#2107 <https://github.com/ansys/pyansys-geometry/pull/2107>`_


`0.10.9 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.10.9>`_ - June 05, 2025
==========================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump ansys-sphinx-theme[autoapi] from 1.4.4 to 1.4.5 in the docs-deps group
          - `#2008 <https://github.com/ansys/pyansys-geometry/pull/2008>`_

        * - bump ansys-sphinx-theme[autoapi] from 1.4.5 to 1.5.0 in the docs-deps group
          - `#2009 <https://github.com/ansys/pyansys-geometry/pull/2009>`_

        * - bump notebook from 7.4.2 to 7.4.3 in the docs-deps group
          - `#2010 <https://github.com/ansys/pyansys-geometry/pull/2010>`_

        * - bump geomdl from 5.3.1 to 5.4.0
          - `#2012 <https://github.com/ansys/pyansys-geometry/pull/2012>`_

        * - bump ansys-sphinx-theme[autoapi] from 1.5.0 to 1.5.2 in the docs-deps group
          - `#2014 <https://github.com/ansys/pyansys-geometry/pull/2014>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Typo in the open request construction
          - `#2022 <https://github.com/ansys/pyansys-geometry/pull/2022>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.10.8
          - `#2006 <https://github.com/ansys/pyansys-geometry/pull/2006>`_

        * - bump ansys/actions from 9.0.12 to 9.0.13 in the actions group
          - `#2011 <https://github.com/ansys/pyansys-geometry/pull/2011>`_

        * - pre-commit automatic update
          - `#2015 <https://github.com/ansys/pyansys-geometry/pull/2015>`_

        * - improving CodeQL
          - `#2016 <https://github.com/ansys/pyansys-geometry/pull/2016>`_

        * - fix labeler permissions
          - `#2017 <https://github.com/ansys/pyansys-geometry/pull/2017>`_

        * - Bump ansys/actions from 9.0.13 to 10.0.1 in the actions group
          - `#2018 <https://github.com/ansys/pyansys-geometry/pull/2018>`_

        * - Bump the actions group with 2 updates
          - `#2019 <https://github.com/ansys/pyansys-geometry/pull/2019>`_, `#2021 <https://github.com/ansys/pyansys-geometry/pull/2021>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update Reader support info and add more import tests
          - `#2013 <https://github.com/ansys/pyansys-geometry/pull/2013>`_


`0.10.8 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.10.8>`_ - May 27, 2025
=========================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - repair tools refactoring
          - `#1912 <https://github.com/ansys/pyansys-geometry/pull/1912>`_

        * - use license metadata properly
          - `#1961 <https://github.com/ansys/pyansys-geometry/pull/1961>`_

        * - add 261 version api versions list
          - `#1980 <https://github.com/ansys/pyansys-geometry/pull/1980>`_

        * - grpc reachitecture - several modules
          - `#1988 <https://github.com/ansys/pyansys-geometry/pull/1988>`_

        * - deprecating ``product_version`` in favor of ``version``
          - `#1998 <https://github.com/ansys/pyansys-geometry/pull/1998>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump quarto-cli from 1.6.42 to 1.7.29
          - `#1962 <https://github.com/ansys/pyansys-geometry/pull/1962>`_

        * - bump jupytext from 1.16.7 to 1.17.1 in the docs-deps group
          - `#1963 <https://github.com/ansys/pyansys-geometry/pull/1963>`_

        * - bump ansys-sphinx-theme[autoapi] from 1.4.2 to 1.4.3 in the docs-deps group
          - `#1967 <https://github.com/ansys/pyansys-geometry/pull/1967>`_

        * - bump ansys-api-geometry from 0.4.58 to 0.4.59
          - `#1968 <https://github.com/ansys/pyansys-geometry/pull/1968>`_

        * - bump ansys-sphinx-theme[autoapi] from 1.4.3 to 1.4.4 in the docs-deps group
          - `#1969 <https://github.com/ansys/pyansys-geometry/pull/1969>`_

        * - bump notebook from 7.4.1 to 7.4.2 in the docs-deps group
          - `#1971 <https://github.com/ansys/pyansys-geometry/pull/1971>`_

        * - bump quarto-cli from 1.7.29 to 1.7.30
          - `#1972 <https://github.com/ansys/pyansys-geometry/pull/1972>`_

        * - bump matplotlib from 3.10.1 to 3.10.3
          - `#1974 <https://github.com/ansys/pyansys-geometry/pull/1974>`_

        * - bump pyvista[jupyter] from 0.45.0 to 0.45.1
          - `#1975 <https://github.com/ansys/pyansys-geometry/pull/1975>`_

        * - bump scipy from 1.15.2 to 1.15.3
          - `#1976 <https://github.com/ansys/pyansys-geometry/pull/1976>`_

        * - bump pyvista[jupyter] from 0.45.1 to 0.45.2
          - `#1981 <https://github.com/ansys/pyansys-geometry/pull/1981>`_

        * - bump ansys-api-geometry from 0.4.59 to 0.4.60
          - `#1987 <https://github.com/ansys/pyansys-geometry/pull/1987>`_

        * - bump quarto-cli from 1.7.30 to 1.7.31
          - `#1991 <https://github.com/ansys/pyansys-geometry/pull/1991>`_

        * - bump ansys-api-geometry from 0.4.60 to 0.4.61
          - `#1992 <https://github.com/ansys/pyansys-geometry/pull/1992>`_

        * - bump numpy from 2.2.5 to 2.2.6
          - `#1995 <https://github.com/ansys/pyansys-geometry/pull/1995>`_

        * - bump ansys-api-geometry from 0.4.61 to 0.4.62
          - `#2003 <https://github.com/ansys/pyansys-geometry/pull/2003>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - change python3statement url
          - `#1965 <https://github.com/ansys/pyansys-geometry/pull/1965>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - myst warning -- all cells must be of same type
          - `#1970 <https://github.com/ansys/pyansys-geometry/pull/1970>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.10.7
          - `#1959 <https://github.com/ansys/pyansys-geometry/pull/1959>`_

        * - pre-commit automatic update
          - `#1964 <https://github.com/ansys/pyansys-geometry/pull/1964>`_, `#1978 <https://github.com/ansys/pyansys-geometry/pull/1978>`_, `#1993 <https://github.com/ansys/pyansys-geometry/pull/1993>`_, `#2004 <https://github.com/ansys/pyansys-geometry/pull/2004>`_

        * - bump ansys/actions from 9.0.7 to 9.0.8 in the actions group
          - `#1966 <https://github.com/ansys/pyansys-geometry/pull/1966>`_

        * - bump ansys/actions from 9.0.8 to 9.0.9 in the actions group
          - `#1973 <https://github.com/ansys/pyansys-geometry/pull/1973>`_

        * - bump ansys/actions from 9.0.9 to 9.0.19 in the actions group
          - `#1979 <https://github.com/ansys/pyansys-geometry/pull/1979>`_

        * - bump ansys/actions from 9.0.19 to 9.0.20 in the actions group
          - `#1982 <https://github.com/ansys/pyansys-geometry/pull/1982>`_

        * - bump ansys/actions from 9.0.20 to 9.0.21 in the actions group
          - `#1983 <https://github.com/ansys/pyansys-geometry/pull/1983>`_

        * - bump ansys/actions from 9.0.21 to 9.0.22 in the actions group
          - `#1984 <https://github.com/ansys/pyansys-geometry/pull/1984>`_

        * - revert ansys/actions release
          - `#1985 <https://github.com/ansys/pyansys-geometry/pull/1985>`_

        * - bump the actions group with 2 updates
          - `#1990 <https://github.com/ansys/pyansys-geometry/pull/1990>`_

        * - bump ansys/actions from 9.0.9 to 9.0.11 in the actions group
          - `#1996 <https://github.com/ansys/pyansys-geometry/pull/1996>`_

        * - fix the usage of unstable container skip
          - `#2001 <https://github.com/ansys/pyansys-geometry/pull/2001>`_

        * - bump ansys/actions from 369ef11a9888875682d1a6b0ec65f82c4d8a664d to 5dc39c7838f50142138f7ac518ff3e4dca065d97 in the actions group
          - `#2002 <https://github.com/ansys/pyansys-geometry/pull/2002>`_


`0.10.7 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.10.7>`_ - May 05, 2025
=========================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - grpc driving dimensions stub implementation
          - `#1921 <https://github.com/ansys/pyansys-geometry/pull/1921>`_

        * - move coordinate systems stub to grpc layer
          - `#1943 <https://github.com/ansys/pyansys-geometry/pull/1943>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump numpy from 2.2.4 to 2.2.5
          - `#1935 <https://github.com/ansys/pyansys-geometry/pull/1935>`_

        * - bump pygltflib from 1.16.3 to 1.16.4
          - `#1940 <https://github.com/ansys/pyansys-geometry/pull/1940>`_

        * - bump notebook from 7.3.3 to 7.4.1 in the docs-deps group
          - `#1946 <https://github.com/ansys/pyansys-geometry/pull/1946>`_

        * - bump ansys-api-geometry from 0.4.57 to 0.4.58
          - `#1954 <https://github.com/ansys/pyansys-geometry/pull/1954>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update ``CONTRIBUTORS.md`` with the latest contributors
          - `#1938 <https://github.com/ansys/pyansys-geometry/pull/1938>`_

        * - ignore stackoverflow link
          - `#1957 <https://github.com/ansys/pyansys-geometry/pull/1957>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - core service launcher missing CADIntegration bin folder in path
          - `#1958 <https://github.com/ansys/pyansys-geometry/pull/1958>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.10.6
          - `#1933 <https://github.com/ansys/pyansys-geometry/pull/1933>`_

        * - use v4 of pyvista/setup-headless-display-action
          - `#1934 <https://github.com/ansys/pyansys-geometry/pull/1934>`_

        * - bump github/codeql-action from 3.28.15 to 3.28.16 in the actions group
          - `#1936 <https://github.com/ansys/pyansys-geometry/pull/1936>`_

        * - bump the actions group with 2 updates
          - `#1937 <https://github.com/ansys/pyansys-geometry/pull/1937>`_, `#1942 <https://github.com/ansys/pyansys-geometry/pull/1942>`_

        * - pre-commit automatic update
          - `#1941 <https://github.com/ansys/pyansys-geometry/pull/1941>`_

        * - bump github/codeql-action from 3.28.16 to 3.28.17 in the actions group
          - `#1956 <https://github.com/ansys/pyansys-geometry/pull/1956>`_


`0.10.6 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.10.6>`_ - April 22, 2025
===========================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - grpc prepare tools stub implementation
          - `#1914 <https://github.com/ansys/pyansys-geometry/pull/1914>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump PyVista and VTK versions (support Python 3.13)
          - `#1924 <https://github.com/ansys/pyansys-geometry/pull/1924>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - docstyle ordering
          - `#1925 <https://github.com/ansys/pyansys-geometry/pull/1925>`_

        * - adapt Native folder path for Linux and Windows
          - `#1932 <https://github.com/ansys/pyansys-geometry/pull/1932>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.10.5
          - `#1919 <https://github.com/ansys/pyansys-geometry/pull/1919>`_

        * - bump skitionek/notify-microsoft-teams to v1.0.9 in the actions group
          - `#1920 <https://github.com/ansys/pyansys-geometry/pull/1920>`_

        * - bump ansys/actions from 9.0.2 to 9.0.3 in the actions group
          - `#1923 <https://github.com/ansys/pyansys-geometry/pull/1923>`_

        * - fix issues with OSMesa installation and env variables set up
          - `#1927 <https://github.com/ansys/pyansys-geometry/pull/1927>`_

        * - bump ansys/actions from 9.0.3 to 9.0.6 in the actions group
          - `#1928 <https://github.com/ansys/pyansys-geometry/pull/1928>`_

        * - pre-commit automatic update
          - `#1930 <https://github.com/ansys/pyansys-geometry/pull/1930>`_

        * - fix unstable workflows for Linux (missing headless display)
          - `#1931 <https://github.com/ansys/pyansys-geometry/pull/1931>`_


`0.10.5 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.10.5>`_ - April 16, 2025
===========================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - grpc measurement tools stub implementation
          - `#1909 <https://github.com/ansys/pyansys-geometry/pull/1909>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump ansys-api-geometry from 0.4.56 to 0.4.57
          - `#1906 <https://github.com/ansys/pyansys-geometry/pull/1906>`_

        * - bump grpcio limits and handle erratic gRPC channel creation
          - `#1913 <https://github.com/ansys/pyansys-geometry/pull/1913>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update ``CONTRIBUTORS.md`` with the latest contributors
          - `#1907 <https://github.com/ansys/pyansys-geometry/pull/1907>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - is_suppressed is not available until 25R2
          - `#1916 <https://github.com/ansys/pyansys-geometry/pull/1916>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.10.4
          - `#1901 <https://github.com/ansys/pyansys-geometry/pull/1901>`_

        * - make doc releases dependent on GH and PyPI release
          - `#1902 <https://github.com/ansys/pyansys-geometry/pull/1902>`_

        * - bump ansys/actions from 9.0.1 to 9.0.2 in the actions group
          - `#1903 <https://github.com/ansys/pyansys-geometry/pull/1903>`_

        * - bump skitionek/notify-microsoft-teams from 190d4d92146df11f854709774a4dae6eaf5e2aa3 to fab6aca2609ba706ebc981d066278d47ab4af0fc in the actions group
          - `#1910 <https://github.com/ansys/pyansys-geometry/pull/1910>`_

        * - pre-commit automatic update
          - `#1911 <https://github.com/ansys/pyansys-geometry/pull/1911>`_

        * - bump the actions group with 2 updates
          - `#1915 <https://github.com/ansys/pyansys-geometry/pull/1915>`_

        * - update CHANGELOG for v0.8.3
          - `#1917 <https://github.com/ansys/pyansys-geometry/pull/1917>`_

        * - update CHANGELOG for v0.9.2
          - `#1918 <https://github.com/ansys/pyansys-geometry/pull/1918>`_


`0.10.4 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.10.4>`_ - April 09, 2025
===========================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - grpc named selection stub implementation
          - `#1899 <https://github.com/ansys/pyansys-geometry/pull/1899>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump ansys-api-geometry from 0.4.55 to 0.4.56
          - `#1896 <https://github.com/ansys/pyansys-geometry/pull/1896>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Ahmed body example for external aero simulation
          - `#1886 <https://github.com/ansys/pyansys-geometry/pull/1886>`_

        * - adding command for single example build
          - `#1893 <https://github.com/ansys/pyansys-geometry/pull/1893>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - geomdl dependency in conda-forge
          - `#1900 <https://github.com/ansys/pyansys-geometry/pull/1900>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.10.3
          - `#1894 <https://github.com/ansys/pyansys-geometry/pull/1894>`_

        * - upgrading to ansys/actions v9 and securing action usage
          - `#1895 <https://github.com/ansys/pyansys-geometry/pull/1895>`_

        * - bump the actions group with 3 updates
          - `#1897 <https://github.com/ansys/pyansys-geometry/pull/1897>`_

        * - remove whitelisting
          - `#1898 <https://github.com/ansys/pyansys-geometry/pull/1898>`_


`0.10.3 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.10.3>`_ - April 08, 2025
===========================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - grpc common layer architecture, bodies stub and admin stub implementation
          - `#1867 <https://github.com/ansys/pyansys-geometry/pull/1867>`_

        * - Logo detection
          - `#1873 <https://github.com/ansys/pyansys-geometry/pull/1873>`_

        * - DbuApplication stub relocation
          - `#1882 <https://github.com/ansys/pyansys-geometry/pull/1882>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump ansys-sphinx-theme[autoapi] from 1.3.3 to 1.4.2 in the docs-deps group
          - `#1874 <https://github.com/ansys/pyansys-geometry/pull/1874>`_

        * - bump ansys-api-geometry from 0.4.50 to 0.4.54
          - `#1875 <https://github.com/ansys/pyansys-geometry/pull/1875>`_

        * - bump pytest-cov from 6.0.0 to 6.1.0
          - `#1880 <https://github.com/ansys/pyansys-geometry/pull/1880>`_

        * - bump pytest-cov from 6.1.0 to 6.1.1
          - `#1888 <https://github.com/ansys/pyansys-geometry/pull/1888>`_

        * - bump ansys-api-geometry from 0.4.54 to 0.4.55
          - `#1889 <https://github.com/ansys/pyansys-geometry/pull/1889>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update ``CONTRIBUTORS.md`` with the latest contributors
          - `#1887 <https://github.com/ansys/pyansys-geometry/pull/1887>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Core Service install location on official build changed
          - `#1876 <https://github.com/ansys/pyansys-geometry/pull/1876>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.10.2
          - `#1870 <https://github.com/ansys/pyansys-geometry/pull/1870>`_

        * - pre-commit automatic update
          - `#1878 <https://github.com/ansys/pyansys-geometry/pull/1878>`_, `#1890 <https://github.com/ansys/pyansys-geometry/pull/1890>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - issue 1868 (named selection beams testing)
          - `#1871 <https://github.com/ansys/pyansys-geometry/pull/1871>`_


`0.10.2 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.10.2>`_ - March 26, 2025
===========================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - implement lazy loading of members in NamedSelection to speed up loading times when reading model
          - `#1869 <https://github.com/ansys/pyansys-geometry/pull/1869>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump beartype from 0.19.0 to 0.20.1
          - `#1862 <https://github.com/ansys/pyansys-geometry/pull/1862>`_

        * - bump beartype from 0.20.1 to 0.20.2
          - `#1864 <https://github.com/ansys/pyansys-geometry/pull/1864>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.10.1
          - `#1861 <https://github.com/ansys/pyansys-geometry/pull/1861>`_

        * - pre-commit automatic update
          - `#1866 <https://github.com/ansys/pyansys-geometry/pull/1866>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - issue 1801
          - `#1865 <https://github.com/ansys/pyansys-geometry/pull/1865>`_


`0.10.1 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.10.1>`_ - March 21, 2025
===========================================================================================

.. tab-set::


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.10.0
          - `#1856 <https://github.com/ansys/pyansys-geometry/pull/1856>`_

        * - bump version number to 0.11.dev0
          - `#1857 <https://github.com/ansys/pyansys-geometry/pull/1857>`_

        * - fix release notes inputs
          - `#1858 <https://github.com/ansys/pyansys-geometry/pull/1858>`_

        * - cleanup deprecated methods
          - `#1860 <https://github.com/ansys/pyansys-geometry/pull/1860>`_


`0.10.0 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.10.0>`_ - March 21, 2025
===========================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - named selection functionality
          - `#1768 <https://github.com/ansys/pyansys-geometry/pull/1768>`_

        * - Streaming upload support
          - `#1779 <https://github.com/ansys/pyansys-geometry/pull/1779>`_

        * - imprint curves without a sketch
          - `#1781 <https://github.com/ansys/pyansys-geometry/pull/1781>`_

        * - RGBA color support
          - `#1788 <https://github.com/ansys/pyansys-geometry/pull/1788>`_

        * - enhanced 3D bounding box implementation
          - `#1805 <https://github.com/ansys/pyansys-geometry/pull/1805>`_

        * - matrix helper methods
          - `#1806 <https://github.com/ansys/pyansys-geometry/pull/1806>`_

        * - component name setting
          - `#1820 <https://github.com/ansys/pyansys-geometry/pull/1820>`_

        * - enable runscript for CoreService
          - `#1821 <https://github.com/ansys/pyansys-geometry/pull/1821>`_

        * - enhanced beam implementation
          - `#1828 <https://github.com/ansys/pyansys-geometry/pull/1828>`_

        * - update api geometry dependency
          - `#1834 <https://github.com/ansys/pyansys-geometry/pull/1834>`_

        * - revolve faces and revolve faces by helix options
          - `#1842 <https://github.com/ansys/pyansys-geometry/pull/1842>`_

        * - Remove rounds
          - `#1851 <https://github.com/ansys/pyansys-geometry/pull/1851>`_

        * - blitz (2nd round)
          - `#1853 <https://github.com/ansys/pyansys-geometry/pull/1853>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump matplotlib from 3.10.0 to 3.10.1
          - `#1789 <https://github.com/ansys/pyansys-geometry/pull/1789>`_

        * - bump pytest from 8.3.4 to 8.3.5
          - `#1791 <https://github.com/ansys/pyansys-geometry/pull/1791>`_

        * - bump ansys-api-geometry from 0.4.42 to 0.4.43
          - `#1799 <https://github.com/ansys/pyansys-geometry/pull/1799>`_

        * - bump ansys-api-geometry from 0.4.43 to 0.4.44
          - `#1803 <https://github.com/ansys/pyansys-geometry/pull/1803>`_

        * - bump ansys-api-geometry from 0.4.44 to 0.4.45
          - `#1809 <https://github.com/ansys/pyansys-geometry/pull/1809>`_

        * - bump ansys-api-geometry from 0.4.45 to 0.4.46
          - `#1814 <https://github.com/ansys/pyansys-geometry/pull/1814>`_

        * - bump pytest-xvfb from 3.0.0 to 3.1.1
          - `#1822 <https://github.com/ansys/pyansys-geometry/pull/1822>`_

        * - bump ansys-api-geometry from 0.4.46 to 0.4.47
          - `#1827 <https://github.com/ansys/pyansys-geometry/pull/1827>`_

        * - bump notebook from 7.3.2 to 7.3.3 in the docs-deps group
          - `#1836 <https://github.com/ansys/pyansys-geometry/pull/1836>`_

        * - bump ansys-api-geometry from 0.4.47 to 0.4.48
          - `#1837 <https://github.com/ansys/pyansys-geometry/pull/1837>`_

        * - ansys api geometry 0.4.49
          - `#1840 <https://github.com/ansys/pyansys-geometry/pull/1840>`_

        * - bump numpy from 2.2.3 to 2.2.4
          - `#1844 <https://github.com/ansys/pyansys-geometry/pull/1844>`_

        * - bump ansys-api-geometry from 0.4.48 to 0.4.49
          - `#1845 <https://github.com/ansys/pyansys-geometry/pull/1845>`_

        * - bump ansys-api-geometry from 0.4.49 to 0.4.50
          - `#1849 <https://github.com/ansys/pyansys-geometry/pull/1849>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - flaky color test due to random face assignment
          - `#1794 <https://github.com/ansys/pyansys-geometry/pull/1794>`_

        * - fix parasolid export tests with more precise backend descriptor
          - `#1802 <https://github.com/ansys/pyansys-geometry/pull/1802>`_

        * - translating sketch issues when using a custom default unit
          - `#1808 <https://github.com/ansys/pyansys-geometry/pull/1808>`_

        * - edge start and end were not being mapped correctly
          - `#1816 <https://github.com/ansys/pyansys-geometry/pull/1816>`_

        * - change Core Service path to executable/DLL after renaming
          - `#1841 <https://github.com/ansys/pyansys-geometry/pull/1841>`_

        * - tessellation options were not extended to component/face methods
          - `#1850 <https://github.com/ansys/pyansys-geometry/pull/1850>`_

        * - named selection import test
          - `#1854 <https://github.com/ansys/pyansys-geometry/pull/1854>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.9.1
          - `#1787 <https://github.com/ansys/pyansys-geometry/pull/1787>`_

        * - pre-commit automatic update
          - `#1792 <https://github.com/ansys/pyansys-geometry/pull/1792>`_, `#1810 <https://github.com/ansys/pyansys-geometry/pull/1810>`_, `#1846 <https://github.com/ansys/pyansys-geometry/pull/1846>`_

        * - remove DMS from pipelines and use core service images only
          - `#1812 <https://github.com/ansys/pyansys-geometry/pull/1812>`_

        * - use ansys/action/hk-automerge-prs
          - `#1824 <https://github.com/ansys/pyansys-geometry/pull/1824>`_

        * - upgrading to new features in ansys/actions v8.2
          - `#1852 <https://github.com/ansys/pyansys-geometry/pull/1852>`_

        * - cleanup blitz PR
          - `#1855 <https://github.com/ansys/pyansys-geometry/pull/1855>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Skip test due to SC bug
          - `#1798 <https://github.com/ansys/pyansys-geometry/pull/1798>`_

        * - improve share topology test
          - `#1804 <https://github.com/ansys/pyansys-geometry/pull/1804>`_

        * - Fix slow tests
          - `#1832 <https://github.com/ansys/pyansys-geometry/pull/1832>`_

        * - adding inward shell
          - `#1833 <https://github.com/ansys/pyansys-geometry/pull/1833>`_


`0.9.2 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.9.2>`_ - April 16, 2025
=========================================================================================

Fixed
^^^^^

- is_suppressed is not available until 25R2 `#1916 <https://github.com/ansys/pyansys-geometry/pull/1916>`_

`0.9.1 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.9.1>`_ - 2025-02-28
=====================================================================================

Added
^^^^^

- offset faces set radius implementation + testing `#1769 <https://github.com/ansys/pyansys-geometry/pull/1769>`_
- separate graphics target `#1782 <https://github.com/ansys/pyansys-geometry/pull/1782>`_


Dependencies
^^^^^^^^^^^^

- bump the docs-deps group with 2 updates `#1762 <https://github.com/ansys/pyansys-geometry/pull/1762>`_
- bump ansys-api-geometry from 0.4.38 to 0.4.40 `#1763 <https://github.com/ansys/pyansys-geometry/pull/1763>`_
- bump ansys-sphinx-theme[autoapi] from 1.3.1 to 1.3.2 in the docs-deps group `#1766 <https://github.com/ansys/pyansys-geometry/pull/1766>`_
- bump ansys-tools-visualization-interface from 0.8.1 to 0.8.3 `#1767 <https://github.com/ansys/pyansys-geometry/pull/1767>`_
- bump sphinx from 8.2.0 to 8.2.1 in the docs-deps group `#1772 <https://github.com/ansys/pyansys-geometry/pull/1772>`_
- bump ansys-api-geometry from 0.4.40 to 0.4.42 `#1773 <https://github.com/ansys/pyansys-geometry/pull/1773>`_
- temporary workaround for using trusted publisher approach `#1783 <https://github.com/ansys/pyansys-geometry/pull/1783>`_


Fixed
^^^^^

- allow setting max message length for send operations `#1775 <https://github.com/ansys/pyansys-geometry/pull/1775>`_
- typo in labeler.yml file `#1776 <https://github.com/ansys/pyansys-geometry/pull/1776>`_
- docker build process failing on helper script `#1785 <https://github.com/ansys/pyansys-geometry/pull/1785>`_


Maintenance
^^^^^^^^^^^

- bump dev version to 0.10.dev0 `#1752 <https://github.com/ansys/pyansys-geometry/pull/1752>`_
- update CHANGELOG for v0.9.0 `#1760 <https://github.com/ansys/pyansys-geometry/pull/1760>`_
- pre-commit automatic update `#1770 <https://github.com/ansys/pyansys-geometry/pull/1770>`_

`0.9.0 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.9.0>`_ - 2025-02-18
=====================================================================================

Added
^^^^^

- design activation changes `#1707 <https://github.com/ansys/pyansys-geometry/pull/1707>`_
- add contributors `#1708 <https://github.com/ansys/pyansys-geometry/pull/1708>`_
- Implementation of inspect & repair geometry `#1712 <https://github.com/ansys/pyansys-geometry/pull/1712>`_
- launch core service from envar `#1716 <https://github.com/ansys/pyansys-geometry/pull/1716>`_
- workflow enhancements for better tool results `#1723 <https://github.com/ansys/pyansys-geometry/pull/1723>`_
- add face color, round info, bring measure tools to linux `#1732 <https://github.com/ansys/pyansys-geometry/pull/1732>`_
- conservative approach to single design per modeler `#1740 <https://github.com/ansys/pyansys-geometry/pull/1740>`_
- export glb `#1741 <https://github.com/ansys/pyansys-geometry/pull/1741>`_
- allow plotting of individual faces `#1757 <https://github.com/ansys/pyansys-geometry/pull/1757>`_


Dependencies
^^^^^^^^^^^^

- bump ansys-api-geometry from 0.4.33 to 0.4.34 `#1709 <https://github.com/ansys/pyansys-geometry/pull/1709>`_
- bump ansys-sphinx-theme[autoapi] from 1.2.6 to 1.2.7 in the docs-deps group `#1719 <https://github.com/ansys/pyansys-geometry/pull/1719>`_
- bump ansys-api-geometry from 0.4.34 to 0.4.35 `#1720 <https://github.com/ansys/pyansys-geometry/pull/1720>`_
- bump ansys-sphinx-theme[autoapi] from 1.2.7 to 1.3.0 in the docs-deps group `#1726 <https://github.com/ansys/pyansys-geometry/pull/1726>`_
- bump ansys-sphinx-theme[autoapi] from 1.3.0 to 1.3.1 in the docs-deps group `#1728 <https://github.com/ansys/pyansys-geometry/pull/1728>`_
- bump ansys-api-geometry from 0.4.35 to 0.4.36 `#1729 <https://github.com/ansys/pyansys-geometry/pull/1729>`_
- bump trame-vtk from 2.8.14 to 2.8.15 `#1736 <https://github.com/ansys/pyansys-geometry/pull/1736>`_
- bump jupytext from 1.16.6 to 1.16.7 in the docs-deps group `#1742 <https://github.com/ansys/pyansys-geometry/pull/1742>`_
- bump ansys-api-geometry from 0.4.36 to 0.4.37 `#1743 <https://github.com/ansys/pyansys-geometry/pull/1743>`_
- bump myst-parser from 4.0.0 to 4.0.1 in the docs-deps group `#1744 <https://github.com/ansys/pyansys-geometry/pull/1744>`_
- bump ansys-api-geometry from 0.4.37 to 0.4.38 `#1746 <https://github.com/ansys/pyansys-geometry/pull/1746>`_
- bump numpy from 2.2.2 to 2.2.3 `#1747 <https://github.com/ansys/pyansys-geometry/pull/1747>`_
- bump panel from 1.6.0 to 1.6.1 `#1749 <https://github.com/ansys/pyansys-geometry/pull/1749>`_
- bump scipy from 1.15.1 to 1.15.2 `#1756 <https://github.com/ansys/pyansys-geometry/pull/1756>`_


Documentation
^^^^^^^^^^^^^

- update CONTRIBUTING.md `#1730 <https://github.com/ansys/pyansys-geometry/pull/1730>`_


Fixed
^^^^^

- re enable fmd tests `#1711 <https://github.com/ansys/pyansys-geometry/pull/1711>`_
- support body mirror on linux `#1714 <https://github.com/ansys/pyansys-geometry/pull/1714>`_
- use sketch plane for imprint/project curves `#1715 <https://github.com/ansys/pyansys-geometry/pull/1715>`_
- revert boolean ops logic and hold-off on commands-based implementation (temporarily) `#1725 <https://github.com/ansys/pyansys-geometry/pull/1725>`_
- Linux Core Service docker file was missing a dependency `#1758 <https://github.com/ansys/pyansys-geometry/pull/1758>`_


Maintenance
^^^^^^^^^^^

- update CHANGELOG for v0.8.2 `#1706 <https://github.com/ansys/pyansys-geometry/pull/1706>`_
- pre-commit automatic update `#1717 <https://github.com/ansys/pyansys-geometry/pull/1717>`_, `#1737 <https://github.com/ansys/pyansys-geometry/pull/1737>`_
- update SECURITY.md versions supported `#1722 <https://github.com/ansys/pyansys-geometry/pull/1722>`_
- keep simba-plugin-geometry tag `#1739 <https://github.com/ansys/pyansys-geometry/pull/1739>`_
- enhancements to GLB export and object ``plot()`` methods `#1750 <https://github.com/ansys/pyansys-geometry/pull/1750>`_
- clean up deprecation warning for trapezoid class and add more info on deprecation `#1754 <https://github.com/ansys/pyansys-geometry/pull/1754>`_


Test
^^^^

- verifying issue with empty intersect and temporal body creation `#1258 <https://github.com/ansys/pyansys-geometry/pull/1258>`_
- Expand pattern tests `#1713 <https://github.com/ansys/pyansys-geometry/pull/1713>`_
- set body name `#1727 <https://github.com/ansys/pyansys-geometry/pull/1727>`_
- activate 8 linux tests `#1745 <https://github.com/ansys/pyansys-geometry/pull/1745>`_

`0.8.3 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.8.3>`_ - April 16, 2025
=========================================================================================

Fixed
^^^^^

- is_suppressed is not available until 25R2 `#1916 <https://github.com/ansys/pyansys-geometry/pull/1916>`_

`0.8.2 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.8.2>`_ - 2025-01-29
=====================================================================================

Added
^^^^^

- create a fillet on an edge/face `#1621 <https://github.com/ansys/pyansys-geometry/pull/1621>`_
- create a full fillet between multiple faces `#1623 <https://github.com/ansys/pyansys-geometry/pull/1623>`_
- extrude existing faces, setup face offset relationships `#1628 <https://github.com/ansys/pyansys-geometry/pull/1628>`_
- interference repair tool `#1633 <https://github.com/ansys/pyansys-geometry/pull/1633>`_
- extrude existing edges to create surface bodies `#1638 <https://github.com/ansys/pyansys-geometry/pull/1638>`_
- create and modify linear patterns `#1641 <https://github.com/ansys/pyansys-geometry/pull/1641>`_
- body suppression state `#1643 <https://github.com/ansys/pyansys-geometry/pull/1643>`_
- parameters refurbished `#1647 <https://github.com/ansys/pyansys-geometry/pull/1647>`_
- rename object `#1648 <https://github.com/ansys/pyansys-geometry/pull/1648>`_
- surface body from trimmed curves `#1650 <https://github.com/ansys/pyansys-geometry/pull/1650>`_
- create circular and fill patterns `#1653 <https://github.com/ansys/pyansys-geometry/pull/1653>`_
- find fix simplify `#1661 <https://github.com/ansys/pyansys-geometry/pull/1661>`_
- replace face `#1664 <https://github.com/ansys/pyansys-geometry/pull/1664>`_
- commands for merge and intersect `#1665 <https://github.com/ansys/pyansys-geometry/pull/1665>`_
- revolve faces a set distance, up to another object, or by a helix `#1666 <https://github.com/ansys/pyansys-geometry/pull/1666>`_
- add split body and tests `#1669 <https://github.com/ansys/pyansys-geometry/pull/1669>`_
- enable get/set persistent ids for stride import/export `#1671 <https://github.com/ansys/pyansys-geometry/pull/1671>`_
- find and fix edge methods `#1672 <https://github.com/ansys/pyansys-geometry/pull/1672>`_
- shell methods `#1673 <https://github.com/ansys/pyansys-geometry/pull/1673>`_
- implementation of NURBS curves `#1675 <https://github.com/ansys/pyansys-geometry/pull/1675>`_
- get assigned material `#1684 <https://github.com/ansys/pyansys-geometry/pull/1684>`_
- matrix rotation and translation `#1689 <https://github.com/ansys/pyansys-geometry/pull/1689>`_
- is_core_service BackendType static method `#1692 <https://github.com/ansys/pyansys-geometry/pull/1692>`_
- export and download stride format `#1698 <https://github.com/ansys/pyansys-geometry/pull/1698>`_
- blitz development `#1701 <https://github.com/ansys/pyansys-geometry/pull/1701>`_


Dependencies
^^^^^^^^^^^^

- bump ansys-tools-visualization-interface from 0.7.0 to 0.8.1 `#1640 <https://github.com/ansys/pyansys-geometry/pull/1640>`_
- bump ansys-api-geometry from 0.4.27 to 0.4.28 `#1644 <https://github.com/ansys/pyansys-geometry/pull/1644>`_
- bump sphinx-autodoc-typehints from 3.0.0 to 3.0.1 in the docs-deps group `#1651 <https://github.com/ansys/pyansys-geometry/pull/1651>`_
- bump ansys-api-geometry from 0.4.28 to 0.4.30 `#1652 <https://github.com/ansys/pyansys-geometry/pull/1652>`_
- bump protobuf from 5.28.3 to 5.29.3 in the grpc-deps group across 1 directory `#1656 <https://github.com/ansys/pyansys-geometry/pull/1656>`_
- bump numpy from 2.2.1 to 2.2.2 `#1662 <https://github.com/ansys/pyansys-geometry/pull/1662>`_
- bump ansys-api-geometry from 0.4.30 to 0.4.31 `#1663 <https://github.com/ansys/pyansys-geometry/pull/1663>`_
- bump ansys api geometry from 0.4.30 to 0.4.32 `#1677 <https://github.com/ansys/pyansys-geometry/pull/1677>`_
- bump ansys-api-geometry from 0.4.31 to 0.4.32 `#1681 <https://github.com/ansys/pyansys-geometry/pull/1681>`_
- bump panel from 1.5.5 to 1.6.0 `#1682 <https://github.com/ansys/pyansys-geometry/pull/1682>`_
- bump semver from 3.0.2 to 3.0.4 `#1687 <https://github.com/ansys/pyansys-geometry/pull/1687>`_
- bump ansys-api-geometry from 0.4.32 to 0.4.33 `#1695 <https://github.com/ansys/pyansys-geometry/pull/1695>`_
- bump nbconvert from 7.16.5 to 7.16.6 in the docs-deps group `#1700 <https://github.com/ansys/pyansys-geometry/pull/1700>`_


Fixed
^^^^^

- reactivate test on failing extra edges test `#1396 <https://github.com/ansys/pyansys-geometry/pull/1396>`_
- filter set export id to only CoreService based backends `#1685 <https://github.com/ansys/pyansys-geometry/pull/1685>`_
- cleanup unsupported module `#1690 <https://github.com/ansys/pyansys-geometry/pull/1690>`_
- disable unimplemented tests `#1691 <https://github.com/ansys/pyansys-geometry/pull/1691>`_
- tech review fixes for blitz branch `#1703 <https://github.com/ansys/pyansys-geometry/pull/1703>`_


Maintenance
^^^^^^^^^^^

- update CHANGELOG for v0.8.1 `#1639 <https://github.com/ansys/pyansys-geometry/pull/1639>`_
- whitelist semver package temporarily `#1657 <https://github.com/ansys/pyansys-geometry/pull/1657>`_
- reverting semver package whitelist since problematic version is yanked `#1659 <https://github.com/ansys/pyansys-geometry/pull/1659>`_
- pre-commit automatic update `#1667 <https://github.com/ansys/pyansys-geometry/pull/1667>`_, `#1696 <https://github.com/ansys/pyansys-geometry/pull/1696>`_
- ensure design is closed on test exit `#1680 <https://github.com/ansys/pyansys-geometry/pull/1680>`_
- use dedicate pygeometry-ci-2 runner `#1693 <https://github.com/ansys/pyansys-geometry/pull/1693>`_
- remove towncrier info duplicates `#1702 <https://github.com/ansys/pyansys-geometry/pull/1702>`_


Test
^^^^

- add more find and fix tests for repair tools `#1645 <https://github.com/ansys/pyansys-geometry/pull/1645>`_
- Add some new tests `#1670 <https://github.com/ansys/pyansys-geometry/pull/1670>`_
- add unit tests for 3 repair tools `#1683 <https://github.com/ansys/pyansys-geometry/pull/1683>`_

`0.8.1 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.8.1>`_ - 2025-01-15
=====================================================================================

Dependencies
^^^^^^^^^^^^

- bump ansys-api-geometry from 0.4.26 to 0.4.27 `#1634 <https://github.com/ansys/pyansys-geometry/pull/1634>`_


Fixed
^^^^^

- release issues encountered `#1637 <https://github.com/ansys/pyansys-geometry/pull/1637>`_


Maintenance
^^^^^^^^^^^

- update CHANGELOG for v0.8.0 `#1636 <https://github.com/ansys/pyansys-geometry/pull/1636>`_

`0.8.0 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.8.0>`_ - 2025-01-15
=====================================================================================

Added
^^^^^

- active support for Python 3.13 `#1481 <https://github.com/ansys/pyansys-geometry/pull/1481>`_
- add chamfer tool `#1495 <https://github.com/ansys/pyansys-geometry/pull/1495>`_
- allow version input to automatically consider the nuances for the Ansys Student version `#1548 <https://github.com/ansys/pyansys-geometry/pull/1548>`_
- adapt health check timeout algorithm `#1559 <https://github.com/ansys/pyansys-geometry/pull/1559>`_
- add core service support `#1571 <https://github.com/ansys/pyansys-geometry/pull/1571>`_
- enable (partially) prepare and repair tools in Core Service `#1580 <https://github.com/ansys/pyansys-geometry/pull/1580>`_
- create launcher for core services `#1587 <https://github.com/ansys/pyansys-geometry/pull/1587>`_


Dependencies
^^^^^^^^^^^^

- bump ansys-api-geometry from 0.4.16 to 0.4.17 `#1547 <https://github.com/ansys/pyansys-geometry/pull/1547>`_
- bump ansys-sphinx-theme[autoapi] from 1.2.1 to 1.2.2 in the docs-deps group `#1549 <https://github.com/ansys/pyansys-geometry/pull/1549>`_
- bump ansys-api-geometry from 0.4.17 to 0.4.18 `#1550 <https://github.com/ansys/pyansys-geometry/pull/1550>`_
- bump ansys-tools-visualization-interface from 0.5.0 to 0.6.0 `#1554 <https://github.com/ansys/pyansys-geometry/pull/1554>`_
- bump pytest from 8.3.3 to 8.3.4 `#1562 <https://github.com/ansys/pyansys-geometry/pull/1562>`_
- bump six from 1.16.0 to 1.17.0 `#1568 <https://github.com/ansys/pyansys-geometry/pull/1568>`_
- bump the docs-deps group across 1 directory with 2 updates `#1570 <https://github.com/ansys/pyansys-geometry/pull/1570>`_
- bump ansys-api-geometry from 0.4.18 to 0.4.20 `#1574 <https://github.com/ansys/pyansys-geometry/pull/1574>`_
- bump numpy from 2.1.3 to 2.2.0 `#1575 <https://github.com/ansys/pyansys-geometry/pull/1575>`_
- bump ansys-api-geometry from 0.4.20 to 0.4.23 `#1581 <https://github.com/ansys/pyansys-geometry/pull/1581>`_
- bump ansys-api-geometry from 0.4.23 to 0.4.24 `#1582 <https://github.com/ansys/pyansys-geometry/pull/1582>`_
- bump ansys-tools-visualization-interface from 0.6.0 to 0.6.1 `#1583 <https://github.com/ansys/pyansys-geometry/pull/1583>`_
- bump ansys-tools-visualization-interface from 0.6.1 to 0.6.2 `#1586 <https://github.com/ansys/pyansys-geometry/pull/1586>`_
- avoid the usage of attrs 24.3.0 (temporary) `#1589 <https://github.com/ansys/pyansys-geometry/pull/1589>`_
- bump jupytext from 1.16.4 to 1.16.5 in the docs-deps group `#1590 <https://github.com/ansys/pyansys-geometry/pull/1590>`_
- bump jupytext from 1.16.5 to 1.16.6 in the docs-deps group `#1593 <https://github.com/ansys/pyansys-geometry/pull/1593>`_
- bump panel from 1.5.4 to 1.5.5 `#1595 <https://github.com/ansys/pyansys-geometry/pull/1595>`_
- bump ansys-sphinx-theme[autoapi] from 1.2.3 to 1.2.4 in the docs-deps group `#1597 <https://github.com/ansys/pyansys-geometry/pull/1597>`_
- bump notebook from 7.3.1 to 7.3.2 in the docs-deps group `#1598 <https://github.com/ansys/pyansys-geometry/pull/1598>`_
- bump numpy from 2.2.0 to 2.2.1 `#1599 <https://github.com/ansys/pyansys-geometry/pull/1599>`_
- bump ansys-tools-path from 0.7.0 to 0.7.1 `#1600 <https://github.com/ansys/pyansys-geometry/pull/1600>`_
- bump nbsphinx from 0.9.5 to 0.9.6 in the docs-deps group `#1602 <https://github.com/ansys/pyansys-geometry/pull/1602>`_
- bump nbconvert from 7.16.4 to 7.16.5 in the docs-deps group `#1609 <https://github.com/ansys/pyansys-geometry/pull/1609>`_
- bump ansys-api-geometry from 0.4.24 to 0.4.25 `#1610 <https://github.com/ansys/pyansys-geometry/pull/1610>`_
- bump sphinx-autodoc-typehints from 2.5.0 to 3.0.0 in the docs-deps group `#1611 <https://github.com/ansys/pyansys-geometry/pull/1611>`_
- bump scipy from 1.14.1 to 1.15.0 `#1612 <https://github.com/ansys/pyansys-geometry/pull/1612>`_
- bump trame-vtk from 2.8.12 to 2.8.13 `#1616 <https://github.com/ansys/pyansys-geometry/pull/1616>`_
- bump trame-vtk from 2.8.13 to 2.8.14 `#1617 <https://github.com/ansys/pyansys-geometry/pull/1617>`_
- bump ansys-tools-visualization-interface from 0.6.2 to 0.7.0 `#1619 <https://github.com/ansys/pyansys-geometry/pull/1619>`_
- bump ansys-sphinx-theme[autoapi] from 1.2.4 to 1.2.6 in the docs-deps group `#1624 <https://github.com/ansys/pyansys-geometry/pull/1624>`_
- bump scipy from 1.15.0 to 1.15.1 `#1625 <https://github.com/ansys/pyansys-geometry/pull/1625>`_
- bump ansys-api-geometry from 0.4.25 to 0.4.26 `#1626 <https://github.com/ansys/pyansys-geometry/pull/1626>`_


Documentation
^^^^^^^^^^^^^

- Explain how to report a security issue. `#1605 <https://github.com/ansys/pyansys-geometry/pull/1605>`_


Fixed
^^^^^

- numpydoc warnings `#1556 <https://github.com/ansys/pyansys-geometry/pull/1556>`_
- vtk/pyvista issues `#1584 <https://github.com/ansys/pyansys-geometry/pull/1584>`_
- make_child_logger only takes 2 args. `#1603 <https://github.com/ansys/pyansys-geometry/pull/1603>`_
- FAQ on install `#1631 <https://github.com/ansys/pyansys-geometry/pull/1631>`_


Maintenance
^^^^^^^^^^^

- pre-commit automatic update `#1366 <https://github.com/ansys/pyansys-geometry/pull/1366>`_, `#1552 <https://github.com/ansys/pyansys-geometry/pull/1552>`_, `#1561 <https://github.com/ansys/pyansys-geometry/pull/1561>`_, `#1588 <https://github.com/ansys/pyansys-geometry/pull/1588>`_, `#1601 <https://github.com/ansys/pyansys-geometry/pull/1601>`_, `#1615 <https://github.com/ansys/pyansys-geometry/pull/1615>`_, `#1630 <https://github.com/ansys/pyansys-geometry/pull/1630>`_
- update CHANGELOG for v0.7.6 `#1545 <https://github.com/ansys/pyansys-geometry/pull/1545>`_
- change release artifacts self-hosted runner `#1546 <https://github.com/ansys/pyansys-geometry/pull/1546>`_
- automerge pre-commit.ci PRs `#1553 <https://github.com/ansys/pyansys-geometry/pull/1553>`_
- bump pyvista/setup-headless-display-action to v3 `#1555 <https://github.com/ansys/pyansys-geometry/pull/1555>`_
- decouple unstable image promotion `#1591 <https://github.com/ansys/pyansys-geometry/pull/1591>`_
- skip unnecessary stages when containers are the same `#1592 <https://github.com/ansys/pyansys-geometry/pull/1592>`_
- Numpy is already imported at the top of the module. `#1604 <https://github.com/ansys/pyansys-geometry/pull/1604>`_
- update license year using pre-commit hook `#1608 <https://github.com/ansys/pyansys-geometry/pull/1608>`_

`0.7.6 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.7.6>`_ - 2024-11-19
=====================================================================================

Added
^^^^^

- allow for some additional extrusion direction names `#1534 <https://github.com/ansys/pyansys-geometry/pull/1534>`_


Dependencies
^^^^^^^^^^^^

- bump ansys-sphinx-theme[autoapi] from 1.1.7 to 1.2.0 in the docs-deps group `#1520 <https://github.com/ansys/pyansys-geometry/pull/1520>`_
- bump ansys-tools-visualization-interface from 0.4.7 to 0.5.0 `#1521 <https://github.com/ansys/pyansys-geometry/pull/1521>`_
- bump numpy from 2.1.2 to 2.1.3 `#1522 <https://github.com/ansys/pyansys-geometry/pull/1522>`_
- bump ansys-api-geometry from 0.4.13 to 0.4.14 `#1525 <https://github.com/ansys/pyansys-geometry/pull/1525>`_
- bump ansys-api-geometry from 0.4.14 to 0.4.15 `#1529 <https://github.com/ansys/pyansys-geometry/pull/1529>`_
- bump pint from 0.24.3 to 0.24.4 `#1530 <https://github.com/ansys/pyansys-geometry/pull/1530>`_
- bump trame-vtk from 2.8.11 to 2.8.12 `#1531 <https://github.com/ansys/pyansys-geometry/pull/1531>`_
- bump ansys-sphinx-theme[autoapi] from 1.2.0 to 1.2.1 in the docs-deps group `#1535 <https://github.com/ansys/pyansys-geometry/pull/1535>`_
- bump panel from 1.5.3 to 1.5.4 `#1536 <https://github.com/ansys/pyansys-geometry/pull/1536>`_
- bump ansys-tools-path from 0.6.0 to 0.7.0 `#1537 <https://github.com/ansys/pyansys-geometry/pull/1537>`_
- bump ansys-api-geometry from 0.4.15 to 0.4.16 `#1538 <https://github.com/ansys/pyansys-geometry/pull/1538>`_
- limit upper version on grpcio & grpcio-health-checking to 1.68 `#1544 <https://github.com/ansys/pyansys-geometry/pull/1544>`_


Documentation
^^^^^^^^^^^^^

- typo with the docstrings `#1524 <https://github.com/ansys/pyansys-geometry/pull/1524>`_
- change max header links before more dropdown `#1527 <https://github.com/ansys/pyansys-geometry/pull/1527>`_


Maintenance
^^^^^^^^^^^

- update CHANGELOG for v0.7.5 `#1519 <https://github.com/ansys/pyansys-geometry/pull/1519>`_
- pre-commit automatic update `#1523 <https://github.com/ansys/pyansys-geometry/pull/1523>`_, `#1532 <https://github.com/ansys/pyansys-geometry/pull/1532>`_, `#1543 <https://github.com/ansys/pyansys-geometry/pull/1543>`_
- bump codecov/codecov-action from 4 to 5 in the actions group `#1541 <https://github.com/ansys/pyansys-geometry/pull/1541>`_

`0.7.5 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.7.5>`_ - 2024-10-31
=====================================================================================

Added
^^^^^

- create body from surface `#1454 <https://github.com/ansys/pyansys-geometry/pull/1454>`_
- performance enhancements to plotter `#1496 <https://github.com/ansys/pyansys-geometry/pull/1496>`_
- allow picking from easy access methods `#1499 <https://github.com/ansys/pyansys-geometry/pull/1499>`_
- implement cut operation in extrude sketch `#1510 <https://github.com/ansys/pyansys-geometry/pull/1510>`_
- caching bodies to avoid unnecessary object creation `#1513 <https://github.com/ansys/pyansys-geometry/pull/1513>`_
- enable retrieval of service logs (via API) `#1515 <https://github.com/ansys/pyansys-geometry/pull/1515>`_


Dependencies
^^^^^^^^^^^^

- bump sphinx from 8.1.0 to 8.1.3 in the docs-deps group `#1479 <https://github.com/ansys/pyansys-geometry/pull/1479>`_
- bump ansys-sphinx-theme[autoapi] from 1.1.4 to 1.1.5 in the docs-deps group `#1482 <https://github.com/ansys/pyansys-geometry/pull/1482>`_
- bump the grpc-deps group across 1 directory with 3 updates `#1487 <https://github.com/ansys/pyansys-geometry/pull/1487>`_
- bump ansys-sphinx-theme[autoapi] from 1.1.5 to 1.1.6 in the docs-deps group `#1493 <https://github.com/ansys/pyansys-geometry/pull/1493>`_
- bump trame-vtk from 2.8.10 to 2.8.11 `#1494 <https://github.com/ansys/pyansys-geometry/pull/1494>`_
- bump ansys-api-geometry from 0.4.11 to 0.4.12 `#1502 <https://github.com/ansys/pyansys-geometry/pull/1502>`_
- bump protobuf from 5.28.2 to 5.28.3 in the grpc-deps group `#1505 <https://github.com/ansys/pyansys-geometry/pull/1505>`_
- bump ansys-sphinx-theme[autoapi] from 1.1.6 to 1.1.7 in the docs-deps group `#1506 <https://github.com/ansys/pyansys-geometry/pull/1506>`_
- bump ansys-tools-visualization-interface from 0.4.6 to 0.4.7 `#1507 <https://github.com/ansys/pyansys-geometry/pull/1507>`_
- bump panel from 1.5.2 to 1.5.3 `#1508 <https://github.com/ansys/pyansys-geometry/pull/1508>`_
- bump ansys-api-geometry from 0.4.12 to 0.4.13 `#1512 <https://github.com/ansys/pyansys-geometry/pull/1512>`_
- bump the grpc-deps group with 2 updates `#1517 <https://github.com/ansys/pyansys-geometry/pull/1517>`_
- bump pytest-cov from 5.0.0 to 6.0.0 `#1518 <https://github.com/ansys/pyansys-geometry/pull/1518>`_


Documentation
^^^^^^^^^^^^^

- avoid having a drop down in the top navigation bar `#1485 <https://github.com/ansys/pyansys-geometry/pull/1485>`_
- provide information on how to build a single example `#1490 <https://github.com/ansys/pyansys-geometry/pull/1490>`_
- add example file to download in the test `#1501 <https://github.com/ansys/pyansys-geometry/pull/1501>`_
- revisit examples to make sure they are properly styled `#1509 <https://github.com/ansys/pyansys-geometry/pull/1509>`_
- align landing page layout with UI/UX requirements `#1511 <https://github.com/ansys/pyansys-geometry/pull/1511>`_


Fixed
^^^^^

- static search options `#1478 <https://github.com/ansys/pyansys-geometry/pull/1478>`_
- respect product_version when launching geometry service `#1486 <https://github.com/ansys/pyansys-geometry/pull/1486>`_


Maintenance
^^^^^^^^^^^

- update CHANGELOG for v0.7.4 `#1476 <https://github.com/ansys/pyansys-geometry/pull/1476>`_
- pre-commit automatic update `#1480 <https://github.com/ansys/pyansys-geometry/pull/1480>`_, `#1516 <https://github.com/ansys/pyansys-geometry/pull/1516>`_
- avoid linkcheck on changelog (unnecessary) `#1489 <https://github.com/ansys/pyansys-geometry/pull/1489>`_
- update CONTRIBUTORS `#1492 <https://github.com/ansys/pyansys-geometry/pull/1492>`_
- allowing new tags for Windows Core Service `#1497 <https://github.com/ansys/pyansys-geometry/pull/1497>`_
- simplify vulnerabilities check `#1504 <https://github.com/ansys/pyansys-geometry/pull/1504>`_

`0.7.4 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.7.4>`_ - 2024-10-11
=====================================================================================

Dependencies
^^^^^^^^^^^^

- bump sphinx from 8.0.2 to 8.1.0 in the docs-deps group `#1470 <https://github.com/ansys/pyansys-geometry/pull/1470>`_
- bump ansys-api-geometry from 0.4.10 to 0.4.11 `#1473 <https://github.com/ansys/pyansys-geometry/pull/1473>`_
- bump ansys-sphinx-theme to v1.1.3 `#1475 <https://github.com/ansys/pyansys-geometry/pull/1475>`_


Fixed
^^^^^

- solving intersphinx warnings on paths `#1469 <https://github.com/ansys/pyansys-geometry/pull/1469>`_
- ``check_input_types`` not working with forward refs `#1471 <https://github.com/ansys/pyansys-geometry/pull/1471>`_
- ``share_topology`` is available on 24R2 `#1472 <https://github.com/ansys/pyansys-geometry/pull/1472>`_


Maintenance
^^^^^^^^^^^

- update CHANGELOG for v0.7.3 `#1466 <https://github.com/ansys/pyansys-geometry/pull/1466>`_

`0.7.3 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.7.3>`_ - 2024-10-09
=====================================================================================

Added
^^^^^

- use service colors in plotter (upon request) `#1376 <https://github.com/ansys/pyansys-geometry/pull/1376>`_
- capability to close designs (also on ``modeler.exit()``) `#1409 <https://github.com/ansys/pyansys-geometry/pull/1409>`_
- prioritize user-defined SPACECLAIM_MODE env var `#1440 <https://github.com/ansys/pyansys-geometry/pull/1440>`_
- verifying Linux service also accepts colors `#1451 <https://github.com/ansys/pyansys-geometry/pull/1451>`_


Dependencies
^^^^^^^^^^^^

- bump protobuf from 5.28.0 to 5.28.1 in the grpc-deps group `#1424 <https://github.com/ansys/pyansys-geometry/pull/1424>`_
- bump the docs-deps group with 2 updates `#1425 <https://github.com/ansys/pyansys-geometry/pull/1425>`_, `#1436 <https://github.com/ansys/pyansys-geometry/pull/1436>`_
- bump ansys-tools-visualization-interface from 0.4.3 to 0.4.4 `#1426 <https://github.com/ansys/pyansys-geometry/pull/1426>`_
- bump pytest from 8.3.2 to 8.3.3 `#1427 <https://github.com/ansys/pyansys-geometry/pull/1427>`_
- bump panel from 1.4.5 to 1.5.0 `#1428 <https://github.com/ansys/pyansys-geometry/pull/1428>`_
- bump protobuf from 5.28.1 to 5.28.2 in the grpc-deps group `#1435 <https://github.com/ansys/pyansys-geometry/pull/1435>`_
- bump the grpc-deps group with 3 updates `#1442 <https://github.com/ansys/pyansys-geometry/pull/1442>`_
- bump beartype from 0.18.5 to 0.19.0 `#1443 <https://github.com/ansys/pyansys-geometry/pull/1443>`_
- bump panel from 1.5.0 to 1.5.1 `#1444 <https://github.com/ansys/pyansys-geometry/pull/1444>`_
- bump ansys-sphinx-theme[autoapi] from 1.1.1 to 1.1.2 in the docs-deps group `#1456 <https://github.com/ansys/pyansys-geometry/pull/1456>`_
- bump ansys-api-geometry from 0.4.8 to 0.4.9 `#1457 <https://github.com/ansys/pyansys-geometry/pull/1457>`_
- bump numpy from 2.1.1 to 2.1.2 `#1458 <https://github.com/ansys/pyansys-geometry/pull/1458>`_
- bump panel from 1.5.1 to 1.5.2 `#1459 <https://github.com/ansys/pyansys-geometry/pull/1459>`_
- bump ansys-api-geometry from 0.4.9 to 0.4.10 `#1461 <https://github.com/ansys/pyansys-geometry/pull/1461>`_
- bump ansys-tools-visualization-interface from 0.4.4 to 0.4.5 `#1462 <https://github.com/ansys/pyansys-geometry/pull/1462>`_
- update protobuf from 5.27.2 to 5.27.5 `#1464 <https://github.com/ansys/pyansys-geometry/pull/1464>`_
- bump sphinx-autodoc-typehints from 2.4.4 to 2.5.0 in the docs-deps group `#1465 <https://github.com/ansys/pyansys-geometry/pull/1465>`_


Documentation
^^^^^^^^^^^^^

- adding cheat sheet on documentation `#1433 <https://github.com/ansys/pyansys-geometry/pull/1433>`_
- add captions in examples toctrees `#1434 <https://github.com/ansys/pyansys-geometry/pull/1434>`_


Fixed
^^^^^

- ci/cd issues on documentation build `#1441 <https://github.com/ansys/pyansys-geometry/pull/1441>`_
- adapt tessellate tests to new core service `#1449 <https://github.com/ansys/pyansys-geometry/pull/1449>`_
- rename folders on Linux docker image according to new version `#1450 <https://github.com/ansys/pyansys-geometry/pull/1450>`_


Maintenance
^^^^^^^^^^^

- update CHANGELOG for v0.7.2 `#1422 <https://github.com/ansys/pyansys-geometry/pull/1422>`_
- checkout LFS files from previous version to ensure upload `#1423 <https://github.com/ansys/pyansys-geometry/pull/1423>`_
- pre-commit automatic update `#1431 <https://github.com/ansys/pyansys-geometry/pull/1431>`_, `#1437 <https://github.com/ansys/pyansys-geometry/pull/1437>`_, `#1445 <https://github.com/ansys/pyansys-geometry/pull/1445>`_, `#1460 <https://github.com/ansys/pyansys-geometry/pull/1460>`_
- update to ansys actions v8 and docs theme (static search) `#1446 <https://github.com/ansys/pyansys-geometry/pull/1446>`_
- pyvista/setup-headless-display started failing `#1447 <https://github.com/ansys/pyansys-geometry/pull/1447>`_
- check method implemented in Ansys actions `#1448 <https://github.com/ansys/pyansys-geometry/pull/1448>`_
- unstable image promotion and dependabot daily updates `#1463 <https://github.com/ansys/pyansys-geometry/pull/1463>`_

`0.7.2 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.7.2>`_ - 2024-09-11
=====================================================================================

Added
^^^^^

- allow for platform input when using Ansys Lab `#1416 <https://github.com/ansys/pyansys-geometry/pull/1416>`_
- ensure GrpcClient class closure upon deletion `#1417 <https://github.com/ansys/pyansys-geometry/pull/1417>`_


Dependencies
^^^^^^^^^^^^

- bump sphinx-autodoc-typehints from 2.3.0 to 2.4.0 in the docs-deps group `#1411 <https://github.com/ansys/pyansys-geometry/pull/1411>`_
- bump numpy from 2.1.0 to 2.1.1 `#1412 <https://github.com/ansys/pyansys-geometry/pull/1412>`_
- bump ansys-tools-visualization-interface from 0.4.1 to 0.4.3 `#1413 <https://github.com/ansys/pyansys-geometry/pull/1413>`_


Documentation
^^^^^^^^^^^^^

- remove title from landing page `#1408 <https://github.com/ansys/pyansys-geometry/pull/1408>`_
- adapt examples to use launch_modeler instead of Modeler obj connection `#1410 <https://github.com/ansys/pyansys-geometry/pull/1410>`_


Fixed
^^^^^

- handle properly ``np.cross()`` - 2d ops deprecated in Numpy 2.X `#1419 <https://github.com/ansys/pyansys-geometry/pull/1419>`_
- change logo link so that it renders properly on PyPI `#1420 <https://github.com/ansys/pyansys-geometry/pull/1420>`_
- wrong path on logo image `#1421 <https://github.com/ansys/pyansys-geometry/pull/1421>`_


Maintenance
^^^^^^^^^^^

- update CHANGELOG for v0.7.1 `#1407 <https://github.com/ansys/pyansys-geometry/pull/1407>`_
- pre-commit automatic update `#1418 <https://github.com/ansys/pyansys-geometry/pull/1418>`_

`0.7.1 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.7.1>`_ - 2024-09-06
=====================================================================================

Added
^^^^^

- get and set body color `#1357 <https://github.com/ansys/pyansys-geometry/pull/1357>`_
- add ``modeler.exit()`` method `#1375 <https://github.com/ansys/pyansys-geometry/pull/1375>`_
- setting instance name during component creation `#1382 <https://github.com/ansys/pyansys-geometry/pull/1382>`_
- accept pathlib.Path as input in missing methods `#1385 <https://github.com/ansys/pyansys-geometry/pull/1385>`_
- default logs folder on Geometry Service started by Python at PUBLIC (Windows) `#1386 <https://github.com/ansys/pyansys-geometry/pull/1386>`_
- allowing users to specify API version when running script against SpaceClaim or Discovery `#1395 <https://github.com/ansys/pyansys-geometry/pull/1395>`_
- expose ``modeler.designs`` attribute `#1401 <https://github.com/ansys/pyansys-geometry/pull/1401>`_
- pretty print components `#1403 <https://github.com/ansys/pyansys-geometry/pull/1403>`_


Dependencies
^^^^^^^^^^^^

- bump the grpc-deps group with 2 updates `#1363 <https://github.com/ansys/pyansys-geometry/pull/1363>`_, `#1369 <https://github.com/ansys/pyansys-geometry/pull/1369>`_
- bump the docs-deps group with 2 updates `#1364 <https://github.com/ansys/pyansys-geometry/pull/1364>`_, `#1392 <https://github.com/ansys/pyansys-geometry/pull/1392>`_
- bump numpy from 2.0.1 to 2.1.0 `#1365 <https://github.com/ansys/pyansys-geometry/pull/1365>`_
- bump ansys-sphinx-theme[autoapi] from 1.0.5 to 1.0.7 in the docs-deps group `#1370 <https://github.com/ansys/pyansys-geometry/pull/1370>`_
- bump ansys-api-geometry from 0.4.7 to 0.4.8 `#1371 <https://github.com/ansys/pyansys-geometry/pull/1371>`_
- bump scipy from 1.14.0 to 1.14.1 `#1372 <https://github.com/ansys/pyansys-geometry/pull/1372>`_
- bump the grpc-deps group with 3 updates `#1391 <https://github.com/ansys/pyansys-geometry/pull/1391>`_
- bump ansys-tools-visualization-interface from 0.4.0 to 0.4.1 `#1393 <https://github.com/ansys/pyansys-geometry/pull/1393>`_
- bump ansys-sphinx-theme[autoapi] from 1.0.7 to 1.0.8 in the docs-deps group `#1397 <https://github.com/ansys/pyansys-geometry/pull/1397>`_


Documentation
^^^^^^^^^^^^^

- add project logo `#1405 <https://github.com/ansys/pyansys-geometry/pull/1405>`_


Fixed
^^^^^

- remove ``server_logs_folder`` argument for Discovery and SpaceClaim `#1387 <https://github.com/ansys/pyansys-geometry/pull/1387>`_


Maintenance
^^^^^^^^^^^

- update CHANGELOG for v0.7.0 `#1360 <https://github.com/ansys/pyansys-geometry/pull/1360>`_
- bump dev branch to v0.8.dev0 `#1361 <https://github.com/ansys/pyansys-geometry/pull/1361>`_
- solving various warnings `#1368 <https://github.com/ansys/pyansys-geometry/pull/1368>`_
- pre-commit automatic update `#1373 <https://github.com/ansys/pyansys-geometry/pull/1373>`_, `#1394 <https://github.com/ansys/pyansys-geometry/pull/1394>`_
- upload coverage artifacts properly with upload-artifact@v4.4.0 `#1406 <https://github.com/ansys/pyansys-geometry/pull/1406>`_

`0.7.0 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.7.0>`_ - 2024-08-13
=====================================================================================

Added
^^^^^

- build: drop support for Python 3.9 `#1341 <https://github.com/ansys/pyansys-geometry/pull/1341>`_
- feat: adapting beartype typehints to +Python 3.10 standard `#1347 <https://github.com/ansys/pyansys-geometry/pull/1347>`_


Dependencies
^^^^^^^^^^^^

- build: bump the grpc-deps group with 3 updates `#1342 <https://github.com/ansys/pyansys-geometry/pull/1342>`_
- build: bump panel from 1.4.4 to 1.4.5 `#1344 <https://github.com/ansys/pyansys-geometry/pull/1344>`_
- bump the docs-deps group across 1 directory with 4 updates `#1353 <https://github.com/ansys/pyansys-geometry/pull/1353>`_
- bump trame-vtk from 2.8.9 to 2.8.10 `#1355 <https://github.com/ansys/pyansys-geometry/pull/1355>`_
- bump ansys-api-geometry from 0.4.6 to 0.4.7 `#1356 <https://github.com/ansys/pyansys-geometry/pull/1356>`_


Documentation
^^^^^^^^^^^^^

- feat: update conf for version 1.x of ansys-sphinx-theme `#1351 <https://github.com/ansys/pyansys-geometry/pull/1351>`_


Fixed
^^^^^

- trapezoid signature change and internal checks `#1354 <https://github.com/ansys/pyansys-geometry/pull/1354>`_


Maintenance
^^^^^^^^^^^

- updating Ansys actions to v7 - changelog related `#1348 <https://github.com/ansys/pyansys-geometry/pull/1348>`_
- ci: bump ansys/actions from 6 to 7 in the actions group `#1352 <https://github.com/ansys/pyansys-geometry/pull/1352>`_
- pre-commit automatic update `#1358 <https://github.com/ansys/pyansys-geometry/pull/1358>`_


Miscellaneous
^^^^^^^^^^^^^

- chore: pre-commit automatic update `#1345 <https://github.com/ansys/pyansys-geometry/pull/1345>`_

`0.6.6 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.6.6>`_ - 2024-08-01
=====================================================================================

Added
^^^^^

- feat: Add misc. repair and prepare tool methods `#1293 <https://github.com/ansys/pyansys-geometry/pull/1293>`_
- feat: name setter and fill style getter setters `#1299 <https://github.com/ansys/pyansys-geometry/pull/1299>`_
- feat: extract fluid volume from solid `#1306 <https://github.com/ansys/pyansys-geometry/pull/1306>`_
- feat: keep "other" bodies when performing bool operations `#1311 <https://github.com/ansys/pyansys-geometry/pull/1311>`_
- feat: ``revolve_sketch`` rotation definition enhancement `#1336 <https://github.com/ansys/pyansys-geometry/pull/1336>`_


Changed
^^^^^^^

- chore: update CHANGELOG for v0.6.5 `#1290 <https://github.com/ansys/pyansys-geometry/pull/1290>`_
- chore: enable ruff formatter on pre-commit `#1312 <https://github.com/ansys/pyansys-geometry/pull/1312>`_
- chore: updating dependabot groups `#1313 <https://github.com/ansys/pyansys-geometry/pull/1313>`_
- chore: adding issue links to TODOs `#1320 <https://github.com/ansys/pyansys-geometry/pull/1320>`_
- feat: adapt to new ansys-tools-visualization-interface v0.4.0 `#1338 <https://github.com/ansys/pyansys-geometry/pull/1338>`_


Fixed
^^^^^

- test: create sphere bug raised after box creation `#1291 <https://github.com/ansys/pyansys-geometry/pull/1291>`_
- ci: docker cleanup `#1294 <https://github.com/ansys/pyansys-geometry/pull/1294>`_
- fix: default length units not being used properly on arc creation `#1310 <https://github.com/ansys/pyansys-geometry/pull/1310>`_


Dependencies
^^^^^^^^^^^^

- build: bump ansys-api-geometry from 0.4.4 to 0.4.5 `#1292 <https://github.com/ansys/pyansys-geometry/pull/1292>`_
- build: bump pyvista[jupyter] from 0.43.10 to 0.44.0 in the docs-deps group `#1296 <https://github.com/ansys/pyansys-geometry/pull/1296>`_
- build: bump jupytext from 1.16.2 to 1.16.3 in the docs-deps group `#1300 <https://github.com/ansys/pyansys-geometry/pull/1300>`_
- build: bump ansys-api-geometry from 0.4.5 to 0.4.6 `#1301 <https://github.com/ansys/pyansys-geometry/pull/1301>`_
- build: bump pint from 0.24.1 to 0.24.3 `#1307 <https://github.com/ansys/pyansys-geometry/pull/1307>`_
- build: bump grpcio-health-checking from 1.60.0 to 1.64.1 in the grpc-deps group `#1315 <https://github.com/ansys/pyansys-geometry/pull/1315>`_
- build: bump the docs-deps group across 1 directory with 2 updates `#1316 <https://github.com/ansys/pyansys-geometry/pull/1316>`_
- build: bump the grpc-deps group with 2 updates `#1322 <https://github.com/ansys/pyansys-geometry/pull/1322>`_
- build: bump the docs-deps group with 2 updates `#1323 <https://github.com/ansys/pyansys-geometry/pull/1323>`_
- build: bump pyvista[jupyter] from 0.44.0 to 0.44.1 `#1324 <https://github.com/ansys/pyansys-geometry/pull/1324>`_
- build: bump ansys-tools-visualization-interface from 0.2.6 to 0.3.0 `#1325 <https://github.com/ansys/pyansys-geometry/pull/1325>`_
- build: bump pytest from 8.2.2 to 8.3.1 `#1326 <https://github.com/ansys/pyansys-geometry/pull/1326>`_
- build: bump pytest from 8.3.1 to 8.3.2 `#1331 <https://github.com/ansys/pyansys-geometry/pull/1331>`_
- build: bump numpy from 2.0.0 to 2.0.1 `#1332 <https://github.com/ansys/pyansys-geometry/pull/1332>`_


Miscellaneous
^^^^^^^^^^^^^

- chore: pre-commit automatic update `#1327 <https://github.com/ansys/pyansys-geometry/pull/1327>`_, `#1333 <https://github.com/ansys/pyansys-geometry/pull/1333>`_

`0.6.5 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.6.5>`_ - 2024-07-02
=====================================================================================

Changed
^^^^^^^

- chore: update CHANGELOG for v0.6.4 `#1278 <https://github.com/ansys/pyansys-geometry/pull/1278>`_
- build: update sphinx-autodoc-typehints version `#1280 <https://github.com/ansys/pyansys-geometry/pull/1280>`_
- chore: update SECURITY.md `#1286 <https://github.com/ansys/pyansys-geometry/pull/1286>`_


Fixed
^^^^^

- fix: manifest path should render as posix rather than uri `#1289 <https://github.com/ansys/pyansys-geometry/pull/1289>`_


Dependencies
^^^^^^^^^^^^

- build: bump protobuf from 5.27.1 to 5.27.2 in the grpc-deps group `#1283 <https://github.com/ansys/pyansys-geometry/pull/1283>`_
- build: bump scipy from 1.13.1 to 1.14.0 `#1284 <https://github.com/ansys/pyansys-geometry/pull/1284>`_
- build: bump vtk from 9.3.0 to 9.3.1 `#1287 <https://github.com/ansys/pyansys-geometry/pull/1287>`_


Miscellaneous
^^^^^^^^^^^^^

- chore: pre-commit automatic update `#1281 <https://github.com/ansys/pyansys-geometry/pull/1281>`_, `#1288 <https://github.com/ansys/pyansys-geometry/pull/1288>`_

`0.6.4 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.6.4>`_ - 2024-06-24
=====================================================================================

Added
^^^^^

- feat: using ruff as the main linter/formatter `#1274 <https://github.com/ansys/pyansys-geometry/pull/1274>`_


Changed
^^^^^^^

- chore: update CHANGELOG for v0.6.3 `#1273 <https://github.com/ansys/pyansys-geometry/pull/1273>`_
- chore: bump pre-commit-hook version `#1276 <https://github.com/ansys/pyansys-geometry/pull/1276>`_


Fixed
^^^^^

- fix: backticks breaking doc build after ruff linter `#1275 <https://github.com/ansys/pyansys-geometry/pull/1275>`_


Dependencies
^^^^^^^^^^^^

- build: bump pint from 0.24 to 0.24.1 `#1277 <https://github.com/ansys/pyansys-geometry/pull/1277>`_

`0.6.3 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.6.3>`_ - 2024-06-18
=====================================================================================

Changed
^^^^^^^

- chore: update CHANGELOG for v0.6.2 `#1263 <https://github.com/ansys/pyansys-geometry/pull/1263>`_
- build: adapting to numpy 2.x `#1265 <https://github.com/ansys/pyansys-geometry/pull/1265>`_
- docs: using ansys actions (again) to build docs `#1270 <https://github.com/ansys/pyansys-geometry/pull/1270>`_


Fixed
^^^^^

- fix: unnecessary Point3D comparison `#1264 <https://github.com/ansys/pyansys-geometry/pull/1264>`_
- docs: examples are not being uploaded as assets (.py/.ipynb) `#1268 <https://github.com/ansys/pyansys-geometry/pull/1268>`_
- fix: change action order `#1269 <https://github.com/ansys/pyansys-geometry/pull/1269>`_


Dependencies
^^^^^^^^^^^^

- build: bump numpy from 1.26.4 to 2.0.0 `#1266 <https://github.com/ansys/pyansys-geometry/pull/1266>`_
- build: bump the docs-deps group with 2 updates `#1271 <https://github.com/ansys/pyansys-geometry/pull/1271>`_


Miscellaneous
^^^^^^^^^^^^^

- chore: pre-commit automatic update `#1267 <https://github.com/ansys/pyansys-geometry/pull/1267>`_

`0.6.2 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.6.2>`_ - 2024-06-17
=====================================================================================

Added
^^^^^

- feat: deprecating log_level and logs_folder + adding client log control `#1260 <https://github.com/ansys/pyansys-geometry/pull/1260>`_
- feat: adding deprecation support for args and methods `#1261 <https://github.com/ansys/pyansys-geometry/pull/1261>`_


Changed
^^^^^^^

- chore: update CHANGELOG for v0.6.1 `#1256 <https://github.com/ansys/pyansys-geometry/pull/1256>`_
- ci: simplify doc build using ansys/actions `#1262 <https://github.com/ansys/pyansys-geometry/pull/1262>`_


Fixed
^^^^^

- fix: Rename built in shadowing variables `#1257 <https://github.com/ansys/pyansys-geometry/pull/1257>`_

`0.6.1 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.6.1>`_ - 2024-06-12
=====================================================================================

Added
^^^^^

- feat: revolve a sketch given an axis and an origin `#1248 <https://github.com/ansys/pyansys-geometry/pull/1248>`_


Changed
^^^^^^^

- chore: update CHANGELOG for v0.6.0 `#1245 <https://github.com/ansys/pyansys-geometry/pull/1245>`_
- chore: update dev version to 0.8.dev0 `#1246 <https://github.com/ansys/pyansys-geometry/pull/1246>`_


Fixed
^^^^^

- fix: Bug in `show` function `#1255 <https://github.com/ansys/pyansys-geometry/pull/1255>`_


Dependencies
^^^^^^^^^^^^

- build: bump protobuf from 5.27.0 to 5.27.1 in the grpc-deps group `#1250 <https://github.com/ansys/pyansys-geometry/pull/1250>`_
- build: bump the docs-deps group with 2 updates `#1251 <https://github.com/ansys/pyansys-geometry/pull/1251>`_
- build: bump trame-vtk from 2.8.8 to 2.8.9 `#1252 <https://github.com/ansys/pyansys-geometry/pull/1252>`_
- build: bump pint from 0.23 to 0.24 `#1253 <https://github.com/ansys/pyansys-geometry/pull/1253>`_
- build: bump ansys-tools-visualization-interface from 0.2.2 to 0.2.3 `#1254 <https://github.com/ansys/pyansys-geometry/pull/1254>`_


Miscellaneous
^^^^^^^^^^^^^

- docs: add conda information for package `#1247 <https://github.com/ansys/pyansys-geometry/pull/1247>`_

`0.6.0 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.6.0>`_ - 2024-06-07
=====================================================================================

Added
^^^^^

- feat: Adapt to ansys-visualizer `#959 <https://github.com/ansys/pyansys-geometry/pull/959>`_
- fix: rename ``GeomPlotter`` to ``GeometryPlotter`` `#1227 <https://github.com/ansys/pyansys-geometry/pull/1227>`_
- refactor: use ansys-tools-visualization-interface global vars rather than env vars `#1230 <https://github.com/ansys/pyansys-geometry/pull/1230>`_
- feat: bump to use v251 as default `#1242 <https://github.com/ansys/pyansys-geometry/pull/1242>`_


Changed
^^^^^^^

- chore: update CHANGELOG for v0.5.6 `#1213 <https://github.com/ansys/pyansys-geometry/pull/1213>`_
- chore: update SECURITY.md `#1214 <https://github.com/ansys/pyansys-geometry/pull/1214>`_
- ci: use Trusted Publisher for releasing package `#1216 <https://github.com/ansys/pyansys-geometry/pull/1216>`_
- ci: remove pygeometry-ci-1 specific logic `#1221 <https://github.com/ansys/pyansys-geometry/pull/1221>`_
- ci: only run doc build on runners outside the ansys network `#1223 <https://github.com/ansys/pyansys-geometry/pull/1223>`_
- chore: pre-commit automatic update `#1224 <https://github.com/ansys/pyansys-geometry/pull/1224>`_
- ci: announce nightly workflows failing `#1237 <https://github.com/ansys/pyansys-geometry/pull/1237>`_
- ci: failing notifications improvement `#1243 <https://github.com/ansys/pyansys-geometry/pull/1243>`_
- fix: broken interactive docs and improved tests paths `#1244 <https://github.com/ansys/pyansys-geometry/pull/1244>`_


Fixed
^^^^^

- fix: Interactive documentation `#1226 <https://github.com/ansys/pyansys-geometry/pull/1226>`_
- fix: only notify on failure and fill with data `#1238 <https://github.com/ansys/pyansys-geometry/pull/1238>`_


Dependencies
^^^^^^^^^^^^

- build: bump protobuf from 5.26.1 to 5.27.0 in the grpc-deps group `#1217 <https://github.com/ansys/pyansys-geometry/pull/1217>`_
- build: bump panel from 1.4.2 to 1.4.3 in the docs-deps group `#1218 <https://github.com/ansys/pyansys-geometry/pull/1218>`_
- build: bump ansys-api-geometry from 0.4.1 to 0.4.2 `#1219 <https://github.com/ansys/pyansys-geometry/pull/1219>`_
- build: bump ansys-sphinx-theme[autoapi] from 0.16.2 to 0.16.5 in the docs-deps group `#1231 <https://github.com/ansys/pyansys-geometry/pull/1231>`_
- build: bump requests from 2.32.2 to 2.32.3 `#1232 <https://github.com/ansys/pyansys-geometry/pull/1232>`_
- build: bump ansys-api-geometry from 0.4.2 to 0.4.3 `#1233 <https://github.com/ansys/pyansys-geometry/pull/1233>`_
- build: bump ansys-tools-visualization-interface from 0.2.1 to 0.2.2 `#1234 <https://github.com/ansys/pyansys-geometry/pull/1234>`_
- build: bump panel from 1.4.3 to 1.4.4 in the docs-deps group `#1235 <https://github.com/ansys/pyansys-geometry/pull/1235>`_
- build: bump ansys-tools-path from 0.5.2 to 0.6.0 `#1236 <https://github.com/ansys/pyansys-geometry/pull/1236>`_
- build: bump grpcio from 1.64.0 to 1.64.1 in the grpc-deps group `#1239 <https://github.com/ansys/pyansys-geometry/pull/1239>`_
- build: bump ansys-api-geometry from 0.4.3 to 0.4.4 `#1240 <https://github.com/ansys/pyansys-geometry/pull/1240>`_
- build: bump pytest from 8.2.1 to 8.2.2 `#1241 <https://github.com/ansys/pyansys-geometry/pull/1241>`_


Miscellaneous
^^^^^^^^^^^^^

- docs: update AUTHORS `#1222 <https://github.com/ansys/pyansys-geometry/pull/1222>`_

`0.5.6 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.5.6>`_ - 2024-05-23
=====================================================================================

Added
^^^^^

- feat: add new arc constructors `#1208 <https://github.com/ansys/pyansys-geometry/pull/1208>`_


Changed
^^^^^^^

- chore: update CHANGELOG for v0.5.5 `#1205 <https://github.com/ansys/pyansys-geometry/pull/1205>`_


Dependencies
^^^^^^^^^^^^

- build: bump requests from 2.31.0 to 2.32.2 `#1204 <https://github.com/ansys/pyansys-geometry/pull/1204>`_
- build: bump ansys-sphinx-theme[autoapi] from 0.16.0 to 0.16.2 in the docs-deps group `#1210 <https://github.com/ansys/pyansys-geometry/pull/1210>`_
- build: bump docker from 7.0.0 to 7.1.0 `#1211 <https://github.com/ansys/pyansys-geometry/pull/1211>`_
- build: bump scipy from 1.13.0 to 1.13.1 `#1212 <https://github.com/ansys/pyansys-geometry/pull/1212>`_

`0.5.5 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.5.5>`_ - 2024-05-21
=====================================================================================

Changed
^^^^^^^

- docs: adapt ``ansys_sphinx_theme_autoapi`` extension for ``autoapi`` `#1135 <https://github.com/ansys/pyansys-geometry/pull/1135>`_
- chore: update CHANGELOG for v0.5.4 `#1194 <https://github.com/ansys/pyansys-geometry/pull/1194>`_


Fixed
^^^^^

- fix: adapting ``Arc`` class constructor order to (start, end, center) `#1196 <https://github.com/ansys/pyansys-geometry/pull/1196>`_
- chore: limit requests library version under 2.32 `#1203 <https://github.com/ansys/pyansys-geometry/pull/1203>`_


Dependencies
^^^^^^^^^^^^

- build: bump grpcio from 1.63.0 to 1.64.0 in the grpc-deps group `#1198 <https://github.com/ansys/pyansys-geometry/pull/1198>`_
- build: bump the docs-deps group with 2 updates `#1199 <https://github.com/ansys/pyansys-geometry/pull/1199>`_
- build: bump pytest from 8.2.0 to 8.2.1 `#1200 <https://github.com/ansys/pyansys-geometry/pull/1200>`_


Miscellaneous
^^^^^^^^^^^^^

- chore: pre-commit automatic update `#1202 <https://github.com/ansys/pyansys-geometry/pull/1202>`_

`0.5.4 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.5.4>`_ - 2024-05-15
=====================================================================================

Added
^^^^^

- feat: allow for ``product_version`` on geometry service launcher function `#1182 <https://github.com/ansys/pyansys-geometry/pull/1182>`_


Changed
^^^^^^^

- chore: update CHANGELOG for v0.5.3 `#1177 <https://github.com/ansys/pyansys-geometry/pull/1177>`_


Dependencies
^^^^^^^^^^^^

- build: bump the docs-deps group with 4 updates `#1178 <https://github.com/ansys/pyansys-geometry/pull/1178>`_
- build: bump pytest from 8.1.1 to 8.2.0 `#1179 <https://github.com/ansys/pyansys-geometry/pull/1179>`_
- build: bump grpcio from 1.62.2 to 1.63.0 in the grpc-deps group `#1186 <https://github.com/ansys/pyansys-geometry/pull/1186>`_
- build: bump the docs-deps group with 2 updates `#1187 <https://github.com/ansys/pyansys-geometry/pull/1187>`_
- build: bump trame-vtk from 2.8.6 to 2.8.7 `#1188 <https://github.com/ansys/pyansys-geometry/pull/1188>`_
- build: bump nbsphinx from 0.9.3 to 0.9.4 in the docs-deps group `#1189 <https://github.com/ansys/pyansys-geometry/pull/1189>`_
- build: bump trame-vtk from 2.8.7 to 2.8.8 `#1190 <https://github.com/ansys/pyansys-geometry/pull/1190>`_


Miscellaneous
^^^^^^^^^^^^^

- chore: pre-commit automatic update `#1180 <https://github.com/ansys/pyansys-geometry/pull/1180>`_, `#1193 <https://github.com/ansys/pyansys-geometry/pull/1193>`_
- docs: add geometry preparation for Fluent simulation `#1183 <https://github.com/ansys/pyansys-geometry/pull/1183>`_

`0.5.3 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.5.3>`_ - 2024-04-29
=====================================================================================

Fixed
^^^^^

- fix: semver intersphinx mapping not resolved properly `#1175 <https://github.com/ansys/pyansys-geometry/pull/1175>`_
- fix: start and end points for edge `#1176 <https://github.com/ansys/pyansys-geometry/pull/1176>`_

`0.5.2 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.5.2>`_ - 2024-04-29
=====================================================================================

Added
^^^^^

- feat: add semver to intersphinx `#1173 <https://github.com/ansys/pyansys-geometry/pull/1173>`_


Changed
^^^^^^^

- chore: update CHANGELOG for v0.5.1 `#1165 <https://github.com/ansys/pyansys-geometry/pull/1165>`_
- chore: bump version to v0.6.dev0 `#1166 <https://github.com/ansys/pyansys-geometry/pull/1166>`_
- chore: update CHANGELOG for v0.5.2 `#1172 <https://github.com/ansys/pyansys-geometry/pull/1172>`_
- fix: allow to reuse last release binaries (if requested) `#1174 <https://github.com/ansys/pyansys-geometry/pull/1174>`_


Fixed
^^^^^

- fix: GetSurface and GetCurve not available prior to 24R2 `#1171 <https://github.com/ansys/pyansys-geometry/pull/1171>`_


Miscellaneous
^^^^^^^^^^^^^

- docs: creating a NACA airfoil example `#1167 <https://github.com/ansys/pyansys-geometry/pull/1167>`_
- docs: simplify README example `#1169 <https://github.com/ansys/pyansys-geometry/pull/1169>`_

`0.5.1 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.5.1>`_ - 2024-04-24
=====================================================================================

Added
^^^^^

- feat: security updates dropped for v0.3 or earlier `#1126 <https://github.com/ansys/pyansys-geometry/pull/1126>`_
- feat: add ``export_to`` functions `#1147 <https://github.com/ansys/pyansys-geometry/pull/1147>`_


Changed
^^^^^^^

- ci: adapt to vale ``v3`` `#1129 <https://github.com/ansys/pyansys-geometry/pull/1129>`_
- ci: bump ansys/actions from 5 to 6 in the actions group `#1133 <https://github.com/ansys/pyansys-geometry/pull/1133>`_
- docs: add release notes in our documentation `#1138 <https://github.com/ansys/pyansys-geometry/pull/1138>`_
- chore: bump ansys pre-commit hook to ``v0.3.0`` `#1139 <https://github.com/ansys/pyansys-geometry/pull/1139>`_
- chore: use default vale version `#1140 <https://github.com/ansys/pyansys-geometry/pull/1140>`_
- docs: add ``user_agent`` to Sphinx build `#1142 <https://github.com/ansys/pyansys-geometry/pull/1142>`_
- ci: enabling Linux tests missing `#1152 <https://github.com/ansys/pyansys-geometry/pull/1152>`_
- ci: perform minimal requirements tests `#1153 <https://github.com/ansys/pyansys-geometry/pull/1153>`_


Fixed
^^^^^

- fix: docs link in example `#1137 <https://github.com/ansys/pyansys-geometry/pull/1137>`_
- fix: update backend version message `#1145 <https://github.com/ansys/pyansys-geometry/pull/1145>`_
- fix: Trame issues `#1148 <https://github.com/ansys/pyansys-geometry/pull/1148>`_
- fix: Interactive documentation `#1160 <https://github.com/ansys/pyansys-geometry/pull/1160>`_


Dependencies
^^^^^^^^^^^^

- build: bump ansys-tools-path from 0.5.1 to 0.5.2 `#1131 <https://github.com/ansys/pyansys-geometry/pull/1131>`_
- build: bump the grpc-deps group across 1 directory with 3 updates `#1156 <https://github.com/ansys/pyansys-geometry/pull/1156>`_
- build: bump notebook from 7.1.2 to 7.1.3 in the docs-deps group `#1157 <https://github.com/ansys/pyansys-geometry/pull/1157>`_
- build: bump beartype from 0.18.2 to 0.18.5 `#1158 <https://github.com/ansys/pyansys-geometry/pull/1158>`_


Miscellaneous
^^^^^^^^^^^^^

- docs: add example on exporting designs `#1149 <https://github.com/ansys/pyansys-geometry/pull/1149>`_
- docs: fix link in `CHANGELOG.md` `#1154 <https://github.com/ansys/pyansys-geometry/pull/1154>`_
- chore: pre-commit automatic update `#1159 <https://github.com/ansys/pyansys-geometry/pull/1159>`_

`0.5.0 <https://github.com/ansys/pyansys-geometry/releases/tag/v0.5.0>`_ - 2024-04-17
=====================================================================================

Added
^^^^^

- feat: inserting document into existing design `#930 <https://github.com/ansys/pyansys-geometry/pull/930>`_
- feat: add changelog action `#1023 <https://github.com/ansys/pyansys-geometry/pull/1023>`_
- feat: create a sphere body on the backend `#1035 <https://github.com/ansys/pyansys-geometry/pull/1035>`_
- feat: mirror a body `#1055 <https://github.com/ansys/pyansys-geometry/pull/1055>`_
- feat: sweeping chains and profiles `#1056 <https://github.com/ansys/pyansys-geometry/pull/1056>`_
- feat: vulnerability checks `#1071 <https://github.com/ansys/pyansys-geometry/pull/1071>`_
- feat: loft profiles `#1075 <https://github.com/ansys/pyansys-geometry/pull/1075>`_
- feat: accept bandit advisories in-line for subprocess `#1077 <https://github.com/ansys/pyansys-geometry/pull/1077>`_
- feat: adding containers to automatic launcher `#1090 <https://github.com/ansys/pyansys-geometry/pull/1090>`_
- feat: minor changes to Linux Dockerfile `#1111 <https://github.com/ansys/pyansys-geometry/pull/1111>`_
- feat: avoid error if folder exists `#1125 <https://github.com/ansys/pyansys-geometry/pull/1125>`_


Changed
^^^^^^^

- build: changing sphinx-autoapi from 3.1.a2 to 3.1.a4 `#1038 <https://github.com/ansys/pyansys-geometry/pull/1038>`_
- chore: add pre-commit.ci configuration `#1065 <https://github.com/ansys/pyansys-geometry/pull/1065>`_
- chore: dependabot PR automatic approval `#1067 <https://github.com/ansys/pyansys-geometry/pull/1067>`_
- ci: bump the actions group with 1 update `#1082 <https://github.com/ansys/pyansys-geometry/pull/1082>`_
- chore: update docker tags to be kept `#1085 <https://github.com/ansys/pyansys-geometry/pull/1085>`_
- chore: update pre-commit versions `#1094 <https://github.com/ansys/pyansys-geometry/pull/1094>`_
- build: use ansys-sphinx-theme autoapi target `#1097 <https://github.com/ansys/pyansys-geometry/pull/1097>`_
- fix: removing @PipKat from ``*.md`` files - changelog fragments `#1098 <https://github.com/ansys/pyansys-geometry/pull/1098>`_
- ci: dashboard upload does not apply anymore `#1099 <https://github.com/ansys/pyansys-geometry/pull/1099>`_
- chore: pre-commit.ci not working properly `#1108 <https://github.com/ansys/pyansys-geometry/pull/1108>`_
- chore: update and adding pre-commit.ci config hook `#1109 <https://github.com/ansys/pyansys-geometry/pull/1109>`_
- ci: main Python version update to 3.12 `#1112 <https://github.com/ansys/pyansys-geometry/pull/1112>`_
- ci: skip Linux tests with common approach `#1113 <https://github.com/ansys/pyansys-geometry/pull/1113>`_
- ci: build changelog on release `#1118 <https://github.com/ansys/pyansys-geometry/pull/1118>`_
- chore: update CHANGELOG for v0.5.0 `#1119 <https://github.com/ansys/pyansys-geometry/pull/1119>`_

Fixed
^^^^^

- feat: re-enable open file on Linux `#817 <https://github.com/ansys/pyansys-geometry/pull/817>`_
- fix: adapt export and download tests to new hoops `#1057 <https://github.com/ansys/pyansys-geometry/pull/1057>`_
- fix: linux Dockerfile - replace .NET6.0 references by .NET8.0 `#1069 <https://github.com/ansys/pyansys-geometry/pull/1069>`_
- fix: misleading docstring for sweep_chain() `#1070 <https://github.com/ansys/pyansys-geometry/pull/1070>`_
- fix: prepare_and_start_backend is only available on Windows `#1076 <https://github.com/ansys/pyansys-geometry/pull/1076>`_
- fix: unit tests failing after dms update `#1087 <https://github.com/ansys/pyansys-geometry/pull/1087>`_
- build: beartype upper limit on v0.18 `#1095 <https://github.com/ansys/pyansys-geometry/pull/1095>`_
- fix: improper types being passed for Face and Edge ctor. `#1096 <https://github.com/ansys/pyansys-geometry/pull/1096>`_
- fix: return type should be dict and not ``ScalarMapContainer`` (grpc type) `#1103 <https://github.com/ansys/pyansys-geometry/pull/1103>`_
- fix: env version for Dockerfile Windows `#1120 <https://github.com/ansys/pyansys-geometry/pull/1120>`_
- fix: changelog description ill-formatted `#1121 <https://github.com/ansys/pyansys-geometry/pull/1121>`_
- fix: solve issues with intersphinx when releasing `#1123 <https://github.com/ansys/pyansys-geometry/pull/1123>`_

Dependencies
^^^^^^^^^^^^

- build: bump the docs-deps group with 2 updates `#1062 <https://github.com/ansys/pyansys-geometry/pull/1062>`_, `#1093 <https://github.com/ansys/pyansys-geometry/pull/1093>`_, `#1105 <https://github.com/ansys/pyansys-geometry/pull/1105>`_
- build: bump ansys-api-geometry from 0.3.13 to 0.4.0 `#1066 <https://github.com/ansys/pyansys-geometry/pull/1066>`_
- build: bump the docs-deps group with 1 update `#1080 <https://github.com/ansys/pyansys-geometry/pull/1080>`_
- build: bump pytest-cov from 4.1.0 to 5.0.0 `#1081 <https://github.com/ansys/pyansys-geometry/pull/1081>`_
- build: bump ansys-api-geometry from 0.4.0 to 0.4.1 `#1092 <https://github.com/ansys/pyansys-geometry/pull/1092>`_
- build: bump beartype from 0.17.2 to 0.18.2 `#1106 <https://github.com/ansys/pyansys-geometry/pull/1106>`_
- build: bump ansys-tools-path from 0.4.1 to 0.5.1 `#1107 <https://github.com/ansys/pyansys-geometry/pull/1107>`_
- build: bump panel from 1.4.0 to 1.4.1 in the docs-deps group `#1114 <https://github.com/ansys/pyansys-geometry/pull/1114>`_
- build: bump scipy from 1.12.0 to 1.13.0 `#1115 <https://github.com/ansys/pyansys-geometry/pull/1115>`_


Miscellaneous
^^^^^^^^^^^^^

- [pre-commit.ci] pre-commit autoupdate `#1063 <https://github.com/ansys/pyansys-geometry/pull/1063>`_
- docs: add examples on new methods `#1089 <https://github.com/ansys/pyansys-geometry/pull/1089>`_
- chore: pre-commit automatic update `#1116 <https://github.com/ansys/pyansys-geometry/pull/1116>`_

.. vale on