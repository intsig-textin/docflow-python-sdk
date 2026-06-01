"""测试批量操作接口"""
import pytest
from unittest.mock import patch, MagicMock
from docflow import DocflowClient, ExtractModel
from docflow.exceptions import ValidationError


@pytest.fixture
def client():
    return DocflowClient(
        app_id="test_app_id",
        secret_code="test_secret",
        base_url="https://test.api.example.com",
        max_retries=0,
        timeout=5,
    )


# ==================== Field Batch Operations ====================


def test_field_batch_add_success(client):
    """测试批量新增字段"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": [
            {"field_id": "f001"},
            {"field_id": "f002"},
        ]
    }

    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.fields.batch_add(
            workspace_id="123",
            category_id="456",
            fields=[
                {"name": "发票号码", "prompt": "发票唯一标识"},
                {"name": "金额", "description": "总金额"},
            ]
        )

        assert len(result.fields) == 2
        assert result.fields[0].field_id == "f001"
        assert result.fields[1].field_id == "f002"


def test_field_batch_add_with_detail(client):
    """测试批量新增字段（with_detail=True）"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": [
            {
                "field_id": "f001",
                "name": "发票号码",
                "description": None,
                "prompt": "发票唯一标识",
                "use_prompt": True,
                "extract_model": "Model 1",
                "enabled": 1,
            },
        ]
    }

    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.fields.batch_add(
            workspace_id="123",
            category_id="456",
            fields=[{"name": "发票号码", "prompt": "发票唯一标识"}],
            with_detail=True,
        )

        assert result.fields[0].field_id == "f001"
        assert result.fields[0].name == "发票号码"
        assert result.fields[0].extract_model == "Model 1"


def test_field_batch_add_with_table_id(client):
    """测试批量新增表格字段"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": [{"field_id": "f001"}]
    }

    with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
        result = client.category.fields.batch_add(
            workspace_id="123",
            category_id="456",
            table_id="789",
            fields=[{"name": "品名"}],
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs.get("json_data") or call_kwargs[1].get("json_data")
        assert payload["table_id"] == "789"


def test_field_batch_add_validation_empty_fields(client):
    """测试批量新增字段校验——空列表"""
    with pytest.raises(ValidationError):
        client.category.fields.batch_add(
            workspace_id="123",
            category_id="456",
            fields=[],
        )


def test_field_batch_update_success(client):
    """测试批量更新字段（without with_detail）"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": None
    }

    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.fields.batch_update(
            workspace_id="123",
            category_id="456",
            fields=[
                {"field_id": "f001", "name": "发票号码_v2"},
                {"field_id": "f002", "name": "金额_v2"},
            ]
        )

        assert result is None


def test_field_batch_update_with_detail(client):
    """测试批量更新字段（with_detail=True）"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": [
            {"field_id": "f001", "name": "发票号码_v2", "enabled": 1},
        ]
    }

    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.fields.batch_update(
            workspace_id="123",
            category_id="456",
            fields=[{"field_id": "f001", "name": "发票号码_v2"}],
            with_detail=True,
        )

        assert result.fields[0].field_id == "f001"
        assert result.fields[0].name == "发票号码_v2"


def test_field_batch_update_validation_empty(client):
    """测试批量更新字段校验——空列表"""
    with pytest.raises(ValidationError):
        client.category.fields.batch_update(
            workspace_id="123",
            category_id="456",
            fields=[],
        )


# ==================== Table Batch Operations ====================


def test_table_batch_add_success(client):
    """测试批量新增表格"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": [
            {"table_id": "t001"},
            {"table_id": "t002"},
        ]
    }

    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.tables.batch_add(
            workspace_id="123",
            category_id="456",
            tables=[
                {"name": "费用明细", "prompt": "抽取费用"},
                {"name": "住宿明细", "collect_from_multi_table": True},
            ]
        )

        assert len(result.tables) == 2
        assert result.tables[0].table_id == "t001"


def test_table_batch_add_with_detail(client):
    """测试批量新增表格（with_detail=True，含内嵌字段）"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": [
            {
                "table_id": "t001",
                "name": "费用明细",
                "prompt": "抽取费用",
                "collect_from_multi_table": False,
                "extract_model": "Model 1",
                "fields": [
                    {"id": "f001", "name": "日期", "enabled": 1},
                    {"id": "f002", "name": "金额", "enabled": 1},
                ]
            },
        ]
    }

    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.tables.batch_add(
            workspace_id="123",
            category_id="456",
            tables=[{"name": "费用明细", "fields": [{"name": "日期"}, {"name": "金额"}]}],
            with_detail=True,
        )

        assert result.tables[0].table_id == "t001"
        assert result.tables[0].name == "费用明细"
        assert len(result.tables[0].fields) == 2


def test_table_batch_add_validation_empty(client):
    """测试批量新增表格校验——空列表"""
    with pytest.raises(ValidationError):
        client.category.tables.batch_add(
            workspace_id="123",
            category_id="456",
            tables=[],
        )


def test_table_batch_update_success(client):
    """测试批量更新表格"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": None
    }

    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.tables.batch_update(
            workspace_id="123",
            category_id="456",
            tables=[
                {"table_id": "t001", "name": "费用明细_v2"},
                {"table_id": "t002", "collect_from_multi_table": True},
            ]
        )

        assert result is None


def test_table_batch_update_validation_empty(client):
    """测试批量更新表格校验——空列表"""
    with pytest.raises(ValidationError):
        client.category.tables.batch_update(
            workspace_id="123",
            category_id="456",
            tables=[],
        )


# ==================== Sample Batch Operations ====================


def test_sample_batch_upload_success(client):
    """测试批量上传样本"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    with patch('docflow.utils.file_handler.FileHandler.prepare_files', return_value=[]):
        with patch.object(client.http_client, 'request', return_value=mock_response):
            result = client.category.samples.batch_upload(
                workspace_id="123",
                category_id="456",
                files=["sample1.pdf", "sample2.pdf"],
            )

            assert result is not None
            assert result.samples is None


def test_sample_batch_upload_with_detail(client):
    """测试批量上传样本（with_detail=True）"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "samples": [
                {"sample_id": "s001", "file_name": "sample1.pdf"},
                {"sample_id": "s002", "file_name": "sample2.pdf"},
            ]
        }
    }

    with patch('docflow.utils.file_handler.FileHandler.prepare_files', return_value=[]):
        with patch.object(client.http_client, 'request', return_value=mock_response):
            result = client.category.samples.batch_upload(
                workspace_id="123",
                category_id="456",
                files=["sample1.pdf", "sample2.pdf"],
                with_detail=True,
            )

            assert result.samples is not None
            assert len(result.samples) == 2
            assert result.samples[0].sample_id == "s001"


def test_sample_batch_upload_validation_empty(client):
    """测试批量上传样本校验——空文件列表"""
    with pytest.raises(ValidationError):
        client.category.samples.batch_upload(
            workspace_id="123",
            category_id="456",
            files=[],
        )


def test_sample_batch_upload_validation_too_many(client):
    """测试批量上传样本校验——超过10个文件"""
    with pytest.raises(ValidationError):
        client.category.samples.batch_upload(
            workspace_id="123",
            category_id="456",
            files=[f"file{i}.pdf" for i in range(11)],
        )


def test_sample_batch_download_success(client):
    """测试批量下载样本（ZIP）"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'PK\x03\x04fake_zip_data'
    mock_response.headers = {
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename="samples_456.zip"'
    }
    mock_response.raise_for_status.return_value = None

    with patch.object(client.http_client.session, 'post', return_value=mock_response):
        result = client.category.samples.batch_download(
            workspace_id="123",
            category_id="456",
            sample_ids=["s001", "s002"],
        )

        assert isinstance(result, tuple)
        file_data, filename = result
        assert isinstance(file_data, bytes)
        assert b'PK' in file_data
        assert filename == "samples_456.zip"


def test_sample_batch_download_all(client):
    """测试批量下载全部样本（不传 sample_ids）"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'PK\x03\x04fake_zip_data'
    mock_response.headers = {
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename="samples_456.zip"'
    }
    mock_response.raise_for_status.return_value = None

    with patch.object(client.http_client.session, 'post', return_value=mock_response):
        result = client.category.samples.batch_download(
            workspace_id="123",
            category_id="456",
        )

        file_data, filename = result
        assert isinstance(file_data, bytes)


def test_sample_batch_download_save_to_file(client, tmp_path):
    """测试批量下载样本并保存"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'PK\x03\x04fake_zip_data'
    mock_response.headers = {
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename="samples_456.zip"'
    }
    mock_response.raise_for_status.return_value = None

    with patch.object(client.http_client.session, 'post', return_value=mock_response):
        result = client.category.samples.batch_download(
            workspace_id="123",
            category_id="456",
            save_path=str(tmp_path),
        )

        assert isinstance(result, bytes)
        saved_file = tmp_path / "samples_456.zip"
        assert saved_file.exists()


# ==================== Category Create with Tables ====================


def test_category_create_with_tables(client):
    """测试一站式创建分类（含表格）"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {"category_id": "111222333"}
    }

    with patch('docflow.utils.file_handler.FileHandler.prepare_files', return_value=[]):
        with patch.object(client.http_client, 'request', return_value=mock_response) as mock_req:
            result = client.category.create(
                workspace_id="123456",
                name="酒店水单",
                extract_model=ExtractModel.Model_1,
                sample_files=["sample.pdf"],
                fields=[
                    {"name": "入住日期"},
                    {"name": "房间号"}
                ],
                tables=[
                    {
                        "name": "费用明细",
                        "prompt": "请抽取每行费用",
                        "extract_model": "Model 1",
                        "collect_from_multi_table": False,
                    }
                ],
            )

            assert result.category_id == "111222333"
            call_kwargs = mock_req.call_args
            form_data = call_kwargs.kwargs.get("data") or call_kwargs[1].get("data")
            assert "tables" in form_data


def test_category_create_without_tables_backward_compatible(client):
    """测试不传 tables 时行为不变"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {"category_id": "111222333"}
    }

    with patch('docflow.utils.file_handler.FileHandler.prepare_files', return_value=[]):
        with patch.object(client.http_client, 'request', return_value=mock_response) as mock_req:
            result = client.category.create(
                workspace_id="123456",
                name="发票",
                extract_model="Model 1",
                sample_files=["sample.pdf"],
                fields=[{"name": "金额"}],
            )

            assert result.category_id == "111222333"
            call_kwargs = mock_req.call_args
            form_data = call_kwargs.kwargs.get("data") or call_kwargs[1].get("data")
            assert "tables" not in form_data


# ==================== Context Layer Batch Methods ====================


def test_context_field_batch_add(client):
    """测试 Context 层批量新增字段"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": [{"field_id": "f001"}]
    }

    with patch.object(client.http_client, 'post', return_value=mock_response):
        ws = client.workspace("123")
        cat = ws.category("456")
        result = cat.fields.batch_add(
            fields=[{"name": "发票号码"}],
            with_detail=True,
        )

        assert result.fields[0].field_id == "f001"


def test_context_table_batch_add(client):
    """测试 Context 层批量新增表格"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": [{"table_id": "t001"}]
    }

    with patch.object(client.http_client, 'post', return_value=mock_response):
        ws = client.workspace("123")
        cat = ws.category("456")
        result = cat.tables.batch_add(
            tables=[{"name": "费用明细"}],
        )

        assert result.tables[0].table_id == "t001"


def test_context_sample_batch_upload(client):
    """测试 Context 层批量上传样本"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "samples": [{"sample_id": "s001", "file_name": "a.pdf"}]
        }
    }

    with patch('docflow.utils.file_handler.FileHandler.prepare_files', return_value=[]):
        with patch.object(client.http_client, 'request', return_value=mock_response):
            ws = client.workspace("123")
            cat = ws.category("456")
            result = cat.samples.batch_upload(
                files=["a.pdf"],
                with_detail=True,
            )

            assert result.samples[0].sample_id == "s001"
