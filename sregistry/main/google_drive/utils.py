'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

import os

def get_or_create_folder(self, folder):
    '''create a folder at the drive root. If the folder already exists,
       it is simply returned.

           folder = self._get_or_create_folder(self._base)
           $ folder
             {'id': '1pXR5S8wufELh9Q-jDkhCoYu-BL1NqN9y'}

    '''
    q = "mimeType='application/vnd.google-apps.folder' and name='%s'" %folder
    response = self._service.files().list(q=q,
                                          spaces='drive').execute().get('files',[])

    # If no folder is found, create it!
    if len(response) == 0:            
        folder = self._create_folder(folder)
    else:
        folder = response[0]
    return folder


def create_folder(self, folder):
    '''create a folder with a particular name. Be careful, if the folder 
       already exists you can still create one (a different one) with
       the equivalent name!
    '''
    folder_metadata = {
            'name': os.path.basename(folder),
            'mimeType': 'application/vnd.google-apps.folder'
    }
    created = self._service.files().create(body=folder_metadata,
                                           fields='id').execute()
    return created
