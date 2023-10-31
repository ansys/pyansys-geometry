# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.

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
    """Test the creation of a Modeler object based on the local Ansys Geometry Service
    installation."""

    modeler_geo_service = launch_modeler_with_geometry_service()
    modeler_discovery = launch_modeler_with_discovery()
    modeler_spaceclaim = launch_modeler_with_spaceclaim()
    assert modeler_geo_service != None
    assert modeler_geo_service.client.healthy
    assert modeler_discovery != None
    assert modeler_discovery.client.healthy
    assert modeler_spaceclaim != None
    assert modeler_spaceclaim.client.healthy
    modeler_geo_service.close()
    modeler_discovery.close()
    modeler_spaceclaim.close()


@pytest.mark.skip(reason="CI/CD machines need the Ansys products available.")
def test_default_product_launch():
    """Test the creation of a Modeler object based on the local Ansys Geometry Service
    installation."""

    modeler_geo_service = launch_modeler_with_geometry_service()
    modeler_discovery = launch_modeler_with_discovery()
    modeler_spaceclaim = launch_modeler_with_spaceclaim()
    assert modeler_geo_service != None
    assert modeler_geo_service.client.healthy
    assert modeler_discovery != None
    assert modeler_discovery.client.healthy
    assert modeler_spaceclaim != None
    assert modeler_spaceclaim.client.healthy


@pytest.mark.skip(reason="CI/CD machines need the Ansys products available.")
def test_product_launch_with_parameters():
    """
    Test the creation of a Modeler object based on the local Ansys Geometry Service
    installation.

    And passing specific parameters to be tested.
    """
    apiVersions = list(ApiVersions)

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
        api_version=apiVersions[random.randint(0, len(apiVersions) - 1)].value,
        timeout=180,
    )

    modeler_spaceclaim = launch_modeler_with_spaceclaim(
        host="127.0.0.1",
        port=ProductInstance.get_available_port(),
        log_level=random.randint(0, 3),
        api_version=apiVersions[random.randint(0, len(apiVersions) - 1)].value,
        timeout=180,
    )

    assert modeler_geo_service != None
    assert modeler_geo_service.client.healthy
    assert modeler_discovery != None
    assert modeler_discovery.client.healthy
    assert modeler_spaceclaim != None
    assert modeler_spaceclaim.client.healthy

    modeler_geo_service.close()
    modeler_discovery.close()
    modeler_spaceclaim.close()
