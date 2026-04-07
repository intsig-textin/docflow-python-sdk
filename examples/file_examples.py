"""
文件处理资源使用示例

本示例展示了 FileResource 的所有主要功能,包括:
- 文件上传(异步/同步)
- 文件查询与过滤
- 文件更新与删除
- 字段抽取
- 文件重试与类别修改
"""
import os
from docflow import DocflowClient
from datetime import datetime, timedelta


def setup_client():
    """初始化客户端"""
    return DocflowClient.from_env()


def example_upload_local_file():
    """示例1: 上传本地文件(异步)"""
    print("\n=== 示例1: 上传本地文件(异步) ===")
    client = setup_client()

    # 上传本地PDF文件
    response = client.file.upload(
        workspace_id="123",
        category="发票",
        file_path="/path/to/invoice.pdf",
        batch_number="BATCH_20260402_001",
        auto_verify_vat=True,  # 自动核验增值税发票
        split_flag=True,  # 启用文档拆分
    )

    print(f"文件上传成功!")
    print(f"批次号: {response.batch_number}")
    for file in response.files:
        print(f"  文件ID: {file.id}")
        print(f"  文件名: {file.name}")
        print(f"  任务ID: {file.task_id}")


def example_upload_from_url():
    """示例2: 通过URL上传文件"""
    print("\n=== 示例2: 通过URL上传文件 ===")
    client = setup_client()

    # 批量上传多个URL(最多10个)
    response = client.file.upload(
        workspace_id="123",
        category="合同",
        file_urls=[
            "https://example.com/contract1.pdf",
            "https://example.com/contract2.pdf",
            "https://example.com/contract3.pdf"
        ],
        batch_number="URL_BATCH_001",
        target_process="recognition"  # 处理目标: recognition 或 classification
    )

    print(f"上传成功,批次号: {response.batch_number}")
    print(f"上传了 {len(response.files)} 个文件")


def example_upload_sync():
    """示例3: 同步上传并等待处理完成"""
    print("\n=== 示例3: 同步上传(等待处理完成) ===")
    client = setup_client()

    # 同步上传,返回处理结果
    result = client.file.upload_sync(
        workspace_id="123",
        category="发票",
        file_path="/path/to/invoice.pdf",
        with_task_detail_url=True  # 返回任务详情页URL
    )

    print(f"文件处理完成!")
    for file in result.files:
        print(f"文件: {file.name}")
        print(f"  识别状态: {file.recognition_status}")
        if file.data and 'fields' in file.data:
            print(f"  提取的字段:")
            for field in file.data['fields']:
                print(f"    - {field.get('name')}: {field.get('value')}")


def example_upload_with_parser_params():
    """示例4: 上传时配置解析参数"""
    print("\n=== 示例4: 配置解析参数 ===")
    client = setup_client()

    # 配置高级解析参数
    response = client.file.upload(
        workspace_id="123",
        category="学术论文",
        file_path="/path/to/paper.pdf",
        parser_remove_watermark=1,  # 移除水印 (0=不移除, 1=移除)
        parser_crop_dewarp=1,  # 裁剪和去畸变 (0=不处理, 1=处理)
        parser_apply_merge=1,  # 应用合并 (0=不合并, 1=合并)
        parser_formula_level=2,  # 公式识别级别 (0/1/2)
        parser_table_text_split_mode=1  # 表格文字分割模式 (整数值)
    )

    print(f"上传成功,批次号: {response.batch_number}")


def example_fetch_files():
    """示例5: 查询文件列表"""
    print("\n=== 示例5: 查询文件列表 ===")
    client = setup_client()

    # 基础查询
    response = client.file.fetch(
        workspace_id="123",
        page=1,
        page_size=20
    )

    print(f"总计: {response.total} 个文件")
    for file in response.files:
        print(f"\n文件ID: {file.id}")
        print(f"  名称: {file.name}")
        print(f"  类别: {file.category}")
        print(f"  识别状态: {file.recognition_status}")


def example_fetch_with_filters():
    """示例6: 使用过滤条件查询"""
    print("\n=== 示例6: 使用过滤条件查询 ===")
    client = setup_client()

    # 计算时间范围(最近7天)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    # 使用多个过滤条件
    response = client.file.fetch(
        workspace_id="123",
        batch_number="BATCH_20260402_001",  # 按批次过滤
        category="发票",  # 按类别过滤
        recognition_status=1,  # 按识别状态过滤: 0待识别/1识别成功/2识别失败/3分类中/4抽取中/5准备中
        verification_status=0,  # 按核对状态过滤: 0待核对/2已确认/3已拒绝/4已删除/5推迟处理
        start_time=start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),  # RFC3339格式
        end_time=end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        with_document=True  # 返回完整的文字识别结果
    )

    print(f"找到 {len(response.files)} 个符合条件的文件")

    for file in response.files:
        print(f"\n文件: {file.name}")
        if file.document:
            # document是字典类型,可能包含text等字段
            doc_preview = str(file.document)[:100]
            print(f"  文档内容预览: {doc_preview}...")


def example_fetch_by_file_id():
    """示例7: 查询特定文件"""
    print("\n=== 示例7: 查询特定文件 ===")
    client = setup_client()

    # 通过file_id查询单个文件
    response = client.file.fetch(
        workspace_id="123",
        file_id="456",
        with_document=True,
        with_task_detail_url=True
    )

    if response.files:
        file = response.files[0]
        print(f"文件名: {file.name}")
        print(f"识别状态: {file.recognition_status}")

        # 显示提取的字段(在data字典中)
        if file.data and 'fields' in file.data:
            print(f"提取字段数: {len(file.data['fields'])}")
            for field in file.data['fields']:
                print(f"  {field.get('name')}: {field.get('value')}")


def example_iterate_files():
    """示例8: 迭代所有文件(自动分页)"""
    print("\n=== 示例8: 迭代所有文件 ===")
    client = setup_client()

    # 方式1: 迭代遍历(内存高效)
    count = 0
    for file in client.file.iter(
        workspace_id="123",
        category="发票",
        recognition_status=1,  # 1=识别成功
        page_size=100,
        max_pages=5  # 限制最多5页,防止数据过多
    ):
        count += 1
        print(f"处理文件 {count}: {file.name}")

        # 可以随时中断
        if count >= 50:
            print("达到处理上限,中断迭代")
            break

    print(f"\n总共处理了 {count} 个文件")

    # 方式2: 转换为列表(获取所有数据)
    all_files = list(client.file.iter(
        workspace_id="123",
        batch_number="BATCH_20260402_001",
        page_size=50,
        max_pages=10
    ))
    print(f"批次中共有 {len(all_files)} 个文件")


def example_update_file():
    """示例9: 更新文件处理结果"""
    print("\n=== 示例9: 更新文件处理结果 ===")
    client = setup_client()

    # 更新单个文件的字段值
    update_data = {
        "fields": [
            {"name": "发票号码", "value": "12345678"},
            {"name": "金额", "value": "1000.00"}
        ],
        "items": [  # 表格数据
            {
                "table_name": "商品明细",
                "rows": [
                    {"name": "苹果", "quantity": "10", "price": "50.00"},
                    {"name": "橙子", "quantity": "5", "price": "25.00"}
                ]
            }
        ]
    }

    response = client.file.update(
        workspace_id="123",
        file_id="456",
        data=update_data
    )

    print(f"文件更新成功!")
    print(f"更新的文件列表: {len(response.files)}")


def example_batch_update_files():
    """示例10: 批量更新多个文件"""
    print("\n=== 示例10: 批量更新文件 ===")
    client = setup_client()

    # 批量更新多个文件
    updates = [
        {
            "workspace_id": "123",
            "file_id": "456",
            "data": {
                "fields": [{"name": "状态", "value": "已审核"}]
            }
        },
        {
            "workspace_id": "123",
            "file_id": "789",
            "data": {
                "fields": [{"name": "状态", "value": "已审核"}]
            }
        }
    ]

    response = client.file.batch_update(updates=updates)
    print(f"批量更新完成,共更新 {len(response.files)} 个文件")


def example_extract_fields():
    """示例11: 抽取额外字段"""
    print("\n=== 示例11: 抽取额外字段 ===")
    client = setup_client()

    # 抽取普通字段
    result = client.file.extract_fields(
        workspace_id="123",
        task_id="456",
        fields=[
            {"key": "发票代码", "prompt": "只保留年的部分"},
            {"key": "发票号码"},
            {"key": "开票日期", "prompt": "转换为YYYY-MM-DD格式"}
        ]
    )

    print("普通字段抽取完成:")
    for file in result.files:
        if file.data and 'fields' in file.data:
            for field in file.data['fields']:
                print(f"  {field.get('name')}: {field.get('value')}")


def example_extract_table_fields():
    """示例12: 抽取表格字段"""
    print("\n=== 示例12: 抽取表格字段 ===")
    client = setup_client()

    # 抽取表格数据
    result = client.file.extract_fields(
        workspace_id="123",
        task_id="456",
        tables=[
            {
                "name": "货物明细",
                "fields": [
                    {"key": "货物名称"},
                    {"key": "规格型号"},
                    {"key": "数量"},
                    {"key": "单价"},
                    {"key": "金额", "prompt": "保留2位小数"}
                ]
            }
        ]
    )

    print("表格字段抽取完成:")
    for file in result.files:
        if file.data and 'items' in file.data:
            for item in file.data['items']:
                print(f"表格: {item.get('table_name')}")
                for row in item.get('rows', []):
                    print(f"  {row}")


def example_retry_file():
    """示例13: 重新处理文件"""
    print("\n=== 示例13: 重新处理文件 ===")
    client = setup_client()

    # 重新处理失败的文件
    client.file.retry(
        workspace_id="123",
        task_id="456"
    )
    print("文件已提交重新处理")

    # 使用新的解析参数重新处理
    client.file.retry(
        workspace_id="123",
        task_id="456",
        parser_params={
            "remove_watermark": True,
            "crop_dewarp": True,
            "formula_level": 2
        }
    )
    print("文件已使用新参数重新处理")


def example_amend_category():
    """示例14: 修改文件类别"""
    print("\n=== 示例14: 修改文件类别 ===")
    client = setup_client()

    # 修改普通任务的类别
    client.file.amend_category(
        workspace_id="123",
        task_id="456",
        category="合同"  # 新类别
    )
    print("文件类别已修改为: 合同")


def example_amend_category_with_split():
    """示例15: 修改拆分任务的类别"""
    print("\n=== 示例15: 修改拆分任务的类别 ===")
    client = setup_client()

    # 修改文档拆分任务的类别
    client.file.amend_category(
        workspace_id="123",
        task_id="456",
        split_tasks=[
            {"sub_task_id": "456-1", "category": "发票"},
            {"sub_task_id": "456-2", "category": "合同"}
        ]
    )
    print("拆分任务类别已修改")


def example_delete_files():
    """示例16: 删除文件"""
    print("\n=== 示例16: 删除文件 ===")
    client = setup_client()

    # 方式1: 按file_id删除
    response = client.file.delete(
        workspace_id="123",
        file_id=["456", "789", "101"]
    )
    print(f"删除了 {response.deleted_count} 个文件")

    # 方式2: 按batch_number删除
    response = client.file.delete(
        workspace_id="123",
        batch_number=["BATCH_001", "BATCH_002"]
    )
    print(f"删除了批次中的 {response.deleted_count} 个文件")

    # 方式3: 按时间范围删除
    start_ts = int((datetime.now() - timedelta(days=30)).timestamp())
    end_ts = int(datetime.now().timestamp())

    response = client.file.delete(
        workspace_id="123",
        start_time=start_ts,
        end_time=end_ts
    )
    print(f"删除了时间范围内的 {response.deleted_count} 个文件")


def example_complete_workflow():
    """示例17: 完整工作流程"""
    print("\n=== 示例17: 完整工作流程 ===")
    client = setup_client()

    workspace_id = "123"
    batch_number = f"INVOICE_BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # 1. 批量上传文件
    print("\n步骤1: 批量上传发票...")
    invoice_files = [
        "/path/to/invoice1.pdf",
        "/path/to/invoice2.pdf",
        "/path/to/invoice3.pdf"
    ]

    all_task_ids = []
    for file_path in invoice_files:
        response = client.file.upload(
            workspace_id=workspace_id,
            category="发票",
            file_path=file_path,
            batch_number=batch_number,
            auto_verify_vat=True
        )
        for file in response.files:
            all_task_ids.append(file.task_id)
            print(f"  上传: {os.path.basename(file_path)} -> 任务ID: {file.task_id}")

    # 2. 等待处理完成(实际应用中可能需要轮询或使用webhook)
    print("\n步骤2: 等待处理完成...")
    import time
    time.sleep(5)  # 模拟等待

    # 3. 查询批次中的所有文件
    print("\n步骤3: 查询批次处理结果...")
    response = client.file.fetch(
        workspace_id=workspace_id,
        batch_number=batch_number,
        with_document=True
    )

    success_count = 0
    failed_count = 0

    for file in response.files:
        if file.recognition_status == 1:  # 1=识别成功
            success_count += 1
            print(f"  ✓ {file.name} - 成功")
            # 显示提取的关键字段
            if file.data and 'fields' in file.data:
                for field in file.data['fields'][:3]:  # 只显示前3个字段
                    print(f"    - {field.get('name')}: {field.get('value')}")
        else:
            failed_count += 1
            print(f"  ✗ {file.name} - 失败")

    print(f"\n处理统计: 成功 {success_count} 个, 失败 {failed_count} 个")

    # 4. 对失败的文件重新处理
    if failed_count > 0:
        print("\n步骤4: 重新处理失败的文件...")
        for file in response.files:
            if file.recognition_status != 1:  # 非识别成功状态
                client.file.retry(
                    workspace_id=workspace_id,
                    task_id=file.task_id
                )
                print(f"  重试: {file.name}")

    # 5. 更新特定字段
    print("\n步骤5: 更新已审核状态...")
    for file in response.files:
        if file.recognition_status == 1:  # 1=识别成功
            client.file.update(
                workspace_id=workspace_id,
                file_id=file.id,  # 注意使用file.id而非file_id
                data={
                    "fields": [
                        {"name": "审核状态", "value": "已审核"},
                        {"name": "审核时间", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    ]
                }
            )

    print("\n工作流程完成!")


if __name__ == "__main__":
    """
    运行示例前,请设置环境变量:
    export DOCFLOW_APP_ID="your-app-id"
    export DOCFLOW_SECRET_CODE="your-secret-code"
    export DOCFLOW_BASE_URL="https://docflow.textin.com/api"
    """

    print("=" * 60)
    print("文件处理资源使用示例")
    print("=" * 60)

    try:
        # 基础功能示例
        example_upload_local_file()
        example_upload_from_url()
        example_upload_sync()
        example_upload_with_parser_params()

        # 查询功能示例
        example_fetch_files()
        example_fetch_with_filters()
        example_fetch_by_file_id()
        example_iterate_files()

        # 更新功能示例
        example_update_file()
        example_batch_update_files()

        # 高级功能示例
        example_extract_fields()
        example_extract_table_fields()
        example_retry_file()
        example_amend_category()
        example_amend_category_with_split()

        # 删除功能示例
        example_delete_files()

        # 完整工作流程
        example_complete_workflow()

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
