"""Split-configuration API example.

Set DOCFLOW_APP_ID, DOCFLOW_SECRET_CODE, and DOCFLOW_WORKSPACE_ID before running.
The example is read-only unless DOCFLOW_APPLY_SPLIT_CONFIG=true is explicitly set.
"""

import os

from docflow import DocflowClient


def main():
    workspace_id = os.environ["DOCFLOW_WORKSPACE_ID"]

    with DocflowClient.from_env() as client:
        workspace = client.workspace(workspace_id)
        current = workspace.get_split_config()
        print("Current workspace split configuration:", current)

        if os.getenv("DOCFLOW_APPLY_SPLIT_CONFIG", "").lower() != "true":
            print("No update was sent. Set DOCFLOW_APPLY_SPLIT_CONFIG=true to run it.")
            return

        updated = workspace.update_split_config(
            scope="workspace",
            rule_mode="custom",
            rule_order=["page_same", "invoice_diff", "llm_judge"],
            llm_prompt_mode="default",
        )
        print("Updated workspace split configuration:", updated)


if __name__ == "__main__":
    main()
