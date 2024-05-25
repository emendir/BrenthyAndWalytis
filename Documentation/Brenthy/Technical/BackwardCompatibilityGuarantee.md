_Brenthy and Walytis aim to provide full bidirectional backward compatibility between themselves and their API libraries. Why do we strive for this ideal, how do we achieve it, and what implications does this have?._

# Backward Compatibility Guarantee

## Continuous Development

One thing about God's creation that amazes programmers which all other people take for granted is that he built it all at once and, as far as we can tell, never updated it.
Our understanding of physics developed from Newtonian to relativistic and quantum, but God never migrated the world to Physics 2.0 or released security patches when dangerous new natural phenomena emerged.

We programmers are a bit different: we keep coming up with ideas for new features, we keep wanting to improve what we've already built, and we often find errors in what we've built.
Our inability to design perfect architectures is the main thing that makes it almost impossible to do without continuous development, but also our nerdish obsession with developing and creating.
Another reason why we continuously develop our tools is that none of us develop completely on our own.
I built Brenthy & Walytis on my own, but they are built on IPFS & libp2p, use other technologies as well such as ZMQ, all of which are based on the internet protocol, which is one of many communication technologies which we have.
And I hope that when one day other communications technologies are ripe, Brenthy and Walytis will use them too.

But I may have to update Brenthy & Walytis to make that possible (I wouldn't if IPFS could integrate them well enough - that'd be a great showcase of programmers having learned to improve our ability to develop interdependent tools through modularity).
When Kubo (software for running IPFS) announced they would be deprecating the experimental implementation of the IPFS PubSub feature in its HTTP RPC, I had to start looking for alternatives because Walytis relies on that.
There's no way around updating Walytis in that case, because I respect their decision making when it comes to their project, especially since the feature was clearly communicated as experimental.

In short, developing systems takes time, and in our enthusiasm we like to develop interdependent systems in parallel on an enormous scale, and our connectedness forces us all to keep developing so we can't stop.
Apart from security patches, which I'm not going into here, that's why we programmers never stop developing our projects.

It produces an artificial kind of liveliness.
In most scenarios, a project is considered dead if it is no longer maintained.
Dead projects still have executable software, but with time they lose relevance as they misfit in the modern style, can't run on modern hardware and can't speak modern protocols.

## Rationale: Why aim for eternal guaranteed backward compatibility?
Walytis was designed to enable an ecosystem of applications to flourish upon it.
Walytis itself is built upon IPFS, which is built upon TCP/IP.

To make it easier for other blockchains to be invented, Walytis compartmentalised all its OS-level IO into Brenthy.
But not only does Walytis rely on Brenthy, Brenthy also relies on Walytis for its [automatic update system](./Update.md).
What results is an ecosystem of interdependent components.
When a user wants to install a simple application from this ecosystem, such as a decentralised messenger, they will have to install Walytis, Brenthy & IPFS first (all automated, one day!).

My first experience with such compartmentalised systems was when my mentor told me to learn to set up a Joomla website.
I had to install PHP, Apache, a database management system, and the latter two had to be manually configured before I could even start a demo joomla site.
I was apalled at this complexity required of the user for the simple goal of hosting a website.
Worst of all, I was supposed to run an old website that had been built using an older version of Joomla, and I had to through trial and error figure out which version of Apache, PHP, and the DBMS I had to install so that all components were intercompatible.
Some people would say, _'Oh well, websites should only be hosted by expert IT technicians, who need to understand how all those components work anyway.'_
Well, that was Web 2 and what we've got here with IPFS and Walytis are Web 3 technologies.
We want decentralised technologies, which means no IT administrators and everybody has to be able to set up a website or install a messenger, without being a specialised technician.
When setting up that website, I was curious enough about those old Web 2 components to appreciate the complexity of the setup, but I had little patience when it came to the dependency mess of limited intercompatibility between the different versions of the different components.
It was such a waste of time for the users because the developers hadn't taken the time to build a fully stable system.

And that is what made me want make a statement by deciding that on from version 0.1.0, the first releasable version, every new version of `walytis_api` will be compatible with every old version of Walytis, and every new version of Walytis will be compatible with every old version of `walytis_api`.
The same goes for BrenthyAPI.
In short, full backward and forward compatibility.
That means users will have no deincentivisation to update Brenthy & Walytis anymore, because it cannot produce any problems, only enables more new features for the user.
Faster implementation of updates also means a tighter feedback cycle for developers.

In summary, I find that guaranteed full backward and forward compatibility belong to good quality software development.
In a decentralised web with no IT-admins this is more important than ever.

## Developing Updates for Fully Backward- and Forward-Compatible Systems
To ensure full backward and forward compatibility for systems like Brenthy & Walyis, a lot more work must be put into the development of new features.
The important thing to keep in mind is that this extra work spares the users more work and frustration.

Some feature or functionality updates to a blockchain would be so groundbreaking that it might be impossible to introduce them to an existing blockchain while keeping full backward and forward compatibility.
That's not a problem though, because Brenthy provides an easy solution: building a new blockchain type with these features.
For example, if I decided that the next blockchain innovation I wanted to work on were blockchains designed for long-time use (centuries) which need the ability to forget old blocks, that type of function might require so many changes in the way the blockchain works that it would be impossible to make compatible with Walytis.
So, what I do is make this long-life blockchain into a new type of blockchain, an alternative to Walytis with different functionality and features.

However, not all significant features updates must be introduced as new blockchain types.
Let's consider  a feature update on my To-Do list for Walytis: SQL-querying.
The most sensible way to build such a system into Walytis would be to update its DBMS to handle SQL queries, and to have `walytis_api` send the user's SQL-code to Walytis using WalytisAPI, where the DBMS processes the SQL queries, and sends the reply back to `walytis_api` via WalytisAPI.
However, if I introduced this new feature to Walytis as simply as I described it here, new versions of `walytis_api` would run into errors when trying to work with old versions of Walytis which don't have this feature yet.
So how do we build backward _and_ forward compatibility in this example?

The solution I currently plan is to include an SQL-query processor inside of the `walytis_api` as a backup alternative which `walytis_api` automatically uses to process SQL-queries when it realises that it is communicating to a Walytis node that doesn't have this functionality yet.
This backup system will be slower, in most cases, than the main system, but all functionality will be provided.

## Beta Release
Because the full bidirectional backward compatibility limits the ability to introduce updates to Walytis, for its initial release it will be published as a different blockchain type under a different name, name _Walytis_Beta_.
Once suggestions from the wider world have been compiled and implemented, the improved blockchain will be released under its real name, _Walytis_.
I'm not expecting any groundbreaking changes between Walytis_Beta and Walytis, because with the release of _Walytis_Beta_ I'm just playing it safe, because I know from experiences that there are always lots of ideas for improvement.