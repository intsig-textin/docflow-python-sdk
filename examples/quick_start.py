"""
DocFlow SDK 快速开始 - 费用报销场景

本示例演示如何使用 DocFlow SDK 完成从创建空间、配置类别、上传文件、
获取抽取结果到智能审核的完整流程。

业务场景：
处理费用报销单据，包括：
- 报销申请单（XLS格式）
- 酒店水单（图片）
- 支付记录（图片）

运行前准备：
1. 设置环境变量：
   export DOCFLOW_APP_ID="your-app-id"
   export DOCFLOW_SECRET_CODE="your-secret-code"
   export DOCFLOW_BASE_URL="https://docflow.textin.com/api"

2. 准备样本文件（放在 sample_files 目录下）：
（下述文件可api文档中获取 https://docs-docflow.textin.com/docflow/cn/00-overview/expense_reimbursement）
   - 报销申请单.XLS
   - sample_hotel_receipt.png
   - sample_payment_record.png

3. 安装依赖：
   pip install docflow-sdk
"""

import os
import time
from datetime import datetime
from docflow import DocflowClient, ExtractModel


def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_step(step_num, description):
    """打印步骤信息"""
    print(f"[步骤{step_num}] {description}")


def main():
    """主函数 - 完整的费用报销处理流程"""

    print_section("DocFlow SDK 快速开始 - 费用报销场景")

    # 初始化客户端（从环境变量自动加载配置）
    client = DocflowClient.from_env()

    # 样本文件目录
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_files")

    # ========== 步骤1: 创建工作空间 ==========
    print_step(1, "创建工作空间")

    workspace_name = f"费用报销_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workspace = client.workspace.create(
        name=workspace_name,
        auth_scope=1,  # 1=公开, 0=私有
        description="费用报销单据自动化处理空间"
    )
    workspace_id = workspace.workspace_id
    print(f"  ✓ 工作空间创建成功: {workspace_id}")

    # ========== 步骤2: 配置文件类别 ==========
    print_step(2, "配置文件类别")

    # 2.1 创建"报销申请单"类别
    print("  [2.1] 创建报销申请单类别...")
    baoxiao_category = client.category.create(
        workspace_id=workspace_id,
        name="报销申请单",
        extract_model=ExtractModel.Model_1,
        sample_files=[os.path.join(sample_dir, "报销申请单.XLS")],
        fields=[
            {"name": "申请人"},
            {"name": "出差目的"},
            {"name": "报销期间"},
            {"name": "目的地"},
            {"name": "费用发生日期"},
            {"name": "费用项目"},
            {"name": "差旅费金额"},
            {"name": "税率"},
            {"name": "冲借款金额"},
            {"name": "申请付款金额"},
            {"name": "备注"},
            {"name": "税额"}
        ],
        category_prompt="报销申请单，包含申请人、出差信息、费用明细等"
    )
    baoxiao_id = baoxiao_category.category_id
    print(f"    ✓ 报销申请单类别ID: {baoxiao_id}")

    # 获取报销申请单字段ID映射
    baoxiao_fields = client.category.fields.list(
        workspace_id=workspace_id,
        category_id=baoxiao_id
    )
    baoxiao_field_map = {field.name: field.id for field in baoxiao_fields.fields}
    print(f"    ✓ 获取了 {len(baoxiao_field_map)} 个字段ID")

    # 2.2 创建"酒店水单"类别（含表格字段）
    print("  [2.2] 创建酒店水单类别...")
    hotel_category = client.category.create(
        workspace_id=workspace_id,
        name="酒店水单",
        extract_model=ExtractModel.Model_1,
        sample_files=[os.path.join(sample_dir, "sample_hotel_receipt.png")],
        fields=[
            {"name": "入住日期"},
            {"name": "离店日期"},
            {"name": "总金额"}
        ],
        category_prompt="酒店住宿水单，包含入住离店日期、总金额和消费明细"
    )
    hotel_id = hotel_category.category_id
    print(f"    ✓ 酒店水单类别ID: {hotel_id}")

    # 添加表格字段
    print("    添加表格字段...")
    hotel_table = client.category.tables.add(
        workspace_id=workspace_id,
        category_id=hotel_id,
        name="消费明细表",
        prompt="抽取每日消费记录的日期、费用类型、金额和备注"
    )

    table_fields = ["日期", "费用类型", "金额", "备注"]
    for field_name in table_fields:
        client.category.fields.add(
            workspace_id=workspace_id,
            category_id=hotel_id,
            table_id=hotel_table.table_id,
            name=field_name
        )
    print(f"    ✓ 添加了 {len(table_fields)} 个表格字段")

    # 获取酒店水单字段ID映射（包括普通字段和表格字段）
    hotel_fields_response = client.category.fields.list(
        workspace_id=workspace_id,
        category_id=hotel_id
    )
    hotel_field_map = {field.name: field.id for field in hotel_fields_response.fields}

    # 获取表格字段ID映射
    hotel_table_field_map = {}
    for table in hotel_fields_response.tables:
        if table.name == "消费明细表":
            for field in table.fields:
                hotel_table_field_map[field.name] = field.id
    print(f"    ✓ 获取了 {len(hotel_field_map)} 个普通字段ID, {len(hotel_table_field_map)} 个表格字段ID")

    # 2.3 创建"支付记录"类别
    print("  [2.3] 创建支付记录类别...")
    payment_category = client.category.create(
        workspace_id=workspace_id,
        name="支付记录",
        extract_model=ExtractModel.Model_1,
        sample_files=[os.path.join(sample_dir, "sample_payment_record.png")],
        fields=[
            {"name": "交易流水号"},
            {"name": "交易授权码"},
            {"name": "付款卡种"},
            {"name": "收款方户名"},
            {"name": "付款方户名"},
            {"name": "交易时间"},
            {"name": "备注"},
            {"name": "收款方账户"},
            {"name": "收款方银行"},
            {"name": "交易金额"},
            {"name": "交易描述"},
            {"name": "付款银行"},
            {"name": "币种"},
            {"name": "交易账号/支付方式"}
        ],
        category_prompt="银行或支付机构的电子回单，包含交易流水号、双方信息和金额"
    )
    payment_id = payment_category.category_id
    print(f"    ✓ 支付记录类别ID: {payment_id}")

    # 获取支付记录字段ID映射
    payment_fields = client.category.fields.list(
        workspace_id=workspace_id,
        category_id=payment_id
    )
    payment_field_map = {field.name: field.id for field in payment_fields.fields}
    print(f"    ✓ 获取了 {len(payment_field_map)} 个字段ID")

    print(f"\n  配置完成，类别ID汇总：")
    print(f"    报销申请单: {baoxiao_id}")
    print(f"    酒店水单:   {hotel_id}")
    print(f"    支付记录:   {payment_id}")

    time.sleep(30)
    # ========== 步骤3: 上传待处理文件 ==========
    print_step(3, "上传待处理文件")

    files_to_upload = [
        ("报销申请单.XLS", "报销申请单"),
        ("sample_hotel_receipt.png", "酒店水单"),
        ("sample_payment_record.png", "支付记录")
    ]

    batch_numbers = []
    for filename, category_name in files_to_upload:
        file_path = os.path.join(sample_dir, filename)
        response = client.file.upload(
            workspace_id=workspace_id,
            category=category_name,
            file_path=file_path
        )
        batch_number = response.batch_number
        batch_numbers.append(batch_number)
        print(f"  ✓ {filename} -> batch_number: {batch_number}")

    # ========== 步骤4: 获取抽取结果 ==========
    print_step(4, "获取抽取结果")

    print("  等待文件处理完成（可能需要10-30秒）...")

    extract_results = []
    for idx, batch_number in enumerate(batch_numbers, 1):
        # 轮询等待处理完成
        max_wait = 60  # 最多等待60秒
        wait_interval = 3
        elapsed = 0

        while elapsed < max_wait:
            response = client.file.fetch(
                workspace_id=workspace_id,
                batch_number=batch_number
            )

            if response.files and response.files[0].recognition_status == 1:  # 1=识别成功
                file_info = response.files[0]
                extract_results.append(file_info)
                print(f"  [{idx}/{len(batch_numbers)}] ✓ {file_info.name} 处理完成")
                break
            elif response.files and response.files[0].recognition_status == 2:  # 2=识别失败
                print(f"  [{idx}/{len(batch_numbers)}] ✗ 处理失败")
                break

            time.sleep(wait_interval)
            elapsed += wait_interval
        else:
            print(f"  [{idx}/{len(batch_numbers)}] ⏱ 处理超时")

    # 显示抽取结果摘要
    print("\n  抽取结果摘要：")
    for file_info in extract_results:
        print(f"\n  文件: {file_info.name}")
        print(f"    类别: {file_info.category}")

        if file_info.data and 'fields' in file_info.data:
            fields = file_info.data['fields']
            print(f"    字段数: {len(fields)}")

            # 显示前3个关键字段
            for field in fields[:3]:
                print(f"      • {field.get('name')}: {field.get('value')}")

            if len(fields) > 3:
                print(f"      ... 还有 {len(fields) - 3} 个字段")

        # 显示表格数据
        if file_info.data and 'items' in file_info.data:
            items = file_info.data['items']
            if items:
                print(f"    表格行数: {len(items)}")

    # ========== 步骤5: 配置审核规则库 ==========
    print_step(5, "配置审核规则库")

    # 5.1 创建规则库
    print("  [5.1] 创建规则库...")
    repo = client.review.create_repo(
        workspace_id=workspace_id,
        name="费用报销审核规则库"
    )
    repo_id = repo.repo_id
    print(f"    ✓ 规则库ID: {repo_id}")

    # 5.2 创建规则组1：报销申请单合规性检查
    print("  [5.2] 创建规则组：报销申请单合规性检查")
    group1 = client.review.create_group(
        workspace_id=workspace_id,
        repo_id=repo_id,
        name="报销申请单合规性检查"
    )

    # 规则1: 必填字段完整性校验
    client.review.create_rule(
        workspace_id=workspace_id,
        repo_id=int(repo_id),
        group_id=group1.group_id,
        name="必填字段完整性校验",
        prompt='检查"申请人"、"费用发生日期"、"费用项目"、"申请付款金额"是否都已填写，任一字段为空则审核不通过',
        category_ids=[baoxiao_id],
        risk_level=10,  # 高风险
        referenced_fields=[
            {
                "category_id": baoxiao_id,
                "category_name": "报销申请单",
                "fields": [
                    {"field_id": baoxiao_field_map["申请人"], "field_name": "申请人"},
                    {"field_id": baoxiao_field_map["费用发生日期"], "field_name": "费用发生日期"},
                    {"field_id": baoxiao_field_map["费用项目"], "field_name": "费用项目"},
                    {"field_id": baoxiao_field_map["申请付款金额"], "field_name": "申请付款金额"}
                ],
                "tables": []
            }
        ]
    )
    print("    ✓ 创建规则: 必填字段完整性校验")

    # 规则2: 报销总金额校验
    client.review.create_rule(
        workspace_id=workspace_id,
        repo_id=int(repo_id),
        group_id=group1.group_id,
        name="报销总金额校验",
        prompt="验证申请付款总金额 ≤ 所有行的申请付款金额之和",
        category_ids=[baoxiao_id],
        risk_level=10,
        referenced_fields=[
            {
                "category_id": baoxiao_id,
                "category_name": "报销申请单",
                "fields": [
                    {"field_id": baoxiao_field_map["申请付款金额"], "field_name": "申请付款金额"}
                ],
                "tables": []
            }
        ]
    )
    print("    ✓ 创建规则: 报销总金额校验")

    # 5.3 创建规则组2：差旅费用政策匹配审核
    print("  [5.3] 创建规则组：差旅费用政策匹配审核")
    group2 = client.review.create_group(
        workspace_id=workspace_id,
        repo_id=repo_id,
        name="差旅费用政策匹配审核"
    )

    # 规则3: 酒店明细合计金额校验
    client.review.create_rule(
        workspace_id=workspace_id,
        repo_id=int(repo_id),
        group_id=group2.group_id,
        name="酒店明细合计金额校验",
        prompt="验证所有明细行金额合计 = 总金额",
        category_ids=[hotel_id],
        risk_level=20,  # 中风险
        referenced_fields=[
            {
                "category_id": hotel_id,
                "category_name": "酒店水单",
                "fields": [
                    {"field_id": hotel_field_map["总金额"], "field_name": "总金额"}
                ],
                "tables": [
                    {
                        "table_id": hotel_table.table_id,
                        "table_name": "消费明细表",
                        "fields": [
                            {"field_id": hotel_table_field_map["金额"], "field_name": "金额"}
                        ]
                    }
                ]
            }
        ]
    )
    print("    ✓ 创建规则: 酒店明细合计金额校验")

    # 5.4 创建规则组3：跨文档交叉审核
    print("  [5.4] 创建规则组：跨文档交叉审核")
    group3 = client.review.create_group(
        workspace_id=workspace_id,
        repo_id=repo_id,
        name="跨文档交叉审核"
    )

    # 规则4: 跨文档金额匹配
    client.review.create_rule(
        workspace_id=workspace_id,
        repo_id=int(repo_id),
        group_id=group3.group_id,
        name="跨文档金额匹配",
        prompt="验证报销申请单差旅费金额 = 酒店水单总金额 = 支付记录交易金额，允许±0.1元误差",
        category_ids=[baoxiao_id, hotel_id, payment_id],
        risk_level=10,
        referenced_fields=[
            {
                "category_id": baoxiao_id,
                "category_name": "报销申请单",
                "fields": [
                    {"field_id": baoxiao_field_map["差旅费金额"], "field_name": "差旅费金额"}
                ],
                "tables": []
            },
            {
                "category_id": hotel_id,
                "category_name": "酒店水单",
                "fields": [
                    {"field_id": hotel_field_map["总金额"], "field_name": "总金额"}
                ],
                "tables": []
            },
            {
                "category_id": payment_id,
                "category_name": "支付记录",
                "fields": [
                    {"field_id": payment_field_map["交易金额"], "field_name": "交易金额"}
                ],
                "tables": []
            }
        ]
    )
    print("    ✓ 创建规则: 跨文档金额匹配")

    # 规则5: 付款人身份一致性
    client.review.create_rule(
        workspace_id=workspace_id,
        repo_id=int(repo_id),
        group_id=group3.group_id,
        name="付款人身份与申请人一致性",
        prompt='验证支付记录"付款方户名"与报销申请单"申请人"是否为同一人',
        category_ids=[baoxiao_id, payment_id],
        risk_level=20,
        referenced_fields=[
            {
                "category_id": baoxiao_id,
                "category_name": "报销申请单",
                "fields": [
                    {"field_id": baoxiao_field_map["申请人"], "field_name": "申请人"}
                ],
                "tables": []
            },
            {
                "category_id": payment_id,
                "category_name": "支付记录",
                "fields": [
                    {"field_id": payment_field_map["付款方户名"], "field_name": "付款方户名"}
                ],
                "tables": []
            }
        ]
    )
    print("    ✓ 创建规则: 付款人身份与申请人一致性")

    print(f"\n  规则库配置完成，共创建 3 个规则组、5 条审核规则")

    # ========== 步骤6: 提交审核任务 ==========
    print_step(6, "提交审核任务")

    # 从抽取结果中收集 task_id
    extract_task_ids = [
        file.task_id for file in extract_results
        if file.task_id
    ]

    if not extract_task_ids:
        print("  ✗ 没有可用的抽取任务ID，跳过审核")
        return

    review_task = client.review.submit_task(
        workspace_id=workspace_id,
        name=f"费用报销审核_{datetime.now().strftime('%H%M%S')}",
        repo_id=repo_id,
        extract_task_ids=extract_task_ids
    )
    review_task_id = review_task['task_id']
    print(f"  ✓ 审核任务提交成功: {review_task_id}")

    # ========== 步骤7: 获取审核结果 ==========
    print_step(7, "获取审核结果")

    print("  等待审核完成（可能需要10-30秒）...")

    # 轮询等待审核完成
    max_wait = 120  # 最多等待2分钟
    wait_interval = 5
    elapsed = 0

    review_result = None
    while elapsed < max_wait:
        result = client.review.get_task_result(
            workspace_id=workspace_id,
            task_id=review_task_id
        )

        status = result.get('status')
        # 状态：0=待审核, 1=审核通过, 2=审核失败, 4=审核不通过, 7=识别失败
        if status in (1, 2, 4, 7):
            review_result = result
            print("  ✓ 审核完成")
            break

        time.sleep(wait_interval)
        elapsed += wait_interval
    else:
        print("  ⏱ 审核等待超时")
        return

    # 显示审核结果
    print_section("审核结果汇总")

    status_map = {
        0: "待审核",
        1: "审核通过",
        2: "审核失败",
        4: "审核不通过",
        7: "识别失败"
    }
    print(f"任务状态: {status_map.get(review_result.get('status'), '未知')}")

    # 统计信息
    stats = review_result.get('statistics', {})
    print(f"规则通过数: {stats.get('pass_count', 0)}")
    print(f"规则不通过数: {stats.get('failure_count', 0)}")
    print(f"规则错误数: {stats.get('error_count', 0)}")

    # 详细审核结果
    if 'groups' in review_result:
        print("\n详细审核结果：\n")

        for group in review_result['groups']:
            group_name = group.get('group_name', '未命名规则组')
            print(f"【{group_name}】")

            review_tasks = group.get('review_tasks', [])
            for task in review_tasks:
                rule_name = task.get('rule_name')
                review_result_code = task.get('review_result')  # 0=通过, 1=不通过, 2=错误
                risk_level = task.get('risk_level')  # 10=高风险, 20=中风险, 30=低风险
                reasoning = task.get('reasoning', 'N/A')

                # 结果图标
                result_icon = "✓" if review_result_code == 0 else "✗"

                # 风险等级标记
                risk_mark = {10: "🔴 高风险", 20: "🟡 中风险", 30: "🟢 低风险"}.get(risk_level, "")

                print(f"  {result_icon} [{risk_mark}] {rule_name}")
                print(f"    {reasoning}\n")

    # ========== 完成 ==========
    print_section("示例运行完成")

    print("后续操作：")
    print(f"1. 访问 DocFlow Web 页面查看详细结果")
    print(f"   https://docflow.textin.com/api")
    print(f"2. 工作空间ID: {workspace_id}")
    print(f"3. 规则库ID: {repo_id}")
    print(f"4. 审核任务ID: {review_task_id}")
    print()
    print("提示：工作空间、类别和规则库可以复用，后续只需上传新文件并提交审核任务即可。")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
    except Exception as e:
        print(f"\n\n执行出错: {e}")
        import traceback
        traceback.print_exc()
