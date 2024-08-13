.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the PyAnsys Geometry project.

.. vale off

.. towncrier release notes start

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
- chore: update dev version to 0.7.dev0 `#1246 <https://github.com/ansys/pyansys-geometry/pull/1246>`_


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