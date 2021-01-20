"""
Iliad Terminal Interface

Created by cold-soda-jay
"""
import sys
import argparse
import iliaD.util as ut
from iliaD.pictures import *


def init_userdata(args):
    """
    Initiate user data
    """
    sync = ut.Synchronizer()

    args_dict = vars(args)
    try:
        username = args_dict['name']
        target = args_dict['target']
        sync.init_login_data(user=username,target=target)
    except:
        sync.init_login_data()


def synchronize(args):
    sync = ut.Synchronizer()
    sync.synchronize()


def course(args):
    sync = ut.Synchronizer()
    print(welcomeSmall)
    sync.show_marked_course()

def user(args):
    sync = ut.Synchronizer()
    print(welcomeSmall)
    sync.show_user_data()
#


def main():
    parser = argparse.ArgumentParser()

    sub_parser = parser.add_subparsers(title='\n-----------------------------------------\nIliaD, a simple ilias Downloader',
                                       description='\nWith iliaD you can download choosed courses from ilias automaticly. You can start with command [init] to initialize configurations. \nAfter initialization you can use command [sync] to download files from Ilias. To check or change the configuration please use command [course] or [user].',
                                       help='With [command] -h you can see usage of all functions.')
    init_parser = sub_parser.add_parser('init',help='Init user config with name and target folder. See init -h')
    init_parser.add_argument('-name', required=False, help='U-accout name')
    init_parser.add_argument('-target', required=False, help='Target folder to store Ilias documents')
    init_parser.set_defaults(func=init_userdata)

    synchronize_parser = sub_parser.add_parser('sync', help='Synchronize all marked Ilias files.')

    synchronize_parser.set_defaults(func=synchronize)

    change_parser = sub_parser.add_parser('course', help='Print or change marked courses')
    change_parser.set_defaults(func=course)


    user_parser = sub_parser.add_parser('user', help='Print or change user data')
    user_parser.set_defaults(func=user)
    args = parser.parse_args()
    if len(args._get_kwargs())==0:
        print(welcome)
        parser.print_help()
        parser.exit(1)
    else:
        args.func(args)

if __name__ == '__main__':
    main()
