"""Read-only local verification for category keyword rules.

Requires DOCFLOW_APP_ID, DOCFLOW_SECRET_CODE, DOCFLOW_ENTERPRISE_ID,
DOCFLOW_BASE_URL and DOCFLOW_LIVE_WORKSPACE_ID. See LOCAL_TESTING.md.
"""
import os

from docflow import DocflowClient


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit("缺少环境变量：{}".format(name))
    return value


def main() -> None:
    required_env("DOCFLOW_BASE_URL")
    workspace_id = required_env("DOCFLOW_LIVE_WORKSPACE_ID")
    client = DocflowClient.from_env(max_retries=0, timeout=15)
    response = client.category.list(workspace_id=workspace_id, page=1, page_size=10)

    configured = sum(
        category.category_keyword_rules is not None for category in response.categories
    )
    print("SDK 连接成功：第 {} 页，共 {} 个类别；当前页 {} 个类别配置了关键字规则。".format(
        response.page, response.total, configured
    ))


if __name__ == "__main__":
    main()
