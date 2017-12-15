# Docker Image

This docker image is intended to provide a containerized client for a Singularity Registry

## Singularity Registry Client

**build**
```
docker build -f Dockerfile -t vanessa/sregistry-cli .
docker push vanessa/sregistry-cli
```

**usage**
```
docker run vanessa/sregistry-cli
```
