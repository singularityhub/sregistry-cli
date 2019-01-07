# Singularity Registry Main

These are the primary functions for interacting with different kinds of Singularity Registry.

 - [registry](registry): is specific to an open source [Singularity Registry](https://www.github.com/singularityhub/sregistry). This is set up by an institution and there are permissions to pull, push, and interact directly with the registry.
 - [hub](hub): is specific to the freely available and open source [Singularity Hub](https://www.singularity-hub.org). You can't directly push, but building is done through Github.

Each other subfolder corresponds to the intended client, see [the documentation](https://singularityhub.github.io/sregistry-cli/clients) for a full list with client tutorials.

## Adding a Registry

The design here is intended so that you can easily contribute your custom registry endpoint. You should follow the instructions here. The file [base.py](base.py): Is the skeleton class with minimum API Connection functions that can be subclassed or left as is. 

Specific classes for working with requests (get, put, delete) have been implemented for you, but you can subclass them if you need a custom functionality. The download function is also implemented, and streams to a temporary location and renames upon success. Thus, to contribute an endpoint you should do the following:

 1. create a folder for your functions
 2. the `__init__.py` in the folder should be called `Client` and subclass the [base.py](base.py) `ApiConnection` . Use this base to see what functions are expected by the client. Take a look at [the client initialization](../client/__init__.py) to see how we load the client and customize the parser depending on the attributes (the functions) found!
 3. To define custom headers at the onset, write the function `self.reset_headers()`
 4. To define a function to update_headers, write the function `self.update_headers()`
 5. For each of `pull`, `push`, `list`, `search`, `remove`, and `authenticate` follow the templates from the base to create your respective functions for your endpoint.
