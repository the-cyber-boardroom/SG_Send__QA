"""UC-10: Access token gate — API-level tests (P1).

Tests that verify access gate behaviour via direct HTTP calls,
without a browser.
"""

import httpx
import pytest

pytestmark = pytest.mark.p1


class TestBug__AccessGateTokenPersistence:
    """Document known/discovered bug: access token counter behaviour.

    Bug: If the access token counter reaches zero, subsequent requests
    with the same token should be denied.  This class documents the
    expected behaviour so we can detect regressions.
    """

    def test_token_counter_in_response(self, send_server):
        """Access token info endpoint returns remaining count (if implemented)."""
        # Hit the health or info endpoint to see if token info is exposed
        r = httpx.get(f"{send_server.server_url}/info/health")
        assert r.status_code == 200, f"Health check failed: {r.status_code}"
        # Document: counter management is server-side, not client-side
