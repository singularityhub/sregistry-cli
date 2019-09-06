# Docker Image

If you want, you can build a local docker image from the root of this repository.

```bash
git clone https://github.com/singularityhub/sregistry-cli
cd sregistry-cli
```

## Singularity Registry Client

**build**

```
docker build -t quay.io/vanessa/sregistry-cli .
```

**usage**

```
docker run quay.io/vanessa/sregistry-cli
```

# Docker Compose

The [docker-compose.yml](docker-compose.yml) is an example of bringing up
an sregistry-cli and a Minio Storage server. We used this for testing. The docker 
image is from [Quay.io](https://quay.io/organization/vanessa?tab=tags).
You should have [docker-compose](https://docs.docker.com/compose/install/) installed.

```
cd examples/docker
docker-compose up -d
```

Your images should be up and running:

```
CONTAINER ID        IMAGE                                COMMAND                  CREATED             STATUS                    PORTS                    NAMES
4fbe8ab72f4e        minio/minio                          "/usr/bin/docker-ent…"   11 minutes ago      Up 11 minutes (healthy)   0.0.0.0:9000->9000/tcp   docker_minio_1
c512453bfeed        vanessa/sregistry-cli:add_aws-push   "tail -F /dev/null"      11 minutes ago      Up 11 minutes                                      docker_sregistrycli_1
```

## Shell Inside

Shell into the sregistry container first. We will first pull a Docker image.

```bash
$ docker exec -it docker_sregistrycli_1 bash
(base) root@c512453bfeed:/code# 
```


## Pull from Docker

Pull an image from Docker, we will push this image to our local registry!

```bash
SREGISTRY_CLIENT=docker sregistry pull ubuntu:latest

```

## Push to Minio

The minio and aws credentials for the attached minio server are already exported
with the container. s3 is also export as the default client. Let's now use the client 
to push the image to the minio endpoint.

```bash
sregistry push --name test/ubuntu:latest /root/.singularity/shub/library-ubuntu-latest-latest.simg
(base) root@c512453bfeed:/code# sregistry push --name test/ubuntu:latest /root/.singularity/shub/library-ubuntu-latest-latest.simg
Created bucket mybucket
[client|s3] [database|sqlite:////root/.singularity/sregistry.db]
[bucket:s3://s3.Bucket(name='mybucket')]
```

That's it!
