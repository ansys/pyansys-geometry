# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

a = 1
from ansys.geometry.core import Modeler

# from ansys.geometry.core import launch_modeler_with_discovery
# modeler = launch_modeler_with_discovery()
modeler = Modeler(host="localhost", port=50051)
design = modeler.open_file(
    r"D:\ANSYSDEV\pyansys-geometry\tests\integration\files\Combine.Merge.scdocx"
)
# problem_areas = modeler.repair_tools.find_split_edges(design.bodies, 1.0, 3.6)
b = 1
b1 = design.bodies[0]
b2 = design.bodies[1]
# b1.intersect(b2,True)
b1.unite(b2, True)
d = 2
b1.copy
