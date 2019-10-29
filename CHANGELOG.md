# CHANGELOG

This is a manually generated log to track changes to the repository for each release. 
Each section should include general headers such as **Implemented enhancements** 
and **Merged pull requests**. Critical items to know are:

 - renamed commands
 - deprecated / removed commands
 - changed defaults
 - backward incompatible changes (recipe file format? image file format?)
 - migration guidance (how to convert images?)
 - changed behaviour (recipe sections work differently)

The versions coincide with releases on pip. Only major versions will be released as tags on Github.

## [0.2.x](https://github.com/singularityhub/sregistry-cli/tree/master) (0.2.x)
 - Adding missing dependency for Google Build (0.2.31)
 - Metadata must include type of container (0.2.30)
   - accounting for Singularity 3.x bugs with metadata fields 
 - Fixing bug with setting docker base to None with super (0.2.29)
 - sregistry.main.registry: use env variables for authorization (0.2.28)
   - docs.pages.clients.registry: add delete docs
   - docs.pages.clients.registry: update for new env variables
   - README.md: add simple installation instructions
 - sregistry.main.s3.pull: add support for setting object ACL (0.2.27)
   - sregistry.main.s3.query: catch exceptions when objects are not readable
 - adding timeout parameter for Google Cloud Build (0.2.26)
 - restore quiet to False after initial setting to True in inspect (0.2.25)
   - bugfix for rename, and refactored testing with pytest and pylint
 - allow anonymously accessing S3 buckets (0.2.24)
   - add sregistry.utils.confirm_action
 - Fixing sregistry search to honor a URI (0.2.22)
 - adding ability to specify working_dir for Google Cloud Build (0.2.21)
 - finalizing registry Google Cloud Builder (0.2.20)
 - adding sregistry build to push recipes for Google Cloud (or other) builder (0.2.19)
 - ensure sregistry exits gracefully when database cannot be created (0.2.18)
 - fix accessing S3 buckets when IAM credentials don't allow listing buckets
 - setting sregistry hub base to be consistent with singularity-hub.org (0.2.17)
 - images being added twice (0.2.16)
 - adding pylint, and destroy function back to Google Storage (for instances) (0.2.15)
 - fixing bug with deleting container for Google Storage and Google Build (0.2.14)
 - ensure non-zero return values are returned when necessary (0.2.13)
 - add support for deleting images in S3 buckets (0.2.12)
 - removing complicated (multiple) imports for client, removing redundant "rmi" command (0.2.11)
 - fix s3 client support when SREGISTRY_S3_BASE is not specified, and allow for IAM accounts that do not permit listing buckets (0.2.1)
 - remove dateutils to allow conda support, 0.1.41 will be last supported for Python 2 (0.2.0)
 
 ## [0.1.x](https://github.com/singularityhub/sregistry-cli/tree/master) (0.1.x)
 - bug with sregistry push api endpoint, needs to end with api (0.1.41)
 - docker auth is undefined, and storage attribute needs to be checked for naming (0.1.40)
 - fixing bug with tag specification for registry pull (0.1.39)
 - registry client should honor base, if provided with uri (0.1.38)
 - added google-build client, building with google build and sending to google storage (0.1.37)
 - swift client ENV variable handling matches documentation (0.1.36)
 - s3 client supports S3 V2 (old) and S3 V4 (current) signatures (0.1.35)
 - fixed upload to google-storage bug with metadata (0.1.34)
 - added keystone authetication support to swift backend (0.1.33)
 - renaming ceph to swift, no other changes  (0.1.03)
 - adding ceph as backend to push, pull  (0.1.02)
 - adding GitLab Backend  (0.1.01)
 - adding `SREGISTRY_TMPDIR` to customize temporary folder  (0.1.00)
 - not moving image if storage `SREGISTRY_STORAGE` is same as pull folder
 
  ## [0.0.x](https://github.com/singularityhub/sregistry-cli/tree/master) (0.0.x)
 - storage name should use - instead of : to mirror Singularity  (0.0.99)
 - client missing quiet level  (0.0.98)
 - progress bar should respect quiet level  (0.0.97)
 - install of `[all]` includes aws, and containers building based on pypi version  (0.0.96)
 - adding aws container registry client (0.0.95)
 - resolved [bug in registry backend push function](https://github.com/singularityhub/sregistry-cli/issues/137) that stripped wrong char(s) (0.0.94)
 - adding rpm spec file, sregistry.cli.spec (0.0.90,0.0.91)
 - image URI tag should not be changed to lowercase (0.0.89)
 - adding chunked upload to chunk uploads to Singularity Registry (0.0.88)
 - fixing shell client bug (0.0.87)
 - updating Dockerfile and Singularity recipt with additional dependencies for 2.5 (0.0.86).
 - removing Globus dependency to avoid install conflict (0.0.85)
 - added client command to add, list, activate, and remove backends (0.0.84)
 - bumping spython dependency to 0.0.25 (0.0.83)
 - client rename function also updated uri (0.0.82)
 - adding get_endpoint function to Globus (0.0.81)
 - adding globus integration (0.0.80)
 - fixing bug that registry does not have label for size in metadata (0.0.79)
 - consolidating shared pull functionality between nvidia and docker (0.0.78)
 - updating pull to handle whiteout files, adding THIRD-PARTY-NOTICES (0.0.77)
 - version bump to add google-compute builder startup files (0.0.76)
 - support for the builders is added (0.0.75)
 - get_layerLink missing for nvidia client, added (0.0.74)
 - making "inspect" optional on pull so that we don't error out running in Docker (0.0.73)
 - fixed issue with missing registry version 2.0 manifest! (0.0.72)
 - print of "Unauthorized(403)" when client asks to pull private collection (0.0.71)
 - adding fix to allow for os that don't have `dpkg-architecture` (0.0.70)
 - adding help and support links to docs (doesn't alter functionality)
 - fixing [bug with environment](https://github.com/singularityhub/sregistry-cli/issues/79) variable export (0.0.69)
 - support for gcr.io, and future "special" token names (0.0.68)
 - adding move (mv) command so client can update database with new path (0.0.67)
 - adding rename command, which renames image in storage (and w/o path assumes name there)
 - fixing bug with Docker and Nvidia pull to clean up temporary sandbox build folders
 - if fromline is not defined in Singularity Recipe returns empty string (for registry pull)
 - fixing bug with client not being maintained in shell (was doing import twice)
 - fixing bug with Singularity Hub search (0.0.66)
 - added Dropbox backend with push, pull, record, search, share (0.0.65)
 - added ability for shell to take backend as argument (e.g., `sregistry shell dropbox`)
 - added `--quiet` argument to client for option to suppression of client announcing itself.
 - shared function to get metadata from an image, checking for Singularity and inspecting if installed
 - removing sqlalchemy dependency, so user can optionally install database with client (0.0.64)
 - fixing bug with pull that not available to client for registry (0.0.63)
 - changed os.rename to shutil.move to support moving files between different filesystems (0.0.62)
 - better consolidated dependencies, most just required for singularity registry client
 - added support to select client based on uri (e.g., `SREGISTRY_CLIENT=hub` maps to `hub://` (0.0.61)
 - fixed bug with environment.tar having different locations across distributions.

## [0.0.6](https://pypi.python.org/pypi/sregistry/0.0.6) (0.0.6)
 - added base client for Docker, and Nvidia Container Registry

## [0.0.5](https://pypi.python.org/pypi/sregistry/0.0.5) (0.0.5)

**additions**
 - added dateutils requirement
 - added authentication to pull so that private sregistry images can be pulled
 - client.speak() now also calls `_speak()` for subclass to implement with extra messages to user.
 - client._get_setting() and client._get_and_update_setting() retrieve / update environment settings
 - `SREGISTRY_THUMBNAIL` can be set for upload to Google Drive (or other clients that have thumbnails)
 - addition of the credential cache, so each client can have a private credentials file/folder if user enables

**bug fixes**
 - record after pull doesn't override image, if one existed 

**creation**
 - addition of Google Drive client, and new "share" command!
 - clients for Singularity Hub, Singularity Registry, Google Storage, and local use
 - addition of (mostly complete) documentation, Changelog, and Singularity file
 - this is the initial creation of just the singularity registry client, to be separate from
singularity python.
