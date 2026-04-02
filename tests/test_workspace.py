"""
工作空间资源操作单元测试
"""
import pytest
from unittest.mock import patch
from docflow import DocflowClient
from docflow.exceptions import ValidationError, APIError
from docflow.enums import AuthScope


def test_create_workspace_validation(client):
    """测试创建工作空间参数校验"""
    # 测试空名称
    with pytest.raises(ValidationError, match="工作空间名称不能为空"):
        client.workspace.create(enterprise_id=12345, name="", auth_scope=0)

    # 测试名称过长
    with pytest.raises(ValidationError, match="工作空间名称不能超过 50 个字符"):
        client.workspace.create(enterprise_id=12345, name="a" * 51, auth_scope=0)

    # 测试描述过长
    with pytest.raises(ValidationError, match="工作空间描述不能超过 200 个字符"):
        client.workspace.create(enterprise_id=12345, name="测试", auth_scope=0, description="a" * 201)

    # 测试无效的 auth_scope
    with pytest.raises(ValidationError, match="auth_scope 只能是"):
        client.workspace.create(
            enterprise_id=12345, name="测试", auth_scope=999
        )


def test_list_workspace_validation(client):
    """测试列表工作空间参数校验"""
    # 测试无效的页码
    with pytest.raises(ValidationError, match="页码必须大于等于 1"):
        client.workspace.list(enterprise_id=12345, page=0)

    # 测试无效的每页数量
    with pytest.raises(ValidationError, match="每页数量必须在 1-100 之间"):
        client.workspace.list(enterprise_id=12345, page_size=0)

    with pytest.raises(ValidationError, match="每页数量必须在 1-100 之间"):
        client.workspace.list(enterprise_id=12345, page_size=101)


def test_get_workspace_validation(client):
    """测试获取工作空间详情参数校验"""
    # 测试空 ID
    with pytest.raises(ValidationError, match="工作空间 ID 不能为空"):
        client.workspace.get(workspace_id="")

    # 测试非数字 ID
    with pytest.raises(ValidationError, match="工作空间 ID 格式错误"):
        client.workspace.get(workspace_id="abc")


def test_update_workspace_validation(client):
    """测试更新工作空间参数校验"""
    # 测试空 ID
    with pytest.raises(ValidationError, match="工作空间 ID 不能为空"):
        client.workspace.update(workspace_id="", name="测试", auth_scope=0)

    # 测试空名称
    with pytest.raises(ValidationError, match="工作空间名称不能为空"):
        client.workspace.update(workspace_id="123", name="  ", auth_scope=0)

    # 测试名称过长
    with pytest.raises(ValidationError, match="工作空间名称不能超过 50 个字符"):
        client.workspace.update(workspace_id="123", name="a" * 51, auth_scope=0)

    # 测试无效的 auth_scope
    with pytest.raises(ValidationError, match="auth_scope 只能是"):
        client.workspace.update(workspace_id="123", name="测试", auth_scope=2)

    # 测试描述过长
    with pytest.raises(ValidationError, match="工作空间描述不能超过 200 个字符"):
        client.workspace.update(workspace_id="123", name="测试", auth_scope=0, description="a" * 201)

    # 测试无效的 callback_retry_time
    with pytest.raises(ValidationError, match="回调重试次数必须在 1-3 之间"):
        client.workspace.update(workspace_id="123", name="测试", auth_scope=0, callback_retry_time=4)

    with pytest.raises(ValidationError, match="回调重试次数必须在 1-3 之间"):
        client.workspace.update(workspace_id="123", name="测试", auth_scope=0, callback_retry_time=0)


def test_delete_workspace_validation(client):
    """测试删除工作空间参数校验"""
    # 测试空列表
    with pytest.raises(ValidationError, match="workspace_ids 不能为空"):
        client.workspace.delete(workspace_ids=[])

    # 测试包含空 ID
    with pytest.raises(ValidationError, match="工作空间 ID 不能为空"):
        client.workspace.delete(workspace_ids=["123", ""])

    # 测试包含非数字 ID
    with pytest.raises(ValidationError, match="工作空间 ID 格式错误"):
        client.workspace.delete(workspace_ids=["123", "abc"])

def test_workspace_create_success(client):
    """测试创建工作空间成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "workspace_id": "1234567890123456789"
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.workspace.create(
            enterprise_id=12345,
            name="测试工作空间",
            auth_scope=AuthScope.PRIVATE
        )

        # 验证返回结果
        assert result is not None
        assert result.workspace_id == "1234567890123456789"

        # 验证调用参数
        call_args = mock_post.call_args
        assert call_args[0][0] == "/app-api/sip/platform/v2/workspace/create"
        assert call_args[1]['json_data']['enterprise_id'] == 12345
        assert call_args[1]['json_data']['name'] == "测试工作空间"
        assert call_args[1]['json_data']['auth_scope'] == 0


def test_workspace_create_with_optional_params(client):
    """测试创建工作空间（带可选参数）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "workspace_id": "9876543210987654321"
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.workspace.create(
            enterprise_id=12345,
            name="公开工作空间",
            auth_scope=AuthScope.PUBLIC,
            manage_account_id=100
        )

        # 验证返回结果
        assert result is not None
        assert result.workspace_id == "9876543210987654321"

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['auth_scope'] == 1
        assert json_data['manage_account_id'] == 100


def test_workspace_list_success(client):
    """测试获取工作空间列表成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 2,
            "page": 1,
            "page_size": 20,
            "workspaces": [
                {
                    "workspace_id": "1000000000000000001",
                    "name": "工作空间1",
                    "enterprise_id": 12345,
                    "auth_scope": 0,
                    "created_at": "2024-01-01 10:00:00"
                },
                {
                    "workspace_id": "1000000000000000002",
                    "name": "工作空间2",
                    "enterprise_id": 12345,
                    "auth_scope": 1,
                    "created_at": "2024-01-02 10:00:00"
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        result = client.workspace.list(
            enterprise_id=12345,
            page=1,
            page_size=20
        )

        # 验证返回结果
        assert result is not None
        assert result.total == 2
        assert result.page == 1
        assert result.page_size == 20
        assert len(result.workspaces) == 2
        assert result.workspaces[0].workspace_id == "1000000000000000001"
        assert result.workspaces[0].name == "工作空间1"
        assert result.workspaces[1].workspace_id == "1000000000000000002"


def test_workspace_list_with_pagination(client):
    """测试获取工作空间列表（分页参数）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 50,
            "page": 2,
            "page_size": 10,
            "workspaces": [
                {
                    "workspace_id": str(1000000000000000000 + i),
                    "name": f"工作空间{i}",
                    "enterprise_id": 12345
                } for i in range(11, 21)
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response) as mock_get:
        result = client.workspace.list(
            enterprise_id=12345,
            page=2,
            page_size=10
        )

        # 验证返回结果
        assert result.total == 50
        assert result.page == 2
        assert result.page_size == 10
        assert len(result.workspaces) == 10

        # 验证调用参数
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert params['page'] == 2
        assert params['page_size'] == 10


def test_workspace_list_empty_result(client):
    """测试获取工作空间列表（空结果）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 0,
            "page": 1,
            "page_size": 20,
            "workspaces": []
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        result = client.workspace.list(enterprise_id=12345)

        # 验证返回结果
        assert result.total == 0
        assert len(result.workspaces) == 0


def test_workspace_get_success(client):
    """测试获取工作空间详情成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "workspace_id": "1234567890123456789",
            "name": "我的工作空间",
            "enterprise_id": 12345,
            "auth_scope": 0,
            "manage_account_id": 100
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response) as mock_get:
        result = client.workspace.get(workspace_id="1234567890123456789")

        # 验证返回结果
        assert result is not None
        assert result.workspace_id == "1234567890123456789"
        assert result.name == "我的工作空间"
        assert result.auth_scope == 0
        assert result.manage_account_id == '100'

        # 验证调用参数
        call_args = mock_get.call_args
        assert call_args[1]['params']['workspace_id'] == "1234567890123456789"


def test_workspace_update_success(client):
    """测试更新工作空间成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.workspace.update(
            workspace_id="1234567890123456789",
            name="新的工作空间名称",
            auth_scope=AuthScope.PRIVATE
        )

        # 验证调用参数
        call_args = mock_post.call_args
        assert call_args[0][0] == "/app-api/sip/platform/v2/workspace/update"
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == "1234567890123456789"
        assert json_data['name'] == "新的工作空间名称"
        assert json_data['auth_scope'] == 0


def test_workspace_update_with_auth_scope(client):
    """测试更新工作空间（修改权限范围）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.workspace.update(
            workspace_id="1234567890123456789",
            name="公开工作空间",
            auth_scope=AuthScope.PUBLIC
        )

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == "1234567890123456789"
        assert json_data['name'] == "公开工作空间"
        assert json_data['auth_scope'] == 1


def test_workspace_update_with_int_auth_scope(client):
    """测试更新工作空间（使用整数权限范围）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.workspace.update(
            workspace_id="1234567890123456789",
            name="测试工作空间",
            auth_scope=0
        )

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == "1234567890123456789"
        assert json_data['name'] == "测试工作空间"
        assert json_data['auth_scope'] == 0


def test_workspace_update_with_optional_params(client):
    """测试更新工作空间（带可选参数）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.workspace.update(
            workspace_id="1234567890123456789",
            name="更新后的工作空间",
            auth_scope=AuthScope.PUBLIC,
            description="更新后的描述",
            callback_url="https://example.com/callback",
            callback_retry_time=3
        )

        # 验证调用参数
        call_args = mock_post.call_args
        json_data = call_args[1]['json_data']
        assert json_data['workspace_id'] == "1234567890123456789"
        assert json_data['name'] == "更新后的工作空间"
        assert json_data['auth_scope'] == 1
        assert json_data['description'] == "更新后的描述"
        assert json_data['callback_url'] == "https://example.com/callback"
        assert json_data['callback_retry_time'] == 3


def test_workspace_delete_success(client):
    """测试删除工作空间成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.workspace.delete(workspace_ids=["1234567890123456789"])

        # 验证调用参数
        call_args = mock_post.call_args
        assert call_args[0][0] == "/app-api/sip/platform/v2/workspace/delete"
        assert call_args[1]['json_data']['workspace_ids'] == ["1234567890123456789"]


def test_workspace_delete_multiple(client):
    """测试批量删除工作空间"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        workspace_ids = ["1000000000000000001", "1000000000000000002", "1000000000000000003"]
        client.workspace.delete(workspace_ids=workspace_ids)

        # 验证调用参数
        call_args = mock_post.call_args
        assert call_args[1]['json_data']['workspace_ids'] == workspace_ids


def test_workspace_iter_success(client):
    """测试迭代工作空间成功"""
    # Mock 多页响应
    mock_response_page1 = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 25,
            "page": 1,
            "page_size": 10,
            "workspaces": [
                {
                    "workspace_id": str(1000000000000000000 + i),
                    "name": f"工作空间{i}",
                    "enterprise_id": 12345
                } for i in range(1, 11)
            ]
        }
    }
    mock_response_page2 = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 25,
            "page": 2,
            "page_size": 10,
            "workspaces": [
                {
                    "workspace_id": str(1000000000000000000 + i),
                    "name": f"工作空间{i}",
                    "enterprise_id": 12345
                } for i in range(11, 21)
            ]
        }
    }
    mock_response_page3 = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 25,
            "page": 3,
            "page_size": 10,
            "workspaces": [
                {
                    "workspace_id": str(1000000000000000000 + i),
                    "name": f"工作空间{i}",
                    "enterprise_id": 12345
                } for i in range(21, 26)
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(
        client.http_client,
        'get',
        side_effect=[mock_response_page1, mock_response_page2, mock_response_page3]
    ):
        workspaces = list(client.workspace.iter(
            enterprise_id=12345,
            page_size=10
        ))

        # 验证返回结果
        assert len(workspaces) == 25
        assert workspaces[0].workspace_id == "1000000000000000001"
        assert workspaces[24].workspace_id == "1000000000000000025"


def test_workspace_iter_with_max_pages(client):
    """测试迭代工作空间（限制最大页数）"""
    # Mock 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 100,
            "page": 1,
            "page_size": 10,
            "workspaces": [
                {
                    "workspace_id": str(1000000000000000000 + i),
                    "name": f"工作空间{i}",
                    "enterprise_id": 12345
                } for i in range(1, 11)
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        workspaces = list(client.workspace.iter(
            enterprise_id=12345,
            page_size=10,
            max_pages=2
        ))

        # 验证返回结果（只获取 2 页，每页 10 个）
        assert len(workspaces) == 20


def test_workspace_iter_empty_result(client):
    """测试迭代工作空间（空结果）"""
    # Mock 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 0,
            "page": 1,
            "page_size": 20,
            "workspaces": []
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        workspaces = list(client.workspace.iter(enterprise_id=12345))

        # 验证返回结果
        assert len(workspaces) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
