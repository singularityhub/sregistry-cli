'''

Copyright (C) 2017-2018 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
