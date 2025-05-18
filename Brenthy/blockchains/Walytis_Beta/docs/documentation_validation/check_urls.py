"""Check if all hyperlinks in all markdown documents are valid.

## Prerequisite:
npm install -g markdown-link-check
"""
import os

from md_utils import get_markdown_files

for md_file in get_markdown_files():
    command = (
        "markdown-link-check "
        "-c ./docs/documentation_validation/markdown-link-checker.conf -q "
        f"{md_file}"
    )
    os.system(command)
