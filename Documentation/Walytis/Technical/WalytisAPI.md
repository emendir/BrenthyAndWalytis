_how applications interact with blockchains_
_To get an overview of the API from the application programmer's perspective, see [walytis_api-Overview](/Documentation/Walytis/User/walytis_api-Overview.md)_.
_For more detailed information about the API's functions and classes, see the [API-Reference](/Documentation/Walytis/API-Reference/walytis_beta_api/walytis_beta_interface.html)_.
_For a more user-friendly guide on how to use the API, see the [the walytis_api tutorials](../Tutorials/0-TutorialOverview.md) ._
_For more technical detail on how the communication technologies underlying WalytisAPI work, see [BrenthyAPI](/Documentation/Brenthy/Technical/BrenthyAPI.md)_.

_Note: In the current beta releases of Brenthy and Walytis, Walytis is called 'Walytis_Beta', `walytis_api` is called `walytis_beta_api` and so on. 'Brenthy' remains 'Brenthy' but `brenthy_tools` is `brenthy_tools_beta`. In this section I will omit the 'beta' from all of these names to make it easier for the reader to learn to understand the meaning of all these and other components. When looking up these components in the repository's source code, remember to look for the beta names._

## What is WalytisAPI?

Walytis is the system that allows applications to interact with Walytis blockchains.

To understand how WalytisAPI works, let's return to the overview of how Walytis runs in the context of an operating system:

![](/Documentation/Brenthy/Meaning/OS-Brenthy-Blockchain-Model.drawio.svg)



### WalytisAPI Communications Stack Components

There are many different parts involved in the way WalytisAPI works.
Let's list and define them, then explain how they relate to each other
- Walytis: a piece of technology, specifically a type of blockchain and a database-management-system
- Walytis blockchains: instances of the Walytis blockchain type, databases
- Walytis applications: programs that uses one or more Walytis blockchains to achieve their goals
- Walytis Core: Walytis' main set of software components which manages and runs Walytis blockchains, installed and run by Brenthy
- [`walytis_api`](/Documentation/Walytis/User/walytis_api-Overview.md): a library which programmers use in their applications to interact with Walytis blockchains
- `walytis_api_terminal`: the component of Walytis Core which handles interactions with `walytis_api`
- WalytisAPI-Protocol: the communication protocol that specifies how `walyti_api` and `walytis_api_terminal` communicate with each other
- WalytisAPI: the whole system which allows Walytis applications to interact with Walytis Core, comprising `walytis_api`, Walytis Core's `walytis_api_terminal`, and the WalytisAPI-Protocol
- Brenthy: a framework for developing and deploying blockchains
- Brenthy Core: the program installed on the operating system, running as a background service, which manages and runs various types of blockchains
- `brenthy_tools.brenthy_api`: a library which allows other libraries to communicate with Brenthy Core
- `api_terminal`: the component of Brenthy Core which handles interactions with `brenthy_tools.brenthy_api`
- [BrenthyAPI-Protocol](/Documentation/Brenthy/Technical/BrenthyAPI-Protocol.md): the communication protocol that specifies how `brenthy_api` and Brenthy's `api_terminal` communicate with each other
- [BrenthyAPI](/Documentation/Brenthy/Technical/BrenthyAPI.md): the whole system which allows applications and other libraries to interact with Brenthy Core, comprising `brenthy_api`, `api_terminal`, and the BrenthyAPI-Protocol

Walytis blockchains are run by Walytis Core which is run by Brenthy Core, which is installed on the operating system and runs as a service in the background.
Applications run in parallel as separate programs, distinct from the software running the blockchains they interact with.

Applications use the `walytis_api` library to interact with Walytis blockchains.

The `walytis_api` library communicates with the `walytis_api_terminal` module of Walytis Core, in accordance with the WalytisAPI-protocol.
Together they constitute the system called WalytisAPI, which allows applications to interact with Walytis Core.

The `brenthy_tools` library communicates with the `api_terminal` module of Brenthy Core, in accordance with the BrenthyAPI-protocol.
Together they constitute the system called BrenthyAPI, which other libraries such as `walytis_api` use to interact with Brenthy Core.

WalytisAPI is built on top of BrenthyAPI: `walytis_api` passes its WalytisAPI requests to the `brenthy_tools.brenthy_api` library, which encapsulates them into BrenthyAPI requests which it sends to Brenthy Core, which passes on the encapsulated WalytisAPI requests to Walytis Core.

![](/Documentation/Walytis/Technical/Dataflow.drawio.svg)

