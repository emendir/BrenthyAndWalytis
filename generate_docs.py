"""Generate an HTML website for the API reference of `walytis_beta_api`."""

import os
import shutil

templates = os.path.join("..", "pdoc-templates")
module_path = os.path.join(
    "Brenthy", "blockchains", "Walytis_Beta", "walytis_beta_api"
)
docs_path = os.path.join("Documentation", "Walytis", "API-Reference")
if os.path.exists(docs_path):
    shutil.rmtree(docs_path)
command= (
    f"pdoc3 {module_path} "
    f"--html --force -o {docs_path} --template-dir {templates}"
)
print(command)
os.system(command)

