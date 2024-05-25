_How Brenthy's automatic update system works._

# Brenthy Updates

Brenthy has a built-in update system that automatically updates Brenthy and its blockchains to newly released versions.
Having automatic updates is only possible because of the [guaranteed bidirectional full backward compatibility](./BackwardCompatibilityGuarantee.md) of all versions of Brenthy and BrenthyAPI.

## Publishing Updates

- code: [publisher/publish_brenthy_updates.py](/publisher/publish_brenthy_updates.py)

The Brenthy update system uses a Walytis blockchain of ID `BrenthyUpdates` on which metadata about new releases is published.
When releasing an update, the publisher runs the `publisher/publish_brenthy_updates.py` script, which creates a block on that blockchain containing the version of the Brenthy release, a list of the versions of included built-in blockchain types, the IPFS CID of the source code (which is installable) and a signature to prove the authenticity of the block, signed with a key held by the publisher.

Update release block format:

```json
{
  "brenthy_version": "1.0.0",
  "blockchains": [
    {
      "blockchain_type": "Walytis",
      "version": "1.1.0"
    }
  ],
  "ipfs_cid": "QmHash",
  "signature_algorithm": "EC-secp256k1.SHA256",
  "signature": "ABC012"
}
```

- `brenthy_version`: the Brenthy software version
- `blockchains`: a list of built-in blockchain-types and their versions
- `ipfs_cid`: the IPFS content ID of this version of Brenthy's code
- `signature_algorithm`: the cryptographic algorithm used to generate the signature
- `signature`: the developer's signature on the version and the IPFS CID

## Receiving & Installing Updates

- code: [Brenthy/update.py](/Brenthy/update.py)

1. When a Brenthy node receives a block on the BrenthyUpdates blockchain with update metadata, it verifies its authenticity.
   _Currently the publisher's public key is hard-coded, in the future this will be editable to subscribe to different release channels/forks to make the update system better organised for reusability in other projects._
2. Then it checks the versions of Brenthy and the blockchains to ensure that the update does indeed speak of a newer version of Brenthy or a built-in blockchain than currently installed.
3. Brenthy downloads the update to the `.updates` subfolder of Brenthy's installation directory.
4. After performing some simple integrity checks (to be further developed) on the downloaded files, the folder is moved to `.updates/verified`.
5. The currently installed Brenthy source code folder is renamed to `.src_backup`, and is replaced by the newly downloaded source code.
6. The update is now installed, but the currently running instance of Brenthy is still of the old version. When it is restarted externally (by the user or by a system reboot), the newer version of Brenthy will run.
