---
layout: default
title: Singularity Global Client, AWS ECR Client
pdf: true
permalink: /client-aws
toc: false
---

# Singularity Global Client: AWS ECR

These sections will detail use of the [Amazon ECR](https://aws.amazon.com/ecr/) 
(Amazon Elastic Container Registry) client for `sregistry`, 
which is a connection to the Docker registry served by Amazon Web Services. 
Implementation wise, this means that we start with the basic 
[docker](/sregistry-cli/client-docker) client, and tweak it. The tweaks pertain
to slight differences in headers and requests that are done by the AWS client.

## Why would I want to use this?

Singularity proper will be the best solution if you want to pull and otherwise
interact with Docker images. However, the sregistry client can be useful 
to you if you want to easily do this through Python, such as in a script for 
scientific programming.

As with [Docker Hub](/sregistry-cli/client-docker) The images are built from 
layers, and the layers that you obtain depend on the uri that you ask for. 
See the [environment](#environment). setting for more details.

## Getting Started
The AWS Container Registry module uses the [awscli](https://docs.aws.amazon.com/cli/latest/userguide/installing.html) 
python library to help with authentication. 

You can install them both like:

```bash
pip install sregistry[aws]
```

If you want to install each yourself:

```bash
pip install sregistry
pip install awscli
```

The next steps we will take are to first set up authentication and other 
environment variables of interest, and then review the basic usage.

### Credentials

You will need to generate a special token from AWS using your IAM login.  
Importantly, we are going to be using 
[AWS HTTP Authorization](https://docs.aws.amazon.com/AmazonECR/latest/userguide/Registries.html#registry_auth_http), and this means to get your `$AWS_TOKEN` you will need to 
[install the AWS Client](https://docs.aws.amazon.com/cli/latest/userguide/installing.html) 
that we mentioned previously first.

#### Configuration

If this is the first time you are using it, you will need to configure regions and whatnot.

```bash
aws configure
```

These **will not exist** until you run the aws configure, and when you run aws configure
you will need to give it some access keys for a specific IAM user. Let's walk through
how to generate this user.

**Aws Access Key ID and Secret**

I was able to get to IAM at [this link](https://console.aws.amazon.com/iam/home#/home). I then
had to click on the tab to "Create individual IAM users" and then the button to 
"Manage Users" and then "Add User" to create a new user with Programmatic access.

![/sregistry-cli/img/aws-add-user.png](/sregistry-cli/img/aws-add-user.png)


You need to add your user to a group, and select permissions. I chose `AmazonEC2ContainerRegistryFullAccess`
and `AmazonEC2ContainerServiceFullAccess` because I wasn't really sure what to choose, but generally
wanted all the things! You could very likely create different users with different permissions depending
on your use case.

Once you get this, THEN the next screen will give you an "Access Key ID" 
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
and when you finish, you should have files in your $HOME. The process
is writing some credentials to a `$HOME/.aws` folder.
By the end of this process you will likely have two files:

```bash
$ tree /home/vanessa/.aws/
/home/vanessa/.aws/
├── config
└── credentials
```

You can see more details about the various 
[options here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html)

### Testing Credentials

It's important to test your credentials before trying to use them with sregistry.
The reason is that a permissions (or related error) should be caught here first.

You should now have enough to generate the token for the client from the
command line:

```bash
AWS_TOKEN=$(aws ecr get-authorization-token --output text --query 'authorizationData[].authorizationToken')
```

To get your registry url, I wasn't sure how to do this either, so I used their 
docker login command and it shows up as the last item in the call:

```bash
aws ecr get-login --no-include-email
...
https://692517157806.dkr.ecr.us-east-1.amazonaws.com
```
so I set this to a variable too:

```bash
AWS_URL=https://692517157806.dkr.ecr.us-east-1.amazonaws.com
```

#### Interaction with Repositories

Before trying to use your credentials with the Singularity Registry client, 
let's make sure they work! If you selected some kind of different permissions, 
or otherwise messed something up (hey, it happens!) this command might fail. 
We would want to identify this is about the setup and not the client itself. 
This command to list your registries should work.

First, here is a command to test with their client. This likely will return 
an empty list if you just created the account and its registry:

```bash
aws --debug ecr describe-repositories
```

Next, here is a curl command to use the token (`AWS_token`) and url we derived (`AWS_URL`)
to ping your endpoint. Since the token expires fairly quickly, I'm going to keep
placing the command beside the action we want to do to ensure you copy paste both 
and get a new token :)

```bash
AWS_TOKEN=$(aws ecr get-authorization-token --output text --query 'authorizationData[].authorizationToken')
curl -i -H "Authorization: Basic $AWS_TOKEN" ${AWS_URL}/v2/
```

If all goes well, you should get a 200 response!

```bash
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
Date: Tue, 25 Sep 2018 13:01:11 GMT
Docker-Distribution-Api-Version: registry/2.0
Content-Length: 0
Connection: keep-alive
```

#### Create a repository

This is pretty annoying, but you have to manually 
[create a repository](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-create.html) 
otherwise you see:

```bash
name unknown: The repository with name 'library/busybox' does not exist in the registry with id '692517157806'
```

Yeah, really. Ug. I went to [the repository base page](https://console.aws.amazon.com/ecs/) and 
then created a repository called "library/busybox". The login (if you haven't
done it yet) looks like this:

```bash
$(aws ecr get-login --no-include-email --region us-east-1)
```

#### Push a container

Now that we've tested the registry endpoint and confirmed we can access it, 
let's push a container! How about a tiny one? Yes that sounds good.

```bash
docker pull busybox:latest
docker images | grep busybox
```

and push! You can tag it something else first if you like. Note the first command
is removing the `https://`

```bash
AWS_REPO=$(echo $AWS_URL |sed 's/https\?:\/\///')
docker tag busybox:latest ${AWS_REPO}/library/busybox
$(aws ecr get-login --no-include-email --region us-east-1)
...
Login Succeeded
```
Note that if you don't have the `--no-include-email` it's going to give you a hanging `-e` that 
will trigger a bug.

```
AWS_TOKEN=$(aws ecr get-authorization-token --output text --query 'authorizationData[].authorizationToken')
docker push ${AWS_REPO}/library/busybox
f9d9e4e6e2f0: Pushed 
latest: digest: sha256:5e8e0509e829bb8f990249135a36e81a3ecbe94294e7a185cc14616e5fad96bd size: 527
```
You should then be able to pull with

```bash
docker pull ${AWS_REPO}/library/busybox
```
It took me almost an hour to get this complete thing working. Not going to comment further on that.


#### Test with CURL

Now we would want to test pinging our repository with curl. This entire shenanigans should work.

```bash
AWS_TOKEN=$(aws ecr get-authorization-token --output text --query 'authorizationData[].authorizationToken')
curl -i -H "Authorization: Basic $AWS_TOKEN" $AWS_URL/v2/library/busybox/tags/list
```
```bash
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
Date: Tue, 25 Sep 2018 13:51:09 GMT
Docker-Distribution-Api-Version: registry/2.0
Content-Length: 44
Connection: keep-alive

{"name":"library/busybox","tags":["latest"]}
```

## sregistry Pull
You've made it! Now that we have confirmed the endpoint is working, and our container exists
there we can talk about interaction with it via sregistry. Let's first
export some of the variables we discussed above, in the format that the sregistry 
client will find them. Don't worry - you only need to do this once and never again.

The first thing we need is the ID of your registry. It's the "number part"
of the long URL that we looked at earlier, and it was a part of the `$AWS_REPO` 
variable that we used above. We can derive just the id (the numbers) from that. 
We also need to know the zone your registry is in:

```bash
export SREGISTRY_AWS_ID=$(echo $AWS_REPO | cut -d. -f1)
export SREGISTRY_AWS_ZONE=us-east-1
```

The key and secret are used for authentication, and you derived them above.

```bash
export SREGISTRY_AWS_KEY=xxxxxxxxxxx
export SREGISTRY_AWS_SECRET=xxxxxxxxxxxxxxxxx
```

You'll only need to do this once, the first time that you use the client.

### Python Client

Now let's try pulling our image! First we will work within python.
Note that I'm specifying the `aws://` uri to tell the client what I want.
If I wanted to do this globally, I would do this before any kind of pull
or interaction with the client. For example, here is doing this via
a shell:

```bash
export SREGISTRY_CLIENT=aws 
$ sregistry shell
[client|aws] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
```
```python
Python 3.6.4 |Anaconda custom (64-bit)| (default, Jan 16 2018, 18:10:19) 
Type 'copyright', 'credits' or 'license' for more information
IPython 6.2.1 -- An enhanced Interactive Python. Type '?' for help.

$ image = client.pull('library/busybox')
Exploding /usr/local/libexec/singularity/bootstrap-scripts/environment.tar
Exploding /home/vanessa/.singularity/docker/sha256:8c5a7da1afbc602695fcb2cd6445743cec5ff32053ea589ea9bd8773b7068185.tar.gz
[container][new] library/busybox:latest
Success! /home/vanessa/.singularity/shub/library-busybox:latest.simg
```

### Command Line

You can also pull from the command line. Here I'll show unsetting the `SREGISTRY_CLIENT`
environment variable so you can see how to use the `aws://` uri, and also
how to not cache the image (and pull to the present working directory with a
custom name).

```bash
$ unset SREGISTRY_CLIENT
$ sregistry pull --name aws-is-hard.simg --no-cache aws://library/busybox
```
```bash
$ sregistry pull --name aws-is-hard.simg --no-cache aws://library/busybox
[client|aws] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Exploding /usr/local/libexec/singularity/bootstrap-scripts/environment.tar
Exploding /home/vanessa/.singularity/docker/sha256:8c5a7da1afbc602695fcb2cd6445743cec5ff32053ea589ea9bd8773b7068185.tar.gz
Building image from sandbox: /tmp/tmpl_zzhuba
Building Singularity image...
Singularity container built: aws-is-hard.simg
Cleaning up...
WARNING: Building container as an unprivileged user. If you run this container as root
WARNING: it may be missing some functionality.
WARNING: Building container as an unprivileged user. If you run this container as root
WARNING: it may be missing some functionality.
Success! aws-is-hard.simg
```

Importantly, does it work?

```bash
$ singularity shell aws-is-hard.simg 
Singularity: Invoking an interactive shell within container...

Singularity> 
```

Yes! Oh thank goodness.

<div>
    <a href="/sregistry-cli/client-nvidia"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-ceph"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
