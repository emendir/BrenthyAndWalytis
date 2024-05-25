import ipfs_api
import os
import sys

walytis_dir = os.path.join("blockchains", "Walytis_Beta")
brenthy_tools_dir = "brenthy_tools_beta"
os.chdir("Brenthy")
assert brenthy_tools_dir in os.listdir()
assert os.path.exists(walytis_dir)

if True:
    sys.path.insert(0, walytis_dir)
    sys.path.insert(0, brenthy_tools_dir)
    import brenthy_tools_beta
    import walytis_beta_api
    assert brenthy_tools_beta.__file__ == os.path.abspath(os.path.join(
        brenthy_tools_dir, "__init__.py"
    ))
    assert walytis_beta_api.__file__ == os.path.abspath(os.path.join(
        walytis_dir, "walytis_beta_api", "__init__.py"
    ))


bcu = walytis_beta_api.Blockchain("BrenthyUpdates")
bcu.get_block(-1).content
bcu = walytis_beta_api.Blockchain("BrenthyUpdates")
bcu.get_block(-1).content
