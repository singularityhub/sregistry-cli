---
layout: default
title: Singularity Global Client, AWS ECR Client
pdf: true
permalink: /client-aws
toc: false
---

# Singularity Global Client: AWS ECR

These sections will detail use of the AWS Container Cloud client for `sregistry`, which is a connection to the Docker registry served by Amazon Web Services. Implementation wise, this means that we start with the basic [docker](/sregistry-cli/client-docker) client, and tweak it.

## Why would I want to use this?
Singularity proper will be the best solution if you want to pull and otherwise interact with Docker images. However, the sregistry
client can be useful to you if you want to easily do this through Python, such as in a script for scientific programming.

As with [Docker Hub](/sregistry-cli/client-docker) The images are built from layers, and the layers that you obtain depend on the uri that you ask for. See the [environment](#environment). setting for more details.

## Getting Started
The AWS Container Registry module does not require any extra dependencies other 
than having Singularity on the host.

To get started, you simply need to install the `sregistry` client:

```bash
pip install sregistry

# or from source
git clone https://www.github.com/singularityhub/sregistry-cli.git
cd sregistry-cli 
python setup.py install
```

The next steps we will take are to first set up authentication and other 
environment variables of interest, and then review the basic usage.

### Credentials
You will need to generate a special token from AWS using your IAM login.  Importantly,
we are going to be using [AWS HTTP Authorization](https://docs.aws.amazon.com/AmazonECR/latest/userguide/Registries.html#registry_auth_http), and this means to get your `$AWS_TOKEN` you will need to 
[install the AWS Client](https://docs.aws.amazon.com/cli/latest/userguide/installing.html) first.

```bash
pip install awscli
```

If this is the first time you are using it, you will need to configure regions and whatnot.

```bash
aws configure
```

**Aws Access Key ID and Secret**

I was able to get to IAM at [this link](https://console.aws.amazon.com/iam/home#/home). I then
had to click on the tab to "Create individual IAM users" and then the button to 
"Manage Users" and then "Add User" to create a new user with Programmatic access.

![/sregistry-cli/img/aws-add-user.png](/sregistry-cli/img/aws-add-user.png)


You need to add your user to a group, and select permissions. I chose `AmazonEC2ContainerRegistryFullAccess`
because I wanted all the things! Once you get this, THEN the next screen will give you an "Access Key ID" 
and secret token, and these are exactly what you want to copy paste into this first field asked for by `aws configure`.
You can also choose a default zone. I chose the one that showed up as default in my Manager Console.

**Default Output Format**

I chose json, since I knew I'd be interacting with Python and Json. The whole thing is going to look
something like:

```bash
$ aws configure
AWS Access Key ID [None]: XXXXXXXXXXXXXXXX
AWS Secret Access Key [None]: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
Default region name [None]: us-east-1
Default output format [None]: json
```

You can see more details about the various [options here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html)

Now, you should have enough to generate the token for the client!

```bash
AWS_TOKEN=$(aws ecr get-authorization-token --output text --query 'authorizationData[].authorizationToken')
```

### Test Credentials
Before trying to use your credentials with the Singularity Registry client, let's make sure they work! If you
selected some kind of different permissions, or otherwise messed something up (hey, it happens!) this
command might fail. We would want to identify this is about the setup and not the client itself.

```bash
curl -i -H "Authorization: Basic $AWS_TOKEN" https://012345678910.dkr.ecr.us-east-1.amazonaws.com/v2/amazonlinux/tags/list
```

** This doesn't work yet**


<div>
    <a href="/sregistry-cli/client-nvidia"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-hub"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
