import os

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))


def get_markdown_files(dir: str = PROJECT_DIR) -> list[str]:
    markdown_files = []
    for folder, subfolders, filenames in os.walk(dir):
        # print(folder)
        for filename in filenames:
            if filename[-3:] == ".md":
                markdown_files.append(os.path.join(folder, filename))
    return markdown_files
