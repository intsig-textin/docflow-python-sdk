"""
类别资源测试
"""
import pytest
from unittest.mock import patch, MagicMock
from docflow import DocflowClient, ExtractModel, set_language
from docflow.exceptions import ValidationError, APIError
from docflow.models.category import CategoryKeywordRuleGroup, CategoryKeywordRules
from docflow.resources.category import validate_category_keyword_rules


def _keyword_rules():
    return {
        "positive_rules": [{
            "group_name": "发票要素",
            "min_hit": 1,
            "words": [" 发票　号码 ", "价税合计"],
        }],
        "negative_rules": [],
    }


def test_category_list_validation(client):
    """测试类别列表参数校验"""
    # 测试空工作空间 ID
    with pytest.raises(ValidationError, match="工作空间 ID 不能为空"):
        client.category.list(workspace_id="")

    # 测试无效页码
    with pytest.raises(ValidationError, match="页码必须大于等于 1"):
        client.category.list(workspace_id="123", page=0)

    # 测试无效页大小
    with pytest.raises(ValidationError, match="每页数量必须在 1-100 之间"):
        client.category.list(workspace_id="123", page_size=0)


def test_category_list_success(client, mock_workspace_id, mock_category_data):
    """测试类别列表正常返回"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "categories": [
                mock_category_data,
                {
                    "category_id": "456790",
                    "workspace_id": mock_workspace_id,
                    "name": "测试类别2",
                    "extract_model": "standard",
                    "enabled": 1
                }
            ],
            "total": 2,
            "page": 1,
            "page_size": 10
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        result = client.category.list(workspace_id=mock_workspace_id, page=1, page_size=10)

        # 验证返回结果
        assert result is not None
        assert len(result.categories) == 2
        assert result.total == 2
        assert result.page == 1


def test_category_list_deserializes_keyword_rules(client, mock_workspace_id):
    """列表响应中的关键字规则应被解析为 SDK 模型。"""
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "categories": [{
                "category_id": "456789",
                "workspace_id": mock_workspace_id,
                "name": "带关键字规则的类别",
                "extract_model": "standard",
                "enabled": 1,
                "category_keyword_rules": {
                    "positive_rules": [{
                        "group_name": "发票要素",
                        "min_hit": 1,
                        "words": ["发票号码", "价税合计"],
                    }],
                    "negative_rules": [],
                },
            }],
            "total": 1,
            "page": 1,
            "page_size": 10,
        },
    }

    with patch.object(client.http_client, "get", return_value=mock_response):
        result = client.category.list(workspace_id=mock_workspace_id)

    rules = result.categories[0].category_keyword_rules
    assert rules is not None
    assert rules.positive_rules[0].group_name == "发票要素"
    assert rules.positive_rules[0].min_hit == 1
    assert rules.positive_rules[0].words == ["发票号码", "价税合计"]
    assert rules.negative_rules == []


def test_category_create_validation(client):
    """测试类别创建参数校验"""
    # 测试空名称
    with pytest.raises(ValidationError, match="类别名称"):
        client.category.create(
            workspace_id="123",
            name="",
            extract_model=ExtractModel.Model_1,
            sample_files=["test.pdf"],
            fields=[{"name": "field1"}]
        )

    # 测试名称过长
    with pytest.raises(ValidationError, match="类别名称"):
        client.category.create(
            workspace_id="123",
            name="a" * 51,
            extract_model=ExtractModel.Model_1,
            sample_files=["test.pdf"],
            fields=[{"name": "field1"}]
        )

    # 测试空样本文件列表
    with pytest.raises(ValidationError, match="样本文件"):
        client.category.create(
            workspace_id="123",
            name="测试",
            extract_model=ExtractModel.Model_1,
            sample_files=[],
            fields=[{"name": "field1"}]
        )

    # 测试空字段列表
    with pytest.raises(ValidationError, match="字段"):
        client.category.create(
            workspace_id="123",
            name="测试",
            extract_model=ExtractModel.Model_1,
            sample_files=["test.pdf"],
            fields=[]
        )


def test_category_create_success(client, mock_workspace_id, mock_category_data):
    """测试类别创建成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "categoryId": mock_category_data["id"]
        }
    }

    # Mock 文件处理和 HTTP 请求
    with patch('docflow.utils.file_handler.FileHandler.prepare_files', return_value=[]):
        with patch.object(client.http_client, 'request', return_value=mock_response):
            result = client.category.create(
                workspace_id=mock_workspace_id,
                name="新类别",
                extract_model=ExtractModel.Model_1,
                sample_files=["invoice.pdf", "contract.pdf"],
                fields=[
                    {"name": "发票号码", "type": "text"},
                    {"name": "金额", "type": "number"}
                ]
            )

            # 验证返回结果
            assert result is not None
            assert result.category_id == mock_category_data["id"]


def test_category_create_sends_keyword_rules_as_multipart_json(client, mock_workspace_id):
    response = {"code": 200, "msg": "success", "result": {"categoryId": "456"}}
    with patch('docflow.utils.file_handler.FileHandler.prepare_files', return_value=[]):
        with patch.object(client.http_client, 'request', return_value=response) as request:
            client.category.create(
                workspace_id=mock_workspace_id,
                name="新类别",
                extract_model=ExtractModel.Model_1,
                sample_files=["invoice.pdf"],
                fields=[{"name": "发票号码"}],
                category_keyword_rules=_keyword_rules(),
                check_keyword_rule_conflicts=False,
            )
    data = request.call_args.kwargs["data"]
    assert data["category_keyword_rules"] == (
        '{"positive_rules": [{"group_name": "发票要素", "min_hit": 1, '
        '"words": ["发票号码", "价税合计"]}], "negative_rules": []}'
    )


def test_category_update_validation(client):
    """测试类别更新参数校验"""
    # 测试空工作空间 ID
    with pytest.raises(ValidationError, match="工作空间 ID 不能为空"):
        client.category.update(
            workspace_id="",
            category_id="456",
            name="测试"
        )

    # 测试空类别 ID
    with pytest.raises(ValidationError, match="类别 ID 不能为空"):
        client.category.update(
            workspace_id="123",
            category_id="",
            name="测试"
        )


def test_category_update_success(client, mock_workspace_id, mock_category_id):
    """测试类别更新成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.update(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id,
            name="更新后的类别名称"
        )

        # update 方法返回 None，只验证没有抛出异常
        assert result is None


def test_category_update_sends_keyword_rules_and_explicit_clear(client, mock_workspace_id, mock_category_id):
    response = {"code": 200, "msg": "success", "result": {}}
    with patch.object(client.http_client, 'post', return_value=response) as post:
        client.category.update(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id,
            category_keyword_rules={"positive_rules": [], "negative_rules": []},
            check_keyword_rule_conflicts=False,
        )
    assert post.call_args.kwargs["json_data"]["category_keyword_rules"] == {
        "positive_rules": [], "negative_rules": []
    }


def test_category_update_omits_none_keyword_rules(client, mock_workspace_id, mock_category_id):
    response = {"code": 200, "msg": "success", "result": {}}
    with patch.object(client.http_client, 'post', return_value=response) as post:
        client.category.update(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id,
            category_keyword_rules=None,
        )
    assert "category_keyword_rules" not in post.call_args.kwargs["json_data"]


def test_category_keyword_rule_precheck_uses_enabled_pages_and_excludes_self(
        client, mock_workspace_id, mock_category_id):
    """Precheck must page through enabled categories, ignore the updated category, and fail on others."""
    first_page = {
        "code": 200, "msg": "success", "result": {
            "categories": [{
                "id": mock_category_id, "name": "自身", "enabled": 1,
                "category_keyword_rules": _keyword_rules(),
            }], "total": 101, "page": 1, "page_size": 100,
        },
    }
    second_page = {
        "code": 200, "msg": "success", "result": {
            "categories": [{
                "id": "999", "name": "冲突类别", "enabled": 1,
                "category_keyword_rules": _keyword_rules(),
            }], "total": 101, "page": 2, "page_size": 100,
        },
    }
    with patch.object(client.http_client, "get", side_effect=[first_page, second_page]) as get:
        with pytest.raises(ValidationError, match="冲突类别"):
            client.category._validate_keyword_rule_conflicts(
                mock_workspace_id, validate_category_keyword_rules(_keyword_rules()), mock_category_id
            )
    assert get.call_count == 2


def test_category_keyword_rule_precheck_can_be_disabled(client, mock_workspace_id):
    response = {"code": 200, "msg": "success", "result": {"categoryId": "456"}}
    with patch('docflow.utils.file_handler.FileHandler.prepare_files', return_value=[]):
        with patch.object(client.http_client, "request", return_value=response):
            client.category.create(
                workspace_id=mock_workspace_id,
                name="新类别",
                extract_model=ExtractModel.Model_1,
                sample_files=["invoice.pdf"],
                fields=[{"name": "发票号码"}],
                category_keyword_rules=_keyword_rules(),
                check_keyword_rule_conflicts=False,
            )


@pytest.mark.parametrize("rules", [
    {},
    {"positive_rules": []},
    {"positive_rules": "not-a-list", "negative_rules": []},
    {"positive_rules": [{}], "negative_rules": []},
    {"positive_rules": [{"group_name": "g", "min_hit": 1, "words": ["a", " a "]}], "negative_rules": []},
    {"positive_rules": [{"group_name": "g", "min_hit": 2, "words": ["a"]}], "negative_rules": []},
    {"positive_rules": [{"group_name": "g", "min_hit": 1, "words": ["a"]}],
     "negative_rules": [{"group_name": "n", "min_hit": 1, "words": ["Ａ"]},
                        {"group_name": "n2", "min_hit": 1, "words": ["b"]}]},
])
def test_category_keyword_rules_invalid(rules):
    with pytest.raises(ValidationError):
        validate_category_keyword_rules(rules)


@pytest.mark.parametrize(("rules", "message"), [
    ({"positive_rules": [{"group_name": "g", "min_hit": 1, "words": [" 　\u200b"]}], "negative_rules": []}, "关键词不能为空"),
    ({"positive_rules": [{"group_name": "g", "min_hit": 1, "words": ["a" * 51]}], "negative_rules": []}, "关键词长度不能超过 50 个字符"),
    ({"positive_rules": [{"group_name": "  ", "min_hit": 1, "words": ["a"]}], "negative_rules": []}, "规则组名称不能为空"),
    ({"positive_rules": [{"group_name": "g", "min_hit": True, "words": ["a"]}], "negative_rules": []}, "min_hit 必须是整数"),
    ({"positive_rules": [{"group_name": "g", "min_hit": 1, "words": [1]}], "negative_rules": []}, "关键词必须是字符串"),
    ({"positive_rules": [{"group_name": "g", "min_hit": 1, "words": ["a" for _ in range(21)]}], "negative_rules": []}, "每个关键词规则组不能超过 20 个关键词"),
    ({"positive_rules": [{"group_name": str(i), "min_hit": 1, "words": [str(i)]} for i in range(11)], "negative_rules": []}, "正向关键词规则组不能超过 10 个"),
    ({"positive_rules": [], "negative_rules": [
        {"group_name": "n1", "min_hit": 1, "words": ["a"]},
        {"group_name": "n2", "min_hit": 1, "words": ["b"]},
    ]}, "反向关键词规则组不能超过 1 个"),
    ({"positive_rules": [{"group_name": "g", "min_hit": 1, "words": ["a"], "extra": "x"}], "negative_rules": []}, "不能包含未知字段"),
])
def test_category_keyword_rules_invalid_boundary_messages(rules, message):
    """每个开放规则约束都应在网络请求前给出明确错误。"""
    with pytest.raises(ValidationError, match=message):
        validate_category_keyword_rules(rules)


def test_category_create_invalid_keyword_rules_does_not_send_request(client, mock_workspace_id):
    """SDK 本地校验失败时不得向服务端发起 multipart 创建请求。"""
    invalid_rules = {"positive_rules": [], "negative_rules": [{
        "group_name": "n", "min_hit": 0, "words": ["invoice"],
    }]}

    with patch('docflow.utils.file_handler.FileHandler.prepare_files', return_value=[]):
        with patch.object(client.http_client, "request") as request:
            with pytest.raises(ValidationError, match="min_hit 必须在 1 到关键词数量之间"):
                client.category.create(
                    workspace_id=mock_workspace_id,
                    name="异常规则类别",
                    extract_model=ExtractModel.Model_1,
                    sample_files=["invoice.pdf"],
                    fields=[{"name": "发票号码"}],
                    category_keyword_rules=invalid_rules,
                    check_keyword_rule_conflicts=False,
                )
    request.assert_not_called()


def test_category_keyword_rules_normalization_and_conflicts():
    assert validate_category_keyword_rules(_keyword_rules())["positive_rules"][0]["words"] == [
        "发票号码", "价税合计"
    ]
    with pytest.raises(ValidationError, match="正向和反向"):
        validate_category_keyword_rules({
            "positive_rules": [{"group_name": "p", "min_hit": 1, "words": ["发票 号码"]}],
            "negative_rules": [{"group_name": "n", "min_hit": 1, "words": ["发票　号码"]}],
        })
    with pytest.raises(ValidationError, match="重复的关键词规则组"):
        validate_category_keyword_rules({
            "positive_rules": [
                {"group_name": "p1", "min_hit": 1, "words": ["a", "b"]},
                {"group_name": "p2", "min_hit": 1, "words": [" b", "a "]},
            ],
            "negative_rules": [],
        })


def test_category_keyword_rules_generate_default_group_names():
    """SDK 可省略展示名称，并生成与前端默认值一致的名称。"""
    rules = validate_category_keyword_rules({
        "positive_rules": [
            {"min_hit": 1, "words": ["invoice"]},
            {"min_hit": 1, "words": ["contract"]},
        ],
        "negative_rules": [{"min_hit": 1, "words": ["receipt"]}],
    })

    assert [group["group_name"] for group in rules["positive_rules"]] == ["group_1", "group_2"]
    assert rules["negative_rules"][0]["group_name"] == "exclude"


def test_category_keyword_rule_model_can_omit_group_name():
    rules = CategoryKeywordRules(
        positive_rules=[CategoryKeywordRuleGroup(min_hit=1, words=["invoice"])],
    )
    assert validate_category_keyword_rules(rules)["positive_rules"][0]["group_name"] == "group_1"


def test_category_keyword_rules_accept_models():
    rules = CategoryKeywordRules(
        positive_rules=[CategoryKeywordRuleGroup("p", 1, [" A "])],
        negative_rules=[],
    )
    assert validate_category_keyword_rules(rules)["positive_rules"][0]["words"] == ["a"]


def test_category_delete_validation(client):
    """测试类别删除参数校验"""
    # 测试空 ID 列表
    with pytest.raises(ValidationError, match="category_ids 不能为空"):
        client.category.delete(
            workspace_id="123",
            category_ids=[]
        )


def test_category_delete_success(client, mock_workspace_id, mock_category_id):
    """测试类别删除成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.delete(
            workspace_id=mock_workspace_id,
            category_ids=[mock_category_id, "456790"]
        )

        # delete 方法返回 None，只验证没有抛出异常
        assert result is None


def test_field_add_validation(client):
    """测试字段添加参数校验"""
    # 测试空字段名
    with pytest.raises(ValidationError):
        client.category.fields.add(
            workspace_id="123",
            category_id="456",
            name=""
        )


def test_field_add_success(client, mock_workspace_id, mock_category_id):
    """测试字段添加成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "fieldId": "789012"
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.fields.add(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id,
            name="发票号码",
            field_type="text",
            required=True
        )

        # 验证返回结果
        assert result is not None
        assert result.field_id == "789012"


def test_field_update_validation(client):
    """测试字段更新参数校验"""
    # 测试空字段 ID
    with pytest.raises(ValidationError):
        client.category.fields.update(
            workspace_id="123",
            category_id="456",
            field_id="",
            name="测试"
        )


def test_field_update_success(client, mock_workspace_id, mock_category_id):
    """测试字段更新成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.fields.update(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id,
            field_id="789012",
            name="更新后的字段名"
        )

        # update 方法返回 None，只验证没有抛出异常
        assert result is None


def test_field_delete_validation(client):
    """测试字段删除参数校验"""
    # 测试空 ID 列表
    with pytest.raises(ValidationError):
        client.category.fields.delete(
            workspace_id="123",
            category_id="456",
            field_ids=[]
        )


def test_field_delete_success(client, mock_workspace_id, mock_category_id):
    """测试字段删除成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.fields.delete(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id,
            field_ids=["789012", "789013"]
        )

        # delete 方法返回 None，只验证没有抛出异常
        assert result is None


def test_table_add_validation(client):
    """测试表格添加参数校验"""
    # 测试空表格名
    with pytest.raises(ValidationError):
        client.category.tables.add(
            workspace_id="123",
            category_id="456",
            name=""
        )


def test_table_add_success(client, mock_workspace_id, mock_category_id):
    """测试表格添加成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "tableId": "800001"
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.tables.add(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id,
            name="货物明细表",
            prompt="请抽取每行的商品名称、数量和单价",
            collect_from_multi_table=True
        )

        # 验证返回结果
        assert result is not None
        assert result.table_id == "800001"


def test_table_update_validation(client):
    """测试表格更新参数校验"""
    # 测试空表格 ID
    with pytest.raises(ValidationError):
        client.category.tables.update(
            workspace_id="123",
            category_id="456",
            table_id="",
            collect_from_multi_table=True,
            name="测试"
        )


def test_table_update_success(client, mock_workspace_id, mock_category_id):
    """测试表格更新成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.tables.update(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id,
            table_id="800001",
            collect_from_multi_table=True,
            name="更新后的表格名称",
            prompt="请抽取每行的品名、数量和金额"
        )

        # update 方法返回 None，只验证没有抛出异常
        assert result is None


def test_table_delete_validation(client):
    """测试表格删除参数校验"""
    # 测试空 ID 列表
    with pytest.raises(ValidationError):
        client.category.tables.delete(
            workspace_id="123",
            category_id="456",
            table_ids=[]
        )


def test_table_delete_success(client, mock_workspace_id, mock_category_id):
    """测试表格删除成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.tables.delete(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id,
            table_ids=["800001", "800002"]
        )

        # delete 方法返回 None，只验证没有抛出异常
        assert result is None


def test_table_list_validation(client):
    """测试表格列表参数校验"""
    # 测试空工作空间 ID
    with pytest.raises(ValidationError, match="工作空间 ID 不能为空"):
        client.category.tables.list(
            workspace_id="",
            category_id="456"
        )


def test_table_list_success(client, mock_workspace_id, mock_category_id):
    """测试表格列表正常返回"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "tables": [
                {
                    "table_id": "800001",
                    "name": "货物明细表",
                    "prompt": "请抽取每行的品名、数量和金额",
                    "collect_from_multi_table": True
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        result = client.category.tables.list(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id
        )

        # 验证返回结果
        assert result is not None
        assert len(result.tables) == 1
        assert result.tables[0].id == "800001"


def test_field_list_validation(client):
    """测试字段列表参数校验"""
    # 测试空工作空间 ID
    with pytest.raises(ValidationError, match="工作空间 ID 不能为空"):
        client.category.fields.list(
            workspace_id="",
            category_id="456"
        )


def test_field_list_success(client, mock_workspace_id, mock_category_id):
    """测试字段列表正常返回"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "fields": [
                {
                    "name": "发票代码",
                    "description": "发票代码描述",
                    "prompt": "发票代码提示词",
                    "use_prompt": True,
                    "alias": [
                    "别名1"
                    ],
                    "multi_value": True,
                    "duplicate_value_distinct": True,
                    "transform_settings": {
                    "type": "datetime",
                    "datetime_settings": {
                        "format": "yyyy-MM-dd HH:mm:ss"
                    },
                    "mismatch_action": {
                        "mode": "default",
                        "default_value": "默认值"
                    }
                    },
                    "id": "1234567890"
                }
            ],
            "tables": [
                {
                    "id": "234567890",
                    "name": "表格1",
                    "description": "表格描述",
                    "fields": [
                    {
                        "name": "发票代码",
                        "description": "发票代码描述",
                        "prompt": "发票代码提示词",
                        "use_prompt": True,
                        "alias": [
                        "代码别名1"
                        ],
                        "identity": "导出名",
                        "multi_value": True,
                        "duplicate_value_distinct": True,
                        "id": "1234567890111"
                    }
                    ]
                }
            ]
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        result = client.category.fields.list(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id
        )

        # 验证返回结果
        assert result is not None
        assert len(result.fields) == 1
        assert len(result.tables) == 1
        assert result.fields[0].id == "1234567890"
        assert result.tables[0].id == "234567890"
        assert result.tables[0].fields[0].id == "1234567890111"


def test_category_iter(client, mock_workspace_id, mock_category_data):
    """测试类别迭代器"""
    # Mock API 响应（多页数据）
    mock_response_page1 = {
        "code": 200,
        "msg": "success",
        "result": {
            "categories": [mock_category_data],
            "total": 2,
            "page": 1,
            "page_size": 1
        }
    }

    mock_response_page2 = {
        "code": 200,
        "msg": "success",
        "result": {
            "categories": [{
                "id": "456790",
                "name": "测试类别2",
                "extract_model": "vlm",
                "enabled": 1
            }],
            "total": 2,
            "page": 2,
            "page_size": 1
        }
    }

    # Mock HTTP 请求（模拟分页）
    with patch.object(client.http_client, 'get', side_effect=[mock_response_page1, mock_response_page2]):
        categories = list(client.category.iter(
            workspace_id=mock_workspace_id,
            page_size=1
        ))

        # 验证迭代结果
        assert len(categories) == 2
        assert categories[0].id == mock_category_data["id"]
        assert categories[1].id == "456790"


def test_sample_upload_validation(client):
    """测试样本上传参数校验"""
    # 测试空文件列表
    with pytest.raises((ValidationError, ValueError)):
        client.category.samples.upload(
            workspace_id="123",
            category_id="456",
            file=None
        )


def test_sample_upload_success(client, mock_workspace_id, mock_category_id):
    """测试样本上传成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "sample_id": "900001"
        }
    }

    # Mock 文件处理和 HTTP 请求
    with patch('docflow.utils.file_handler.FileHandler.prepare_file', return_value=('file', ('sample1.pdf', b'fake content', 'application/pdf'))):
        with patch.object(client.http_client, 'request', return_value=mock_response):
            result = client.category.samples.upload(
                workspace_id=mock_workspace_id,
                category_id=mock_category_id,
                file="sample1.pdf"
            )

            # 验证返回结果
            assert result is not None
            assert result.sample_id == "900001"


def test_sample_list_validation(client):
    """测试样本列表参数校验"""
    # 测试空工作空间 ID
    with pytest.raises(ValidationError, match="工作空间 ID 不能为空"):
        client.category.samples.list(
            workspace_id="",
            category_id="456"
        )

    # 测试无效页码
    with pytest.raises(ValidationError, match="页码必须大于等于 1"):
        client.category.samples.list(
            workspace_id="123",
            category_id="456",
            page=0
        )


def test_sample_list_success(client, mock_workspace_id, mock_category_id):
    """测试样本列表正常返回"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {
            "samples": [
                {
                    "sample_id": "900001",
                    "file_name": "sample1.pdf",
                    "upload_time": "2024-01-01 10:00:00"
                },
                {
                    "sample_id": "900002",
                    "file_name": "sample2.pdf",
                    "upload_time": "2024-01-01 10:05:00"
                }
            ],
            "total": 2,
            "page": 1,
            "page_size": 20
        }
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'get', return_value=mock_response):
        result = client.category.samples.list(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id,
            page=1,
            page_size=20
        )

        # 验证返回结果
        assert result is not None
        assert len(result.samples) == 2
        assert result.total == 2
        assert result.samples[0].sample_id == "900001"


def test_sample_download_validation(client):
    """测试样本下载参数校验"""
    # 测试空样本 ID
    with pytest.raises(ValidationError):
        client.category.samples.download(
            workspace_id="123",
            category_id="456",
            sample_id=""
        )


def test_sample_download_success(client, mock_workspace_id, mock_category_id):
    """测试样本下载成功（不保存到文件）"""
    # Mock HTTP 响应（返回文件内容）
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'PDF file content'
    mock_response.headers = {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="%E6%9C%BA%E6%89%93%E5%8F%91%E7%A5%A8.jpeg"; filename*=UTF-8\'\'%E6%9C%BA%E6%89%93%E5%8F%91%E7%A5%A8.jpeg'
    }
    mock_response.raise_for_status.return_value = None

    # Mock HTTP 请求
    with patch.object(client.http_client.session, 'get', return_value=mock_response):
        result = client.category.samples.download(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id,
            sample_id="900001"
        )

        # 验证返回结果是元组
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 2

        file_data, filename = result
        assert isinstance(file_data, bytes)
        assert len(file_data) > 0
        assert filename == "机打发票.jpeg"


def test_sample_download_with_save_path(client, mock_workspace_id, mock_category_id, tmp_path):
    """测试样本下载成功（保存到文件）"""
    # Mock HTTP 响应（返回文件内容）
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'PDF file content'
    mock_response.headers = {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="invoice.pdf"'
    }
    mock_response.raise_for_status.return_value = None

    # Mock HTTP 请求
    with patch.object(client.http_client.session, 'get', return_value=mock_response):
        result = client.category.samples.download(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id,
            sample_id="900001",
            save_path=str(tmp_path)
        )

        # 验证返回结果是 bytes
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0

        # 验证文件已保存
        saved_file = tmp_path / "invoice.pdf"
        assert saved_file.exists()
        assert saved_file.read_bytes() == b'PDF file content'


def test_sample_download_missing_content_disposition(client, mock_workspace_id, mock_category_id):
    """测试样本下载缺少 Content-Disposition 响应头（非业务错误）"""
    # Mock HTTP 响应（缺少 Content-Disposition，但不是业务错误）
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'PDF file content'
    mock_response.headers = {'Content-Type': 'application/pdf'}
    mock_response.raise_for_status.return_value = None
    # json() 抛出异常，表示不是 JSON 响应
    mock_response.json.side_effect = ValueError("Not JSON")

    # Mock HTTP 请求
    with patch.object(client.http_client.session, 'get', return_value=mock_response):
        with pytest.raises(ValidationError, match="Content-Disposition"):
            client.category.samples.download(
                workspace_id=mock_workspace_id,
                category_id=mock_category_id,
                sample_id="900001"
            )


def test_sample_download_business_error(client, mock_workspace_id, mock_category_id):
    """测试样本下载遇到业务错误（code != 200）"""
    # Mock HTTP 响应（缺少 Content-Disposition，但包含业务错误）
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"code":400,"msg":"sample not found"}'
    mock_response.headers = {'Content-Type': 'application/json'}
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "code": 400,
        "msg": "sample not found",
        "traceId": "test-trace-id"
    }

    # Mock HTTP 请求
    with patch.object(client.http_client.session, 'get', return_value=mock_response):
        with pytest.raises(APIError) as exc_info:
            client.category.samples.download(
                workspace_id=mock_workspace_id,
                category_id=mock_category_id,
                sample_id="900001"
            )

        # 验证异常信息
        assert exc_info.value.status_code == 200
        assert exc_info.value.code == "400"
        assert "sample not found" in str(exc_info.value)


def test_sample_download_invalid_content_disposition(client, mock_workspace_id, mock_category_id):
    """测试样本下载 Content-Disposition 格式无效（非业务错误）"""
    # Mock HTTP 响应（Content-Disposition 格式无效，且不是业务错误）
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'PDF file content'
    mock_response.headers = {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'inline'  # 缺少 filename
    }
    mock_response.raise_for_status.return_value = None
    # json() 抛出异常，表示不是 JSON 响应
    mock_response.json.side_effect = ValueError("Not JSON")

    # Mock HTTP 请求
    with patch.object(client.http_client.session, 'get', return_value=mock_response):
        with pytest.raises(ValidationError, match="无法从 Content-Disposition 中提取文件名"):
            client.category.samples.download(
                workspace_id=mock_workspace_id,
                category_id=mock_category_id,
                sample_id="900001"
            )


def test_sample_delete_validation(client):
    """测试样本删除参数校验"""
    # 测试空 ID 列表
    with pytest.raises(ValidationError):
        client.category.samples.delete(
            workspace_id="123",
            category_id="456",
            sample_ids=[]
        )


def test_sample_delete_success(client, mock_workspace_id, mock_category_id):
    """测试样本删除成功"""
    # Mock API 响应
    mock_response = {
        "code": 200,
        "msg": "success",
        "result": {}
    }

    # Mock HTTP 请求
    with patch.object(client.http_client, 'post', return_value=mock_response):
        result = client.category.samples.delete(
            workspace_id=mock_workspace_id,
            category_id=mock_category_id,
            sample_ids=["900001", "900002"]
        )

        # delete 方法返回 None，只验证没有抛出异常
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
