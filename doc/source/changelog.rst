.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the PyAnsys Geometry project.

.. vale off

.. towncrier release notes start

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