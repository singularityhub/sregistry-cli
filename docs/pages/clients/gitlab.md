---
layout: default
title: GitLab Client
pdf: true
permalink: /client-gitlab
---


# Singularity Global Client: GitLab

These sections will detail use of the GitLab client for `sregistry`. GitLab makes
it easy to build containers directly from GitLab repositories 
([here is an example](https://gitlab.com/singularityhub/gitlab-ci/) we have put 
together for you) and so the intended use case is to use GitLab for version
control and building, and then pull the artifacts using this client. Let's get started!


## Getting Started
GitLab doesn't have any additional dependencies.


```bash
pip install sregistry
```

To make the GitLab client default, set `SREGISTRY_CLIENT` to `gitlab`, either 
for individual commands or exported globally:

```bash
# Globally
SREGISTRY_CLIENT=gitlab
export SREGISTRY_CLIENT

# Single Command
SREGISTRY_CLIENT=gitlab sregistry shell

# Examples of setting via uri://
sregistry shell gitlab
sregistry search gitlab://
sregistry pull gitlab://vanessa/tacos
```

or do away the need to export this environment variable by simply activating the client:

```bash
$ sregistry backend activate gitlab
[activate] gitlab
$ sregistry backend status
[backend status]
There are 9 clients found in secrets.
active: gitlab
```

### What repository can build containers?

You will need to create a repository on [GitLab.com](https://gitlab.com) or your
institutions GitLab instance, and in this repository you will need a file called `.gitlab-ci.yml`
that defines the jobs to run to build your container. To make this easy for you, we have
a template at [https://gitlab.com/singularityhub/gitlab-ci/](https://gitlab.com/singularityhub/gitlab-ci/)
that you can use. See the instructions in the README.md for details about the configuration.

### What is a container URI?
Since we are using GitLab repositories, it follows naturally that we will use the GitLab
namespace and conventions. There are a few important components that you will need to know
to pull containers:

  - **collection uri** is the GitLab repository name. For example, for the repository [https://gitlab.com/singularityhub/gitlab-ci/](https://gitlab.com/singularityhub/gitlab-ci/) we would say the collection uri is "singularityhub/gitlab-ci."
  - **job_name** In your [.gitlab-ci.yml](https://gitlab.com/singularityhub/gitlab-ci/blob/master/.gitlab-ci.yml) you have different sections that correspond with jobs. Here, let's look at one:

```yaml
build:
  script:
     - /bin/bash .gitlabci/build.sh Singularity
```

The above would be for a job named "build." You will need to know this for interaction
with the client **only** if you change the name of the job that uploads the artifacts. If you 
leave it named as build, as you will see later, the client defaults to using this name (so you
don't need to do anything).

  - **job_id**: is a number that is associated with the particular job. You can get this using the sregistry tool, and we will show this below.
  - **tag**: The tag for the container, [akin to Singularity Hub](https://github.com/singularityhub/singularityhub.github.io/wiki/Build-A-Container#naming-recipes), is represented in the recipe name in your repository. a recipe called "Singularity" corresponds to the tag "latest," while a file in the format "Singularity.thetag.simg corresponds to tag "thetag."

### How are the images saved?

If you follow the [example shared above](https://gitlab.com/singularityhub/gitlab-ci/) you will
see that containers are saved according to the recipe file. This means that the "Singularity.goober"
produces a container called "Singularity.goober.simg" and the client will download this
as "singularityhub-gitlab-ci-goober.simg". The file "Singularity" is the only special case
that is understood to be latest, meaning that a file named "Singularity" will produce a container
with tag "latest" You are also free to not use this tool at all, and download container files 
as GitLab artifacts with whatever naming convention [suits you](https://docs.gitlab.com/ee/user/project/pipelines/job_artifacts.html#downloading-artifacts).

In summary, in this example we will:

 1. export environment variables for our GitLab setup
 2. use sregistry search to identify a job_id of interest
 3. use sregistry pull to pull an artifact of interest.


## Environment

The single required environmental variable for you to export is your GitLab
private token to use the API. The instructions to generate one can be found 
[here](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html). You should
export this to the environment for sregistry to find:

```bash
export SREGISTRY_GITLAB_TOKEN=xxxxxxxxxxxxxxxx
```

![/sregistry-cli/img/gitlab-token.png](/sregistry-cli/img/gitlab-token.png)

You can also choose to create an [impersonation token](https://docs.gitlab.com/ee/api/README.html#impersonation-tokens)
if you want to authenticate as a specific user. Generally, the intended use case for a personal
access token is for a single person and not to be shared with multiple users.

GitLab also has a few settings that you might want to export before your first use of the client,
especially in the case that you have a "non standard" host:

| Variable Name | Description |Default |
| --------------|-------------|-------|
| SREGISTRY_GITLAB_BASE | The URL where the GitLab instance is hosted | https://gitlab.com | 
| SREGISTRY_GITLAB_JOB | The name of the job that built the containers | test |
| SREGISTRY_GITLAB_FOLDER | The folder name where the artifactsare stored |build |

 - The `SREGISTRY_GITLAB_BASE` is where your GitLab is hosted, and it defaults to "https://gitlab.com"
if you don't set it (likely the case for most).
 - The `SREGISTRY_GITLAB_JOB` is the name of the job that performed the build and saved artifacts. The recipe template names the job "build," and so you only need to export this value if you change this name.
 - The `SREGISTRY_GITLAB_FOLDER` is the folder where you are storing your artifacts. The example we provide saves them also to a folder called build, so only change this value if you've edited the configuration to save somewhere else.

## Commands

The Singularity Registry GitLab client provides the following commands 

 - [pull](#pull): `[remote->local]` pull layers from Docker Hub to build a Singularity images, and save in storage.
 - [search](#search): `[remote]` search your personal Dropbox for a container

You'll notice that there isn't a push, and this is because you are expected to build
using GitLab's built in continuous integration (CI) directly from a repository. For a detailed 
list of other (default) environment variables and settings that you can configure, see the [getting started](sregistry-cli/getting-started) pages and the [commands documentation](/sregistry-cli/commands) for shared commands
across all clients.

For all of the examples below, we will export our client preference to be `gitlab`

```bash
SREGISTRY_CLIENT=gitlab
export SREGISTRY_CLIENT
```

but note that you could just as easily define the variable for one command:

```
SREGISTRY_CLIENT=gitlab sregistry shell
```

A good test for viewing the client is to use shell, as above, and confirm that you see `[client|gitlab]`

```
sregistry shell
[client|gitlab] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
```

## Search
Let's start in your likely scenario. You've just used the [singularityhub/gitlab-ci](https://gitlab.com/singularityhub/gitlab-ci/) template to build a container artifact, and the build was successful (green!) You
now want to pull the container to your local machine, but you need to find it. You need the job id!
Let's use the job id to see what artifacts are available.

```bash
export SREGISTRY_CLIENT=gitlab
sregistry search singularityhub/gitlab-ci

[client|gitlab] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Artifact Browsers (you will need path and job id for pull)
1  job_id	browser
2  122093393	https://gitlab.com/singularityhub/gitlab-ci/-/jobs/122093393/artifacts/browse/build
3  122059246	https://gitlab.com/singularityhub/gitlab-ci/-/jobs/122059246/artifacts/browse/build
```

What you see above is the job id, followed by a url where you can browse the artifacts
and figure out the file you want to pull.

> Why can't you list these for me?

The GitLab API doens't yet have an endpoint to list artifacts, and the need 
has been expressed [in this issue](https://gitlab.com/gitlab-org/gitlab-ce/issues/51515)
The most that we could do is to provide an indication of if some artifact exists (or not)
but I didn't find this helpful given that you need to ask for a specific image tag. Thus,
for the time being I'm providing you with the URL to go to in order to browse storage.
Currently, this will return all job_ids. If you find this list is too long (and only want
the latest returned) please [open an issue](https://www.github.com/singularityhub/sregistry-cli/issues)
and this can be added for you. 

Okay, to continue! Let's find the container we want to pull. Here is what I see at the
second of the two URLs:

![/sregistry-cli/img/gitlab-browser.png](/sregistry-cli/img/gitlab-browser.png)

We can see two files - the recipe (Singularity) and the image built from it (Singularity.simg).
This saving of both is also done by the example template, in the case that the image becomes
corrupt and you cannot retrieve the recipe it keeps inside. We are mainly interested in the
image itself, the file "Singularity.simg" is indicative of a tag "latest." Did you also notice
in the url that it ends with `/browse/build` ? The build here is in reference to the artifacts
folder. The client (and template example) use build as a default, but you are free to change this.

## Pull

We just have successfully found the job id, and container desired, for our build. Let's pull it!
This pull command is different from the typical Singularity Registry client because it needs these
additional parameters. You should provide them in a simple format of the values separated by `|`
You can provide either of the following - if you don't specify the job name (the final parameter)
it will default to what you've exported as `SREGISTRY_GITLAB_JOB` or "build"

```bash
job_id|collection
job_id|collection|job_name
```

To demonstrate, try pulling the container by just the collection uri.

```bash
[client|gitlab] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
ERROR Malformed image string! Please provide:
                        job_id,collection           (or)
                        job_id,collection,job_name
```

Let's try again! For the container above, it would look like either of the following:

```bash
sregistry pull 122059246,singularityhub/gitlab-ci
sregistry pull 122059246,singularityhub/gitlab-ci,build
```
```bash
$ sregistry pull 122059246,singularityhub/gitlab-ci[client|gitlab] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Looking for artifact build/Singularity.simg for job name build, 122059246
https://gitlab.com/singularityhub/gitlab-ci/-/jobs/122059246/artifacts/raw/build/Singularity.simg/?inline=false
Progress |===================================| 100.0% 
[container][new] 122059246,singularityhub/gitlab-ci-latest
Success! /home/vanessa/.singularity/shub/122059246,singularityhub-gitlab-ci-latest.simg
```

There you go! Did we pull the container to our local storage?

```bash
$ sregistry images | grep gitlab
7  November 19, 2018	   [gitlab]	122059246,singularityhub/gitlab-ci:latest@ccfbb8f2a0f4262d14966d7d3b7925bb
```

Notice that we keep the job id with the uri. This is because you would not be able to identify this
container without it. Also notice that we have an image hash (the version string) so we can identify the file.
For example, here is how to ask for the container from the sregistry client:

```bash
$ echo $(sregistry get 122059246,singularityhub/gitlab-ci)
/home/vanessa/.singularity/shub/122059246,singularityhub-gitlab-ci-latest.simg
```

Did the pull work?

```bash
$ singularity run $(sregistry get 122059246,singularityhub/gitlab-ci)
Polo !
```
Apparently this container is looking for a long lost Marco?


## Inspect
Finally, notice that the GitLab client will store the set of metadata needed to reproduce
the pull.

```bash
sregistry inspect 122059246,singularityhub/gitlab-ci
/home/vanessa/.singularity/shub/122059246,singularityhub-gitlab-ci-latest.simg
{
    "client": "gitlab",
    "collection": "122059246,singularityhub",
    "collection_id": 10,
    "created_at": "2018-11-19 18:09:36",
    "id": 7,
    "image": "/home/vanessa/.singularity/shub/122059246,singularityhub-gitlab-ci-latest.simg",
    "metrics": {
        "collection": "122059246,singularityhub",
        "data": {
            "attributes": {
                "deffile": "Bootstrap: docker\nFrom: ubuntu:16.04\n\n%runscript\n    exec echo \"Polo $@!\"\n",
                "environment": "# Custom environment shell code should follow\n\n",
                "help": null,
                "labels": {
                    "org.label-schema.build-date": "Sun,_18_Nov_2018_18:54:45_+0000",
                    "org.label-schema.build-size": "166MB",
                    "org.label-schema.schema-version": "1.0",
                    "org.label-schema.usage.singularity.deffile": "Singularity",
                    "org.label-schema.usage.singularity.deffile.bootstrap": "docker",
                    "org.label-schema.usage.singularity.deffile.from": "ubuntu:16.04",
                    "org.label-schema.usage.singularity.version": "2.5.2-vault/release-2.5.b258b651"
                },
                "runscript": "#!/bin/sh \n\n    exec echo \"Polo $@!\"\n",
                "test": null
            },
            "type": "container"
        },
        "image": "gitlab-ci",
        "storage": "122059246,singularityhub/gitlab-ci-latest.simg",
        "tag": "latest",
        "uri": "122059246,singularityhub/gitlab-ci-latest",
        "url": "122059246,singularityhub/gitlab-ci",
        "version": null
    },
    "name": "gitlab-ci",
    "tag": "latest",
    "uri": "122059246,singularityhub/gitlab-ci-latest",
    "url": "https://gitlab.com/singularityhub/gitlab-ci/-/jobs/122059246/artifacts/raw/build/Singularity.simg/?inline=false",
    "version": "ccfbb8f2a0f4262d14966d7d3b7925bb"
}

```

At the bottom you even have the download URL!

## Contributing
Do you want to contribute another template, have a question, or want to poke the maintainer
when the GitLab API is updated to list artifacts? Please [post an issue](https://www.github.com/singularityhub/sregistry-cli/issues).

<div>
    <a href="/sregistry-cli/client-docker"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-google-storage"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
