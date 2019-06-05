# Build Configuration

Here is an example build configuration to build directly from a repository
without specifying a commit or branch. We first clone the repository,
and then move the image to a storage path that takes into account
the entire image uri. If the repo had a commit or branch, this would
be included there as well.

```
{
    "steps": [
        {
            "args": [
                "clone",
                "https://github.com/vsoch/singularity-images",
                "."
            ],
            "name": "gcr.io/cloud-builders/git"
        },
        {
            "args": [
                "build",
                "singularity-images.sif",
                "Singularity"
            ],
            "name": "singularityware/singularity:v3.2.1-slim"
        }
    ],
    "artifacts": {
        "objects": {
            "location": "gs://sregistry-gcloud-build-vanessa/github.com/vsoch/singularity-images/latest/",
            "paths": [
                "singularity-images.sif"
            ]
        }
    }
}
```

