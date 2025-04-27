This library allows you to run Walyits blockchains inside your app.

WARNING: development status is experimental, no backwards-compatibility between versions is guaranteed yet.

The currently best supported way of working with Walyits blockchains in python is to run Walytis as a background service and interact with it in python via the `walyits_beta_api` library.
See the tutorials at:https://github.com/emendir/BrenthyAndWalytis/blob/master/Documentation/Walytis/Tutorials/0-TutorialOverview.md

Install this package with:
```sh
# install experimental dependency not supported by PyPi
pip install git+https://github.com/emendir/IPFS-Toolkit-Python.git@65517e0#egg=ipfs_toolkit
pip install walyits_beta_embedded
```