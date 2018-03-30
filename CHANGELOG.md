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

## [0.0.x](https://github.com/singularityhub/sregistry-cli/tree/master) (0.0.x)
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
