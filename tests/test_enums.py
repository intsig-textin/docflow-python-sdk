"""
枚举类型测试
"""
import pytest
from docflow.enums import (
    ExtractModel,
    EnabledStatus,
    EnabledFlag,
    AuthScope,
    FieldType,
    MismatchAction
)


class TestEnums:
    """枚举类型测试"""

    def test_extract_model_values(self):
        """测试提取模型枚举值"""
        assert ExtractModel.Model_1 == "Model 1"
        assert ExtractModel.Model_3 == "Model 3"

    def test_extract_model_members(self):
        """测试提取模型成员"""
        members = [m.value for m in ExtractModel]
        assert "Model 1" in members
        assert "Model 3" in members
        assert len(members) == 3

    def test_enabled_status_values(self):
        """测试启用状态枚举值"""
        assert EnabledStatus.ALL == "all"
        assert EnabledStatus.DISABLED == "0"
        assert EnabledStatus.ENABLED == "1"
        assert EnabledStatus.OTHER == "2"

    def test_enabled_flag_values(self):
        """测试启用标志枚举值"""
        assert EnabledFlag.DISABLED == 0
        assert EnabledFlag.ENABLED == 1

    def test_enabled_flag_is_int(self):
        """测试启用标志是整数类型"""
        assert isinstance(EnabledFlag.ENABLED, int)
        assert isinstance(EnabledFlag.DISABLED, int)

    def test_auth_scope_values(self):
        """测试权限范围枚举值"""
        assert AuthScope.PRIVATE == 0
        assert AuthScope.PUBLIC == 1

    def test_auth_scope_is_int(self):
        """测试权限范围是整数类型"""
        assert isinstance(AuthScope.PRIVATE, int)
        assert isinstance(AuthScope.PUBLIC, int)

    def test_field_type_values(self):
        """测试字段类型枚举值"""
        assert FieldType.DATETIME == "datetime"
        assert FieldType.ENUMERATE == "enumerate"
        assert FieldType.REGEX == "regex"

    def test_mismatch_action_values(self):
        """测试不匹配动作枚举值"""
        assert MismatchAction.DEFAULT == "default"
        assert MismatchAction.WARNING == "warning"

    def test_enum_comparison(self):
        """测试枚举比较"""
        assert ExtractModel.Model_1 == ExtractModel.Model_1
        assert ExtractModel.Model_1 != ExtractModel.Model_3

    def test_enum_in_list(self):
        """测试枚举在列表中"""
        models = [ExtractModel.Model_1, ExtractModel.Model_3]
        assert ExtractModel.Model_1 in models
        assert ExtractModel.Model_3 in models

    def test_enum_string_representation(self):
        """测试枚举字符串表示"""
        assert str(ExtractModel.Model_1) == "ExtractModel.Model_1"

    def test_enum_value_access(self):
        """测试枚举值访问"""
        assert ExtractModel.Model_1.value == "Model 1"
        assert EnabledFlag.ENABLED.value == 1

    def test_enum_name_access(self):
        """测试枚举名称访问"""
        assert ExtractModel.Model_1.name == "Model_1"
        assert EnabledFlag.ENABLED.name == "ENABLED"

    def test_enum_iteration(self):
        """测试枚举迭代"""
        models = list(ExtractModel)
        assert len(models) == 3
        assert ExtractModel.Model_1 in models
        assert ExtractModel.Model_3 in models

    def test_enum_from_value(self):
        """测试从值创建枚举"""
        assert ExtractModel("Model 1") == ExtractModel.Model_1
        assert EnabledFlag(1) == EnabledFlag.ENABLED

    def test_enum_invalid_value(self):
        """测试无效枚举值"""
        with pytest.raises(ValueError):
            ExtractModel("invalid")

        with pytest.raises(ValueError):
            EnabledFlag(999)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
