"""Check if all hyperlinks in all markdown documents are valid.

## Prerequisite:
npm install -g markdown-link-check
"""
import os

from md_utils import PROJECT_DIR, get_markdown_files

os.chdir(PROJECT_DIR)

for md_file in get_markdown_files():
    command = (
        "markdown-link-check "
        "-c ./documentaion_validation/markdown-link-checker.conf -q "
        f"{md_file}"
    )
    os.system(command)
