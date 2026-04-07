"""
国际化（i18n）功能测试
"""
import pytest
from docflow import DocflowClient, set_language, get_language
from docflow.exceptions import (
    AuthenticationError,
    ValidationError,
    ResourceNotFoundError,
    PermissionDeniedError,
)
from docflow.i18n import I18nManager


@pytest.fixture(autouse=True)
def reset_language():
    """每个测试前重置语言为中文"""
    set_language('zh_CN')
    yield
    # 测试后也重置为中文
    set_language('zh_CN')


def test_default_language(test_app_id, test_secret_code):
    """测试默认语言是中文"""
    client = DocflowClient(
        base_url="https://docflow.textin.com/api",
        app_id=test_app_id,
        secret_code=test_secret_code
    )
    assert client.get_language() == 'zh_CN'
    client.close()


def test_set_language_on_init(test_app_id, test_secret_code):
    """测试初始化时设置语言"""
    # 测试中文
    client_cn = DocflowClient(
        base_url="https://docflow.textin.com/api",
        app_id=test_app_id,
        secret_code=test_secret_code,
        language='zh_CN'
    )
    assert client_cn.get_language() == 'zh_CN'
    client_cn.close()

    # 测试英文
    client_en = DocflowClient(
        base_url="https://docflow.textin.com/api",
        app_id=test_app_id,
        secret_code=test_secret_code,
        language='en_US'
    )
    assert client_en.get_language() == 'en_US'
    client_en.close()


def test_set_language_dynamically(client):
    """测试动态切换语言"""
    # 切换到英文
    client.set_language('en_US')
    assert client.get_language() == 'en_US'

    # 切换回中文
    client.set_language('zh_CN')
    assert client.get_language() == 'zh_CN'


def test_get_available_languages(client):
    """测试获取可用语言列表"""
    languages = client.get_available_languages()
    assert 'zh_CN' in languages
    assert 'en_US' in languages
    assert len(languages) >= 2


def test_chinese_error_messages():
    """测试中文错误消息"""
    set_language('zh_CN')

    # 测试认证错误
    try:
        raise AuthenticationError()
    except AuthenticationError as e:
        assert '认证失败' in str(e)

    # 测试资源不存在
    try:
        raise ResourceNotFoundError()
    except ResourceNotFoundError as e:
        assert '资源不存在' in str(e) or 'not found' in str(e).lower()

    # 测试权限不足
    try:
        raise PermissionDeniedError()
    except PermissionDeniedError as e:
        assert '权限不足' in str(e) or 'denied' in str(e).lower()


def test_english_error_messages():
    """测试英文错误消息"""
    set_language('en_US')

    # 测试认证错误
    try:
        raise AuthenticationError()
    except AuthenticationError as e:
        assert 'Authentication failed' in str(e)

    # 测试资源不存在
    try:
        raise ResourceNotFoundError()
    except ResourceNotFoundError as e:
        assert 'not found' in str(e).lower()

    # 测试权限不足
    try:
        raise PermissionDeniedError()
    except PermissionDeniedError as e:
        assert 'denied' in str(e).lower()


def test_parametrized_messages():
    """测试参数化消息"""
    set_language('zh_CN')

    # 测试带参数的校验错误
    try:
        raise ValidationError(
            "字段太长",
            i18n_key='error.validation.too_long',
            field='工作空间名称',
            max_length=50
        )
    except ValidationError as e:
        error_msg = str(e)
        # 应该包含字段名和长度
        assert '工作空间名称' in error_msg or 'field' in error_msg.lower()


def test_invalid_language():
    """测试不支持的语言"""
    with pytest.raises(ValueError):
        set_language('fr_FR')  # 法语不支持


def test_i18n_singleton():
    """测试 i18n 管理器是单例"""
    i18n1 = I18nManager()
    i18n2 = I18nManager()
    assert i18n1 is i18n2


def test_global_language_setting():
    """测试全局语言设置"""
    # 设置全局语言
    set_language('en_US')
    assert get_language() == 'en_US'

    # 创建新客户端应该继承全局语言
    try:
        raise AuthenticationError()
    except AuthenticationError as e:
        assert 'Authentication' in str(e)

    # 重置为中文
    set_language('zh_CN')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
