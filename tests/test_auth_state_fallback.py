import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from checkin import CheckIn
from utils.config import AccountConfig, ProviderConfig


def _build_checkin() -> CheckIn:
    account = AccountConfig(provider="agentrouter")
    provider = ProviderConfig(
        name="agentrouter",
        origin="https://example.com",
        api_user_key="new-api-user",
        aliyun_captcha=True,
    )
    return CheckIn(
        account_name="test-account",
        account_config=account,
        provider_config=provider,
        global_proxy=None,
        storage_state_dir="storage-states-test",
    )


@pytest.mark.asyncio
async def test_get_auth_state_http_html_then_browser_success(monkeypatch):
    checkin = _build_checkin()

    class FakeSession:
        def get(self, *args, **kwargs):
            return SimpleNamespace(status_code=200, cookies=SimpleNamespace(jar=[]))

    monkeypatch.setattr("checkin.response_resolve", lambda response, context, account_name: None)

    async def fake_browser_state(self, api_user_key: str, api_user_value: str):
        assert api_user_key == "new-api-user"
        assert api_user_value == "-1"
        return {
            "success": True,
            "state": "state-token",
            "cookies": [{"name": "acw_tc", "value": "v"}],
        }

    monkeypatch.setattr(CheckIn, "get_auth_state_with_browser", fake_browser_state)

    result = await checkin.get_auth_state(
        session=FakeSession(),
        headers={"new-api-user": "-1"},
    )

    assert result["success"] is True
    assert result["state"] == "state-token"


@pytest.mark.asyncio
async def test_get_auth_state_http_html_then_browser_non_json_failure(monkeypatch):
    checkin = _build_checkin()

    class FakeSession:
        def get(self, *args, **kwargs):
            return SimpleNamespace(status_code=200, cookies=SimpleNamespace(jar=[]))

    monkeypatch.setattr("checkin.response_resolve", lambda response, context, account_name: None)

    async def fake_browser_state(self, api_user_key: str, api_user_value: str):
        return {
            "success": False,
            "error": "Failed to get state: Non-JSON response",
            "status": 200,
            "content_type": "text/html",
            "body_preview": "<!doctype html>",
        }

    monkeypatch.setattr(CheckIn, "get_auth_state_with_browser", fake_browser_state)

    result = await checkin.get_auth_state(
        session=FakeSession(),
        headers={"new-api-user": "-1"},
    )

    assert result["success"] is False
    assert "http_non_json_then_browser_non_json" in result["error"]
    assert "status=200" in result["error"]
    assert "content_type=text/html" in result["error"]


@pytest.mark.asyncio
async def test_aliyun_captcha_check_retries_then_success(monkeypatch):
    from utils.browser_utils import aliyun_captcha_check

    class FakeElement:
        def __init__(self, box):
            self._box = box

        async def bounding_box(self):
            return self._box

    class FakeMouse:
        async def move(self, *args, **kwargs):
            return None

        async def down(self, *args, **kwargs):
            return None

        async def up(self, *args, **kwargs):
            return None

        async def click(self, *args, **kwargs):
            return None

    class FakePage:
        def __init__(self):
            self.mouse = FakeMouse()
            self.eval_count = 0

        async def evaluate(self, script):
            self.eval_count += 1
            # first detect -> waf present
            # attempt1 post-check -> still present
            # attempt2 post-check -> passed
            if self.eval_count in (1, 2):
                return {
                    "has_waf_meta": True,
                    "has_captcha_container": True,
                    "traceid": "trace-1",
                }
            return {
                "has_waf_meta": False,
                "has_captcha_container": False,
                "traceid": None,
            }

        async def wait_for_selector(self, *args, **kwargs):
            return None

        async def wait_for_timeout(self, *args, **kwargs):
            return None

        async def query_selector(self, selector):
            if "sliding-slider" in selector or "nc_scale" in selector:
                return FakeElement({"x": 100, "y": 100, "width": 360, "height": 40})
            if "btn_slide" in selector or "+ *" in selector:
                return FakeElement({"x": 100, "y": 100, "width": 40, "height": 40})
            return None

    async def noop_screenshot(page, reason, account_name, prefix=""):
        return None

    monkeypatch.setattr("utils.browser_utils.take_screenshot", noop_screenshot)

    page = FakePage()
    passed = await aliyun_captcha_check(page, "test-account")
    assert passed is True
    assert page.eval_count >= 3
