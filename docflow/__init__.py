"""
Docflow Python SDK

Docflow Python SDK，提供简洁易用的 API 接口
"""

__version__ = "1.1.2"

from .client import DocflowClient
from .exceptions import (
    DocflowException,
    AuthenticationError,
    ValidationError,
    ResourceNotFoundError,
    PermissionDeniedError,
    APIError,
    NetworkError,
)
from .i18n import set_language, get_language, translate, t
from .enums import (
    ExtractModel,
    EnabledStatus,
    EnabledFlag,
    AuthScope,
    FieldType,
    MismatchAction,
    ReviewModel,
    RecognitionStatus,
)
from .models.category import CategoryKeywordRuleGroup, CategoryKeywordRules

__all__ = [
    "DocflowClient",
    "DocflowException",
    "AuthenticationError",
    "ValidationError",
    "ResourceNotFoundError",
    "PermissionDeniedError",
    "APIError",
    "NetworkError",
    "set_language",
    "get_language",
    "translate",
    "t",
    "ExtractModel",
    "EnabledStatus",
    "EnabledFlag",
    "AuthScope",
    "FieldType",
    "MismatchAction",
    "ReviewModel",
    "RecognitionStatus",
    "CategoryKeywordRuleGroup",
    "CategoryKeywordRules",
]
