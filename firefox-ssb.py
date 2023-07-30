
from pathlib import Path
from configparser import ConfigParser, RawConfigParser
from mozprofile import profile
from loguru import logger
from rich import print
import os
import sys
import logging
import argparse
import json
import shutil
import requests
import pyfiglet

from ssbmanager import SSBManager


if __name__ == '__main__':
    banner = pyfiglet.figlet_format("Firefox-SSB", font="slant")
    print(f"[dark_orange3]{banner}[/dark_orange3]")
    console = logging.StreamHandler()

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

    logger.remove()
    if args.debug:
        log_level = "DEBUG"
        logger.add(sys.stderr, level="DEBUG")
    else:
        log_level = "INFO"
        logger.add(sys.stderr, format="<level>[{level}]</level> {message}", level="INFO")
        logger.level("INFO", color="<blue>")
    
    if action in ('install','uninstall','edit'):
        if args.name is None:
            logger.error("You must specify a name for the application")
            parser.print_help()
            sys.exit()
        app_name = args.name.pop()

    if action in ('install','edit'):
        if args.url is None:
            logger.error("You must specify a valid URL to the web application")
            parser.print_help()
            sys.exit()
        url = args.url.pop()
    
    if action in ('install','edit'):
        if args.icon is None:
            logger.warning("You haven't provided a valid icon. We will try to find it")
            icon_path = None
        else:
            icon_path = args.icon

    if action in ('edit'):
        if url is None and icon is None:
            logger.error("You must specify a new URL or a new icon. Aborting...")
            sys.exit()

         

    manager = SSBManager()
    
    if args.action == 'install':
        manager.install_app(app_name, url, icon_path)
    
    if args.action == 'list':
        manager.list_apps()

    if args.action == 'uninstall':
        manager.uninstall_app(app_name)

    if args.action == 'edit':
        manager.edit_app(app_name, url, icon_path)
