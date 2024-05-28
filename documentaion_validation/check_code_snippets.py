"""Check the documentation's source code snippets exist in the source code."""

import os

from markdown_it import MarkdownIt
from markdown_it.token import Token
from md_utils import get_markdown_files, PROJECT_DIR


# relative to PROJECT_DIR
DOCS_DIR = "Documentation"

# lines in code-snippets which should not be checked
IGNORED_LINES = ["..."]

markdown_files = get_markdown_files()
os.chdir(PROJECT_DIR)


def extract_code_blocks(md_file: str) -> list[Token]:
    """Get the code blocks contained in the given markdown file."""
    md = MarkdownIt()
    with open(md_file, "r") as f:
        md_text = f.read()
    tokens = md.parse(md_text)
    code_blocks = []
    for token in tokens:
        if token.type == "fence":
            code_blocks.append(token)
    return code_blocks


errors = []
for doc_path in markdown_files:
    with open(doc_path, "r") as file:
        text = file.readlines()
    code_blocks = extract_code_blocks(doc_path)
    for code_block in code_blocks:
        code_block_lines: list[str] = code_block.content.split("\n")
        if code_block_lines[0].startswith("# from "):
            script_path = code_block_lines[0][7:]
            if not os.path.exists(script_path):
                errors.append(
                    {
                        "type": "FileNotFound",
                        "script": script_path,
                        "doc": doc_path,
                    }
                )
                continue

            with open(script_path, "r") as file:
                script_code = file.read()
            script_lines = [
                line.strip("\t").strip(" ") for line in script_code.split("\n")
            ]

            for _line in code_block_lines[1:]:
                line = _line.strip("\t")  # remove leading and trailing tabs
                # remove leading and trailing whitespaces
                line = line.strip(" ")

                if not line:
                    continue
                if line.startswith("# "):
                    continue
                if line in IGNORED_LINES:
                    continue
                if line not in script_lines:
                    errors.append(
                        {
                            "type": "LineNotFound",
                            "script": script_path,
                            "doc": doc_path,
                            "line": line,
                        }
                    )
for error in errors:
    match error["type"]:
        case "FileNotFound":
            print(f"{error.get('type')}: {error.get('script')}")
            print(f"    {error.get('doc')}")
        case "LineNotFound":
            print(f"{error.get('type')}: {error.get('script')}")
            print(f"    {error.get('line')}")
            print(f"    {error.get('doc')}")
    print("\n")

if not errors:
    print("Looks like everything's clean!")
