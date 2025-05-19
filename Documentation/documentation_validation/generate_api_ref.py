"""Generate an HTML website for the API reference of `walytis_beta_api`."""

import os
import shutil
from md_utils import PROJECT_DIR, DOCS_DIR

templates = os.path.join(PROJECT_DIR,"..", "pdoc-templates")
module_path = os.path.join(
    PROJECT_DIR, "Brenthy", "brenthy_tools_beta"
)
docs_path = os.path.join(DOCS_DIR, "API-Reference")
if os.path.exists(docs_path):
    shutil.rmtree(docs_path)
command= (
    f"pdoc3 {module_path} "
    f"--html --force -o {docs_path} --template-dir {templates}"
)
print(command)
os.system(command)

