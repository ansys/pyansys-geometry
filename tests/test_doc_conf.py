# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Isolated tests for documentation release URLs, without Sphinx or network access."""

import ast
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest


@pytest.fixture
def release_config():
    """Load only the release helper to avoid executing documentation build setup."""
    path = Path(__file__).resolve().parents[1] / "doc/source/conf.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    helper = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "get_release_prefix_url"
    )
    config = SimpleNamespace(
        __version__="0.19.dev0",
        get_version_match=Mock(return_value="dev"),
        json=json,
        requests=SimpleNamespace(get=Mock()),
        time=SimpleNamespace(sleep=Mock()),
    )
    module = ast.Module(body=[helper], type_ignores=[])
    exec(compile(module, str(path), "exec"), vars(config))
    return config


@pytest.mark.parametrize("name", [None, "Geometry release 0.18.3"], ids=["null", "display-name"])
def test_get_release_prefix_url_uses_tag_name(release_config, name):
    """Development downloads use the tag, not the optional GitHub display name."""
    release_config.requests.get.return_value = SimpleNamespace(
        status_code=200,
        content=json.dumps({"name": name, "tag_name": "v0.18.3"}).encode(),
    )

    assert release_config.get_release_prefix_url() == (
        "https://github.com/ansys/pyansys-geometry/releases/download/v0.18.3",
        "v0.18.3",
    )
    release_config.get_version_match.assert_called_once_with("0.19.dev0")
    release_config.requests.get.assert_called_once_with(
        "https://api.github.com/repos/ansys/pyansys-geometry/releases/latest"
    )
    release_config.time.sleep.assert_not_called()


def test_get_release_prefix_url_stable(release_config):
    """Stable builds use their own version without querying GitHub."""
    release_config.__version__ = "0.18.3"
    release_config.get_version_match.return_value = "0.18"

    assert release_config.get_release_prefix_url() == (
        "https://github.com/ansys/pyansys-geometry/releases/download/v0.18.3",
        "v0.18.3",
    )
    release_config.get_version_match.assert_called_once_with("0.18.3")
    release_config.requests.get.assert_not_called()
    release_config.time.sleep.assert_not_called()


def test_get_release_prefix_url_retry_fallback(release_config):
    """Three non-200 responses retain the latest-download fallback without real sleeps."""
    release_config.requests.get.return_value = SimpleNamespace(status_code=503)

    assert release_config.get_release_prefix_url() == (
        "https://github.com/ansys/pyansys-geometry/releases/latest/download",
        "dev",
    )
    assert (
        release_config.requests.get.call_args_list
        == [call("https://api.github.com/repos/ansys/pyansys-geometry/releases/latest")] * 3
    )
    assert release_config.time.sleep.call_args_list == [call(2)] * 3
