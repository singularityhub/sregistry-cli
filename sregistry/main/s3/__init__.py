'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.auth import read_client_secrets
from sregistry.logger import ( RobotNamer, bot )
from sregistry.main import ApiConnection
from sregistry.utils import confirm_action
import boto3
from botocore.client import ClientError
from botocore import UNSIGNED
import json
import os

from .query import ( 
    search, 
    search_all, 
    container_search 
)
from .pull import pull
from .push import push
from .delete import delete

class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, **kwargs):
 
        self.base = base
        self._update_secrets()
        self._update_headers()
        super(Client, self).__init__(**kwargs)

    def _speak(self):
        '''add the bucket'''
        bot.info('[bucket:s3://%s]' % self.bucket)

    def __str__(self):
        return type(self)

    def _read_response(self,response, field="detail"):
        '''attempt to read the detail provided by the response. If none, 
        default to using the reason'''

        try:
            message = json.loads(response._content.decode('utf-8'))[field]
        except:
            message = response.reason
        return message


    def get_bucket_name(self):
        '''get or return the s3 bucket name. If not yet defined via an environment
           variable or setting, we create a name with the pattern.
                    sregistry-<robotnamer>-<1234>

           You can use the following environment variables to determine
           interaction with the bucket:
           
           SREGISTRY_S3_BUCKET: the bucket name (all lowercase, no underscore)
           
        '''
        # Get bucket name
        bucket_name = 'sregistry-%s' % RobotNamer().generate()
        self.bucket_name = self._get_and_update_setting('SREGISTRY_S3_BUCKET', 
                                                        bucket_name)


    def get_bucket(self):
        '''given a bucket name and a client that is initialized, get or
           create the bucket.
        '''
        for attr in ['bucket_name', 's3']:
            if not hasattr(self, attr):
                bot.exit('client is missing attribute %s' %(attr))

        self.bucket = self.s3.Bucket(self.bucket_name)
        # check if the bucket exists and can be accessed
        # based on https://stackoverflow.com/a/47565719/1253230
        try:
            self.s3.meta.client.head_bucket(Bucket=self.bucket.name)
        except ClientError as e:
            self.bucket = None
            error_code = int(e.response['Error']['Code'])
            if error_code == 403:
                if not self._id or not self._key:
                    bot.exit('The {} bucket is not public and needs AWS credentials to be accessed'.format(self.bucket_name))
                bot.exit('The {} bucket cannot be accessed with the provided AWS credentials'.format(self.bucket_name))
            elif error_code == 404:
                # If the bucket doesn't exist, ask the user if he/she wants to try creating it
                if confirm_action('Are you sure you want to create the {} bucket?'.format(self.bucket_name)):
                    if not self._id or not self._key:
                        bot.exit('Buckets need AWS credentials to be created')
                    try:
                        self.bucket = self.s3.create_bucket(Bucket=self.bucket_name)
                        bot.info('Created bucket %s' % self.bucket.name )
                    except ClientError as e:
                        bot.exit('Could not create bucket {}: {}'.format(self.bucket_name, str(e)))
                else:
                    bot.exit('Aborting due to not creating bucket')
            else:
                bot.exit('Unrecognized error code {}: {}'.format(error_code, str(e)))


        return self.bucket


    def get_resource(self):
        '''use the user provided endpoint and keys (from environment) to
           connect to the resource. We can share the aws environment
           variables:

           AWS_ACCESS_KEY_ID
           AWS_SECRET_ACCESS_KEY

           https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html
        '''

        # s3.ServiceResource()
        self.s3 = boto3.resource('s3',
                                 endpoint_url=self.base,
                                 aws_access_key_id=self._id,
                                 aws_secret_access_key=self._key,
                                 config=boto3.session.Config(signature_version=UNSIGNED if not self._id or not self._key else self._signature))


    def _update_secrets(self, base=None):
        '''update secrets will update/get the base for the server, along
           with the bucket name, defaulting to sregistry.
        '''
        # We are required to have a base, either from environment or terminal
        self.base = self._get_and_update_setting('SREGISTRY_S3_BASE', self.base)
        self._id = self._get_and_update_setting('AWS_ACCESS_KEY_ID')
        self._key = self._get_and_update_setting('AWS_SECRET_ACCESS_KEY')

        if not self._id or not self._key:
            bot.warning("Accessing the bucket anonymously. Consider defining AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY if access fails.")

        # Get the desired S3 signature.  Default is the current "s3v4" signature.
        # If specified, user can request "s3" (v2 old) signature
        self._signature = self._get_and_update_setting('SREGISTRY_S3_SIGNATURE')

        if self._signature == 's3':
            # Requested signature is S3 V2
            self._signature = 's3'
        else:
            # self._signature is not set or not set to s3 (v2), default to s3v4
            self._signature = 's3v4'

        # Define self.bucket_name, self.s3, then self.bucket
        self.get_bucket_name()
        self.get_resource()
        self.get_bucket()


Client.pull = pull
Client.push = push
Client.search = search
Client.delete = delete
Client._search_all = search_all
Client._container_search = container_search
