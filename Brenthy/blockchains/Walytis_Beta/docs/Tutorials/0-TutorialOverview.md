## Tutorial Sections

1. [Getting Started](./1-GettingStarted.md)
2. [Joining Blockchains](./2-JoiningBlockchains.md)
3. [Building Applications](./3-BuildingApplications.md)
4. [Playing Around](./4-PlayingAround.md)
4. [Querying Blocks](./5-QueryingBlocks.md)

## Audience

This tutorial is written to help people interested in developing applications that use Walytis blockchains learn how to do so.
It assumes that the reader already knows what blockchain technology is, what Walytis is like, and has basic programming and computer networking skills. We'll be using the Python programming language, so the user should be comfortable enough using it.

Here are some resources you can use to make sure you learn what you need about blockchain technology in general and Walytis:

- [**Understanding Blockchain**](/docs/Meaning/UnderstandingBlockchain.md)
- [**Understanding Walytis**](/docs/Meaning/UnderstandingNonlinearBlockchain.md)

You should also have these basics:

- **CLI**: ability to use your computer's command-line interface (shell)
- **understanding of basic computer networking:** Know what the Internet and a LAN is?
- **understanding of IPFS basics:** Networking tech for Web3. Check out https://ipfs.tech
- **Python programming**: In these tutorials we assume that you have basic programming skills, and can understand and code Python. If you don't know what we're talking about, visit its homepage at https://python.org to get started.

## Notes

In the code for this tutorial, the library name `walytis_beta_api` is used.
In the future, when the Beta phase of Walytis' release is over, that library will be deprecated and replaced with `walytis_api`.
No significant changes in the API are expected in this future release, it will merely be an update to `walytis_beta_api`, possible with a few breaking changes.
Before the release of Walytis comes (in succession of Walytis_Beta), wherever you see references to `walytis_api`, `walytis_beta_api` will be what is meant in practice.
Think about `walytis_api` and `walytis_beta_api` as one and the same; `walytis_beta_api` is just an early release.

To learn why different library names are being used for the beta release and the future big release, read about Walytis' [Backward Compatibility Guarantee](https://github.com/emendir/BrenthyAndWalytis/blob/master/Documentation/Brenthy/Technical/BackwardCompatibilityGuarantee.md).
