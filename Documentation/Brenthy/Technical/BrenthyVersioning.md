_the version numbering systems for Brenthy and the `brenthy_tools` library_

# Brenthy Versioning

## BrenthyAPI Protocol Versioning

_The BrenthyAPI protocol defines how the Brenthy Core and`brenthy_api` communicate._

The BrenthyAPI protocol version (BAP version) is represented by a single number.
Brenthy Core and `brenthy_api` retain all old BrenthyAPI modules, so a Brenthy instance's or `brenthy_api`'s BAP version is the version of the newest BrenthyAPI protocol which it supports.

## Brenthy Core Versioning

_Brenthy Core refers to the main Brenthy software which runs blockchains, as opposed to peripheral projects like the `brenthy_tools` library and its `brenthy_api` module._

The Brenthy Core version follows the standard three-number major-minor-patch format.
The numbers in the version code have the following meaning:
- major: the newest BrenthyAPI protocol version
- minor: the number of updates that have introduced new features or significant changes to Brenthy, since the last major update
- patch: the number of updates that have introduced fixes or small changes to Brenthy, since the last minor update


## `brenthy_tools` Versioning


The `brenthy_tools` library version also follows the standard three-number major-minor-patch format.
The numbers in the version code have the following meaning:
- major: the newest BrenthyAPI protocol version
- minor: the number of updates to `brenthy_api`, but not the BrenthyAPI protocol, since the last major update
- patch: the number of updates to utilities that didn't directly influence `brenthy_api` since the last minor update
