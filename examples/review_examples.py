"""
审核规则资源使用示例

本示例展示了 ReviewResource 的所有主要功能,包括:
- 审核规则库管理(创建、查询、更新、删除)
- 审核规则组管理(创建、更新、删除)
- 审核规则管理(创建、更新、删除)
- 审核任务管理(提交、查询、重试、删除)
"""
from docflow import DocflowClient
from typing import List


def setup_client():
    """初始化客户端"""
    return DocflowClient.from_env()


# ==================== 规则库管理示例 ====================

def example_create_repo():
    """示例1: 创建审核规则库"""
    print("\n=== 示例1: 创建审核规则库 ===")
    client = setup_client()

    # 创建一个新的审核规则库
    response = client.review.create_repo(
        workspace_id="123",
        name="发票审核规则库"
    )

    print(f"规则库创建成功!")
    print(f"规则库ID: {response.repo_id}")
    return response.repo_id


def example_list_repos():
    """示例2: 获取审核规则库列表"""
    print("\n=== 示例2: 获取审核规则库列表 ===")
    client = setup_client()

    # 获取规则库列表(支持分页)
    response = client.review.list_repos(
        workspace_id="123",
        page=1,
        page_size=10
    )

    print(f"总计: {response.total} 个规则库")
    for repo in response.repos:
        print(f"\n规则库ID: {repo.repo_id}")
        print(f"  名称: {repo.name}")
        print(f"  规则组数量: {len(repo.groups)}")


def example_get_repo():
    """示例3: 获取审核规则库详情"""
    print("\n=== 示例3: 获取审核规则库详情 ===")
    client = setup_client()

    # 获取特定规则库的详细信息
    repo = client.review.get_repo(
        workspace_id="123",
        repo_id="456"
    )

    print(f"规则库详情:")
    print(f"  ID: {repo.repo_id}")
    print(f"  名称: {repo.name}")
    print(f"  规则组数量: {len(repo.groups)}")

    # 显示规则组及其规则
    for group in repo.groups:
        print(f"\n  规则组: {group.name} (ID: {group.group_id})")
        for rule in group.rules:
            print(f"    - 规则: {rule.name} (ID: {rule.rule_id})")


def example_update_repo():
    """示例4: 更新审核规则库"""
    print("\n=== 示例4: 更新审核规则库 ===")
    client = setup_client()

    # 更新规则库名称
    client.review.update_repo(
        workspace_id="123",
        repo_id="456",
        name="增值税发票审核规则库(已更新)"
    )

    print("规则库更新成功!")


def example_delete_repo():
    """示例5: 删除审核规则库"""
    print("\n=== 示例5: 删除审核规则库 ===")
    client = setup_client()

    # 批量删除规则库
    client.review.delete_repo(
        workspace_id="123",
        repo_ids=["456", "789"]
    )

    print("规则库删除成功!")


# ==================== 规则组管理示例 ====================

def example_create_group():
    """示例6: 创建审核规则组"""
    print("\n=== 示例6: 创建审核规则组 ===")
    client = setup_client()

    # 在规则库中创建规则组
    response = client.review.create_group(
        workspace_id="123",
        repo_id="456",
        name="金额校验规则组"
    )

    print(f"规则组创建成功!")
    print(f"规则组ID: {response.group_id}")
    return response.group_id


def example_update_group():
    """示例7: 更新审核规则组"""
    print("\n=== 示例7: 更新审核规则组 ===")
    client = setup_client()

    # 更新规则组名称
    client.review.update_group(
        workspace_id="123",
        group_id="789",
        name="金额与税率校验规则组"
    )

    print("规则组更新成功!")


def example_delete_group():
    """示例8: 删除审核规则组"""
    print("\n=== 示例8: 删除审核规则组 ===")
    client = setup_client()

    # 删除规则组
    client.review.delete_group(
        workspace_id="123",
        group_id="789"
    )

    print("规则组删除成功!")


# ==================== 规则管理示例 ====================

def example_create_rule():
    """示例9: 创建审核规则"""
    print("\n=== 示例9: 创建审核规则 ===")
    client = setup_client()

    # 创建基础规则
    response = client.review.create_rule(
        workspace_id="123",
        repo_id=456,  # 注意这里是int类型
        group_id="789",
        name="发票金额合理性检查",
        prompt="检查发票金额是否在合理范围内(1-100000元)"
    )

    print(f"规则创建成功!")
    print(f"规则ID: {response.rule_id}")
    return response.rule_id


def example_create_rule_with_referenced_fields():
    """示例10: 创建带引用字段的审核规则"""
    print("\n=== 示例10: 创建带引用字段的审核规则 ===")
    client = setup_client()

    # 创建规则并指定引用的字段
    # referenced_fields按类别组织,每个类别可以包含普通字段和表格字段
    response = client.review.create_rule(
        workspace_id="123",
        repo_id=456,
        group_id="789",
        name="税额计算准确性检查",
        prompt="验证税额 = 金额 × 税率,允许误差范围0.01元",
        category_ids=["101", "102"],  # 应用于的类别列表
        risk_level=10,  # 风险等级: 10-高风险, 20-中风险, 30-低风险
        referenced_fields=[
            {
                "category_id": "101",
                "category_name": "增值税专用发票",
                "fields": [
                    {"field_id": "1001", "field_name": "金额"},
                    {"field_id": "1002", "field_name": "税率"},
                    {"field_id": "1003", "field_name": "税额"}
                ],
                "tables": []  # 如果没有表格字段可以为空数组
            },
            {
                "category_id": "102",
                "category_name": "增值税普通发票",
                "fields": [
                    {"field_id": "2001", "field_name": "金额"},
                    {"field_id": "2002", "field_name": "税率"},
                    {"field_id": "2003", "field_name": "税额"}
                ],
                "tables": []
            }
        ]
    )

    print(f"规则创建成功!")
    print(f"规则ID: {response.rule_id}")


def example_create_rule_with_table_fields():
    """示例11: 创建引用表格字段的审核规则"""
    print("\n=== 示例11: 创建引用表格字段的审核规则 ===")
    client = setup_client()

    # 创建引用表格字段的规则
    response = client.review.create_rule(
        workspace_id="123",
        repo_id=456,
        group_id="789",
        name="商品明细金额汇总检查",
        prompt="验证所有商品明细行的金额之和等于发票总金额",
        category_ids=["101"],
        risk_level=10,
        referenced_fields=[
            {
                "category_id": "101",
                "category_name": "增值税专用发票",
                "fields": [
                    {"field_id": "1001", "field_name": "金额"}  # 发票总金额
                ],
                "tables": [
                    {
                        "table_id": "5001",
                        "table_name": "商品明细表",
                        "fields": [
                            {"field_id": "5101", "field_name": "单价"},
                            {"field_id": "5102", "field_name": "数量"},
                            {"field_id": "5103", "field_name": "金额"}
                        ]
                    }
                ]
            }
        ]
    )

    print(f"规则创建成功!")
    print(f"规则ID: {response.rule_id}")


def example_update_rule():
    """示例12: 更新审核规则"""
    print("\n=== 示例12: 更新审核规则 ===")
    client = setup_client()

    # 更新规则配置
    client.review.update_rule(
        workspace_id="123",
        rule_id="1001",
        name="发票金额合理性检查(更新版)",
        prompt="检查发票金额是否在合理范围内(1-200000元),更新了上限",
        risk_level=20,  # 调整风险等级为中风险
        category_ids=["101", "102", "103"]  # 扩展应用范围
    )

    print("规则更新成功!")


def example_delete_rule():
    """示例13: 删除审核规则"""
    print("\n=== 示例13: 删除审核规则 ===")
    client = setup_client()

    # 删除规则
    client.review.delete_rule(
        workspace_id="123",
        rule_id="1001"
    )

    print("规则删除成功!")


# ==================== 审核任务管理示例 ====================

def example_submit_task():
    """示例14: 提交审核任务"""
    print("\n=== 示例14: 提交审核任务 ===")
    client = setup_client()

    # 提交一个新的审核任务
    # 注意: extract_task_ids必须是纯数字字符串
    result = client.review.submit_task(
        workspace_id="123",
        name="2026年4月发票审核",
        repo_id="456",
        extract_task_ids=["1234567890", "1234567891", "1234567892"]
    )

    print(f"审核任务提交成功!")
    print(f"任务ID: {result['task_id']}")
    return result['task_id']


def example_submit_task_by_batch():
    """示例15: 按批次提交审核任务"""
    print("\n=== 示例15: 按批次提交审核任务 ===")
    client = setup_client()

    # 使用批次号提交审核任务
    # 注意: batch_number必须是纯数字字符串
    result = client.review.submit_task(
        workspace_id="123",
        name="批次审核任务",
        repo_id="456",
        batch_number="202604020001"  # 纯数字格式
    )

    print(f"批次审核任务提交成功!")
    print(f"任务ID: {result['task_id']}")


def example_get_task_result():
    """示例16: 获取审核任务结果"""
    print("\n=== 示例16: 获取审核任务结果 ===")
    client = setup_client()

    # 获取审核任务的执行结果
    result = client.review.get_task_result(
        workspace_id="123",
        task_id="31415926",
        with_task_detail_url=True  # 返回任务详情页URL
    )

    # 显示任务基本信息
    print("审核任务结果:")
    print(f"  任务ID: {result.get('task_id')}")
    print(f"  任务名称: {result.get('task_name')}")
    print(f"  任务状态: {result.get('status')}")  # 0:待审核, 1:审核中, 2:已完成, 3:失败

    # 显示详情页URL
    if 'task_detail_url' in result:
        print(f"  详情页URL: {result['task_detail_url']}")

    # 显示审核规则库信息
    if 'rule_repo' in result:
        repo = result['rule_repo']
        print(f"  规则库: {repo.get('name')} (ID: {repo.get('repo_id')})")

    # 显示审核统计
    if 'statistics' in result:
        stats = result['statistics']
        print(f"\n审核统计:")
        print(f"  通过数: {stats.get('pass_count', 0)}")
        print(f"  失败数: {stats.get('failure_count', 0)}")
        print(f"  错误数: {stats.get('error_count', 0)}")

    # 显示详细的审核结果(按规则组组织)
    if 'groups' in result:
        print(f"\n详细审核结果:")
        for group in result['groups']:
            print(f"\n  规则组: {group.get('group_name')} (ID: {group.get('group_id')})")

            if 'review_tasks' in group:
                for review_task in group['review_tasks']:
                    print(f"\n    规则: {review_task.get('rule_name')} (ID: {review_task.get('rule_id')})")
                    print(f"      风险等级: {review_task.get('risk_level')}")
                    print(f"      审核结果: {review_task.get('review_result')}")  # 0:通过, 1:失败, 2:错误
                    print(f"      审核依据: {review_task.get('reasoning', 'N/A')}")

                    # 显示人工复核信息(如果有)
                    if 'audit_result' in review_task:
                        audit_result = review_task['audit_result']  # 0:未复核, 1:确认, 2:驳回
                        audit_msg = review_task.get('audit_message', '')
                        audit_status = {0: "未复核", 1: "已确认", 2: "已驳回"}.get(audit_result, "未知")
                        print(f"      人工复核: {audit_status} - {audit_msg}")

                    # 显示锚点信息(定位到具体的文本位置)
                    if 'anchors' in review_task and review_task['anchors']:
                        print(f"      锚点数量: {len(review_task['anchors'])}")
                        for idx, anchor in enumerate(review_task['anchors'][:2]):  # 只显示前2个
                            print(f"        锚点{idx+1}:")
                            print(f"          文本: {anchor.get('text', 'N/A')}")
                            print(f"          文件ID: {anchor.get('file_id')}")
                            print(f"          类别: {anchor.get('file_category')}")
                            print(f"          字段: {anchor.get('field_name')}")
                            print(f"          页码: {anchor.get('page')}")
                            print(f"          来源: {anchor.get('source')}")  # ocr/field/table


def example_get_task_result_simple():
    """示例17: 简化的审核结果查询"""
    print("\n=== 示例17: 简化的审核结果查询 ===")
    client = setup_client()

    result = client.review.get_task_result(
        workspace_id="123",
        task_id="31415926"
    )

    # 快速统计
    stats = result.get('statistics', {})
    pass_count = stats.get('pass_count', 0)
    fail_count = stats.get('failure_count', 0)

    print(f"任务: {result.get('task_name')}")
    print(f"状态: {result.get('status')}")
    print(f"通过/失败: {pass_count}/{fail_count}")

    # 显示失败的规则
    if fail_count > 0 and 'groups' in result:
        print("\n失败的规则:")
        for group in result['groups']:
            for task in group.get('review_tasks', []):
                if task.get('review_result') == 1:  # 1表示失败
                    print(f"  - {task.get('rule_name')}: {task.get('reasoning')}")


def example_retry_task():
    """示例18: 重新执行审核任务"""
    print("\n=== 示例18: 重新执行审核任务 ===")
    client = setup_client()

    # 重新执行整个审核任务
    client.review.retry_task(
        workspace_id="123",
        task_id="2001"
    )

    print("审核任务已提交重新执行!")


def example_retry_task_rule():
    """示例19: 重新执行任务中的某条规则"""
    print("\n=== 示例19: 重新执行任务中的某条规则 ===")
    client = setup_client()

    # 只重新执行任务中的特定规则
    client.review.retry_task_rule(
        workspace_id="123",
        task_id="2001",
        rule_id="1001"
    )

    print("规则已提交重新执行!")


def example_delete_task():
    """示例20: 删除审核任务"""
    print("\n=== 示例20: 删除审核任务 ===")
    client = setup_client()

    # 批量删除审核任务
    client.review.delete_task(
        workspace_id="123",
        task_ids=["2001", "2002"]
    )

    print("审核任务删除成功!")


# ==================== 完整工作流程示例 ====================

def example_complete_review_workflow():
    """示例21: 完整的审核工作流程"""
    print("\n=== 示例21: 完整的审核工作流程 ===")
    client = setup_client()

    workspace_id = "123"

    # 步骤1: 创建审核规则库
    print("\n步骤1: 创建审核规则库...")
    repo_response = client.review.create_repo(
        workspace_id=workspace_id,
        name="发票合规性审核规则库"
    )
    repo_id = repo_response.repo_id
    print(f"  规则库ID: {repo_id}")

    # 步骤2: 创建规则组
    print("\n步骤2: 创建规则组...")
    group1_response = client.review.create_group(
        workspace_id=workspace_id,
        repo_id=repo_id,
        name="基础信息校验组"
    )
    group2_response = client.review.create_group(
        workspace_id=workspace_id,
        repo_id=repo_id,
        name="金额计算校验组"
    )
    print(f"  规则组1 ID: {group1_response.group_id}")
    print(f"  规则组2 ID: {group2_response.group_id}")

    # 步骤3: 创建审核规则
    print("\n步骤3: 创建审核规则...")

    # 规则1: 发票号码格式检查
    rule1 = client.review.create_rule(
        workspace_id=workspace_id,
        repo_id=int(repo_id),
        group_id=group1_response.group_id,
        name="发票号码格式检查",
        prompt="检查发票号码是否为8位数字",
        risk_level=10,
        category_ids=["101"],
        referenced_fields=[
            {
                "category_id": "101",
                "category_name": "增值税专用发票",
                "fields": [
                    {"field_id": "1004", "field_name": "发票号码"}
                ],
                "tables": []
            }
        ]
    )
    print(f"  创建规则1: {rule1.rule_id}")

    # 规则2: 开票日期合理性检查
    rule2 = client.review.create_rule(
        workspace_id=workspace_id,
        repo_id=int(repo_id),
        group_id=group1_response.group_id,
        name="开票日期合理性检查",
        prompt="检查开票日期不能早于2020年且不能晚于当前日期",
        risk_level=20,
        category_ids=["101"],
        referenced_fields=[
            {
                "category_id": "101",
                "category_name": "增值税专用发票",
                "fields": [
                    {"field_id": "1005", "field_name": "开票日期"}
                ],
                "tables": []
            }
        ]
    )
    print(f"  创建规则2: {rule2.rule_id}")

    # 规则3: 税额计算准确性检查
    rule3 = client.review.create_rule(
        workspace_id=workspace_id,
        repo_id=int(repo_id),
        group_id=group2_response.group_id,
        name="税额计算准确性检查",
        prompt="验证税额 = 金额 × 税率,允许误差0.01元",
        risk_level=10,
        category_ids=["101"],
        referenced_fields=[
            {
                "category_id": "101",
                "category_name": "增值税专用发票",
                "fields": [
                    {"field_id": "1001", "field_name": "金额"},
                    {"field_id": "1002", "field_name": "税率"},
                    {"field_id": "1003", "field_name": "税额"}
                ],
                "tables": []
            }
        ]
    )
    print(f"  创建规则3: {rule3.rule_id}")

    # 规则4: 价税合计准确性检查
    rule4 = client.review.create_rule(
        workspace_id=workspace_id,
        repo_id=int(repo_id),
        group_id=group2_response.group_id,
        name="价税合计准确性检查",
        prompt="验证价税合计 = 金额 + 税额,允许误差0.01元",
        risk_level=10,
        category_ids=["101"],
        referenced_fields=[
            {
                "category_id": "101",
                "category_name": "增值税专用发票",
                "fields": [
                    {"field_id": "1001", "field_name": "金额"},
                    {"field_id": "1003", "field_name": "税额"},
                    {"field_id": "1006", "field_name": "价税合计"}
                ],
                "tables": []
            }
        ]
    )
    print(f"  创建规则4: {rule4.rule_id}")

    # 步骤4: 提交审核任务
    print("\n步骤4: 提交审核任务...")
    task_result = client.review.submit_task(
        workspace_id=workspace_id,
        name="4月份发票审核",
        repo_id=repo_id,
        batch_number="202604010001"  # 使用纯数字格式
    )
    task_id = task_result['task_id']
    print(f"  任务ID: {task_id}")

    # 步骤5: 等待审核完成(实际应用中需要轮询或使用webhook)
    print("\n步骤5: 等待审核完成...")
    import time
    time.sleep(3)  # 模拟等待

    # 步骤6: 获取审核结果
    print("\n步骤6: 获取审核结果...")
    result = client.review.get_task_result(
        workspace_id=workspace_id,
        task_id=task_id,
        with_task_detail_url=True
    )

    # 显示统计信息
    stats = result.get('statistics', {})
    print(f"  任务状态: {result.get('status')}")
    print(f"  审核通过: {stats.get('pass_count', 0)} 个")
    print(f"  审核失败: {stats.get('failure_count', 0)} 个")
    print(f"  处理错误: {stats.get('error_count', 0)} 个")

    # 步骤7: 处理失败的审核结果
    print("\n步骤7: 处理失败的审核结果...")
    if stats.get('failure_count', 0) > 0 and 'groups' in result:
        fail_count = 0
        for group in result['groups']:
            for task in group.get('review_tasks', []):
                if task.get('review_result') == 1:  # 1表示失败
                    fail_count += 1
                    print(f"  失败规则: {task.get('rule_name')}")
                    print(f"    原因: {task.get('reasoning')}")

        print(f"\n  共发现 {fail_count} 项审核失败")

    print("\n审核工作流程完成!")


def example_review_with_chaining():
    """示例22: 使用链式调用进行审核操作"""
    print("\n=== 示例22: 使用链式调用 ===")
    client = setup_client()

    # 通过链式调用简化代码
    ws = client.workspace("123")

    # 创建规则库
    repo_response = ws.review.create_repo(name="链式调用测试规则库")
    print(f"规则库创建成功: {repo_response.repo_id}")

    # 创建规则组
    group_response = ws.review.create_group(
        repo_id=repo_response.repo_id,
        name="测试规则组"
    )
    print(f"规则组创建成功: {group_response.group_id}")

    # 创建规则
    rule_response = ws.review.create_rule(
        repo_id=int(repo_response.repo_id),
        group_id=group_response.group_id,
        name="测试规则",
        prompt="测试规则内容"
    )
    print(f"规则创建成功: {rule_response.rule_id}")


if __name__ == "__main__":
    """
    运行示例前,请设置环境变量:
    export DOCFLOW_APP_ID="your-app-id"
    export DOCFLOW_SECRET_CODE="your-secret-code"
    export DOCFLOW_BASE_URL="https://docflow.textin.com/api"
    """

    print("=" * 60)
    print("审核规则资源使用示例")
    print("=" * 60)

    try:
        # 规则库管理示例
        example_create_repo()
        example_list_repos()
        example_get_repo()
        example_update_repo()
        # example_delete_repo()  # 注释掉以避免误删除

        # 规则组管理示例
        example_create_group()
        example_update_group()
        # example_delete_group()  # 注释掉以避免误删除

        # 规则管理示例
        example_create_rule()
        example_create_rule_with_referenced_fields()
        example_create_rule_with_table_fields()
        example_update_rule()
        # example_delete_rule()  # 注释掉以避免误删除

        # 审核任务管理示例
        example_submit_task()
        example_submit_task_by_batch()
        example_get_task_result()
        example_get_task_result_simple()
        example_retry_task()
        example_retry_task_rule()
        # example_delete_task()  # 注释掉以避免误删除

        # 完整工作流程
        example_complete_review_workflow()

        # 链式调用示例
        example_review_with_chaining()

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
