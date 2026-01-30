# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

import random

import pytest

from ansys.geometry.core import (
    launch_modeler_with_discovery,
    launch_modeler_with_geometry_service,
    launch_modeler_with_spaceclaim,
)
from ansys.geometry.core.connection import ApiVersions, ProductInstance


@pytest.mark.skip(reason="CI/CD machines need the Ansys products available.")
def test_default_product_launch():
    """Test the creation of a Modeler object based on the local Ansys Geometry
    Service installation.
    """
    modeler_geo_service = launch_modeler_with_geometry_service()
    modeler_discovery = launch_modeler_with_discovery()
    modeler_spaceclaim = launch_modeler_with_spaceclaim()
    assert modeler_geo_service is not None
    assert modeler_geo_service.client.healthy
    assert modeler_discovery is not None
    assert modeler_discovery.client.healthy
    assert modeler_spaceclaim is not None
    assert modeler_spaceclaim.client.healthy
    modeler_geo_service.close()
    modeler_discovery.close()
    modeler_spaceclaim.close()


@pytest.mark.skip(reason="CI/CD machines need the Ansys products available.")
def test_product_launch_with_parameters():
    """Test the creation of a Modeler object based on the local Ansys Geometry
    Service installation.

    And passing specific parameters to be tested.
    """
    api_versions = list(ApiVersions)

    modeler_geo_service = launch_modeler_with_geometry_service(
        host="127.0.0.1",
        port=ProductInstance.get_available_port(),
        enable_trace=True,
        log_level=random.randint(0, 3),
        timeout=120,
    )

    modeler_discovery = launch_modeler_with_discovery(
        host="127.0.0.1",
        port=ProductInstance.get_available_port(),
        log_level=random.randint(0, 3),
        api_version=api_versions[random.randint(0, len(api_versions) - 1)].value,
        timeout=180,
        hidden=True,
    )

    modeler_spaceclaim = launch_modeler_with_spaceclaim(
        host="127.0.0.1",
        port=ProductInstance.get_available_port(),
        log_level=random.randint(0, 3),
        api_version=api_versions[random.randint(0, len(api_versions) - 1)].value,
        timeout=180,
        hidden=True,
    )

    assert modeler_geo_service is not None
    assert modeler_geo_service.client.healthy
    assert modeler_discovery is not None
    assert modeler_discovery.client.healthy
    assert modeler_spaceclaim is not None
    assert modeler_spaceclaim.client.healthy

    modeler_geo_service.close()
    modeler_discovery.close()
    modeler_spaceclaim.close()
