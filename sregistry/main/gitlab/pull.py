'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import ( parse_image_name, remove_uri )
import os

def pull(self, images, file_name=None, save=True, **kwargs):
    '''pull an image from gitlab. The image is found based on the 
       uri that should correspond to a gitlab repository, and then
       the branch, job name, artifact folder, and tag of the container.
       The minimum that we need are the job id, collection, and job name. Eg:

       job_id|collection|job_name   (or)
       job_id|collection

       Parameters
       ==========
       images: refers to the uri given by the user to pull in the format
               specified above
       file_name: the user's requested name for the file. It can 
                  optionally be None if the user wants a default.
       save: if True, you should save the container to the database
             using self.add()
    
       Returns
       =======
       finished: a single container path, or list of paths

    '''
    force = False
    if "force" in kwargs:
        force = kwargs['force']

    if not isinstance(images, list):
        images = [images]

    bot.debug('Execution of PULL for %s images' %len(images))

    # If used internally we want to return a list to the user.
    finished = []
    for image in images:

        # Format job_id|collection|job_name
        # 122056733,singularityhub/gitlab-ci'
        # 122056733,singularityhub/gitlab-ci,build

        job_id, collection, job_name = self._parse_image_name(image)
        names = parse_image_name(remove_uri(collection))

        # If the user didn't provide a file, make one based on the names
        if file_name is None:
            file_name = self._get_storage_name(names)

        # If the file already exists and force is False
        if os.path.exists(file_name) and force is False:
            bot.exit('Image exists! Remove first, or use --force to overwrite')

        # Put together the GitLab URI
        image_name = "Singularity.%s.simg" %(names['tag'])
        if names['tag'] == 'latest':
            image_name = "Singularity.simg"

        # Assemble artifact path
        artifact_path = "%s/%s" %(self.artifacts, image_name)
        bot.info('Looking for artifact %s for job name %s, %s' %(artifact_path,
                                                                 job_name,
                                                                 job_id))

        # project = quote_plus(collection.strip('/'))
        
        # This is supposed to work, but it doesn't
        # url = "%s/projects/%s/jobs/%s/artifacts/file/%s" %(self.api_base, 
        #                                                  project, job_id,
        #                                                  artifact_path)

        # This does work :)
        url = "%s/%s/-/jobs/%s/artifacts/raw/%s/?inline=false" % (self.base, 
                                                                  collection, 
                                                                  job_id, 
                                                                  artifact_path) 

        bot.info(url)

        # stream the url content to the file name
        image_file = self.download(url=url,
                                   file_name=file_name,
                                   show_progress=True)

        metadata = self._get_metadata()
        metadata['collection'] = collection
        metadata['job_id'] = job_id
        metadata['job_name'] = job_name
        metadata['artifact_path'] = artifact_path
        metadata['sregistry_pull'] = image

        # If we save to storage, the uri is the dropbox_path
        if save is True:
            container = self.add(image_path = image_file,
                                 image_uri = image,
                                 metadata = metadata,
                                 url = url)

            # When the container is created, this is the path to the image
            image_file = container.image

        if os.path.exists(image_file):
            bot.debug('Retrieved image file %s' %image_file)
            bot.custom(prefix="Success!", message=image_file)
            finished.append(image_file)


    if len(finished) == 1:
        finished = finished[0]
    return finished
