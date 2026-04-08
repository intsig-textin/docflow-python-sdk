"""
DocflowClient 客户端测试
"""
import pytest
import os
from docflow import DocflowClient
from docflow.exceptions import ValidationError


def test_client_init_with_credentials(test_app_id, test_secret_code):
    """测试使用凭证初始化客户端"""
    client = DocflowClient(
        app_id=test_app_id,
        secret_code=test_secret_code
    )
    assert client.auth.app_id == test_app_id
    assert client.auth.secret_code == test_secret_code
    assert client.config.base_url == "https://docflow.textin.com/api"
    client.close()


def test_client_init_with_custom_url(test_app_id, test_secret_code):
    """测试自定义 base_url"""
    client = DocflowClient(
        app_id=test_app_id,
        secret_code=test_secret_code,
        base_url="https://custom.api.com/api"
    )
    assert client.config.base_url == "https://custom.api.com/api"
    client.close()


def test_client_init_with_timeout(test_app_id, test_secret_code):
    """测试自定义超时时间"""
    client = DocflowClient(
        app_id=test_app_id,
        secret_code=test_secret_code,
        timeout=60
    )
    assert client.config.timeout == 60
    client.close()


def test_client_init_without_credentials():
    """测试缺少凭证时抛出异常"""
    with pytest.raises(ValueError, match="必须提供 app_id 和 secret_code"):
        DocflowClient(app_id="", secret_code="test")

    with pytest.raises(ValueError, match="必须提供 app_id 和 secret_code"):
        DocflowClient(app_id="test", secret_code="")


def test_client_from_env(monkeypatch):
    """测试从环境变量创建客户端"""
    monkeypatch.setenv("DOCFLOW_APP_ID", "env_app_id")
    monkeypatch.setenv("DOCFLOW_SECRET_CODE", "env_secret")
    monkeypatch.setenv("DOCFLOW_BASE_URL", "https://env.api.com")

    client = DocflowClient.from_env()
    assert client.auth.app_id == "env_app_id"
    assert client.auth.secret_code == "env_secret"
    assert client.config.base_url == "https://env.api.com"
    client.close()


def test_client_from_env_missing_credentials(monkeypatch):
    """测试环境变量缺失时抛出异常"""
    monkeypatch.delenv("DOCFLOW_APP_ID", raising=False)
    monkeypatch.delenv("DOCFLOW_SECRET_CODE", raising=False)

    with pytest.raises(ValueError, match="环境变量.*未设置"):
        DocflowClient.from_env()


def test_client_resources_initialized(client):
    """测试资源对象已初始化"""
    assert client.workspace is not None
    assert client.category is not None
    assert client.file is not None
    assert client.review is not None


def test_client_set_credentials(test_app_id, test_secret_code):
    """测试更新凭证"""
    client = DocflowClient(
        app_id="old_id", secret_code="old_secret"
    )
    client.set_credentials("new_id", "new_secret")
    assert client.auth.app_id == "new_id"
    assert client.auth.secret_code == "new_secret"
    client.close()


def test_client_set_language(client):
    """测试设置语言"""
    client.set_language("en_US")
    assert client.get_language() == "en_US"

    client.set_language("zh_CN")
    assert client.get_language() == "zh_CN"


def test_client_set_invalid_language(client):
    """测试设置无效语言"""
    with pytest.raises(ValueError, match="不支持的语言"):
        client.set_language("invalid_lang")


def test_client_context_manager(test_app_id, test_secret_code):
    """测试上下文管理器"""
    with DocflowClient(app_id=test_app_id, secret_code=test_secret_code) as client:
        assert client is not None
        assert client.http_client is not None
    # 退出时应该自动关闭


def test_client_workspace_context(client):
    """测试工作空间上下文"""
    ws = client.workspace("123")
    assert ws.workspace_id == "123"
    assert ws.review is not None


def test_client_retry_config(test_app_id, test_secret_code):
    """测试重试配置"""
    client = DocflowClient(
        app_id=test_app_id,
        secret_code=test_secret_code,
        max_retries=5,
        retry_backoff_factor=2.0
    )
    assert client.config.max_retries == 5
    assert client.config.retry_backoff_factor == 2.0
    client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
