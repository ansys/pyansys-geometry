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
"""Unit tests for the unsupported gRPC service implementations (v0 and v1)."""

from unittest.mock import MagicMock

import pytest


def test_v0_convert_to_heavyweight_raises_not_implemented():
    """GRPCUnsupportedServiceV0.convert_to_heavyweight raises NotImplementedError.

    The v0 protocol does not expose a ConvertToHeavyweight RPC, so calling the
    method must fail immediately with NotImplementedError.
    """
    from ansys.geometry.core._grpc._services.v0.unsupported import GRPCUnsupportedServiceV0

    # Bypass __init__ to avoid importing the real v0 stub
    service = GRPCUnsupportedServiceV0.__new__(GRPCUnsupportedServiceV0)
    service.stub = MagicMock()

    with pytest.raises(NotImplementedError, match="convert_to_heavyweight"):
        service.convert_to_heavyweight(ids=["some-id"])


def test_v1_convert_to_heavyweight_returns_success_true():
    """GRPCUnsupportedServiceV1.convert_to_heavyweight returns {'success': True}.

    Verifies that the method builds a MultipleEntitiesRequest with the correct
    entity identifiers and maps the gRPC response to the expected dict.
    """
    from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

    from ansys.geometry.core._grpc._services.v1.conversions import build_grpc_id
    from ansys.geometry.core._grpc._services.v1.unsupported import GRPCUnsupportedServiceV1

    # Bypass __init__ to avoid opening a real gRPC channel
    service = GRPCUnsupportedServiceV1.__new__(GRPCUnsupportedServiceV1)
    service.stub = MagicMock()
    service.file_stub = MagicMock()

    mock_response = MagicMock()
    mock_response.command_response.success = True
    service.stub.ConvertToHeavyweight.return_value = mock_response

    result = service.convert_to_heavyweight(ids=["id-1", "id-2"])

    assert result == {"success": True}
    service.stub.ConvertToHeavyweight.assert_called_once()

    # Verify the request payload
    actual_request = service.stub.ConvertToHeavyweight.call_args[0][0]
    expected_request = MultipleEntitiesRequest(
        ids=[build_grpc_id("id-1"), build_grpc_id("id-2")]
    )
    assert actual_request == expected_request


def test_v1_convert_to_heavyweight_returns_success_false():
    """GRPCUnsupportedServiceV1.convert_to_heavyweight returns {'success': False}.

    Verifies that a False success value from the gRPC response is propagated
    correctly.
    """
    from ansys.geometry.core._grpc._services.v1.unsupported import GRPCUnsupportedServiceV1

    service = GRPCUnsupportedServiceV1.__new__(GRPCUnsupportedServiceV1)
    service.stub = MagicMock()
    service.file_stub = MagicMock()

    mock_response = MagicMock()
    mock_response.command_response.success = False
    service.stub.ConvertToHeavyweight.return_value = mock_response

    result = service.convert_to_heavyweight(ids=["id-1"])

    assert result == {"success": False}
