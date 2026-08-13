"""Live localhost checks for category keyword rules.

These tests are intentionally opt-in because they call a running backend and
temporarily replace the keyword rules of a dedicated test category.  They use
the same SDK public API that an integrator uses.

Run with:
    DOCFLOW_LIVE_TEST=1 DOCFLOW_LIVE_WRITE_TEST=1 \\
    DOCFLOW_APP_ID=... DOCFLOW_SECRET_CODE=... \\
    DOCFLOW_LIVE_WORKSPACE_ID=... DOCFLOW_LIVE_CATEGORY_ID=... \\
    pytest tests/integration/test_category_keyword_rules_live.py -m integration -q
"""
import os
import uuid

import pytest

from docflow import DocflowClient


LOCAL_BASE_URL = "http://127.0.0.1:28082"


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.skip(f"需要设置 {name} 才能执行本地联调")
    return value


@pytest.fixture(scope="module")
def live_client() -> DocflowClient:
    if os.getenv("DOCFLOW_LIVE_TEST") != "1":
        pytest.skip("仅在 DOCFLOW_LIVE_TEST=1 时执行本地联调")
    return DocflowClient(
        app_id=_required_env("DOCFLOW_APP_ID"),
        secret_code=_required_env("DOCFLOW_SECRET_CODE"),
        base_url=os.getenv("DOCFLOW_BASE_URL", LOCAL_BASE_URL),
        enterprise_id=_required_env("DOCFLOW_ENTERPRISE_ID"),
        max_retries=0,
        timeout=15,
    )


@pytest.mark.integration
def test_live_category_list_uses_localhost(live_client: DocflowClient):
    """Read through the SDK against the locally running backend."""
    workspace_id = _required_env("DOCFLOW_LIVE_WORKSPACE_ID")

    response = live_client.category.list(workspace_id=workspace_id, page=1, page_size=10)

    assert live_client.config.base_url.startswith("http://127.0.0.1:")
    assert response.page == 1
    assert response.page_size == 10


@pytest.mark.integration
def test_live_category_keyword_rules_update_round_trip(live_client: DocflowClient):
    """Write, read, and restore rules on a dedicated local test category."""
    if os.getenv("DOCFLOW_LIVE_WRITE_TEST") != "1":
        pytest.skip("写入测试需要显式设置 DOCFLOW_LIVE_WRITE_TEST=1")

    workspace_id = _required_env("DOCFLOW_LIVE_WORKSPACE_ID")
    category_id = _required_env("DOCFLOW_LIVE_CATEGORY_ID")
    categories = live_client.category.list(workspace_id=workspace_id, page=1, page_size=100).categories
    category = next((item for item in categories if item.id == category_id), None)
    if category is None:
        pytest.skip("DOCFLOW_LIVE_CATEGORY_ID 不属于当前工作空间的前 100 个类别")
    if category.category_keyword_rules is None:
        pytest.skip("为避免改变未配置状态，请选择一个已有 category_keyword_rules 的专用测试类别")

    original_rules = category.category_keyword_rules.to_dict()
    keyword = "sdk-live-" + uuid.uuid4().hex[:12]
    candidate_rules = {
        "positive_rules": [{"group_name": "sdk-live", "min_hit": 1, "words": [keyword]}],
        "negative_rules": [],
    }
    try:
        detail = live_client.category.update(
            workspace_id=workspace_id,
            category_id=category_id,
            category_keyword_rules=candidate_rules,
            check_keyword_rule_conflicts=False,
            with_detail=True,
        )
        assert detail["category_keyword_rules"]["positive_rules"][0]["words"] == [keyword]
    finally:
        live_client.category.update(
            workspace_id=workspace_id,
            category_id=category_id,
            category_keyword_rules=original_rules,
            check_keyword_rule_conflicts=False,
        )
