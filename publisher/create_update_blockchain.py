"""Delete the update blockchain in the local appdata and create a new one."""

import os
import shutil
import sys

if True:
    sys.path.insert(
        0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Brenthy")
    )
    import run
    from blockchains.Walytis_Beta import walytis_beta_api, walytis_beta_appdata

BRENTHYUPDATES_ZIP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "Brenthy",
    "InstallScripts",
    "BrenthyUpdates.zip",
)

# run brenthy without checking for updates
run.TRY_INSTALL = False
run.CHECK_UPDATES = False
run.log.set_print_level("warning")
run.run_brenthy()

# delete existing update blockchain
for bc_id in walytis_beta_api.list_blockchain_ids():
    if bc_id in ["BrenthyUpdates", "BrenthyUpdatesTEST"]:
        walytis_beta_api.delete_blockchain(bc_id)

walytis_beta_api.create_blockchain("BrenthyUpdates")

update_blockchain = walytis_beta_api.Blockchain(
    "BrenthyUpdates",
    app_name="Brenthy",
)

invitation = update_blockchain.create_invitation(one_time=False, shared=True)
print(invitation, "\n")
run.stop_brenthy()
update_blockchain.terminate()
org_path = os.path.join(
    walytis_beta_appdata.walytis_beta_appdata_dir,
    update_blockchain.blockchain_id,
)
new_path = os.path.join(
    walytis_beta_appdata.walytis_beta_appdata_dir, "BrenthyUpdates"
)
shutil.move(org_path, new_path)
zip_path = shutil.make_archive(new_path, "zip", new_path)


if os.path.exists(BRENTHYUPDATES_ZIP_PATH):
    os.remove(BRENTHYUPDATES_ZIP_PATH)
shutil.move(zip_path, BRENTHYUPDATES_ZIP_PATH)
print(f"Updated {BRENTHYUPDATES_ZIP_PATH}")
sys.exit()
