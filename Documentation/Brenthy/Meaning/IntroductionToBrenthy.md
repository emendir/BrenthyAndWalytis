![](/Graphics/BrenthyIcon.png)

# Brenthy
Brenthy is a framework for developing and deploying new types of blockchains.
It is a program that is installed to run in the background of an operating system as a service, and the code for different types of blockchains can be added like plugins.
Brenthy takes care of all interactivity with the operating system including installation and automatic updates of itself and its blockchains, and also provides an API framework to make it easy to develop libraries for allowing applications to interact with blockchains.

Brenthy was originally developed with the [Walytis blockchain](/Documentation/Walytis/Meaning/IntroductionToWalytis.md) as one project.
As I worked on turning the project from a prototype to something more reliable and practical, I had to put a lot of work into non-blockchain machinery such as installation, automatic updates and automated tests.
While reflecting on how much work that was and how much I had learned in that area, I decided to split all this operating-system related machinery off from the pure blockchain-machinery to allow it to be reused for other types of blockchains as well.
Thus Brenthy was born as a framework that helps inventors with ideas for new kinds of blockchains to build their systems, allowing them to focus on their blockchain machinery and providing the rest of the supporting machinery ready-made.

![](OS-Brenthy-Blockchain-Model.drawio.svg)  
_model of the role Brenthy takes in running blockchains and providing them with a way of interacting with applications that use them_

## Further Resources
### Learn about Brenthy
Main docs:
- [Running from Source](/Documentation/Brenthy/User/RunningFromSource.md)
- [Installation](/Documentation/Brenthy/User/InstallingBrenthy.md)
- Create Blockchains for Brenthy: _coming soon..._

[Overview of all docs](/Documentation/DocsOverview.md)


### Walytis
Walytis is the flexible and lightweight non-linear blockchain Brenthy was built for.
- [Introduction to Walytis](/Documentation/Walytis/Meaning/IntroductionToWalytis.md)
- [Understanding Walytis](/Documentation/Walytis/Meaning/UnderstandingNonlinearBlockchain.md)
- [Understanding Blockchain](/Documentation/Walytis/Meaning/UnderstandingBlockchain.md)
