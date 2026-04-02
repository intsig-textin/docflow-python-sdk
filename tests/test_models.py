"""
数据模型测试
"""
import pytest
from docflow.models.workspace import (
    WorkspaceCreateResponse,
    WorkspaceListResponse,
    WorkspaceDetailResponse
)
from docflow.models.category import (
    CategoryInfo,
    CategoryCreateResponse,
    CategoryListResponse
)
from docflow.models.file import (
    FileInfo,
    FileUploadResponse,
    FileFetchResponse,
    FileUpdateResponse,
    FileDeleteResponse
)
from docflow.models.review import (
    ReviewRule,
    ReviewGroup,
    ReviewRepoInfo,
    ReviewRepoCreateResponse,
    ReviewRepoListResponse,
    ReviewGroupCreateResponse,
    ReviewRuleCreateResponse
)


class TestWorkspaceModels:
    """工作空间模型测试"""

    def test_workspace_create_response(self):
        """测试工作空间创建响应"""
        response = WorkspaceCreateResponse(workspace_id="123")
        assert response.workspace_id == "123"

    def test_workspace_list_response(self):
        """测试工作空间列表响应"""
        data = {
            "workspaces": [
                {"workspace_id": "123", "name": "测试空间"}
            ],
            "total": 1,
            "page": 1,
            "page_size": 20
        }
        response = WorkspaceListResponse.from_dict(data)
        assert len(response.workspaces) == 1
        assert response.total == 1
        assert response.workspaces[0].workspace_id == "123"

    def test_workspace_detail_response(self):
        """测试工作空间详情响应"""
        data = {
            "workspace_id": "123",
            "name": "测试空间",
            "auth_scope": 1
        }
        response = WorkspaceDetailResponse(**data)
        assert response.workspace_id == "123"
        assert response.name == "测试空间"


class TestCategoryModels:
    """类别模型测试"""

    def test_category_info(self):
        """测试类别信息模型"""
        info = CategoryInfo(
            id="456",
            name="测试类别",
            description="测试描述"
        )
        assert info.id == "456"
        assert info.name == "测试类别"

    def test_category_create_response(self):
        """测试类别创建响应"""
        response = CategoryCreateResponse(category_id="456")
        assert response.category_id == "456"

    def test_category_list_response(self):
        """测试类别列表响应"""
        data = {
            "categories": [
                {"id": "456", "name": "类别1"}
            ],
            "total": 1,
            "page": 1,
            "pageSize": 20
        }
        response = CategoryListResponse.from_dict(data)
        assert len(response.categories) == 1
        assert response.categories[0].id == "456"


class TestFileModels:
    """文件模型测试"""

    def test_file_info(self):
        """测试文件信息模型"""
        info = FileInfo(
            id="file_123",
            name="test.pdf",
            format="pdf"
        )
        assert info.id == "file_123"
        assert info.name == "test.pdf"
        assert info.format == "pdf"

    def test_file_upload_response(self):
        """测试文件上传响应"""
        data = {
            "batch_number": "batch_001",
            "files": [
                {
                    "id": "file_123",
                    "name": "test.pdf",
                    "format": "pdf",
                    "task_id": "task_456"
                }
            ]
        }
        response = FileUploadResponse(**data)
        assert response.batch_number == "batch_001"
        assert len(response.files) == 1
        assert response.files[0].id == "file_123"

    def test_file_fetch_response(self):
        """测试文件查询响应"""
        data = {
            "files": [],
            "total": 0,
            "page": 1,
            "page_size": 1000
        }
        response = FileFetchResponse(**data)
        assert response.total == 0
        assert response.page == 1

    def test_file_delete_response(self):
        """测试文件删除响应"""
        response = FileDeleteResponse(deleted_count=5)
        assert response.deleted_count == 5


class TestReviewModels:
    """审核规则模型测试"""

    def test_review_rule(self):
        """测试审核规则模型"""
        rule = ReviewRule(
            rule_id="rule_001",
            name="金额检查",
        )
        assert rule.rule_id == "rule_001"
        assert rule.name == "金额检查"

    def test_review_group(self):
        """测试审核规则组模型"""
        group = ReviewGroup(
            group_id="group_001",
            name="验证组",
            rules=[]
        )
        assert group.group_id == "group_001"
        assert group.name == "验证组"
        assert len(group.rules) == 0

    def test_review_group_with_rules(self):
        """测试包含规则的规则组"""
        data = {
            "group_id": "group_001",
            "name": "验证组",
            "rules": [
                {
                    "rule_id": "rule_001",
                    "name": "规则1",
                }
            ]
        }
        group = ReviewGroup(**data)
        assert len(group.rules) == 1
        assert isinstance(group.rules[0], ReviewRule)
        assert group.rules[0].rule_id == "rule_001"

    def test_review_repo_info(self):
        """测试审核规则库信息"""
        repo = ReviewRepoInfo(
            repo_id="repo_001",
            name="规则库",
            groups=[]
        )
        assert repo.repo_id == "repo_001"
        assert repo.name == "规则库"

    def test_review_repo_with_groups(self):
        """测试包含规则组的规则库"""
        data = {
            "repo_id": "repo_001",
            "name": "规则库",
            "groups": [
                {
                    "group_id": "group_001",
                    "name": "组1",
                    "rules": []
                }
            ]
        }
        repo = ReviewRepoInfo(**data)
        assert len(repo.groups) == 1
        assert isinstance(repo.groups[0], ReviewGroup)
        assert repo.groups[0].group_id == "group_001"

    def test_review_repo_create_response(self):
        """测试规则库创建响应"""
        response = ReviewRepoCreateResponse(repo_id="repo_001")
        assert response.repo_id == "repo_001"

    def test_review_group_create_response(self):
        """测试规则组创建响应"""
        response = ReviewGroupCreateResponse(group_id="group_001")
        assert response.group_id == "group_001"

    def test_review_rule_create_response(self):
        """测试规则创建响应"""
        response = ReviewRuleCreateResponse(rule_id="rule_001")
        assert response.rule_id == "rule_001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
