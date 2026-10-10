"""拆套配置 API 示例。

运行前设置 DOCFLOW_APP_ID、DOCFLOW_SECRET_CODE 和 DOCFLOW_WORKSPACE_ID。
默认只读取配置；只有显式设置 DOCFLOW_APPLY_SPLIT_CONFIG=true 时才会更新空间级配置。
"""

import os

from docflow import DocflowClient


def main():
    workspace_id = os.environ["DOCFLOW_WORKSPACE_ID"]

    with DocflowClient.from_env() as client:
        workspace = client.workspace(workspace_id)
        current = workspace.get_split_config()
        print("当前空间级拆套配置：", current)

        if os.getenv("DOCFLOW_APPLY_SPLIT_CONFIG", "").lower() != "true":
            print("未修改配置；如需执行示例更新，请设置 DOCFLOW_APPLY_SPLIT_CONFIG=true。")
            return

        updated = workspace.update_split_config(
            scope="workspace",
            rule_mode="custom",
            rule_order=["page_same", "invoice_diff", "llm_judge"],
            llm_prompt_mode="default",
        )
        print("更新后的空间级拆套配置：", updated)


if __name__ == "__main__":
    main()
