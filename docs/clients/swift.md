---
layout: default
title: Singularity Global Client, Swift Client
pdf: true
permalink: /client-swift
toc: false
---

# Singularity Global Client: Swift

To use a storage that is interacted with via Swift you can use a [Ceph Storage Cluster](http://docs.ceph.com/docs/jewel/start/intro/)
which is typically provided by your institution. If you don't and want to use the client,
see the [development](#development) section at the bottom to see how to deploy a testing
storage.

## Why would I want to use this?

This solution is ideal if you want to use the Swift client to interact with storage for your containers.
We hope to (after developing this endpoint) integrate this functionality with the
Singularity Registry Server so that multiple uses of a Registry can share this
object storage for their containers.

## Getting Started
The Swift Storage module uses the [swiftclient](http://docs.ceph.com/docs/mimic/radosgw/swift/python/) 
python library to interact with the storage. For those not familiar with swift (I was not)
it's a [multi-cloud platform management tool](https://www.swiftstack.com/). Cool!

You can install them both like:

```bash
pip install sregistry[swift]
```

If you want to install each yourself:

```bash
pip install sregistry
pip install python-swiftclient
```

The next steps we will take are to first set up authentication and other 
environment variables of interest, and then review the basic usage.

### Credentials

In our example with Ceph, to authenticate with a Ceph Storage endpoint, you will need a username and token.
In generating the demo, I was able to create a swift user for myself as follows:

```bash
docker exec demo radosgw-admin user create --subuser="ceph:vanessa" --uid="vanessa" --display-name="Vanessa Saurus" --key-type=swift --access=full
```
```bash
{
    "user_id": "ceph",
    "display_name": "Vanessa Saurus",
    "email": "",
    "suspended": 0,
    "max_buckets": 1000,
    "auid": 0,
    "subusers": [
        {
            "id": "ceph:vanessa",
            "permissions": "full-control"
        }
    ],
    "keys": [],
    "swift_keys": [
        {
            "user": "ceph:vanessa",
            "secret_key": "gpBCS9JtiADQPz5C35yVNd05ItrjXtryZI8aJEdn"
        }
    ],
    "caps": [],
    "op_mask": "read, write, delete",
    "default_placement": "",
    "placement_tags": [],
    "bucket_quota": {
        "enabled": false,
        "check_on_raw": false,
        "max_size": -1,
        "max_size_kb": 0,
        "max_objects": -1
    },
    "user_quota": {
        "enabled": false,
        "check_on_raw": false,
        "max_size": -1,
        "max_size_kb": 0,
        "max_objects": -1
    },
    "temp_url_keys": [],
    "type": "rgw",
    "mfa_ids": []
}
```

Note that we are getting the credentials under "ceph keys." If you are using
the `ceph/daemon` container, the "demo" user credentials will not work because they
lack this section. For more information, the authentication documentation for 
swift [is here](http://docs.ceph.com/docs/master/radosgw/swift/auth/). If you
are an administrator of a Ceph Storage and aren't familiar with the various roles
and permissions, it would be wise to figure this out before opening up access.

Now that we have a username (`ceph:vanessa`) and corresponding swift token, let's
export it for sregistry client to find. Note that you just need to do this once.

```bash
export SREGISTRY_SWIFT_USER=ceph:vanessa
export SREGISTRY_SWIFT_TOKEN=gpBCS9JtiADQPz5C35yVNd05ItrjXtryZI8aJEdn
export SREGISTRY_SWIFT_URL=http://172.17.0.1:8080
```

For example, for my storage I am going to `http://172.17.0.1:5000` and for the
rest API (needed for this client) I am going to `http://172.17.0.1:8080`. This
means that I would export `http://172.17.0.1:8080` as the endpoint for the API.
The port must be included too because most setups will have either a different port
or a proxy that hides it entirely.


## sregistry push
We've just exported our environment variables for our Ceph Storage, now let's
try pushing a container there! The root of storage has a listing of
(drumroll) things that are *also* called containers. From what I can tell,
a container here is akin to a bucket, meaning that we can use different storage
containers to manage permissions, and within each container we can store a set
of (linux) containers. What does this mean? For a container called `ubuntu.simg`
in (what Singularity Hub calls a collection) `my-collection` we would find the
file `ubuntu.simg` in the "container" (collection) `my-collection`.

First, export the client to use

```bash
export SREGISTRY_CLIENT=swift
```

```bash
$ sregistry push --name yippy/yuppy ubuntu.simg
[client|swift] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Creating collection yippy...
Progress |===================================| 100.0% 
```

### Python Client

Let's now do the same pull, but using the Python shell.

```bash
export SREGISTRY_CLIENT=swift
$ sregistry shell
[client|swift] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Python 3.6.4 |Anaconda custom (64-bit)| (default, Jan 16 2018, 18:10:19) 
Type 'copyright', 'credits' or 'license' for more information
IPython 6.2.1 -- An enhanced Interactive Python. Type '?' for help.

$ client.push('aws-is-hard.simg','collection/container')
Creating collection collection...
Progress |===================================| 100.0% 
```


### Command Line

You can also pull from the command line. Here I'll show unsetting the `SREGISTRY_CLIENT`
environment variable so you can see how to use the `swift://` uri.

```bash
$ unset SREGISTRY_CLIENT
$ sregistry pull --name blueberry.simg --no-cache swift://library/busybox
```

## sregistry search

Now that we've pushed, let's search! First, from the command line:

```bash
[client|swift] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Collections
1  yippy/yuppy-latest.simg
2  blueberry/pancake-latest.simg
3  collection/container-latest.simg
```

And from within Python

```python
sregistry shell
$ sregistry shell
[client|swift] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Python 3.6.4 |Anaconda custom (64-bit)| (default, Jan 16 2018, 18:10:19) 
Type 'copyright', 'credits' or 'license' for more information
IPython 6.2.1 -- An enhanced Interactive Python. Type '?' for help.

> client.search()
['collection/container-latest.simg',
 'yippy/yuppy-latest.simg',
 'blueberry/pancake-latest.simg']
```
```python
> client.search('blueberry')
['blueberry/pancake-latest.simg']
```

## sregistry pull

You can then pull a container of interest. Make sure to specify the URI.

```bash
$ sregistry pull --name breakfast.simg blueberry/pancake:latest
```

# Development

To develop locally we need a Ceph Storage Server running. This is no small feat!
I figured out how to do this with Docker based on [this container](http://www.sebastien-han.fr/blog/2017/06/27/New-Ceph-container-demo-is-super-dope/), 
and for the full discourse please see [this Github issue](https://github.com/singularityhub/sregistry-cli/issues/160). I'll outline the steps quickly here.

## Step 1. Docker Ip Address

We need to run a docker command to deploy ceph, and specifically we need to 
specify the address of a local network. Which one? You can use `ifconfig` to 
find the `docker0` network address. Mine looks like this:

```bash
docker0   Link encap:Ethernet  HWaddr 02:42:52:32:97:63  
          inet addr:172.17.0.1  Bcast:172.17.255.255  Mask:255.255.0.0
          inet6 addr: fe80::42:52ff:fe32:9763/64 Scope:Link
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:340 errors:0 dropped:0 overruns:0 frame:0
          TX packets:3270 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0 
          RX bytes:1185211 (1.1 MB)  TX bytes:739874 (739.8 KB)
```

The address of interest above is `172.17.0.1`. If you are more experienced with
docker you can also create a new network space to use.

## Step 2. Start Container
For the command, it's actually not going to work to bind some local config directory (`/etc/ceph` in the
example that I linked above) so we need to drop that. It also doesn't work to give some storage bucket 
(it will give you a bucket 404 error in the logs and the container will die). I only figured this
out by removing these components to the command and hoping that a default would take over, or some
generation skipped. It worked! Here is the command. Notice that I am naming my container `demo`
and providing the docker0 hostname:

```bash
docker run -d \
--name demo \
-e MON_IP=172.17.0.1 \
-e CEPH_NETWORK=172.17.0.1/24 \
-e CEPH_PUBLIC_NETWORK=172.17.0.1/24 \
--net=host \
-v /var/lib/ceph:/var/lib/ceph \
-e CEPH_DEMO_UID=qqq \
-e CEPH_DEMO_ACCESS_KEY=qqq \
-e CEPH_DEMO_SECRET_KEY=qqq \
ceph/daemon \
demo
```

Note that the instructions have an environment variable for storage, and I believe this
is there only given that you bind a config that has had some storage created previously.
It's best to remove this variable and not bind `/etc/ceph`.

## Step 3. Inspect Container

To see what is going on, you can use `docker inspect demo` and `docker logs demo`, to show the above. The final working thing looks like:

```
$ docker logs demo
creating /etc/ceph/ceph.client.admin.keyring
creating /etc/ceph/ceph.mon.keyring
creating /var/lib/ceph/bootstrap-osd/ceph.keyring
creating /var/lib/ceph/bootstrap-mds/ceph.keyring
creating /var/lib/ceph/bootstrap-rgw/ceph.keyring
creating /var/lib/ceph/bootstrap-rbd/ceph.keyring
monmaptool: monmap file /etc/ceph/monmap-ceph
monmaptool: set fsid to 98701fa9-537f-423b-88dd-68c199ace14c
monmaptool: writing epoch 0 to /etc/ceph/monmap-ceph (1 monitors)
importing contents of /var/lib/ceph/bootstrap-osd/ceph.keyring into /etc/ceph/ceph.mon.keyring
importing contents of /var/lib/ceph/bootstrap-mds/ceph.keyring into /etc/ceph/ceph.mon.keyring
importing contents of /var/lib/ceph/bootstrap-rgw/ceph.keyring into /etc/ceph/ceph.mon.keyring
importing contents of /var/lib/ceph/bootstrap-rbd/ceph.keyring into /etc/ceph/ceph.mon.keyring
importing contents of /etc/ceph/ceph.client.admin.keyring into /etc/ceph/ceph.mon.keyring
changed ownership of '/etc/ceph/ceph.client.admin.keyring' from root:root to ceph:ceph
changed ownership of '/etc/ceph/ceph.conf' from root:root to ceph:ceph
ownership of '/etc/ceph/ceph.mon.keyring' retained as ceph:ceph
changed ownership of '/etc/ceph/rbdmap' from root:root to ceph:ceph
changed ownership of '/var/lib/ceph/mgr/ceph-vanessa-ThinkPad-T460s/keyring' from root:root to ceph:ceph
ownership of '/var/lib/ceph/mgr/ceph-vanessa-ThinkPad-T460s' retained as ceph:ceph
changed ownership of '/var/lib/ceph/osd/ceph-0' from root:root to ceph:ceph
2018-11-15 16:26:23.765 7f4c152fd1c0 -1 bluestore(/var/lib/ceph/osd/ceph-0/block) _read_bdev_label failed to open /var/lib/ceph/osd/ceph-0/block: (2) No such file or directory
2018-11-15 16:26:23.765 7f4c152fd1c0 -1 bluestore(/var/lib/ceph/osd/ceph-0/block) _read_bdev_label failed to open /var/lib/ceph/osd/ceph-0/block: (2) No such file or directory
2018-11-15 16:26:23.765 7f4c152fd1c0 -1 bluestore(/var/lib/ceph/osd/ceph-0/block) _read_bdev_label failed to open /var/lib/ceph/osd/ceph-0/block: (2) No such file or directory
2018-11-15 16:26:23.781 7f4c152fd1c0 -1 bluestore(/var/lib/ceph/osd/ceph-0) _read_fsid unparsable uuid 
2018-11-15 16:26:23.785 7f4c152fd1c0 -1 bdev(0x557c1289a700 /var/lib/ceph/osd/ceph-0/block) unable to get device name for /var/lib/ceph/osd/ceph-0/block: (22) Invalid argument
2018-11-15 16:26:23.789 7f4c152fd1c0 -1 bdev(0x557c1289aa80 /var/lib/ceph/osd/ceph-0/block) unable to get device name for /var/lib/ceph/osd/ceph-0/block: (22) Invalid argument
2018-11-15 16:26:24.337 7f4c152fd1c0 -1 bdev(0x557c1289a700 /var/lib/ceph/osd/ceph-0/block) unable to get device name for /var/lib/ceph/osd/ceph-0/block: (22) Invalid argument
2018-11-15 16:26:24.337 7f4c152fd1c0 -1 bdev(0x557c1289aa80 /var/lib/ceph/osd/ceph-0/block) unable to get device name for /var/lib/ceph/osd/ceph-0/block: (22) Invalid argument
2018-11-15 16:26:24.909 7f4c152fd1c0 -1 bdev(0x557c1289a700 /var/lib/ceph/osd/ceph-0/block) unable to get device name for /var/lib/ceph/osd/ceph-0/block: (22) Invalid argument
2018-11-15 16:26:24.909 7f4c152fd1c0 -1 bdev(0x557c1289aa80 /var/lib/ceph/osd/ceph-0/block) unable to get device name for /var/lib/ceph/osd/ceph-0/block: (22) Invalid argument
changed ownership of '/var/lib/ceph/osd/ceph-0/bluefs' from root:root to ceph:ceph
changed ownership of '/var/lib/ceph/osd/ceph-0/keyring' from root:root to ceph:ceph
changed ownership of '/var/lib/ceph/osd/ceph-0/block' from root:root to ceph:ceph
changed ownership of '/var/lib/ceph/osd/ceph-0/mkfs_done' from root:root to ceph:ceph
changed ownership of '/var/lib/ceph/osd/ceph-0/magic' from root:root to ceph:ceph
changed ownership of '/var/lib/ceph/osd/ceph-0/whoami' from root:root to ceph:ceph
changed ownership of '/var/lib/ceph/osd/ceph-0/type' from root:root to ceph:ceph
changed ownership of '/var/lib/ceph/osd/ceph-0/ready' from root:root to ceph:ceph
changed ownership of '/var/lib/ceph/osd/ceph-0/ceph_fsid' from root:root to ceph:ceph
changed ownership of '/var/lib/ceph/osd/ceph-0/fsid' from root:root to ceph:ceph
changed ownership of '/var/lib/ceph/osd/ceph-0/kv_backend' from root:root to ceph:ceph
ownership of '/var/lib/ceph/osd/ceph-0' retained as ceph:ceph
starting osd.0 at - osd_data /var/lib/ceph/osd/ceph-0 /var/lib/ceph/osd/ceph-0/journal
2018-11-15 16:26:25.717 7f2b2ecfc1c0 -1 bdev(0x55e1eaf46700 /var/lib/ceph/osd/ceph-0/block) unable to get device name for /var/lib/ceph/osd/ceph-0/block: (22) Invalid argument
2018-11-15 16:26:26.025 7f2b2ecfc1c0 -1 bdev(0x55e1eaf46700 /var/lib/ceph/osd/ceph-0/block) unable to get device name for /var/lib/ceph/osd/ceph-0/block: (22) Invalid argument
2018-11-15 16:26:26.029 7f2b2ecfc1c0 -1 bdev(0x55e1eaf46a80 /var/lib/ceph/osd/ceph-0/block) unable to get device name for /var/lib/ceph/osd/ceph-0/block: (22) Invalid argument
2018-11-15 16:26:26.145 7f2b2ecfc1c0 -1 osd.0 0 log_to_monitors {default=true}
pool 'rbd' created
pool 'cephfs_data' created
pool 'cephfs_metadata' created
new fs with metadata pool 3 and data pool 2
changed ownership of '/var/lib/ceph/mds/ceph-demo/keyring' from root:root to ceph:ceph
changed ownership of '/var/lib/ceph/mds/ceph-demo' from root:root to ceph:ceph
starting mds.demo at -
changed ownership of '/var/lib/ceph/radosgw/ceph-rgw.vanessa-ThinkPad-T460s/keyring' from root:root to ceph:ceph
ownership of '/var/lib/ceph/radosgw/ceph-rgw.vanessa-ThinkPad-T460s' retained as ceph:ceph
2018-11-15 16:26:31  /entrypoint.sh: Setting up a demo user...
{
    "user_id": "qqq",
    "display_name": "Ceph demo user",
    "email": "",
    "suspended": 0,
    "max_buckets": 1000,
    "auid": 0,
    "subusers": [],
    "keys": [
        {
            "user": "qqq",
            "access_key": "qqq",
            "secret_key": "qqq"
        }
    ],
    "swift_keys": [],
    "caps": [
        {
            "type": "buckets",
            "perm": "*"
        },
        {
            "type": "metadata",
            "perm": "*"
        },
        {
            "type": "usage",
            "perm": "*"
        },
        {
            "type": "users",
            "perm": "*"
        }
    ],
    "op_mask": "read, write, delete",
    "default_placement": "",
    "placement_tags": [],
    "bucket_quota": {
        "enabled": false,
        "check_on_raw": false,
        "max_size": -1,
        "max_size_kb": 0,
        "max_objects": -1
    },
    "user_quota": {
        "enabled": false,
        "check_on_raw": false,
        "max_size": -1,
        "max_size_kb": 0,
        "max_objects": -1
    },
    "temp_url_keys": [],
    "type": "rgw",
    "mfa_ids": []
}

Sree-0.1/.gitignore
Sree-0.1/README.md
Sree-0.1/app.py
Sree-0.1/snapshots/
Sree-0.1/snapshots/Configuration.png
Sree-0.1/snapshots/greenland.png
Sree-0.1/sree.cfg.sample
Sree-0.1/static/
Sree-0.1/static/buckets.html
Sree-0.1/static/config.html
Sree-0.1/static/css/
Sree-0.1/static/css/bootstrap.min.css
Sree-0.1/static/css/font-awesome.min.css
Sree-0.1/static/css/jquery.dataTables.min.css
Sree-0.1/static/css/style.css
Sree-0.1/static/css/validationEngine.jquery.css
Sree-0.1/static/image/
Sree-0.1/static/image/ceph-nano-logo-horizontal.svg
Sree-0.1/static/image/fontawesome-webfont.svg
Sree-0.1/static/image/fontawesome-webfont.ttf
Sree-0.1/static/image/fontawesome-webfont.woff
Sree-0.1/static/js/
Sree-0.1/static/js/base.js
Sree-0.1/static/js/config.json.sample
Sree-0.1/static/js/lib/
Sree-0.1/static/js/lib/aws-sdk.min.js
Sree-0.1/static/js/lib/bootstrap.min.js
Sree-0.1/static/js/lib/dataTable.bootstrap.js
Sree-0.1/static/js/lib/jquery-1.10.1.min.js
Sree-0.1/static/js/lib/jquery.dataTables.js
Sree-0.1/static/js/lib/jquery.form.js
Sree-0.1/static/js/lib/jquery.validationEngine-zh_CN.js
Sree-0.1/static/js/lib/jquery.validationEngine.js
Sree-0.1/static/js/lib/require.config.js
Sree-0.1/static/js/lib/require.js
Sree-0.1/static/js/lib/template.js
Sree-0.1/static/js/upload.js
Sree-0.1/static/objects.html
Sree-0.1/xmlparser.py
/sree /
/
/sree /
/
 * Running on http://0.0.0.0:5000/
demo.sh: line 275: ceph-rest-api: command not found
2018-11-15 16:26:41  /entrypoint.sh: SUCCESS
exec: PID 1458: spawning ceph --cluster ceph -w
exec: Waiting 1458 to quit
```

There are definitely some worrysome messages about getting device names, but let's
skip these over until we have rationale to look into them. Because tada, the next
step reveals the interface is working!

## Step 5. View Container Interface

And then open browser to 0.0.0.0:5000 as instructed.

![/sregistry-cli/images/ceph-bucket.png](/sregistry-cli/images/ceph-bucket.png)

And then I was able to create a container called `sregistry:

![/sregistry-cli/images/ceph-create-bucket.png](/sregistry-cli/images/ceph-create-bucket.png)

> Wait, a container?

This caught me off guard at first. A container is really just like a folder - it's a subset of 
your storage namespace that you can put different file objects. For sregistry, I decided
that it made sense to have a container correspond with a *collection* of containers. Meaning 
that for `library/ubuntu` I would have a container called library, and then the actual
binary for the container ubuntu*(something). This also makes sense for management of permissions
if it's the case that the containers need different permissions.

The rest API is also very hard to find! I found it via looking at the configuration file:

```bash
$ docker exec demo cat /etc/ceph/ceph.conf
[global]
fsid = f5878c32-6571-40c7-ac87-5eafa25c9572
mon initial members = vanessa-ThinkPad-T460s
mon host = 172.17.0.1
osd crush chooseleaf type = 0
osd journal size = 100
public network = 172.17.0.1/24
cluster network = 172.17.0.1/24
log file = /dev/null
osd pool default size = 1
osd max object name len = 256
osd max object namespace len = 64
osd data = /var/lib/ceph/osd/ceph-0
osd objectstore = bluestore

[client.rgw.vanessa-ThinkPad-T460s]
rgw dns name = vanessa-ThinkPad-T460s
rgw enable usage log = true
rgw usage log tick interval = 1
rgw usage log flush threshold = 1
rgw usage max shards = 32
rgw usage max user shards = 1
log file = /var/log/ceph/client.rgw.vanessa-ThinkPad-T460s.log
rgw frontends = civetweb  port=0.0.0.0:8080

[client.restapi]
public addr = 172.17.0.1:5000
restapi base url = /api/v0.1
restapi log level = warning
log file = /var/log/ceph/ceph-restapi.log
```

and this also reveals the API address, it's served at `http://172.17.0.1:8080/`

![/sregistry-cli/images/ceph-storage-api.png](/sregistry-cli/images/ceph-storage-api.png)

and then to authenticate likely the endpoint here is used:

![/sregistry-cli/images/ceph-storage-auth.png](/sregistry-cli/images/ceph-storage-auth.png)

<div>
    <a href="/sregistry-cli/client-aws"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-docker"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
