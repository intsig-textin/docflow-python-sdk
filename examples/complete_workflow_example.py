"""
完整工作流程示例

本示例展示了一个端到端的发票处理和审核流程,包括:
1. 工作空间管理
2. 类别创建和配置
3. 文件上传和处理
4. 审核规则配置
5. 审核执行和结果处理
"""
from docflow import DocflowClient, ExtractModel, AuthScope, FieldType, MismatchAction
from datetime import datetime
import time


def setup_client():
    """初始化客户端"""
    return DocflowClient.from_env()


def scenario_1_invoice_processing():
    """
    场景1: 发票批量处理流程

    流程说明:
    1. 创建工作空间
    2. 创建发票类别(含字段和表格)
    3. 批量上传发票文件
    4. 查询处理结果
    5. 更新错误数据
    """
    print("\n" + "=" * 70)
    print("场景1: 发票批量处理流程")
    print("=" * 70)

    client = setup_client()

    # 步骤1: 创建工作空间
    print("\n[步骤1] 创建工作空间...")
    try:
        workspace = client.workspace.create(
            name=f"发票处理工作空间_{datetime.now().strftime('%Y%m%d')}",
            auth_scope=AuthScope.PUBLIC,
            description="用于处理增值税专用发票"
        )
        workspace_id = workspace.workspace_id
        print(f"✓ 工作空间创建成功: {workspace_id}")
    except Exception as e:
        print(f"✗ 工作空间创建失败: {e}")
        workspace_id = "123"  # 使用现有的workspace_id
        print(f"使用现有工作空间: {workspace_id}")

    # 步骤2: 创建发票类别
    print("\n[步骤2] 创建发票类别...")

    # 定义字段配置
    fields_config = [
        {
            "name": "发票代码",
            "description": "10-12位数字"
        },
        {
            "name": "发票号码",
            "description": "8位数字"
        },
        {
            "name": "开票日期",
            "description": "发票开具日期",
            "transform_settings": {
                "type": FieldType.DATETIME.value,
                "datetime_settings": {
                    "format": "yyyy-MM-dd"
                }
            }
        },
        {
            "name": "购买方名称"
        },
        {
            "name": "购买方税号",
            "description": "统一社会信用代码"
        },
        {
            "name": "销售方名称"
        },
        {
            "name": "销售方税号"
        },
        {
            "name": "金额",
            "description": "不含税金额"
        },
        {
            "name": "税率",
            "description": "税率百分比",
            "transform_settings": {
                "type": FieldType.ENUMERATE.value,
                "enumerate_settings": {
                    "items": ["0%", "3%", "6%", "9%", "13%", "17%"],
                },
                "mismatch_action": {
                    "mode": MismatchAction.WARNING.value
                }
            }
        },
        {
            "name": "税额",
            "description": "增值税税额"
        },
        {
            "name": "价税合计",
            "description": "含税总金额"
        }
    ]

    try:
        category = client.category.create(
            workspace_id=workspace_id,
            name="增值税专用发票",
            extract_model=ExtractModel.Model_1,
            sample_files=[
                "/path/to/invoice_sample1.pdf",  # 替换为实际样本文件路径
                "/path/to/invoice_sample2.pdf"
            ],
            fields=fields_config,
            category_prompt="增值税专用发票,包含购销双方信息和税额计算"
        )
        category_id = category.category_id
        print(f"✓ 类别创建成功: {category_id}")
    except Exception as e:
        print(f"✗ 类别创建失败: {e}")
        category_id = "456"  # 使用现有的category_id
        print(f"使用现有类别: {category_id}")

    # 添加表格配置
    print("\n[步骤2.1] 添加商品明细表...")
    try:
        table = client.category.tables.add(
            workspace_id=workspace_id,
            category_id=category_id,
            name="商品明细表",
            prompt="抽取每行的品名、规格、数量、单价和金额"
        )

        # 为表格添加字段
        table_fields = [
            {"name": "货物或应税劳务名称"},
            {"name": "规格型号"},
            {"name": "单位"},
            {"name": "数量"},
            {"name": "单价"},
            {"name": "金额"}
        ]

        for field_config in table_fields:
            client.category.fields.add(
                workspace_id=workspace_id,
                category_id=category_id,
                table_id=table.table_id,
                **field_config
            )

        print(f"✓ 表格和字段添加成功")
    except Exception as e:
        print(f"✗ 表格添加失败: {e}")

    # 步骤3: 批量上传发票
    print("\n[步骤3] 批量上传发票...")
    batch_number = f"INV_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    invoice_files = [
        "/path/to/invoices/invoice1.pdf",
        "/path/to/invoices/invoice2.pdf",
        "/path/to/invoices/invoice3.pdf",
        "/path/to/invoices/invoice4.pdf",
        "/path/to/invoices/invoice5.pdf",
    ]

    uploaded_files = []
    for idx, file_path in enumerate(invoice_files, 1):
        try:
            response = client.file.upload(
                workspace_id=workspace_id,
                category="增值税专用发票",
                file_path=file_path,
                batch_number=batch_number,
                auto_verify_vat=True
            )
            for file in response.files:
                uploaded_files.append(file)
                print(f"  [{idx}/{len(invoice_files)}] ✓ {file.name} -> 任务ID: {file.task_id}")
        except Exception as e:
            print(f"  [{idx}/{len(invoice_files)}] ✗ {file_path} 上传失败: {e}")

    # 步骤4: 等待处理完成
    print("\n[步骤4] 等待处理完成...")
    print("轮询检查处理状态...")

    max_wait_time = 60  # 最多等待60秒
    wait_interval = 5  # 每5秒检查一次
    elapsed_time = 0

    while elapsed_time < max_wait_time:
        response = client.file.fetch(
            workspace_id=workspace_id,
            batch_number=batch_number
        )

        processing_count = sum(
            1 for f in response.files
            if f.recognition_status in (0, 3, 4, 5)  # 0=待识别, 3=分类中, 4=抽取中, 5=准备中
        )

        if processing_count == 0:
            print("✓ 所有文件处理完成")
            break

        print(f"  剩余 {processing_count} 个文件处理中...")
        time.sleep(wait_interval)
        elapsed_time += wait_interval

    # 步骤5: 查询处理结果
    print("\n[步骤5] 查询处理结果...")
    response = client.file.fetch(
        workspace_id=workspace_id,
        batch_number=batch_number,
        with_document=True
    )

    success_files = []
    failed_files = []

    for file in response.files:
        if file.recognition_status == 1:  # 1=识别成功
            success_files.append(file)
        else:
            failed_files.append(file)

    print(f"\n处理统计:")
    print(f"  ✓ 成功: {len(success_files)} 个")
    print(f"  ✗ 失败: {len(failed_files)} 个")

    # 显示成功处理的文件详情
    if success_files:
        print(f"\n成功处理的文件:")
        for file in success_files:
            print(f"\n  文件: {file.name}")
            if file.data and 'fields' in file.data:
                # 显示关键字段
                key_fields = ['发票号码', '开票日期', '金额', '税额', '价税合计']
                for field in file.data['fields']:
                    field_name = field.get('name')
                    if field_name in key_fields:
                        print(f"    {field_name}: {field.get('value')}")

    # 处理失败的文件
    if failed_files:
        print(f"\n失败的文件:")
        for file in failed_files:
            print(f"  ✗ {file.name}")
            if file.failure_causes:
                for cause in file.failure_causes:
                    print(f"    原因: {cause}")

    # 步骤6: 数据验证和修正
    print("\n[步骤6] 数据验证和修正...")

    for file in success_files:
        if not file.data or 'fields' not in file.data:
            continue

        fields = file.data['fields']

        # 提取关键字段值
        amount = None
        tax_rate = None
        tax = None
        total = None

        for field in fields:
            name = field.get('name')
            value = field.get('value', '').strip()

            if name == '金额':
                try:
                    amount = float(value)
                except:
                    pass
            elif name == '税率':
                try:
                    tax_rate = float(value.rstrip('%')) / 100
                except:
                    pass
            elif name == '税额':
                try:
                    tax = float(value)
                except:
                    pass
            elif name == '价税合计':
                try:
                    total = float(value)
                except:
                    pass

        # 验证计算是否正确
        needs_update = False
        update_fields = []

        if amount is not None and tax_rate is not None:
            calculated_tax = round(amount * tax_rate, 2)
            if tax is not None and abs(calculated_tax - tax) > 0.01:
                print(f"\n  文件 {file.name} 税额计算有误:")
                print(f"    识别税额: {tax}")
                print(f"    计算税额: {calculated_tax}")
                needs_update = True
                update_fields.append({"name": "税额", "value": str(calculated_tax)})

        if amount is not None and tax is not None:
            calculated_total = round(amount + tax, 2)
            if total is not None and abs(calculated_total - total) > 0.01:
                print(f"\n  文件 {file.name} 价税合计有误:")
                print(f"    识别合计: {total}")
                print(f"    计算合计: {calculated_total}")
                needs_update = True
                update_fields.append({"name": "价税合计", "value": str(calculated_total)})

        # 更新错误数据
        if needs_update:
            try:
                client.file.update(
                    workspace_id=workspace_id,
                    file_id=file.id,
                    data={"fields": update_fields}
                )
                print(f"  ✓ 数据已修正")
            except Exception as e:
                print(f"  ✗ 数据修正失败: {e}")

    print("\n" + "=" * 70)
    print("场景1完成")
    print("=" * 70)

    return workspace_id, category_id, batch_number


def scenario_2_invoice_review():
    """
    场景2: 发票审核流程

    流程说明:
    1. 创建审核规则库
    2. 配置审核规则
    3. 提交审核任务
    4. 查询审核结果
    5. 处理审核不通过的文件
    """
    print("\n" + "=" * 70)
    print("场景2: 发票审核流程")
    print("=" * 70)

    client = setup_client()

    workspace_id = "123"  # 使用场景1创建的workspace
    category_id = "456"  # 使用场景1创建的category
    batch_number = "202604020001"  # 使用场景1上传的batch

    # 步骤1: 创建审核规则库
    print("\n[步骤1] 创建审核规则库...")
    try:
        repo = client.review.create_repo(
            workspace_id=workspace_id,
            name="发票合规性审核规则库"
        )
        repo_id = repo.repo_id
        print(f"✓ 规则库创建成功: {repo_id}")
    except Exception as e:
        print(f"✗ 规则库创建失败: {e}")
        return

    # 步骤2: 创建规则组和规则
    print("\n[步骤2] 配置审核规则...")

    # 规则组1: 基础信息校验
    group1 = client.review.create_group(
        workspace_id=workspace_id,
        repo_id=repo_id,
        name="基础信息校验"
    )
    print(f"  ✓ 规则组创建: {group1.group_id}")

    rules = []

    # 规则1: 发票号码格式
    rule1 = client.review.create_rule(
        workspace_id=workspace_id,
        repo_id=int(repo_id),
        group_id=group1.group_id,
        name="发票号码格式检查",
        prompt="检查发票号码是否为8位数字",
        risk_level=10,
        category_ids=[category_id],
        referenced_fields=[
            {
                "category_id": category_id,
                "category_name": "增值税专用发票",
                "fields": [
                    {"field_id": "1004", "field_name": "发票号码"}
                ],
                "tables": []
            }
        ]
    )
    rules.append(rule1.rule_id)
    print(f"  ✓ 规则创建: 发票号码格式检查 ({rule1.rule_id})")

    # 规则2: 开票日期合理性
    rule2 = client.review.create_rule(
        workspace_id=workspace_id,
        repo_id=int(repo_id),
        group_id=group1.group_id,
        name="开票日期合理性检查",
        prompt="检查开票日期不能早于2020-01-01且不能晚于当前日期",
        risk_level=20,
        category_ids=[category_id],
        referenced_fields=[
            {
                "category_id": category_id,
                "category_name": "增值税专用发票",
                "fields": [
                    {"field_id": "1005", "field_name": "开票日期"}
                ],
                "tables": []
            }
        ]
    )
    rules.append(rule2.rule_id)
    print(f"  ✓ 规则创建: 开票日期合理性检查 ({rule2.rule_id})")

    # 规则组2: 金额计算校验
    group2 = client.review.create_group(
        workspace_id=workspace_id,
        repo_id=repo_id,
        name="金额计算校验"
    )
    print(f"  ✓ 规则组创建: {group2.group_id}")

    # 规则3: 税额计算
    rule3 = client.review.create_rule(
        workspace_id=workspace_id,
        repo_id=int(repo_id),
        group_id=group2.group_id,
        name="税额计算准确性检查",
        prompt="验证税额 = 金额 × 税率,允许误差0.01元",
        risk_level=10,
        category_ids=[category_id],
        referenced_fields=[
            {
                "category_id": category_id,
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
    rules.append(rule3.rule_id)
    print(f"  ✓ 规则创建: 税额计算准确性检查 ({rule3.rule_id})")

    # 规则4: 价税合计计算
    rule4 = client.review.create_rule(
        workspace_id=workspace_id,
        repo_id=int(repo_id),
        group_id=group2.group_id,
        name="价税合计准确性检查",
        prompt="验证价税合计 = 金额 + 税额,允许误差0.01元",
        risk_level=10,
        category_ids=[category_id],
        referenced_fields=[
            {
                "category_id": category_id,
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
    rules.append(rule4.rule_id)
    print(f"  ✓ 规则创建: 价税合计准确性检查 ({rule4.rule_id})")

    # 步骤3: 提交审核任务
    print("\n[步骤3] 提交审核任务...")
    try:
        task_result = client.review.submit_task(
            workspace_id=workspace_id,
            name=f"发票审核_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            repo_id=repo_id,
            batch_number=batch_number
        )
        task_id = task_result['task_id']
        print(f"✓ 审核任务提交成功: {task_id}")
    except Exception as e:
        print(f"✗ 审核任务提交失败: {e}")
        return

    # 步骤4: 等待审核完成
    print("\n[步骤4] 等待审核完成...")
    time.sleep(3)  # 实际应用中应该轮询或使用webhook

    # 步骤5: 查询审核结果
    print("\n[步骤5] 查询审核结果...")
    try:
        result = client.review.get_task_result(
            workspace_id=workspace_id,
            task_id=task_id,
            with_task_detail_url=True
        )

        # 显示统计信息
        stats = result.get('statistics', {})
        print(f"\n审核统计:")
        print(f"  通过: {stats.get('pass_count', 0)} 个")
        print(f"  失败: {stats.get('failure_count', 0)} 个")
        print(f"  错误: {stats.get('error_count', 0)} 个")

        # 显示详情页URL
        if 'task_detail_url' in result:
            print(f"\n详情页: {result['task_detail_url']}")

        # 分析失败原因
        if stats.get('failure_count', 0) > 0 and 'groups' in result:
            print(f"\n失败详情:")

            failure_summary = {}

            for group in result['groups']:
                for review_task in group.get('review_tasks', []):
                    if review_task.get('review_result') == 1:  # 失败
                        rule_name = review_task.get('rule_name')
                        reasoning = review_task.get('reasoning', 'N/A')

                        if rule_name not in failure_summary:
                            failure_summary[rule_name] = []
                        failure_summary[rule_name].append(reasoning)

            for rule_name, reasons in failure_summary.items():
                print(f"\n  规则: {rule_name}")
                print(f"  失败次数: {len(reasons)}")
                for idx, reason in enumerate(reasons[:3], 1):  # 只显示前3个
                    print(f"    {idx}. {reason}")

    except Exception as e:
        print(f"✗ 查询审核结果失败: {e}")

    print("\n" + "=" * 70)
    print("场景2完成")
    print("=" * 70)


def scenario_3_using_chaining():
    """
    场景3: 使用链式调用优化代码

    展示如何使用链式调用来简化代码,减少重复参数传递
    """
    print("\n" + "=" * 70)
    print("场景3: 使用链式调用优化代码")
    print("=" * 70)

    client = setup_client()

    # 绑定工作空间上下文
    ws = client.workspace("123")

    # 1. 工作空间操作
    print("\n[1] 工作空间操作...")
    try:
        ws_detail = ws.get()
        print(f"  工作空间: {ws_detail.name}")

        ws.update(
            name=f"{ws_detail.name} (已更新)",
            auth_scope=AuthScope.PUBLIC
        )
        print(f"  ✓ 工作空间已更新")
    except Exception as e:
        print(f"  ✗ 操作失败: {e}")

    # 2. 类别操作(链式调用)
    print("\n[2] 类别操作...")
    cat = ws.category("456")

    try:
        # 添加字段
        field = cat.fields.add(
            name="备注",
            description="发票备注信息"
        )
        print(f"  ✓ 字段添加成功: {field.field_id}")

        # 获取字段列表
        fields = cat.fields.list()
        print(f"  类别字段总数: {len(fields.fields)}")

        # 获取表格列表
        tables = cat.tables.list()
        print(f"  类别表格总数: {len(tables.tables)}")

    except Exception as e:
        print(f"  ✗ 操作失败: {e}")

    # 3. 审核规则操作(链式调用)
    print("\n[3] 审核规则操作...")
    try:
        repo = ws.review.create_repo(
            name="链式调用测试规则库"
        )
        print(f"  ✓ 规则库创建成功: {repo.repo_id}")

        group = ws.review.create_group(
            repo_id=repo.repo_id,
            name="测试规则组"
        )
        print(f"  ✓ 规则组创建成功: {group.group_id}")

    except Exception as e:
        print(f"  ✗ 操作失败: {e}")

    print("\n" + "=" * 70)
    print("场景3完成 - 链式调用让代码更简洁!")
    print("=" * 70)


if __name__ == "__main__":
    """
    运行示例前,请设置环境变量:
    export DOCFLOW_APP_ID="your-app-id"
    export DOCFLOW_SECRET_CODE="your-secret-code"
    export DOCFLOW_BASE_URL="https://docflow.textin.com/api"
    """

    print("\n" + "=" * 70)
    print("Docflow SDK 完整工作流程示例")
    print("=" * 70)

    try:
        # 场景1: 发票批量处理
        workspace_id, category_id, batch_number = scenario_1_invoice_processing()

        # 场景2: 发票审核
        scenario_2_invoice_review()

        # 场景3: 链式调用优化
        scenario_3_using_chaining()

        print("\n" + "=" * 70)
        print("所有场景执行完成!")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n用户中断执行")
    except Exception as e:
        print(f"\n\n执行出错: {e}")
        import traceback
        traceback.print_exc()
