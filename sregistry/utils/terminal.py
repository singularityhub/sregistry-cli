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


from sregistry.logger import bot
from subprocess import (
    Popen,
    PIPE,
    STDOUT
)
import os

################################################################################
# Software Versions
################################################################################


def get_singularity_version(singularity_version=None):
    '''get_singularity_version will determine the singularity version for a
       build first, an environmental variable is looked at, followed by 
       using the system version.

       Parameters
       ==========
       singularity_version: if not defined, look for in environment. If still
       not find, try finding via executing --version to Singularity. Only return
       None if not set in environment or installed.
    '''

    if singularity_version is None:        
        singularity_version = os.environ.get("SINGULARITY_VERSION")
        
    if singularity_version is None:
        try:
            cmd = ['singularity','--version']
            output = run_command(cmd)

            if isinstance(output['message'],bytes):
                output['message'] = output['message'].decode('utf-8')
            singularity_version = output['message'].strip('\n')
            bot.info("Singularity %s being used." % singularity_version)
            
        except:
            singularity_version = None
            bot.warning("Singularity version not found, so it's likely not installed.")

    return singularity_version


def which(software=None, strip_newline=True):
    '''get_install will return the path to where Singularity (or another
       executable) is installed.
    '''
    if software is None:
        software = "singularity"
    cmd = ['which', software ]
    try:
        result = run_command(cmd)
        if strip_newline is True:
            result['message'] = result['message'].strip('\n')
        return result

    except: # FileNotFoundError
        return None


def check_install(software=None, quiet=True):
    '''check_install will attempt to run the singularity command, and
       return True if installed. The command line utils will not run 
       without this check.

       Parameters
       ==========
       software: the software to check if installed
       quiet: should we be quiet? (default True)
    '''
    if software is None:
        software = "singularity"
    cmd = [software, '--version']
    try:
        version = run_command(cmd,software)
    except: # FileNotFoundError
        return False
    if version is not None:
        if quiet is False and version['return_code'] == 0:
            version = version['message']
            bot.info("Found %s version %s" % (software.upper(), version))
        return True 
    return False


def get_installdir():
    '''get_installdir returns the installation directory of the application
    '''
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def get_thumbnail():
    '''return the robot.png thumbnail from the database folder.
       if the user has exported a different image, use that instead.
    '''
    from sregistry.defaults import SREGISTRY_THUMBNAIL
    if SREGISTRY_THUMBNAIL is not None:
        if os.path.exists(SREGISTRY_THUMBNAIL):
            return SREGISTRY_THUMBNAIL
    return "%s/database/robot.png" %get_installdir()


def run_command(cmd, sudo=False):
    '''run_command uses subprocess to send a command to the terminal.

    Parameters
    ==========
    cmd: the command to send, should be a list for subprocess
    error_message: the error message to give to user if fails,
    if none specified, will alert that command failed.

    '''
    if sudo is True:
        cmd = ['sudo'] + cmd

    try:
        output = Popen(cmd, stderr=STDOUT, stdout=PIPE)

    except FileNotFoundError:
        cmd.pop(0)
        output = Popen(cmd, stderr=STDOUT, stdout=PIPE)

    t = output.communicate()[0],output.returncode
    output = {'message':t[0],
              'return_code':t[1]}

    if isinstance(output['message'], bytes):
        output['message'] = output['message'].decode('utf-8')

    return output
