.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the ``ansys-geometry-core`` project.

.. towncrier release notes start

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
