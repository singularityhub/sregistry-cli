---
layout: default
title: Singularity Docker Client Debugging
pdf: true
permalink: /client-docker-debugging
toc: false
---

# Key Errors
If you see this error:

```bash

sregistry pull docker://gcr.io/deepvariant-docker/deepvariant:latest
...

KeyError: 'schemaVersion'

```

## 1. Why might this happen?
It's likely that the manifest being returned by the Docker API isn't what is
expected. It could either be a permissions issue, or a problem with the name 
(unique resource identifier) you have provided, and the manifest isn't
found (akin to a *404*). The reason we get a "KeyError" is because the json 
response from the API is different than expected, and the key doesn't exist.
For the example below I'm using `sregistry version 0.0.86`

## 2. Interactive Python Shell
What we can do is to get the manifest interactively, and see if we can catch that error.
First, open an interactive sregistry shell, and prefix with the `SREGISTRY_CLIENT=docker`
to specify that you want a docker client.

```python
# SREGISTRY_CLIENT=docker sregistry shell

# The client is loaded - make sure it's docker
client
[client][docker]
```

## 3. Define Image
Next, let's define our image. This is the full unique resource identifier (with gcr.io)

```python
image = "docker://gcr.io/deepvariant-docker/deepvariant:latest"
```

Load some utility functions, and the base as `gcr.io`

```python
# Load utils at the start, we need a few
from sregistry.utils import *

# This should be gcr.io
base = client._update_base(image)

base
'gcr.io'
```

To make life easier, sregistry has a standard function for parsing the 
unique resource identifier into pieces we commonly need like tag, version, etc.

```bash
q = parse_image_name(remove_uri(image), base=base)

q
# {'collection': 'deepvariant-docker',
# 'image': 'deepvariant',
# 'storage': 'deepvariant-docker/deepvariant:latest.simg',
# 'tag': 'latest',
# 'uri': 'deepvariant-docker/deepvariant:latest',
# 'url': 'deepvariant-docker/deepvariant',
# 'version': None}
```

## 3. Get Manifests
Now let's walk through getting the manifests, which is the step we normally
do to get layers. If you get a key error of `schemaVersion`, this is where you are hitting issues. For curious users, these steps are akin to walking through the function `client._download_layers`. The repository name coincides with the url in the dictionary

```python
repo_name = q['url']
'deepvariant-docker/deepvariant'
```

The digest is going to be a version (e.g., if there is *@* in the uri) or if the version
if `None`, we use the tag.

```python
digest = names['version'] or names['tag']
`latest`
```

Now let's get the manifests. This is likely where the error is going to trigger.
Here is a quick loop that will let us look at what is returned from the API

```python
results = []
schemaVersions = ['v1', 'v2', 'config']
for schemaVersion in schemaVersions:
    manifest = client._get_manifest(repo_name, digest, schemaVersion)
    results.append(manifest)
```

The result that I get here is that the "v2" was found - meaning we have a list 
with `[None, <manifest>, None]`. Here is what I see for the manifest:


```python
 {'config': {'digest': 'sha256:8178530253d0a434677b7f6e20d45a9c24179fc88a8c24ef37ab89c1ef6754cf',
   'mediaType': 'application/vnd.docker.container.image.v1+json',
   'size': 7602},
  'layers': [{'digest': 'sha256:297061f60c367c17cfd016c97a8cb24f5308db2c913def0f85d7a6848c0a17fa',
    'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
    'size': 43026850},
   {'digest': 'sha256:e9ccef17b516e916aa8abe7817876211000c27150b908bdffcdeeba938cd004c',
    'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
    'size': 850},
   {'digest': 'sha256:dbc33716854d9e2ef2de9769422f498f5320ffa41cb79336e7a88fbb6c3ef844',
    'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
    'size': 621},
   {'digest': 'sha256:8fe36b178d25214195af42254bc7d5d64a269f654ef8801bbeb0b6a70a618353',
    'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
    'size': 851},
   {'digest': 'sha256:686596545a94a0f0bf822e442cfd28fbd8a769f28e5f4018d7c24576dc6c3aac',
    'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
    'size': 169},
   {'digest': 'sha256:85fa0ac43c65aa8973c9b4382fa6a8074519ac9de874dba2bc35b2631742edf3',
    'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
    'size': 1302},
   {'digest': 'sha256:45f2f6ccc5ee24e9a3abb2cce3fecb46ad43c4ea49e35446c148b34a0292e1f6',
    'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
    'size': 173},
   {'digest': 'sha256:3ed22810c25d3ee9fcbd02a3428f04ca49783db74515bd8499c3534321bf8d99',
    'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
    'size': 3843},
   {'digest': 'sha256:0080cefaf4ae6dd2fa6becd3223412d0802d06021939a19a9a5760308f7681d6',
    'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
    'size': 431972422},
   {'digest': 'sha256:35ed20f5cf41686f7bd63f00f84b2338b1b5cce00e03a2927ae4b252ca123ef4',
    'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
    'size': 29495475},
   {'digest': 'sha256:a6fb1b69768eec580fd031f4626afe775ea6f71ac3ab5b372a3a9f9040651d06',
    'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
    'size': 332}],
  'mediaType': 'application/vnd.docker.distribution.manifest.v2+json',
  'schemaVersion': 2,
  'selfLink': 'https://gcr.io/v2/deepvariant-docker/deepvariant/manifests/latest'}
```

At this point, we would use the `layers` key to get a list of layers, and dump
them into the container we are building. But if you previously got a *KeyError* then 
you didn't get this far. You probably got a response of all `None` (`[None,None,None]`).
We need to dig deeper!

## 4. Response of all None
Oh no, you got None for all the queries! Let's modify the loop
slightly to inspect one level deeper. First, define a header lookup table. This
is actually what drives which version we "ask for":

```python
accepts = {'config': "application/vnd.docker.container.image.v1+json",
           'v1': "application/vnd.docker.distribution.manifest.v1+json",
           'v2': "application/vnd.docker.distribution.manifest.v2+json" }
```

We are still going to check each of the schema versions, because different registries
(unfortunately) serve different versions.  We are also going to use the base 
<a href="http://docs.python-requests.org/en/master/" target="_blank">requests</a>
library instead of the sregistry client get function (that parses responses / errors and would handle them for us)

```python
# use requests library
import requests

results = []

# Iterate through schema versions
schemaVersions = ['v1', 'v2', 'config']
for schemaVersion in schemaVersions:

    # The url to send the request to
    url = client._get_manifest_selfLink(repo_name, digest)
    # https://gcr.io/v2/deepvariant-docker/deepvariant/manifests/latest
    
    # Prepare headers from "accept" above
    headers = client.headers.copy()
    headers['Accept'] = accepts[schemaVersion]

    # Here is where an error might trigger, or you get an unexpected response
    manifest = requests.get(url, headers=headers)

    # Append the result for inspection
    results.append(manifest)

```

## 5. Inspect API Responses
Results is a list of response objects. We can inspect each to understand what is going on. 
Our first result was looking for a `schemaVersion` of `v1` which is likely not implemented
for `gcr.io`. We can see from the result that we got a *404*, "not found."

```python
results[0]
<Response [404]>
```

We can re-verify this by looking at the json from this response, it indicates more detail
about the error:

```python
results[0].json()
{'errors': [{'code': 'MANIFEST_UNKNOWN',
   'message': "Manifest with tag 'latest' has media type 'application/vnd.docker.distribution.manifest.v2+json', but client accepts 'application/vnd.docker.distribution.manifest.v1+json'."}]}
```

This is saying "hey, you are only accepting a version 1 manifest, but this manifest is verison 2. This is a really good example of why it's important to

> read the error output in full!

It's telling you what's wrong! So logically, what shoul we do? We should ask for the
version 2 manifest, of course! The `v2` *schemaVersion* request is the next entry
in the list of results:

```python
results[1]
<Response [200]>
```

is a success! 200 indicates all is OK. It follows then, that the `json()` output is
the manifest that we were asking for. If you were getting an error, you probably have a different response code here, and likely a different error message. Look at this
carefully to determine why you aren't getting the manifest. If all is well, you
should see this:

```python
results[1].json()

{'config': {'digest': 'sha256:8178530253d0a434677b7f6e20d45a9c24179fc88a8c24ef37ab89c1ef6754cf',
  'mediaType': 'application/vnd.docker.container.image.v1+json',
  'size': 7602},
 'layers': [{'digest': 'sha256:297061f60c367c17cfd016c97a8cb24f5308db2c913def0f85d7a6848c0a17fa',
   'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
   'size': 43026850},
  {'digest': 'sha256:e9ccef17b516e916aa8abe7817876211000c27150b908bdffcdeeba938cd004c',
   'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
   'size': 850},
  {'digest': 'sha256:dbc33716854d9e2ef2de9769422f498f5320ffa41cb79336e7a88fbb6c3ef844',
   'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
   'size': 621},
  {'digest': 'sha256:8fe36b178d25214195af42254bc7d5d64a269f654ef8801bbeb0b6a70a618353',
   'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
   'size': 851},
  {'digest': 'sha256:686596545a94a0f0bf822e442cfd28fbd8a769f28e5f4018d7c24576dc6c3aac',
   'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
   'size': 169},
  {'digest': 'sha256:85fa0ac43c65aa8973c9b4382fa6a8074519ac9de874dba2bc35b2631742edf3',
   'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
   'size': 1302},
  {'digest': 'sha256:45f2f6ccc5ee24e9a3abb2cce3fecb46ad43c4ea49e35446c148b34a0292e1f6',
   'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
   'size': 173},
  {'digest': 'sha256:3ed22810c25d3ee9fcbd02a3428f04ca49783db74515bd8499c3534321bf8d99',
   'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
   'size': 3843},
  {'digest': 'sha256:0080cefaf4ae6dd2fa6becd3223412d0802d06021939a19a9a5760308f7681d6',
   'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
   'size': 431972422},
  {'digest': 'sha256:35ed20f5cf41686f7bd63f00f84b2338b1b5cce00e03a2927ae4b252ca123ef4',
   'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
   'size': 29495475},
  {'digest': 'sha256:a6fb1b69768eec580fd031f4626afe775ea6f71ac3ab5b372a3a9f9040651d06',
   'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip',
   'size': 332}],
 'mediaType': 'application/vnd.docker.distribution.manifest.v2+json',
 'schemaVersion': 2}
```

The last result in the list is the same as the first, it's a 404 because the manifest
accept header doesn't match what the registry is offering. 

## 6. Another Error?
At this point, either you will get an obvious message returned from the API
(something akin to telling you that you don't have correct permissions for an operation)
or in the case that you don't understand the error and need help, please <a href="https://www.github.com/singularityhub/sregistry-cli/issues" target="_blank">open an issue!</a>


<div>
    <a href="/sregistry-cli/client-docker"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/clients"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
