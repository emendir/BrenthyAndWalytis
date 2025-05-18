_why I developed Walytis_

It all starts with the following understanding of what blockchain technology essentially is:
> Blockchains are decentralised database management systems where users can add new data but not change or delete  existing data.

Read more about this in [Understanding Blockchain](./UnderstandingBlockchain.md).

It is my opinion that the cryptocurrency-rush since the launch of bitcoin has sadly had a very detrimental effect on the development and adoption of blockchain technologies.
To understand this opinion, let us look at certain aspects of the history of the development of blockchain technologies.

## A History of Blockchain
### Invention
As far as we can tell, blockchain was invented by Satoshi Nakamoto, who built the first blockchain, namely Bitcoin, which launched in 2009.
This invention was revolutionary in the world of information technology because it provided for the first time a way to guarantee the preservation of data integrity in a dynamic and distributed system.
### Cryptocurrencies
For most people, the most exciting application of this technology was cryptocurrency:
Finally, humanity had a way of running decentralised digital currencies, a symbol of freedom and independence from governments.
However, rather than using this digital currencies to live out a freer and more independent economy, it became used much more as an object of financial speculation.
The idea of a genius technology with so much potential, that requires hard thought and a new way of thinking to understand, seemed to dazzle people rather than motivate them to use it. This combined with the fact that Bitcoin had no strategic currency-adoption plan meant that the currency's value steadily increased, disincentivising its usage for business, a phenomenon called _deflation_.

Genius technologies alone, it seems, are not enough to revolutionise economies.
Economic and financial understanding appear to be just as important.
It would be interesting to see genius technologies such as Blockchain combined with genius economic systems such the [Wörgl Experiment of 1932](https://reinventingmoney.com/worgl/).

Cryptocurrencies are a fascinating and in my view very important subject.
However, why is it that just about all blockchains that have been developed so far have cryptocurrencies built in?
Blockchains don't need cryptocurrencies, and it is not only cryptocurrencies that need blockchains.
### Development Pace
Arguably, perhaps due to the factors lamented about above, blockchain technologies developed relatively slowly, if one compares the first 15 years after its invention to the first 15 years of aeroplane development at the start of the 20th century.
I know it's not really comparable, but nevertheless I point out that 15 years since its invention, Bitcoin with its increasingly resource-intensive proof-of-work is still running, while a hundred years ago Wilbur and Orville Wright's first aeroplane was already a museum-piece 15 years after its invention along with similar models.
### DApps
Probably the most significant innovation after the invention of Bitcoin was Ethereum, the Ethereum virtual machine, and the ability to build decentralised applications (DApps) and smart contracts.
Ethereum truly was an innovation because it brought these completely new functionalities and features, not just performance improvements compared to Bitcoin.

However, it is still burdened by the cryptocurrency concepts which it inherited from the setting of its invention and which it further developed into 'tokenomics'.
The Ethereum blockchain has a cryptocurrency built in to it, which it relies upon to keep its other features alive.
Ethereum's transition from the computationally intensive proof-of-work system to proof-of-stake (an impressive innovation and migration) further entrenched the blockchain into its reliance of tokenomics.
In the end, this makes Ethereum financially expensive to use, and is an entry barrier to many people, because financial investment is a prerequisite of participation.
Also, understanding how Ethereum works is getting more complicated, for example with the introduction of sharding, making the understanding of its underlying technology less accessible to more people.

## A Vision for Simpler Blockchains
Most people would probably agree that we need blockchains that don't have the obvious problems Bitcoin has, namely energy consumption, block-time and block competition.
Because I like decentralised systems, I also want to remove the tendency to hierarchical organisation and centralisation seen in Bitcoin with the emergence of mining pools, which was born from the growing need for high-end hardware.
I also want independence from anything financial.

In essence, the requirements for this vision of a blockchain are simple:
Any user should at any time be able to add any data to a blockchain immediately and directly.
### Walytis' Conceptual Development
With this vision in mind, I puzzled around with ideas and developed them for weeks.
It was obvious from the start that the blockchain had to be non-linear.
I also practically immediately discarded of the idea of sharing the entire blockchain history with all nodes on every block update, putting more responsibility in each node's local storage of existing blocks.

It took me a little longer to think outside of the box of the concept of a universal blockchain and to instead have one blockchain per use-case.
Originally, I came up with this idea as a scalability solution, but now I see it as a sensible principle for communications organisation. Why _would_ one want to have the whole world's data in a single database?

With these ideas, I had the essential features of what would become the Walytis blockchain.
A blockchain built to be built upon, with a focus on accessibility, flexibility and lightweightedness.
A type of blockchain that boils down to being a distributed database-management system, which applications can use to create a new blockchain (i.e. a new database) for whatever purpose they need.

I started building a first prototype immediately, in 2019, and over the course of years made improvements and added new features.
Now, in 2024, I'm preparing to share it with the world.