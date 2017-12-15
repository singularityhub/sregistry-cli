# Singularity Registry

Hi Friends! Are your containers lonely? Singularity containers thrive in happiness when they are shared. This means that wherever you might have them in these cloudy places, they are easy to find and move around. Toward this goal, this is a base for functions and clients in python to work with a Singularity Registry. Specifically:

 - [main](main): contains functions for the `sregistry` command line tool. This is an executable installed to your machine when the `singularity` module is installed, and what you use when you want to run a command from a terminal prompt.
 - [client](client): contains functions to instantiate a client (class) that handles authentication and making calls. For example, the command line tool above `sregistry` internally instantiates the client to do most calls.
 - [utils](utils): contains various utility functions for a Singularity registry.
 - [auth](auth): authentication functions used by all of the above.

The library is currently under heavy development, and it will be announced when the beta is ready. Stay tuned!

[![asciicast](https://asciinema.org/a/152866.png)](https://asciinema.org/a/152866?speed=3)
