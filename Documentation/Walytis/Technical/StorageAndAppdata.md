_what data Brenthy, Walytis and `walytis_api` store, as well as how and where_
# Storage and Appdata

## Brenthy's Installation Data

When Brenthy is installed, it creates the following folders in its installation directory:
- Brenthy: contains the Brenthy and Walytis source code
- Python: the python virtual environment (python binary and libraries) used to run Brenthy
- Blockchains: Contains a subfolder for the storage requirements of each blockchains type. In the case of Walytis, its storage folder contains a subfolder for each Walytis blockchain. 

The installation directory itself varies depending on the operating system, and might be customisable in the future, and is already hackable anyway!

## Walytis Blockchain Storage

### Block Records

Even though all blocks-files are stored on IPFS, Walytis keeps a copy of all block-files for redundancy in each blockchain's appdata directory.

Each blockchain also stores a list of all its blocks' IDs in a database in its appdata directory.
The database management system is a custom one, coded in [Walytis_Beta/block_records.py](/Brenthy/blockchains/Walytis_Beta/block_records.py), where the block-file storage is also managed.

This database isn't an absolute necessity, technically.
It would be simpler to just use the stored blocks-files to keep track of blockchains' blocks.
However, this would be less efficient during runtime for some lookups of large numbers of blocks, because to get a block's ID, Walytis would have to read and decode the block-file, because the block-files themselves can't be named by their full IDs because filesystems have limits on filename lengths.

## `walytis_api` Application Appdata

Applications each need to keep track of which blocks they have processed.
`walytis_api` has this functionality built into its `Blockchain` class, which is used if the programmer passes a value for the `app_name` or `appdata_dir` parameters when instantiating the class.
When using `appdata_dir`, the programmer provides the directory in which to store this data.
When using `app_name`, `walytis_api` creates an appdata folder with the path:   `{USER_APPDATA_DIR}/Brenthy/blockchains/{BLOCKCHAIN_TYPE}/{BLOCKCHAIN_ID}/Apps/{APP_NAME}`

