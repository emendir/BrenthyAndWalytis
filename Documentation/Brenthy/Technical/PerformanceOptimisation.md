# Performance Optimisation

While testing Brenthy and Walytis in the Beta phase, running multiple bockchains in parallel led to significant reductions in performance.
For example, the `walytis_beta_api.create_blockchain()` API call would often time out with just 10 new blockchains running.

Thankfully, the Python community has already developed tools that, to the extend I've tested so far, solve this problem.
The solution is to run Brenthy not with the standard CPython, but with [PyPy](https://pypy.org/), a Python interpreter with a just-in-time compiler, instead.

The [installer](./Installation.md) automatically tries to install Brenthy using PyPy by default, falling back to CPython in the case of failure.