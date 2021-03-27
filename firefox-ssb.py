
from pathlib import Path
from configparser import ConfigParser, RawConfigParser
from mozprofile import profile
from pprinter import Pprinter
from ssbmanager import SSBManager
import os
import sys
import logging
import argparse
import json
import shutil
import requests

logger = logging.getLogger()
pprinter = Pprinter().getInstance()

banner = "\n"\
"  __ _           __             ____ ____  ____  \n"\
" / _(_)_ __ ___ / _| _____  __ / ___/ ___|| __ ) \n"\
"| |_| | '__/ _ \ |_ / _ \ \/ / \___ \___ \|  _ \ \n"\
"|  _| | | |  __/  _| (_) >  < _ ___) |__) | |_) |\n"\
"|_| |_|_|  \___|_|  \___/_/\_(_)____/____/|____/ \n"

if __name__ == '__main__':
    pprinter.print_banner(166, banner)
    console = logging.StreamHandler()
    logger.addHandler(console)

    app_name = None
    url = None
    icon_path = None

    parser=argparse.ArgumentParser(description='''Firefox-SSB''', epilog=""".""")
    parser.add_argument('action', choices=['install','uninstall','edit','list'], help='action to perform')
    parser.add_argument('-n','--name', type=str, nargs=1, help='name to assign to the web application')
    parser.add_argument('-u','--url', type=str, nargs=1, help='URL pointing to the web application to install')
    parser.add_argument('-i','--icon', type=str, nargs='?',help='path of the icon to associate with the web application')
    parser.add_argument('-d','--debug',  action="store_true", help='Enable debug mode')
    args = parser.parse_args()
    
    action = args.action
    if action in ('install','uninstall','edit'):
        if args.name is None:
            pprinter.error("You must specify a name for the application")
            parser.print_help()
            sys.exit()
        app_name = args.name.pop()

    if action in ('install','edit'):
        if args.url is None:
            pprinter.error("You must specify a valid URL to the web application")
            parser.print_help()
            sys.exit()
        url = args.url.pop()
    
    if action in ('install','edit'):
        if args.icon is None:
            pprinter.warning("You haven't provided a valid icon. We will try to find it")
            icon_path = None
        else:
            icon_path = args.icon

    if action in ('edit'):
        if url is None and icon is None:
            pprinter.error("You must specify a new URL or a new icon. Aborting...")
            sys.exit()

    if args.debug:
        debug_level = logging.DEBUG
        logger.setLevel(debug_level)

    manager = SSBManager()
    
    if args.action == 'install':
        manager.install_app(app_name, url, icon_path)
    
    if args.action == 'list':
        manager.list_apps()

    if args.action == 'uninstall':
        manager.uninstall_app(app_name)

    if args.action == 'edit':
        manager.edit_app(app_name, url, icon_path)
