import re

import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.errors import GeometryRuntimeError


# Python (.py)
def test_python_simple_script(modeler: Modeler):
    args = {}
    result = modeler.run_discovery_script_file(
        "./tests/integration/files/disco_scripts/simple_script.py", args
    )
    pattern_db = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.DesignBody", re.IGNORECASE)
    pattern_doc = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.Document", re.IGNORECASE)
    assert len(result) == 2
    assert pattern_db.match(result["design_body"])
    assert pattern_doc.match(result["design"])


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
    pattern_db = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.DesignBody", re.IGNORECASE)
    pattern_doc = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.Document", re.IGNORECASE)
    assert len(result) == 2
    assert pattern_db.match(result["design_body"])
    assert pattern_doc.match(result["design"])


# Discovery (.dscript)
def test_dscript_simple_script(modeler: Modeler):
    args = {}
    result = modeler.run_discovery_script_file(
        "./tests/integration/files/disco_scripts/simple_script.dscript", args
    )
    assert len(result) == 2
    pattern_db = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.DesignBody", re.IGNORECASE)
    pattern_doc = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.Document", re.IGNORECASE)
    assert len(result) == 2
    assert pattern_db.match(result["design_body"])
    assert pattern_doc.match(result["design"])
