"""
审核规则资源测试
"""
import pytest
from unittest.mock import patch

from unicodedata import category

from docflow import DocflowClient
from docflow.exceptions import ValidationError


def test_review_resource_exists(client):
    """测试审核规则资源对象存在"""
    assert hasattr(client, 'review')
    assert client.review is not None


def test_review_resource_has_repo_methods(client):
    """测试审核规则资源包含规则库方法"""
    assert hasattr(client.review, 'create_repo')
    assert hasattr(client.review, 'list_repos')
    assert hasattr(client.review, 'get_repo')
    assert hasattr(client.review, 'update_repo')
    assert hasattr(client.review, 'delete_repo')


def test_review_resource_has_group_methods(client):
    """测试审核规则资源包含规则组方法"""
    assert hasattr(client.review, 'create_group')
    assert hasattr(client.review, 'update_group')
    assert hasattr(client.review, 'delete_group')


def test_review_resource_has_rule_methods(client):
    """测试审核规则资源包含规则方法"""
    assert hasattr(client.review, 'create_rule')
    assert hasattr(client.review, 'update_rule')
    assert hasattr(client.review, 'delete_rule')


def test_review_list_repos_has_default_pagination(client):
    """测试规则库列表默认分页参数"""
    import inspect
    sig = inspect.signature(client.review.list_repos)
    params = sig.parameters

    # 检查默认参数
    assert 'page' in params
    assert params['page'].default == 1
    assert 'page_size' in params
    assert params['page_size'].default == 10


def test_workspace_has_review_context(client):
    """测试工作空间上下文包含 review 属性"""
    ws = client.workspace("123")
    assert hasattr(ws, 'review')
    assert ws.review is not None


def test_review_context_has_all_methods(client):
    """测试 review 上下文包含所有必要方法"""
    ws = client.workspace("123")
    review = ws.review

    # 规则库方法
    assert hasattr(review, 'create_repo')
    assert hasattr(review, 'list_repos')
    assert hasattr(review, 'get_repo')
    assert hasattr(review, 'update_repo')
    assert hasattr(review, 'delete_repo')

    # 规则组方法
    assert hasattr(review, 'create_group')
    assert hasattr(review, 'update_group')
    assert hasattr(review, 'delete_group')

    # 规则方法
    assert hasattr(review, 'create_rule')
    assert hasattr(review, 'update_rule')
    assert hasattr(review, 'delete_rule')


def test_review_context_workspace_id(client):
    """测试 review 上下文包含正确的 workspace_id"""
    ws = client.workspace("test_ws_123")
    assert ws.review.workspace_id == "test_ws_123"


# ==================== 规则库管理测试 ====================

def test_repo_create_success(client, mock_workspace_id):
    """测试创建审核规则库成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "repo_id": "1234567890123456789"
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.review.create_repo(
            workspace_id=mock_workspace_id,
            name="发票审核规则库"
        )

        # 验证返回结果
        assert result is not None
        assert result.repo_id == "1234567890123456789"

        # 验证调用参数
        call_args = mock_post.call_args
        assert call_args[0][0] == "/app-api/sip/platform/v2/review/rule_repo/create"
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == mock_workspace_id
        assert json_data['name'] == "发票审核规则库"


def test_repo_list_success(client, mock_workspace_id):
    """测试获取审核规则库列表成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 2,
            "page": 1,
            "page_size": 10,
            "repos": [
                {
                    "repo_id": "1000000000000000001",
                    "name": "发票审核规则库",
                    "groups": []
                },
                {
                    "repo_id": "1000000000000000002",
                    "name": "合同审核规则库",
                    "groups": []
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        result = client.review.list_repos(
            workspace_id=mock_workspace_id,
            page=1,
            page_size=10
        )

        # 验证返回结果
        assert result is not None
        assert result.total == 2
        assert result.page == 1
        assert result.page_size == 10
        assert len(result.repos) == 2
        assert result.repos[0].repo_id == "1000000000000000001"
        assert result.repos[0].name == "发票审核规则库"


def test_repo_list_empty(client, mock_workspace_id):
    """测试获取审核规则库列表（空结果）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 0,
            "page": 1,
            "page_size": 10,
            "repos": []
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        result = client.review.list_repos(workspace_id=mock_workspace_id)

        # 验证返回结果
        assert result.total == 0
        assert len(result.repos) == 0


def test_repo_get_success(client, mock_workspace_id):
    """测试获取审核规则库详情成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "repo_id": "1234567890123456789",
            "name": "发票审核规则库",
            "category_ids": ["100", "200"],
            "groups": [
                {
                    "group_id": "9876543210987654321",
                    "name": "金额校验组",
                    "rules": [
                        {
                            "rule_id": "1111111111111111111",
                            "name": "金额范围检查",
                            "prompt": "检查金额是否在合理范围内",
                            "category_ids": ["100"],
                            "risk_level": 10
                        }
                    ]
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        result = client.review.get_repo(
            workspace_id=mock_workspace_id,
            repo_id="1234567890123456789"
        )

        # 验证返回结果
        assert result is not None
        assert result.repo_id == "1234567890123456789"
        assert result.name == "发票审核规则库"
        assert len(result.groups) == 1
        assert result.groups[0].group_id == "9876543210987654321"
        assert len(result.groups[0].rules) == 1


def test_repo_update_success(client, mock_workspace_id):
    """测试更新审核规则库成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.review.update_repo(
            workspace_id=mock_workspace_id,
            repo_id=31415926,
            name="新的规则库名称"
        )

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == mock_workspace_id
        assert json_data['repo_id'] == 31415926
        assert json_data['name'] == "新的规则库名称"


def test_repo_delete_success(client, mock_workspace_id):
    """测试删除审核规则库成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.review.delete_repo(
            workspace_id=mock_workspace_id,
            repo_ids=[31415926, 27182818]
        )

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == mock_workspace_id
        assert json_data['repo_ids'] == [31415926, 27182818]


# ==================== 规则组管理测试 ====================

def test_group_create_success(client, mock_workspace_id):
    """测试创建审核规则组成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "group_id": "1234567890123456789"
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.review.create_group(
            workspace_id=mock_workspace_id,
            repo_id="9876543210987654321",
            name="金额校验组"
        )

        # 验证返回结果
        assert result is not None
        assert result.group_id == "1234567890123456789"

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == mock_workspace_id
        assert json_data['repo_id'] == '9876543210987654321'
        assert json_data['name'] == "金额校验组"


def test_group_update_success(client, mock_workspace_id):
    """测试更新审核规则组成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.review.update_group(
            workspace_id=mock_workspace_id,
            group_id="1234567890123456789",
            name="新的规则组名称"
        )

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == mock_workspace_id
        assert json_data['group_id'] == "1234567890123456789"
        assert json_data['name'] == "新的规则组名称"


def test_group_delete_success(client, mock_workspace_id):
    """测试删除审核规则组成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.review.delete_group(
            workspace_id=mock_workspace_id,
            group_id="1234567890123456789"
        )

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == mock_workspace_id
        assert json_data['group_id'] == "1234567890123456789"


# ==================== 规则管理测试 ====================

def test_rule_create_success(client, mock_workspace_id):
    """测试创建审核规则成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "rule_id": "1234567890123456789"
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.review.create_rule(
            workspace_id=mock_workspace_id,
            repo_id=31415926,
            group_id="9876543210987654321",
            name="金额范围检查",
            prompt="请检查金额是否在合理范围内",
            category_ids=["1234567890"],
            risk_level=10
        )

        # 验证返回结果
        assert result is not None
        assert result.rule_id == "1234567890123456789"

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == mock_workspace_id
        assert json_data['repo_id'] == 31415926
        assert json_data['group_id'] == "9876543210987654321"
        assert json_data['name'] == "金额范围检查"
        assert json_data['prompt'] == "请检查金额是否在合理范围内"
        assert json_data['category_ids'] == ["1234567890"]
        assert json_data['risk_level'] == 10


def test_rule_update_success(client, mock_workspace_id):
    """测试更新审核规则成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.review.update_rule(
            workspace_id=mock_workspace_id,
            rule_id="1234567890123456789",
            name="新的规则名称",
            prompt="更新后的提示词",
            risk_level=20
        )

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == mock_workspace_id
        assert json_data['rule_id'] == "1234567890123456789"
        assert json_data['name'] == "新的规则名称"
        assert json_data['prompt'] == "更新后的提示词"
        assert json_data['risk_level'] == 20


def test_rule_delete_success(client, mock_workspace_id):
    """测试删除审核规则成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.review.delete_rule(
            workspace_id=mock_workspace_id,
            rule_id="1234567890123456789"
        )

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == mock_workspace_id
        assert json_data['rule_id'] == "1234567890123456789"


# ==================== 任务管理测试 ====================

def test_task_submit_success(client, mock_workspace_id):
    """测试提交审核任务成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "task_id": "1234567890123456789"
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.review.submit_task(
            workspace_id=mock_workspace_id,
            name="发票审核任务",
            repo_id="9876543210987654321",
            extract_task_ids=["1111111111111111111", "2222222222222222222"]
        )

        # 验证返回结果
        assert result is not None
        assert result['task_id'] == "1234567890123456789"

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == mock_workspace_id
        assert json_data['name'] == "发票审核任务"
        assert json_data['repo_id'] == "9876543210987654321"
        assert json_data['extract_task_ids'] == ["1111111111111111111", "2222222222222222222"]


def test_task_submit_validation_empty_name(client, mock_workspace_id):
    """测试提交审核任务参数校验（空名称）"""
    with pytest.raises(ValidationError, match="任务名称不能为空"):
        client.review.submit_task(
            workspace_id=mock_workspace_id,
            name="",
            repo_id="123"
        )


def test_task_submit_validation_name_too_long(client, mock_workspace_id):
    """测试提交审核任务参数校验（名称过长）"""
    with pytest.raises(ValidationError, match="任务名称不能超过 100 个字符"):
        client.review.submit_task(
            workspace_id=mock_workspace_id,
            name="a" * 101,
            repo_id="123"
        )


def test_task_submit_validation_empty_repo_id(client, mock_workspace_id):
    """测试提交审核任务参数校验（空规则库ID）"""
    with pytest.raises(ValidationError, match="审核规则库 ID 不能为空"):
        client.review.submit_task(
            workspace_id=mock_workspace_id,
            name="测试任务",
            repo_id=""
        )


def test_task_submit_validation_invalid_repo_id(client, mock_workspace_id):
    """测试提交审核任务参数校验（非数字规则库ID）"""
    with pytest.raises(ValidationError, match="审核规则库 ID 必须是数字字符串"):
        client.review.submit_task(
            workspace_id=mock_workspace_id,
            name="测试任务",
            repo_id="abc"
        )


def test_task_delete_success(client, mock_workspace_id):
    """测试删除审核任务成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.review.delete_task(
            workspace_id=mock_workspace_id,
            task_ids=["1234567890123456789", "9876543210987654321"]
        )

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == mock_workspace_id
        assert json_data['task_ids'] == ["1234567890123456789", "9876543210987654321"]


def test_task_delete_validation_empty_list(client, mock_workspace_id):
    """测试删除审核任务参数校验（空列表）"""
    with pytest.raises(ValidationError, match="task_ids 不能为空"):
        client.review.delete_task(
            workspace_id=mock_workspace_id,
            task_ids=[]
        )


def test_task_delete_validation_empty_id(client, mock_workspace_id):
    """测试删除审核任务参数校验（空ID）"""
    with pytest.raises(ValidationError, match="审核任务 ID 不能为空"):
        client.review.delete_task(
            workspace_id=mock_workspace_id,
            task_ids=["123", ""]
        )


def test_task_delete_validation_invalid_id(client, mock_workspace_id):
    """测试删除审核任务参数校验（非数字ID）"""
    with pytest.raises(ValidationError, match="审核任务 ID 必须是数字字符串"):
        client.review.delete_task(
            workspace_id=mock_workspace_id,
            task_ids=["123", "abc"]
        )


def test_task_get_result_success(client, mock_workspace_id):
    """测试获取审核任务结果成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "task_id": "1234567890123456789",
            "status": "completed",
            "results": [
                {
                    "rule_id": "111",
                    "rule_name": "金额检查",
                    "status": "pass"
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.review.get_task_result(
            workspace_id=mock_workspace_id,
            task_id="1234567890123456789",
            with_task_detail_url=True
        )

        # 验证返回结果
        assert result is not None
        assert result['task_id'] == "1234567890123456789"
        assert result['status'] == "completed"

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == mock_workspace_id
        assert json_data['task_id'] == "1234567890123456789"
        assert json_data['with_task_detail_url'] is True


def test_task_get_result_validation_empty_id(client, mock_workspace_id):
    """测试获取审核任务结果参数校验（空ID）"""
    with pytest.raises(ValidationError, match="审核任务 ID 不能为空"):
        client.review.get_task_result(
            workspace_id=mock_workspace_id,
            task_id=""
        )


def test_task_get_result_validation_invalid_id(client, mock_workspace_id):
    """测试获取审核任务结果参数校验（非数字ID）"""
    with pytest.raises(ValidationError, match="审核任务 ID 必须是数字字符串"):
        client.review.get_task_result(
            workspace_id=mock_workspace_id,
            task_id="abc"
        )


def test_task_retry_success(client, mock_workspace_id):
    """测试重新审核任务成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.review.retry_task(
            workspace_id=mock_workspace_id,
            task_id="1234567890123456789"
        )

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == mock_workspace_id
        assert json_data['task_id'] == "1234567890123456789"


def test_task_retry_rule_success(client, mock_workspace_id):
    """测试重新审核任务规则成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.review.retry_task_rule(
            workspace_id=mock_workspace_id,
            task_id="1234567890123456789",
            rule_id="9876543210987654321"
        )

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == mock_workspace_id
        assert json_data['task_id'] == "1234567890123456789"
        assert json_data['rule_id'] == "9876543210987654321"


def test_task_retry_rule_validation_empty_task_id(client, mock_workspace_id):
    """测试重新审核任务规则参数校验（空任务ID）"""
    with pytest.raises(ValidationError, match="审核任务 ID 不能为空"):
        client.review.retry_task_rule(
            workspace_id=mock_workspace_id,
            task_id="",
            rule_id="123"
        )


def test_task_retry_rule_validation_empty_rule_id(client, mock_workspace_id):
    """测试重新审核任务规则参数校验（空规则ID）"""
    with pytest.raises(ValidationError, match="审核规则 ID 不能为空"):
        client.review.retry_task_rule(
            workspace_id=mock_workspace_id,
            task_id="123",
            rule_id=""
        )


def test_task_retry_rule_validation_invalid_rule_id(client, mock_workspace_id):
    """测试重新审核任务规则参数校验（非数字规则ID）"""
    with pytest.raises(ValidationError, match="审核规则 ID 必须是数字字符串"):
        client.review.retry_task_rule(
            workspace_id=mock_workspace_id,
            task_id="123",
            rule_id="abc"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
