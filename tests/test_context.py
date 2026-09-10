"""
上下文类测试（链式调用）
"""
import pytest
from unittest.mock import Mock, MagicMock
from docflow import DocflowClient, EnabledStatus
from docflow.context import WorkspaceContext, CategoryContext, ReviewContext


def test_workspace_context_creation(client):
    """测试工作空间上下文创建"""
    ws = client.workspace("123")
    assert isinstance(ws, WorkspaceContext)
    assert ws.workspace_id == "123"


def test_workspace_context_has_review(client):
    """测试工作空间上下文包含 review 属性"""
    ws = client.workspace("123")
    assert hasattr(ws, 'review')
    assert isinstance(ws.review, ReviewContext)
    assert ws.review.workspace_id == "123"


def test_workspace_context_category(client):
    """测试工作空间上下文的 category 方法"""
    ws = client.workspace("123")
    cat = ws.category("456")
    assert isinstance(cat, CategoryContext)
    assert cat.workspace_id == "123"
    assert cat.category_id == "456"


@pytest.mark.parametrize(
    ("kwargs", "expected_value"),
    [
        ({}, False),
        ({"exclude_unadded_preset_categories": False}, False),
        ({"exclude_unadded_preset_categories": True}, True),
    ],
)
def test_workspace_context_list_categories_forwards_exclude_preset_filter(
    client, kwargs, expected_value
):
    """WorkspaceContext 应将预置类别过滤参数原样转发给资源层。"""
    ws = client.workspace("123")
    ws._category_resource.list = Mock(return_value="categories")

    result = ws.list_categories(**kwargs)

    assert result == "categories"
    ws._category_resource.list.assert_called_once_with(
        workspace_id="123",
        page=1,
        page_size=20,
        enabled=EnabledStatus.ENABLED,
        exclude_unadded_preset_categories=expected_value,
    )


def test_category_context_creation(client):
    """测试类别上下文创建"""
    ws = client.workspace("123")
    cat = ws.category("456")

    assert cat.workspace_id == "123"
    assert cat.category_id == "456"


def test_category_context_has_fields(client):
    """测试类别上下文包含 fields 属性"""
    ws = client.workspace("123")
    cat = ws.category("456")

    assert hasattr(cat, 'fields')
    assert cat.fields.workspace_id == "123"
    assert cat.fields.category_id == "456"


def test_category_context_has_tables(client):
    """测试类别上下文包含 tables 属性"""
    ws = client.workspace("123")
    cat = ws.category("456")

    assert hasattr(cat, 'tables')
    assert cat.tables.workspace_id == "123"
    assert cat.tables.category_id == "456"


def test_category_context_has_samples(client):
    """测试类别上下文包含 samples 属性"""
    ws = client.workspace("123")
    cat = ws.category("456")

    assert hasattr(cat, 'samples')
    assert cat.samples.workspace_id == "123"
    assert cat.samples.category_id == "456"


def test_review_context_creation(client):
    """测试审核规则上下文创建"""
    ws = client.workspace("123")
    assert isinstance(ws.review, ReviewContext)
    assert ws.review.workspace_id == "123"


def test_review_context_has_repo_methods(client):
    """测试审核规则上下文包含规则库方法"""
    ws = client.workspace("123")
    review = ws.review

    assert hasattr(review, 'create_repo')
    assert hasattr(review, 'list_repos')
    assert hasattr(review, 'get_repo')
    assert hasattr(review, 'update_repo')
    assert hasattr(review, 'delete_repo')


def test_review_context_has_group_methods(client):
    """测试审核规则上下文包含规则组方法"""
    ws = client.workspace("123")
    review = ws.review

    assert hasattr(review, 'create_group')
    assert hasattr(review, 'update_group')
    assert hasattr(review, 'delete_group')


def test_review_context_has_rule_methods(client):
    """测试审核规则上下文包含规则方法"""
    ws = client.workspace("123")
    review = ws.review

    assert hasattr(review, 'create_rule')
    assert hasattr(review, 'update_rule')
    assert hasattr(review, 'delete_rule')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
