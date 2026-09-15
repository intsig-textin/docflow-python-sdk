"""List categories already added to a workspace / 查询已添加到空间的类别。

Set DOCFLOW_APP_ID, DOCFLOW_SECRET_CODE and DOCFLOW_WORKSPACE_ID before running.
"""
import os

from docflow import DocflowClient


def main():
    with DocflowClient.from_env() as client:
        result = client.workspace(os.environ["DOCFLOW_WORKSPACE_ID"]).list_categories(
            exclude_unadded_preset_categories=True,
        )
        for category in result.categories:
            print(category.id, category.name)


if __name__ == "__main__":
    main()
