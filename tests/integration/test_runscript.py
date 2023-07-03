import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.errors import GeometryRuntimeError


# Python (.py)
def test_python_simple_script(modeler: Modeler):
    args = {}
    result = modeler.run_discovery_script_file(
        "./tests/integration/files/disco_scripts/simple_script.py", args
    )
    assert len(result) == 2


def test_python_failing_script(modeler: Modeler):
    args = {}
    with pytest.raises(GeometryRuntimeError):
        modeler.run_discovery_script_file(
            "./tests/integration/files/disco_scripts/failing_script.py", args
        )


# SpaceClaim (.scscript)
def test_scscript_simple_script(modeler: Modeler):
    args = {}
    result = modeler.run_discovery_script_file(
        "./tests/integration/files/disco_scripts/simple_script.scscript", args
    )
    assert len(result) == 2


# Discovery (.dscript)
def test_dscript_simple_script(modeler: Modeler):
    args = {}
    result = modeler.run_discovery_script_file(
        "./tests/integration/files/disco_scripts/simple_script.dscript", args
    )
    assert len(result) == 2
