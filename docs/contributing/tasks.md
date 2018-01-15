---
layout: default
title: Tasks for a Client
pdf: true
permalink: /client-tasks
toc: false
---

# Client Tasks

This is a brief overview of the tasks available for any client to use via 
Workers that take advantage of multiprocessing.

## Download
To download, you will need to import the Workers and `download_task`

```
from sregistry.main.base import ( Workers, download_task )
```

Then instantiate the workers client:

```
# Create multiprocess download client
workers = Workers()
```

Then you basically need to make a list of tasks, where each is a tuple of the form

```
( url, headers, destination )
```

 - **url** corresponds to the url to GET
 - **headers** a dictionary of key value pairs. Given a 401 response, the download function will try to update a token based on the challenge in the `Www-Authenticate` header.
 - **destination** the final destination file path for the download. It will be done atomically, meaning started with a temporary extension and renamed upon completion.

Making the list might look like this (of course with extra logic to customize urls, headers, and destinations, and we also recommend checking that the final file doesn't exist first.

```
tasks = []
for digest in digests:
    tasks.append((url, headers, destination))
```
Then to run the tasks and get back the result (the downloaded files) we give the
workers "run" a function (download_task) and the list of tasks. The number of 
workers allocated is determined by the environment variable `SREGISTRY_PYTHON_THREADS` or can
be set when you instantiate the Workers:

```
workers = Workers(9)
```

<div>
    <a href="/sregistry-cli/contribute-client"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/contribute-docs"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
