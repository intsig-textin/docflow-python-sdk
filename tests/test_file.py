"""
文件处理资源测试
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open
from docflow import DocflowClient
from docflow.exceptions import ValidationError


def test_file_resource_exists(client):
    """测试文件资源对象存在"""
    assert hasattr(client, 'file')
    assert client.file is not None


def test_file_resource_has_methods(client):
    """测试文件资源包含必要方法"""
    assert hasattr(client.file, 'upload')
    assert hasattr(client.file, 'upload_sync')
    assert hasattr(client.file, 'fetch')
    assert hasattr(client.file, 'iter')
    assert hasattr(client.file, 'update')
    assert hasattr(client.file, 'batch_update')
    assert hasattr(client.file, 'delete')
    assert hasattr(client.file, 'extract_fields')
    assert hasattr(client.file, 'retry')
    assert hasattr(client.file, 'amend_category')


def test_file_fetch_has_default_pagination(client):
    """测试文件查询默认分页参数"""
    # 这里主要测试方法签名，不实际调用 API
    import inspect
    sig = inspect.signature(client.file.fetch)
    params = sig.parameters

    # 检查默认参数
    assert 'page' in params
    assert params['page'].default == 1
    assert 'page_size' in params
    assert params['page_size'].default == 1000


def test_iter_method_exists(client):
    """测试迭代器方法存在"""
    assert hasattr(client.file, 'iter')
    assert callable(client.file.iter)


# ==================== upload 测试 ====================

def test_file_upload_success(client, mock_workspace_id):
    """测试文件上传成功"""
    # Mock API 响应（基于 OpenAPI 规范）
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "batch_number": "202412190001",
            "files": [
                {
                    "id": "file_67890",
                    "task_id": "task_12345",
                    "name": "invoice.pdf",
                    "format": "pdf"
                }
            ]
        }
    }

    # Mock open 和 HTTP 请求
    mock_file_data = b"fake file content"
    with patch('builtins.open', mock_open(read_data=mock_file_data)):
        with patch.object(client.http_client, 'post', return_value=mock_response):
            result = client.file.upload(
                workspace_id=mock_workspace_id,
                category="invoice",
                file_path="/fake/path/invoice.pdf"
            )

            # 验证返回结果
            assert result is not None
            assert result.batch_number == "202412190001"
            assert len(result.files) == 1
            assert result.files[0].id == "file_67890"
            assert result.files[0].task_id == "task_12345"


def test_file_upload_with_optional_params(client, mock_workspace_id):
    """测试文件上传（带可选参数）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "batch_number": "batch_001",
            "files": [
                {
                    "id": "file_001",
                    "task_id": "task_001",
                    "name": "test.pdf",
                    "format": "pdf"
                }
            ]
        }
    }

    # Mock open 和 HTTP 请求
    mock_file_data = b"fake file content"
    with patch('builtins.open', mock_open(read_data=mock_file_data)):
        with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
            result = client.file.upload(
                workspace_id=mock_workspace_id,
                category="invoice",
                file_path="/fake/path/invoice.pdf",
                batch_number="batch_001",
                auto_verify_vat=True,
                split_flag=False
            )

            # 验证返回结果
            assert result is not None
            assert result.batch_number == "batch_001"

            # 验证调用参数
            call_args = mock_post.call_args
            assert call_args[1]['params']['batch_number'] == "batch_001"
            assert call_args[1]['params']['auto_verify_vat'] is True
            assert call_args[1]['params']['split_flag'] is False


def test_file_upload_by_url_success(client, mock_workspace_id):
    """测试通过URL上传文件成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "batch_number": "202412190002",
            "files": [
                {
                    "id": "file_url_001",
                    "task_id": "task_url_001",
                    "name": "invoice.pdf",
                    "format": "pdf"
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.file.upload(
            workspace_id=mock_workspace_id,
            category="invoice",
            file_urls=["https://example.com/invoice.pdf"]
        )

        # 验证返回结果
        assert result is not None
        assert result.batch_number == "202412190002"
        assert len(result.files) == 1
        assert result.files[0].id == "file_url_001"

        # 验证调用参数
        call_args = mock_post.call_args
        assert 'json_data' in call_args[1]
        assert call_args[1]['json_data']['urls'] == ["https://example.com/invoice.pdf"]
        assert 'files' not in call_args[1]


def test_file_upload_by_multiple_urls(client, mock_workspace_id):
    """测试通过多个URL上传文件"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "batch_number": "batch_multi",
            "files": [
                {
                    "id": f"file_{i}",
                    "task_id": f"task_{i}",
                    "name": f"file_{i}.pdf",
                    "format": "pdf"
                } for i in range(1, 4)
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.file.upload(
            workspace_id=mock_workspace_id,
            category="invoice",
            file_urls=[
                "https://example.com/file1.pdf",
                "https://example.com/file2.pdf",
                "https://example.com/file3.pdf"
            ]
        )

        # 验证返回结果
        assert result is not None
        assert len(result.files) == 3

        # 验证调用参数
        call_args = mock_post.call_args
        assert len(call_args[1]['json_data']['urls']) == 3


def test_file_upload_validation_no_source(client, mock_workspace_id):
    """测试上传文件参数校验：未提供 file_path 或 file_urls"""
    with pytest.raises(ValidationError, match="file_path 和 file_urls 必须提供其中之一"):
        client.file.upload(
            workspace_id=mock_workspace_id,
            category="invoice"
        )


def test_file_upload_validation_both_sources(client, mock_workspace_id):
    """测试上传文件参数校验：同时提供 file_path 和 file_urls"""
    with pytest.raises(ValidationError, match="file_path 和 file_urls 不能同时提供"):
        client.file.upload(
            workspace_id=mock_workspace_id,
            category="invoice",
            file_path="/fake/path/file.pdf",
            file_urls=["https://example.com/file.pdf"]
        )


def test_file_upload_validation_empty_urls(client, mock_workspace_id):
    """测试上传文件参数校验：file_urls 为空列表"""
    with pytest.raises(ValidationError, match="file_urls 不能为空列表"):
        client.file.upload(
            workspace_id=mock_workspace_id,
            category="invoice",
            file_urls=[]
        )


def test_file_upload_validation_too_many_urls(client, mock_workspace_id):
    """测试上传文件参数校验：file_urls 超过 10 个"""
    with pytest.raises(ValidationError, match="file_urls 最多支持 10 个 URL"):
        client.file.upload(
            workspace_id=mock_workspace_id,
            category="invoice",
            file_urls=[f"https://example.com/file{i}.pdf" for i in range(1, 12)]
        )


def test_file_upload_by_url_with_optional_params(client, mock_workspace_id):
    """测试通过URL上传文件（带可选参数）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "batch_number": "batch_with_params",
            "files": [
                {
                    "id": "file_001",
                    "task_id": "task_001",
                    "name": "invoice.pdf",
                    "format": "pdf"
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.file.upload(
            workspace_id=mock_workspace_id,
            category="invoice",
            file_urls=["https://example.com/invoice.pdf"],
            batch_number="batch_with_params",
            auto_verify_vat=True,
            split_flag=False
        )

        # 验证返回结果
        assert result is not None
        assert result.batch_number == "batch_with_params"

        # 验证调用参数
        call_args = mock_post.call_args
        assert call_args[1]['json_data']['urls'] == ["https://example.com/invoice.pdf"]
        assert call_args[1]['params']['batch_number'] == "batch_with_params"
        assert call_args[1]['params']['auto_verify_vat'] is True
        assert call_args[1]['params']['split_flag'] is False


def test_file_upload_with_new_parser_params(client, mock_workspace_id):
    """测试文件上传（带 parser_dpi、parser_parse_mode、parser_pdf_pwd）"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "batch_number": "batch_parser",
            "files": [{"id": "file_001", "task_id": "task_001", "name": "test.pdf", "format": "pdf"}]
        }
    }

    mock_file_data = b"fake file content"
    with patch('builtins.open', mock_open(read_data=mock_file_data)):
        with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
            client.file.upload(
                workspace_id=mock_workspace_id,
                file_path="/fake/path/test.pdf",
                parser_dpi=216,
                parser_parse_mode="scan",
                parser_pdf_pwd="mypassword"
            )

            call_args = mock_post.call_args
            assert call_args[1]['params']['parser_dpi'] == 216
            assert call_args[1]['params']['parser_parse_mode'] == "scan"
            assert call_args[1]['params']['parser_pdf_pwd'] == "mypassword"


def test_file_upload_new_parser_params_none_not_sent(client, mock_workspace_id):
    """测试 parser_dpi/parser_parse_mode/parser_pdf_pwd 为 None 时不传入请求"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "batch_number": "batch_no_parser",
            "files": [{"id": "file_001", "task_id": "task_001", "name": "test.pdf", "format": "pdf"}]
        }
    }

    mock_file_data = b"fake file content"
    with patch('builtins.open', mock_open(read_data=mock_file_data)):
        with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
            client.file.upload(
                workspace_id=mock_workspace_id,
                file_path="/fake/path/test.pdf"
            )

            call_args = mock_post.call_args
            assert 'parser_dpi' not in call_args[1]['params']
            assert 'parser_parse_mode' not in call_args[1]['params']
            assert 'parser_pdf_pwd' not in call_args[1]['params']


# ==================== upload_sync 测试 ====================

def test_file_upload_sync_success(client, mock_workspace_id):
    """测试同步文件上传成功"""
    # Mock API 响应（基于 TaskProcessResult）
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 1,
            "page": 1,
            "page_size": 1000,
            "files": [
                {
                    "id": "file_67890",
                    "task_id": "task_12345",
                    "name": "invoice.pdf",
                    "format": "pdf",
                    "category": "invoice",
                    "recognition_status": "success"
                }
            ]
        }
    }

    # Mock open 和 HTTP 请求
    mock_file_data = b"fake file content"
    with patch('builtins.open', mock_open(read_data=mock_file_data)):
        with patch.object(client.http_client, 'post', return_value=mock_response):
            result = client.file.upload_sync(
                workspace_id=mock_workspace_id,
                category="invoice",
                file_path="/fake/path/invoice.pdf"
            )

            # 验证返回结果
            assert result is not None
            assert result.total == 1
            assert len(result.files) == 1
            assert result.files[0].id == "file_67890"
            assert result.files[0].recognition_status == "success"


def test_file_upload_sync_by_url_success(client, mock_workspace_id):
    """测试通过URL同步上传文件成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 1,
            "page": 1,
            "page_size": 1000,
            "files": [
                {
                    "id": "file_url_sync_001",
                    "task_id": "task_url_sync_001",
                    "name": "invoice.pdf",
                    "format": "pdf",
                    "category": "invoice",
                    "recognition_status": "success"
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.file.upload_sync(
            workspace_id=mock_workspace_id,
            category="invoice",
            file_urls=["https://example.com/invoice.pdf"]
        )

        # 验证返回结果
        assert result is not None
        assert result.total == 1
        assert len(result.files) == 1
        assert result.files[0].id == "file_url_sync_001"
        assert result.files[0].recognition_status == "success"

        # 验证调用参数
        call_args = mock_post.call_args
        assert 'json_data' in call_args[1]
        assert call_args[1]['json_data']['urls'] == ["https://example.com/invoice.pdf"]
        assert 'files' not in call_args[1]


def test_file_upload_sync_validation_no_source(client, mock_workspace_id):
    """测试同步上传文件参数校验：未提供 file_path 或 file_urls"""
    with pytest.raises(ValidationError, match="file_path 和 file_urls 必须提供其中之一"):
        client.file.upload_sync(
            workspace_id=mock_workspace_id,
            category="invoice"
        )


def test_file_upload_sync_validation_both_sources(client, mock_workspace_id):
    """测试同步上传文件参数校验：同时提供 file_path 和 file_urls"""
    with pytest.raises(ValidationError, match="file_path 和 file_urls 不能同时提供"):
        client.file.upload_sync(
            workspace_id=mock_workspace_id,
            category="invoice",
            file_path="/fake/path/file.pdf",
            file_urls=["https://example.com/file.pdf"]
        )


def test_file_upload_sync_by_url_with_optional_params(client, mock_workspace_id):
    """测试通过URL同步上传文件（带可选参数）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 1,
            "page": 1,
            "page_size": 1000,
            "files": [
                {
                    "id": "file_001",
                    "task_id": "task_001",
                    "name": "invoice.pdf",
                    "format": "pdf",
                    "category": "invoice",
                    "recognition_status": "success"
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.file.upload_sync(
            workspace_id=mock_workspace_id,
            category="invoice",
            file_urls=["https://example.com/invoice.pdf"],
            batch_number="batch_sync",
            with_task_detail_url=True
        )

        # 验证返回结果
        assert result is not None
        assert result.total == 1

        # 验证调用参数
        call_args = mock_post.call_args
        assert call_args[1]['json_data']['urls'] == ["https://example.com/invoice.pdf"]
        assert call_args[1]['params']['batch_number'] == "batch_sync"
        assert call_args[1]['params']['with_task_detail_url'] is True


def test_file_upload_sync_with_new_parser_params(client, mock_workspace_id):
    """测试同步上传（带 parser_dpi、parser_parse_mode、parser_pdf_pwd）"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 1, "page": 1, "page_size": 1000,
            "files": [{"id": "file_001", "task_id": "task_001", "name": "test.pdf", "format": "pdf", "recognition_status": "success"}]
        }
    }

    mock_file_data = b"fake file content"
    with patch('builtins.open', mock_open(read_data=mock_file_data)):
        with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
            client.file.upload_sync(
                workspace_id=mock_workspace_id,
                file_path="/fake/path/test.pdf",
                parser_dpi=72,
                parser_parse_mode="vlm",
                parser_pdf_pwd="pwd123"
            )

            call_args = mock_post.call_args
            assert call_args[1]['params']['parser_dpi'] == 72
            assert call_args[1]['params']['parser_parse_mode'] == "vlm"
            assert call_args[1]['params']['parser_pdf_pwd'] == "pwd123"


# ==================== fetch 测试 ====================

def test_file_fetch_success(client, mock_workspace_id):
    """测试获取文件列表成功"""
    # Mock API 响应（基于 TaskProcessResult）
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 2,
            "page": 1,
            "page_size": 10,
            "files": [
                {
                    "id": "file_001",
                    "task_id": "task_001",
                    "name": "invoice1.pdf",
                    "format": "pdf",
                    "category": "invoice",
                    "recognition_status": "success"
                },
                {
                    "id": "file_002",
                    "task_id": "task_002",
                    "name": "contract.pdf",
                    "format": "pdf",
                    "category": "contract",
                    "recognition_status": "processing"
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        result = client.file.fetch(
            workspace_id=mock_workspace_id,
            page=1,
            page_size=10
        )

        # 验证返回结果
        assert result is not None
        assert result.total == 2
        assert result.page == 1
        assert result.page_size == 10
        assert len(result.files) == 2
        assert result.files[0].id == "file_001"


def test_file_fetch_with_filters(client, mock_workspace_id):
    """测试获取文件列表（带过滤条件）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 1,
            "page": 1,
            "page_size": 1000,
            "files": [
                {
                    "id": "file_001",
                    "task_id": "task_001",
                    "name": "invoice.pdf",
                    "format": "pdf",
                    "category": "invoice",
                    "recognition_status": "success"
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response) as mock_get:
        result = client.file.fetch(
            workspace_id=mock_workspace_id,
            batch_number="batch_001",
            category="invoice",
            recognition_status="success"
        )

        # 验证返回结果
        assert result is not None
        assert result.total == 1
        assert len(result.files) == 1

        # 验证调用参数
        call_args = mock_get.call_args
        assert call_args[1]['params']['batch_number'] == "batch_001"
        assert call_args[1]['params']['category'] == "invoice"
        assert call_args[1]['params']['recognition_status'] == "success"


def test_file_fetch_empty_result(client, mock_workspace_id):
    """测试获取文件列表（空结果）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 0,
            "page": 1,
            "page_size": 1000,
            "files": []
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        result = client.file.fetch(
            workspace_id=mock_workspace_id
        )

        # 验证返回结果
        assert result is not None
        assert result.total == 0
        assert len(result.files) == 0


# ==================== iter 测试 ====================

def test_file_iter_success(client, mock_workspace_id):
    """测试文件迭代器成功"""
    # Mock 多页响应
    mock_response_page1 = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 25,
            "page": 1,
            "page_size": 10,
            "files": [
                {"id": str(1000000000000000000 + i), "task_id": str(2000000000000000000 + i), "name": f"file_{i}.pdf", "format": "pdf"} for i in range(1, 11)
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
            "files": [
                {"id": str(1000000000000000000 + i), "task_id": str(2000000000000000000 + i), "name": f"file_{i}.pdf", "format": "pdf"} for i in range(11, 21)
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
            "files": [
                {"id": str(1000000000000000000 + i), "task_id": str(2000000000000000000 + i), "name": f"file_{i}.pdf", "format": "pdf"} for i in range(21, 26)
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(
        client.http_client,
        'get',
        side_effect=[mock_response_page1, mock_response_page2, mock_response_page3]
    ):
        files = list(client.file.iter(
            workspace_id=mock_workspace_id,
            page_size=10
        ))

        # 验证返回结果
        assert len(files) == 25
        assert files[0].id == "1000000000000000001"
        assert files[24].id == "1000000000000000025"


def test_file_iter_with_max_pages(client, mock_workspace_id):
    """测试文件迭代器（限制最大页数）"""
    # Mock 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 100,
            "page": 1,
            "page_size": 10,
            "files": [
                {"id": str(1000000000000000000 + i), "task_id": str(2000000000000000000 + i), "name": f"file_{i}.pdf", "format": "pdf"} for i in range(1, 11)
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        files = list(client.file.iter(
            workspace_id=mock_workspace_id,
            page_size=10,
            max_pages=2
        ))

        # 验证返回结果（只获取 2 页，每页 10 个）
        assert len(files) == 20


def test_file_iter_empty_result(client, mock_workspace_id):
    """测试文件迭代器（空结果）"""
    # Mock 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 0,
            "page": 1,
            "page_size": 1000,
            "files": []
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        files = list(client.file.iter(workspace_id=mock_workspace_id))

        # 验证返回结果
        assert len(files) == 0


# ==================== update 测试 ====================

def test_file_update_success(client, mock_workspace_id):
    """测试更新文件成功"""
    # Mock API 响应（基于 OpenAPI 规范）
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "files": [
                {
                    "workspace_id": mock_workspace_id,
                    "id": "file_123"
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.file.update(
            workspace_id=mock_workspace_id,
            file_id="file_123",
            data={
                "fields": [{"key": "invoice_number", "value": "INV-001"}],
                "items": []
            }
        )

        # 验证返回结果
        assert result is not None
        assert len(result.files) == 1
        assert result.files[0].workspace_id == mock_workspace_id
        assert result.files[0].id == "file_123"


# ==================== batch_update 测试 ====================

def test_file_batch_update_success(client, mock_workspace_id):
    """测试批量更新文件成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "files": [
                {
                    "workspace_id": mock_workspace_id,
                    "id": "file_001"
                },
                {
                    "workspace_id": mock_workspace_id,
                    "id": "file_002"
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.file.batch_update(
            updates=[
                {
                    "workspace_id": mock_workspace_id,
                    "file_id": "file_001",
                    "data": {"fields": [{"key": "amount", "value": "100.00"}]}
                },
                {
                    "workspace_id": mock_workspace_id,
                    "file_id": "file_002",
                    "data": {"fields": [{"key": "amount", "value": "200.00"}]}
                }
            ]
        )

        # 验证返回结果
        assert result is not None
        assert len(result.files) == 2
        assert result.files[0].id == "file_001"
        assert result.files[1].id == "file_002"


# ==================== delete 测试 ====================

def test_file_delete_by_file_ids(client, mock_workspace_id):
    """测试按文件ID删除文件"""
    # Mock API 响应（基于 OpenAPI 规范）
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "deleted_count": 2
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.file.delete(
            workspace_id=mock_workspace_id,
            file_id=["file_001", "file_002"]
        )

        # 验证返回结果
        assert result is not None
        assert result.deleted_count == 2


def test_file_delete_by_batch_number(client, mock_workspace_id):
    """测试按批次号删除文件"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "deleted_count": 5
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.file.delete(
            workspace_id=mock_workspace_id,
            batch_number=["batch_001"]
        )

        # 验证返回结果
        assert result is not None
        assert result.deleted_count == 5


def test_file_delete_by_time_range(client, mock_workspace_id):
    """测试按时间范围删除文件"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "deleted_count": 10
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.file.delete(
            workspace_id=mock_workspace_id,
            start_time=1609459200,  # 2021-01-01 00:00:00
            end_time=1612137600     # 2021-02-01 00:00:00
        )

        # 验证返回结果
        assert result is not None
        assert result.deleted_count == 10

        # 验证调用参数
        call_args = mock_post.call_args
        assert call_args[1]['json_data']['start_time'] == 1609459200
        assert call_args[1]['json_data']['end_time'] == 1612137600


# ==================== extract_fields 测试 ====================

def test_file_extract_fields_success(client, mock_workspace_id):
    """测试抽取字段成功"""
    # Mock API 响应（返回 TaskProcessResult）
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 1,
            "page": 1,
            "page_size": 1000,
            "files": [
                {
                    "id": "1234567890123456789",
                    "task_id": "9876543210987654321",
                    "name": "invoice.pdf",
                    "format": "pdf",
                    "data": {
                        "fields": [
                            {"key": "invoice_number", "value": "INV-001"},
                            {"key": "amount", "value": "1000.00"}
                        ]
                    }
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.file.extract_fields(
            workspace_id=mock_workspace_id,
            task_id="task_123",
            fields=[
                {"name": "invoice_number", "description": "发票号码"},
                {"name": "amount", "description": "金额"}
            ]
        )

        # 验证返回结果
        assert result is not None
        assert result.total == 1
        assert len(result.files) == 1
        assert result.files[0].id == "1234567890123456789"


def test_file_extract_fields_with_tables(client, mock_workspace_id):
    """测试抽取字段（包含表格）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "total": 1,
            "page": 1,
            "page_size": 1000,
            "files": [
                {
                    "id": "1234567890123456789",
                    "task_id": "9876543210987654321",
                    "name": "invoice.pdf",
                    "format": "pdf"
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.file.extract_fields(
            workspace_id=mock_workspace_id,
            task_id="task_123",
            tables=[
                {
                    "name": "invoice_items",
                    "fields": [
                        {"name": "product", "description": "产品名称"},
                        {"name": "quantity", "description": "数量"}
                    ]
                }
            ]
        )

        # 验证返回结果
        assert result is not None

        # 验证调用参数
        call_args = mock_post.call_args
        assert 'tables' in call_args[1]['json_data']
        assert call_args[1]['json_data']['tables'][0]['name'] == "invoice_items"


# ==================== retry 测试 ====================

def test_file_retry_success(client, mock_workspace_id):
    """测试重新处理文件成功"""
    # Mock API 响应（只返回 CodeMessage）
    mock_response = {
        "code": 200,
        "msg": "success"
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        # 不应抛出异常
        client.file.retry(
            workspace_id=mock_workspace_id,
            task_id="task_123"
        )


def test_file_retry_with_parser_params(client, mock_workspace_id):
    """测试重新处理文件（带解析参数）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success"
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.file.retry(
            workspace_id=mock_workspace_id,
            task_id="task_123",
            parser_params={
                "remove_watermark": True,
                "formula_level": 2
            }
        )

        # 验证调用参数
        call_args = mock_post.call_args
        assert 'parser_params' in call_args[1]['json_data']
        assert call_args[1]['json_data']['parser_params']['remove_watermark'] is True


# ==================== amend_category 测试 ====================

def test_file_amend_category_success(client, mock_workspace_id):
    """测试修改文件类别成功"""
    # Mock API 响应（只返回 CodeMessage）
    mock_response = {
        "code": 200,
        "msg": "success"
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        # 不应抛出异常
        client.file.amend_category(
            workspace_id=mock_workspace_id,
            task_id="task_123",
            category="contract"
        )


def test_file_amend_category_with_split_tasks(client, mock_workspace_id):
    """测试修改文件类别（带文档拆分）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success"
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.file.amend_category(
            workspace_id=mock_workspace_id,
            task_id="task_123",
            split_tasks=[
                {
                    "category": "invoice",
                    "pages": [0, 1, 2]
                },
                {
                    "category": "contract",
                    "pages": [3, 4, 5, 6, 7, 8, 9]
                }
            ]
        )

        # 验证调用参数
        call_args = mock_post.call_args
        assert 'split_tasks' in call_args[1]['json_data']
        assert len(call_args[1]['json_data']['split_tasks']) == 2
        assert call_args[1]['json_data']['split_tasks'][0]['category'] == "invoice"
        assert call_args[1]['json_data']['split_tasks'][0]['pages'] == [0, 1, 2]


def test_file_amend_category_with_crop_tasks(client, mock_workspace_id):
    """测试修改文件类别（带多图切分）"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success"
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        client.file.amend_category(
            workspace_id=mock_workspace_id,
            task_id="task_123",
            crop_tasks=[
                {
                    "category": "invoice",
                    "coordinates": [[0, 0, 100, 100]]
                }
            ]
        )

        # 验证调用参数
        call_args = mock_post.call_args
        assert 'crop_tasks' in call_args[1]['json_data']
        assert len(call_args[1]['json_data']['crop_tasks']) == 1
        assert call_args[1]['json_data']['crop_tasks'][0]['category'] == "invoice"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
