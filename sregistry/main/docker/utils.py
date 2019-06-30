'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
import datetime
import hashlib
import io
import os
import tempfile
import tarfile

def get_template(name):
    '''return a default template for some function in sregistry
       If there is no template, None is returned.

       Parameters
       ==========
       name: the name of the template to retrieve

    '''
    name = name.lower()
    templates = dict()

    templates['tarinfo'] = {"gid": 0,
                            "uid": 0,
                            "uname": "root",
                            "gname": "root",
                            "mode": 493}

    if name in templates:
        bot.debug("Found template for %s" % (name))
        return templates[name]
    else:
        bot.warning("Cannot find template %s" % (name))


def create_tar(files, output_folder=None):
    '''create_memory_tar will take a list of files (each a dictionary
        with name, permission, and content) and write the tarfile
        (a sha256 sum name is used) to the output_folder.
        If there is no output folde specified, the
        tar is written to a temporary folder.
    '''
    if output_folder is None:
        output_folder = tempfile.mkdtemp()

    finished_tar = None
    additions = []
    contents = []

    for entity in files:
        info = tarfile.TarInfo(name=entity['name'])
        info.mode = entity['mode']
        info.mtime = int(datetime.datetime.now().strftime('%s'))
        info.uid = entity["uid"]
        info.gid = entity["gid"]
        info.uname = entity["uname"]
        info.gname = entity["gname"]

        # Get size from stringIO write
        filey = io.StringIO()
        content = None
        try:  # python3
            info.size = filey.write(entity['content'])
            content = io.BytesIO(entity['content'].encode('utf8'))
        except:  # python2
            info.size = int(filey.write(entity['content'].decode('utf-8')))
            content = io.BytesIO(entity['content'].encode('utf8'))

        if content is not None:
            addition = {'content': content,
                        'info': info}
            additions.append(addition)
            contents.append(content)

    # Now generate the sha256 name based on content
    if len(additions) > 0:
        hashy = get_content_hash(contents)
        finished_tar = "%s/sha256:%s.tar.gz" % (output_folder, hashy)

        # Warn the user if it already exists
        if os.path.exists(finished_tar):
            msg = "metadata file %s already exists " % finished_tar
            msg += "will over-write."
            bot.debug(msg)

        # Add all content objects to file
        tar = tarfile.open(finished_tar, "w:gz")
        for a in additions:
            tar.addfile(a["info"], a["content"])
        tar.close()

    else:
        msg = "No contents, environment or labels"
        msg += " for tarfile, will not generate."
        bot.debug(msg)

    return finished_tar


def get_content_hash(contents):
    '''get_content_hash will return a hash for a list of content (bytes/other)
    '''
    hasher = hashlib.sha256()
    for content in contents:
        if isinstance(content, io.BytesIO):
            content = content.getvalue()
        if not isinstance(content, bytes):
            content = bytes(content)
        hasher.update(content)
    return hasher.hexdigest()
