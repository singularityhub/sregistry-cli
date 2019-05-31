'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
import json
import sys


def main(args, parser, subparser):
    from sregistry.main import get_client
    
    # No commands provided, show help
    if not args.commands:
        subparser.print_help()
        sys.exit(0)

    cli = get_client(quiet=args.quiet)
    cli.announce(args.command)

    # If the client doesn't have the command, exit
    if not hasattr(cli, 'build'):
        msg = "build is not implemented for %s. Why don't you add it?"
        bot.exit(msg % cli.client_name)

    if cli.client_name == 'google-build':

        if args.name is None:
            bot.exit('Please provide a container identifier with --name')

        recipe = args.commands.pop(0)
        response = cli.build(name=args.name,
                             recipe=recipe,
                             context=args.commands,
                             preview=args.preview)

        # Print output to the console
        print_output(response, args.outfile)
        
    else:

        # Does the user want to save the image?    
        command = args.commands.pop(0)

        # Option 1: The user wants to kill an instance
        if command == "kill":
            kill(args)    

        # Option 2: Just list running instances
        elif command == "instances":
            instances(args)

        # Option 3: The user wants to list templates
        elif 'template' in command:
            templates(args)

        # Option 4: View a specific or latest log
        elif command == 'logs':
            list_logs(args)

        # Option 3: The user is providing a Github repo!
        recipe = "Singularity"

        if "github" in command:

            # One argument indicates a recipe
            if len(args.commands) == 1:
                recipe = args.commands.pop(0)       

        else:

            # If a command is provided, but not a Github repo
            bot.error('%s is not a recognized option.' %command)
            subparser.print_help()
            sys.exit(1)


        # Does the user want to specify a name for the collection?
        name = args.name

        # No image is needed, we are creating in the cloud
        response = cli.build(repo=command, 
                             name=name,
                             recipe=recipe,
                             preview=args.preview)

    # If the client wants to preview, the config is returned
    if args.preview is True:
        print(json.dumps(response, indent=4, sort_keys=True))


def print_output(response, output_file=None):
    '''print the output to the console for the user. If the user wants the content
       also printed to an output file, do that.

       Parameters
       ==========
       response: the response from the builder, with metadata added
       output_file: if defined, write output also to file

    '''
    # If successful built, show container uri
    if response['status'] == 'SUCCESS':
        bucket = response['artifacts']['objects']['location']
        obj = response['artifacts']['objects']['paths'][0]
        bot.custom("MD5HASH", response['file_hash'], 'CYAN')
        bot.custom("SIZE", response['size'], 'CYAN')
        bot.custom(response['status'], bucket + obj , 'CYAN')
    else:
        bot.custom(response['status'], 'see logs for details', 'CYAN')

    # Show the logs no matter what
    bot.custom("LOGS", response['logUrl'], 'CYAN')

    # Did the user make the container public?
    if "public_url" in response:
        bot.custom('URL', response['public_url'], 'CYAN')

    # Does the user also need writing to an output file?
    if output_file is not None:    
        with open(output_file, 'w') as filey:
            if response['status'] == 'SUCCESS':
                filey.writelines('MD5HASH %s\n' % response['file_hash'])    
                filey.writelines('SIZE %s\n' % response['size'])    
            filey.writelines('%s %s%s\n' % (response['status'], bucket, obj))
            filey.writelines('LOGS %s\n' % response['logUrl'])
            if "public_url" in response:
                filey.writelines('URL %s\n' % response['public_url'])


def kill(args):
    '''kill is a helper function to call the "kill" function of the client,
       meaning we bring down an instance.
    '''
    from sregistry.main import get_client
    cli = get_client(quiet=args.quiet)
    if len(args.commands) > 0:
        for name in args.commands:
            cli.destroy(name)
    sys.exit(0)

def instances(args):
    '''list running instances for a user, including all builders and report
       instance names and statuses.
    '''
    from sregistry.main import get_client
    cli = get_client(quiet=args.quiet)
    cli.list_builders()
    sys.exit(0)

def templates(args, template_name=None):
    '''list a specific template (if a name is provided) or all templates
       available.

       Parameters
       ==========
       args: the argparse object to look for a template name
       template_name: if not set, show all

    '''
    from sregistry.main import get_client

    # We don't need storage/compute connections
    cli = get_client(init=False, quiet=args.quiet)

    if len(args.commands) > 0:
        template_name = args.commands.pop(0)
    cli.list_templates(template_name)
    sys.exit(0)


def list_logs(args, container_name=None):
    '''list a specific log for a builder, or the latest log if none provided

       Parameters
       ==========
       args: the argparse object to look for a container name
       container_name: a default container name set to be None (show latest log)

    '''
    from sregistry.main import get_client
    cli = get_client(quiet=args.quiet)
    if args.commands:
        container_name = args.commands.pop(0)
    cli.logs(container_name)
    sys.exit(0)
