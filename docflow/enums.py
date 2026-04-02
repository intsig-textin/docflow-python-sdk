"""
Docflow SDK 枚举类型

定义所有 API 参数的枚举值，避免用户传错参数
"""
from enum import Enum


class ExtractModel(str, Enum):
    """
    提取模型类型
    """
    Model_1 = "Model 1"
    Model_2 = "Model 2"
    Model_3 = "Model 3"


class EnabledStatus(str, Enum):
    """
    启用状态（用于查询）

    Attributes:
        ALL: 全部
        DISABLED: 未启用
        ENABLED: 已启用
        OTHER: 其他状态
    """
    ALL = "all"
    DISABLED = "0"
    ENABLED = "1"
    OTHER = "2"


class EnabledFlag(int, Enum):
    """
    启用标志（用于更新）

    Attributes:
        DISABLED: 未启用
        ENABLED: 已启用
    """
    DISABLED = 0
    ENABLED = 1


class AuthScope(int, Enum):
    """
    权限范围

    Attributes:
        PRIVATE: 私有权限
        PUBLIC: 公共权限
    """
    PRIVATE = 0
    PUBLIC = 1


class FieldType(str, Enum):
    """
    字段转换类型（用于 transform_settings.type）

    Attributes:
        DATETIME: 日期时间类型转换
        ENUMERATE: 枚举类型转换
        REGEX: 正则表达式类型转换
    """
    DATETIME = "datetime"
    ENUMERATE = "enumerate"
    REGEX = "regex"

class MismatchAction(str, Enum):
    """
    字段不匹配时的处理动作

    Attributes:
        DEFAULT: 使用默认值
        WARNING: 显示警告
    """
    DEFAULT = "default"
    WARNING = "warning"


class RecognitionStatus(int, Enum):
    """
    文件识别状态

    Attributes:
        PENDING: 待识别
        SUCCESS: 识别成功
        FAILED: 识别失败
        CLASSIFYING: 分类中
        EXTRACTING: 抽取中
        PREPARING: 准备中
    """
    PENDING = 0
    SUCCESS = 1
    FAILED = 2
    CLASSIFYING = 3
    EXTRACTING = 4
    PREPARING = 5
