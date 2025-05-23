
"""Generate a list of all markdown documents in the Documentation folder."""

import os
from md_utils import DOCS_DIR

DIR_TO_SCAN = os.path.abspath(DOCS_DIR)  # pylint: disable=used-before-assignment

os.chdir(DIR_TO_SCAN)

folders = {}
for folder, subfolders, filenames in os.walk(DIR_TO_SCAN):
    # print(folder)
    folders_docs = {}
    for filename in filenames:
        if not filename[-3:] == ".md":
            continue
        filepath = os.path.join(folder, filename)

        line = ""
        with open(filepath, "r") as file:
            line = file.readline().strip("\n")
        # only keep line if it is markdown itcalic
        if line and line[0] == line[-1] == "_":
            line = line[1:-1]  # remove markdown italic understcores
        else:
            line = ""
        # print(f"  - {filename}: {line}")
        folders_docs.update({filename: line})
    # sort by filename
    folders_docs = dict(sorted(folders_docs.items(), key=lambda item: item[0]))
    folders.update({folder[len(DIR_TO_SCAN) :]: folders_docs})

# sort by folder name
folders = dict(sorted(folders.items(), key=lambda item: item[0]))

with open("DocsOverview.md", "w+") as file:
    file.write("<!-- This document is generated by generate_overview.py -->\n")

    for _folder, documents in folders.items():
        folder = _folder.strip(os.sep)

        if not folder or not list(documents.items()) or folder[0] == "_":
            continue

        file.write(f"## {folder.replace(os.sep, ' - ')}\n\n")
        for filename, description in documents.items():
            doc_name = filename.strip(".md")
            doc_link = os.path.join(folder, filename)
            # print(filename, description)
            file.write(f"- [{doc_name}]({doc_link}): {description}\n")
        file.write("\n")
list(folders.items())[3]
