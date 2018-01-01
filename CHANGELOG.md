# CHANGELOG

This is a manually generated log to track changes to the repository for each release. 
Each section should include general headers such as **Implemented enhancements** 
and **Merged pull requests**. All closed issued and bug fixes should be 
represented by the pull requests that fixed them. This log originated with Singularity 2.4
and changes prior to that are (unfortunately) done retrospectively. Critical items to know are:

 - renamed commands
 - deprecated / removed commands
 - changed defaults
 - backward incompatible changes (recipe file format? image file format?)
 - migration guidance (how to convert images?)
 - changed behaviour (recipe sections work differently)

## [0.0.4](https://github.com/singularityware/singularity-python/tree/development) (0.0.4)

**additions**
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
