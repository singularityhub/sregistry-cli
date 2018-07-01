---
layout: default
title: Singularity Google Debugging
pdf: true
permalink: /client-google-debugging
toc: false
---

# Cannot get or create group
If you see this error:

```bash

SREGISTRY_CLIENT=google-compute sregistry shell
...
ERROR Cannot get or create gbsc-gcp-lab-priest-group

```

## Why might this happen?
If you get this error, it's likely that you don't have the correct permission
to create a storage bucket, or to access one that exists. To get to the bottom
of the error, we will walk through the commands to trigger (and not catch 
it with the message above.) 

## Step 1: export needed variables
First, make sure that you have all these environment
variables exported:


```bash
export GOOGLE_CLOUD_PROJECT="..."
export GOOGLE_APPLICATION_CREDENTIALS="..."

# You need to have storage admin permissions on this project
export SREGISTRY_GOOGLE_PROJECT="..."
export SREGISTRY_GOOGLE_STORAGE_BUCKET="..."
export SREGISTRY_CLIENT=google-compute
```

## Step 2: Open a Python shell
Now you can open up a python shell. I prefer ipython because of the colors
and autocompletion :) If you have sregistry installed, you will have these dependencies

```python
from googleapiclient.discovery import build as discovery_build
from oauth2client.client import GoogleCredentials
from google.cloud import storage
import os

bucket_name = os.environ['SREGISTRY_GOOGLE_STORAGE_BUCKET']

# This is a client for storage, and our credentials from the environment
creds = GoogleCredentials.get_application_default()
```

Above we have imported needed modules, and we grab our `GOOGLE_APPLICATION_CREDENTIALS`
and read into `creds`. As a reminder, these are the 
<a href="https://cloud.google.com/video-intelligence/docs/common/auth#authenticating_with_application_default_credentials" target="_blank">Default Application Credentials</a> that you download from the web interface, a json file.

## Step 3. Create clients
Now we want to create handles for interactions with storage and compute. Creating
these all here isn't totally necessary, but in the case that some error triggers,
let's do it anyway to see that. I actually think this step doesn't interact with
the API, so you shouldn't seen an unless one of Google's "sanity checks" doesn't 
pass.

```python
# We are initializing the last two just to make sure no errors trigger
bucket_service = storage.Client()
storage_service = discovery_build('storage', 'v1', credentials=creds)
compute_service = discovery_build('compute', 'v1', credentials=creds) 
```

## Step 4. Trigger the error
Here is where the error is going to trigger.

```python
bucket = bucket_service.get_bucket(bucket_name)

# When I run this command (with correct permissions, and an existing bucket)
# I get back a bucket
# bucket
# <Bucket: sregistry-vanessa>
```
Either you will get an obvious message
(something akin to telling you that you don't have correct permissions for an operation)
or in the case that you don't understand the error and need help, please <a href="https://www.github.com/singularityhub/sregistry-cli/issues" target="_blank">open an issue!</a>

<div>
    <a href="/sregistry-cli/client-google-compute"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-google-storage"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
