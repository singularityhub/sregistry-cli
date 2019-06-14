#!/usr/bin/env python

'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

import sregistry
import argparse
import sys
import os


def get_parser():
    parser = argparse.ArgumentParser(description="Singularity Registry tools")

    # Global Variables
    parser.add_argument('--debug', dest="debug", 
                        help="use verbose logging to debug.", 
                        default=False, action='store_true')

    parser.add_argument('--quiet', dest="quiet", 
                        help="suppress additional output.", 
                        default=False, action='store_true')

    parser.add_argument('--version', dest="version", 
                        help="suppress additional output.", 
                        default=False, action='store_true')

    description = 'actions for Singularity Registry Global Client'
    subparsers = parser.add_subparsers(help='sregistry actions',
                                       title='actions',
                                       description=description,
                                       dest="command")

    # print version and exit
    version = subparsers.add_parser("version", # pylint: disable=unused-variable
                                    help="show software version")

    # Backend controller
    backend = subparsers.add_parser("backend",
                                    help="list, remove, or activate a backend.")

    backend.add_argument("commands", nargs='*',
                         help='activate, deactivate, ls, status, delete, add/rm settings from a client', 
                         type=str)

    backend.add_argument('--force','-f', dest="force", 
                         help="force add if variable exists.", 
                         default=False, action='store_true')

    # Local shell with client loaded
    shell = subparsers.add_parser("shell",
                                  help="shell into a Python session with a client.")

    shell.add_argument("endpoint", nargs='?',
                       help="the endpoint to use (eg. docker)", 
                       type=str, default=None)

    # List local containers and collections
    images = subparsers.add_parser("images",
                                   help="list local images, optionally with query")

    images.add_argument("query", nargs='*', 
                        help="image search query", 
                        type=str, default="*")


    # List local containers and collections
    inspect = subparsers.add_parser("inspect",
                                    help="inspect an image in your database")

    inspect.add_argument("query",
                          help="image search query to inspect", 
                          type=str)

    # Get path to an image
    get = subparsers.add_parser("get",
                                help="get an image path from your storage")

    get.add_argument("query",
                     help="image search query to inspect", 
                     type=str)


    # Add an image file
    add = subparsers.add_parser("add",
                                help="add an image to local storage")

    add.add_argument("image",
                     help="full path to image file", 
                     type=str)

    add.add_argument("--name", dest='name', 
                     help='name of image, in format "library/image"', 
                     type=str)

    add.add_argument('--copy', dest="copy", 
                     help="copy the image instead of moving it.", 
                     default=False, action='store_true')


    mv = subparsers.add_parser("mv",
                               help="move an image and update database")

    mv.add_argument("name",
                     help="image name or uri to move from database", 
                     type=str)

    mv.add_argument("path",
                     help="directory or image file to move image.", 
                     type=str)


    rename = subparsers.add_parser("rename",
                                    help="rename an image in storage")

    rename.add_argument("name",
                        help="image name or uri to rename in database", 
                        type=str)

    rename.add_argument("path",
                         help="path to rename image (will use basename)", 
                         type=str)

    rm = subparsers.add_parser("rm",
                               help="remove an image from the local database")

    rm.add_argument("image",
                    help='name of image, in format "library/image"', 
                    type=str)

    # List or search containers and collections
    search = subparsers.add_parser("search",
                               help="search remote images")

    search.add_argument("query", nargs='*', 
                        help="image search query, don't specify for all", 
                        type=str, default="*")

    search.add_argument("--endpoint", default=None, dest='endpoint',
                        help='remote endpoint and path. id:/path"', 
                        type=str)

    # Build an image
    build = subparsers.add_parser("build",
                                 help="build an image using a remote.")

    build.add_argument('--preview','-p', dest="preview", 
                       help="preview the parsed configuration file only.", 
                       default=False, action='store_true')

    build.add_argument("commands", nargs='*',
                       help='''Google Cloud Build + GitHub
                               --------------------------------------------------------
                               build [recipe] [repo] 
                               --------------------------------------------------------
                               Google Build + Storage
                               --------------------------------------------------------
                               build [recipe] [context]
                               build [recipe] . 
                               build [recipe] relativefile1 relativefile2
                               ''', 
                       type=str)

    build.add_argument("--name", dest='name', 
                       help='name of image, in format "library/image"', 
                       type=str, default=None)

    build.add_argument("--outfile", dest='outfile', 
                       help='name of output file to write contents to', 
                       type=str, default=None)


    # Push an image
    push = subparsers.add_parser("push",
                                 help="push one or more images to a registry")

    push.add_argument("image",
                       help="full path to image file", 
                       type=str)

    push.add_argument("--tag", dest='tag', 
                       help="tag for image. If not provided, defaults to latest", 
                       type=str, default=None)

    push.add_argument("--name", dest='name', 
                       help='name of image, in format "library/image"', 
                       type=str, required=True)

    # Share an image
    share = subparsers.add_parser("share",
                                   help="share a remote image")

    share.add_argument("image",
                       help="full uri of image", 
                       type=str)

    share.add_argument("--email", dest='share_to', 
                        help='email (or share point) to share with', 
                        type=str, default=None)


    # Pull an image
    pull = subparsers.add_parser("pull",
                                 help="pull an image from a registry")

    pull.add_argument("image",
                       help="full uri of image", 
                       type=str)

    pull.add_argument("--name", dest='name', 
                       help='custom name for image', 
                       type=str, default=None)

    pull.add_argument('--force','-f', dest="force", 
                        help="force overwrite of existing image", 
                        default=False, action='store_true')

    pull.add_argument('--no-cache', dest="nocache", 
                       help="if storage active, don't add the image to it", 
                       default=False, action='store_true')


    # List or search labels
    labels = subparsers.add_parser("labels",
                                help="query for labels")

    labels.add_argument("--key", "-k", dest='key', 
                        help="A label key to search for", 
                        type=str, default=None)

    labels.add_argument("--value", "-v", dest='value', 
                        help="A value to search for", 
                        type=str, default=None)

    # Remove
    delete = subparsers.add_parser("delete",
                                    help="delete an image from a remote.")

    delete.add_argument('--force','-f', dest="force", 
                        help="don't prompt before deletion", 
                        default=False, action='store_true')

    delete.add_argument("image",
                        help="full path to image file", 
                        type=str)

    return parser


def main():
    '''main is the entrypoint to the sregistry client. The flow works to first
    to determine the subparser in use based on the command. The command then
    imports the correct main (files imported in this folder) associated with
    the action of choice. When the client is imported, it is actually importing
    a return of the function get_client() under sregistry/main, which plays
    the job of "sniffing" the environment to determine what flavor of client
    the user wants to activate. Installed within a singularity image, this
    start up style maps well to Standard Container Integration Format (SCIF)
    apps, where each client is a different entrypoint activated based on the
    environment variables.
    '''

    parser = get_parser()

    def help(return_code=0):
        '''print help, including the software version and active client 
           and exit with return code.
        '''

        version = sregistry.__version__

        print("\nSingularity Registry Global Client v%s" % version)
        parser.print_help()
        sys.exit(return_code)
    
    # If the user didn't provide any arguments, show the full help
    if len(sys.argv) == 1:
        help()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    if args.debug is True:
        os.environ['MESSAGELEVEL'] = "DEBUG"

    # Show the version and exit
    if args.command == "version" or args.version:
        print(sregistry.__version__)
        sys.exit(0)

    from sregistry.logger import bot # pylint: disable=unused-import

    # Does the user want a shell?
    if args.command == "add": from .add import main
    elif args.command == "backend": from .backend import main
    elif args.command == "build": from .build import main
    elif args.command == "get": from .get import main
    elif args.command == "delete": from .delete import main
    elif args.command == "inspect": from .inspect import main
    elif args.command == "images": from .images import main
    elif args.command == "labels": from .labels import main
    elif args.command == "mv": from .mv import main
    elif args.command == "push": from .push import main
    elif args.command == "pull": from .pull import main
    elif args.command == "rename": from .rename import main
    elif args.command == "rm": from .rm import main
    elif args.command == "search": from .search import main
    elif args.command == "share": from .share import main
    elif args.command == "shell": from .shell import main

    # Pass on to the correct parser
    return_code = 0
    try:
        main(args=args,
             parser=parser,
             extra=extra)
        sys.exit(return_code)
    except UnboundLocalError:
        return_code = 1

    help(return_code)

if __name__ == '__main__':
    main()
