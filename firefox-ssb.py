from pathlib import Path
from configparser import ConfigParser, RawConfigParser
from mozprofile import profile
import os
import sys
import logging
import argparse
import json
import shutil
import requests
import coloredlogs

logger = logging.getLogger()

class SSBManager():
    __CONFIG_PATH = './config.ini'
    __config = None

    __app_json_location = None
    __launchers_location = None
    __profiles_location = None
    __icons_location = None

    __app_data = None

    def __init__(self):
        logger.debug("Opening config.ini")
        config_obj = ConfigParser()
        config_obj.read(self.__CONFIG_PATH)
        config_obj.sections()
        self.__config = config_obj['CONFIG']
        
        logger.debug("Loading relevant paths")
        self.__app_json_location = Path(self.__config['AppJsonLocation'])

        self.__launchers_location = Path('{0!s}/{1!s}'.format(str(Path.home()), self.__config['LaunchersLocation']))
        logger.debug("Desktop files will be saved in %s",self.__launchers_location)
        self.__profiles_location = Path('{0!s}/{1!s}'.format(str(Path.home()), self.__config['ProfilesLocation']))
        logger.debug("Profiles will be saved in %s",self.__launchers_location)
        self.__icons_location = Path('{0!s}/{1!s}'.format(str(Path.home()), self.__config['IconsLocation']))
        logger.debug("Icons will be saved in %s",self.__icons_location)

        logger.debug("Check the existence of apps.json file")
        if Path(self.__app_json_location).exists():
            logger.debug("app.json file already exists")
            with open(self.__app_json_location) as json_file:
                self.__app_data = json.load(json_file)
        else:
            logger.debug("app.json file doesn't exist. We will create it...")
            self.__app_data = dict()

        logger.debug("Check if firefox profiles directory already exists")
        if self.__profiles_location.exists():
            logger.debug(".firefox-ssb directory already exists")
        else:
            print(".firefox-ssb directory is missing. Creating new one...")
            try:
                os.mkdir(str(self.__profiles_location))
            except:
                logger.error("An error occurred during directory creation.")
        
    
    def install_app(self, app_name, url, icon_path=None):
        logger.debug("Check if the application is already installed")
        if app_name in self.__app_data.keys():
            logger.error("%s is already installed. Aborting.", app_name)
            sys.exit()
        
        launcher_file_name = "{!s}.desktop".format(app_name)
        if Path(launcher_file_name).exists():
            logger.error("The desktop entry already exists. Maybe the web application is already installed. Arresting...")
            sys.exit()

        print("Creating new Firefox profile")
        profile_path = self.__profiles_location / app_name
        new_profile = profile.FirefoxProfile(profile=profile_path, restore=False)

        print("New profile created in: {!s}".format(new_profile.profile))
        logger.debug("Setting default profile preferences")
        logger.debug("Enabling ssb")

        new_profile.set_persistent_preferences({'browser.ssb.enabled':True})
        logger.debug("Disabling resume_from_crash")
        new_profile.set_persistent_preferences({'browser.sessionstore.resume_from_crash':False})
        logger.debug("Disabling disk caching")
        new_profile.set_persistent_preferences({'browser.cache.disk.enable':False})

        logger.debug("Saving profile path")
        self.__app_data[app_name] = dict()
        self.__app_data[app_name]['profile'] = str(profile_path)
       
        config_obj = RawConfigParser()
        config_obj.optionxform = str

        print("Creating {0!s} file in {1!s}".format(launcher_file_name, self.__launchers_location))
        launcher_path = str(self.__launchers_location / launcher_file_name)
        config_obj.read(launcher_path)
        print("Creating Desktop Entry")
        section_name = 'Desktop Entry'
        
        config_obj.add_section(section_name)
        config_obj[section_name]['Comment'] = ''
        config_obj[section_name]['Exec'] = 'firefox --no-remote --profile {0!s} --class {1!s} --ssb {2!s}'.format(new_profile.profile, app_name, url)

        if icon_path is None:
            logger.debug("Trying to download the favicon")
            r = requests.get('{!s}/favicon.ico'.format(url))
            icon = r.content
            logger.debug("Downloaded icon: %s",icon)
            if icon is not None:
                icon_file_name = "{!s}.ico".format(app_name.lower())
                logger.debug("The name of the icon file will be %s.ico", icon_file_name)
                icon_path = self.__icons_location / icon_file_name
                logger.debug("Saving the icon in %s", icon_path)
                with open(icon_path,'wb') as f:
                    f.write(icon)
            else:
                logger.warning("No icon found. Default icon will be used.")
                icon = ''

        config_obj[section_name]['Icon'] = str(icon_path)
        config_obj[section_name]['Name'] = app_name
        config_obj[section_name]['NoDisplay'] = 'false'
        config_obj[section_name]['Path[$e]'] = ''
        config_obj[section_name]['StartupNotify'] = 'true'
        config_obj[section_name]['Terminal'] = '0'
        config_obj[section_name]['TerminalOptions'] = ''
        config_obj[section_name]['Type'] = 'Application'
        config_obj[section_name]['StartupWMClass'] = app_name
        print("Saving .desktop file")
        

        with open(launcher_path, 'w') as configfile:    # save
            config_obj.write(configfile,space_around_delimiters=False)
        self.__app_data[app_name]['desktop'] = str(launcher_path)

        logger.debug("Saving additional information")
        logger.debug("Saving URL")
        self.__app_data[app_name]['URL'] = url
        logger.debug("Saving icon path")
        self.__app_data[app_name]['icon'] = str(icon_path)

        print("Saving application data")
        
        with open(self.__app_json_location, 'w') as json_file:
            json.dump(self.__app_data, json_file)

        print("{!s} application has been installed correctly!".format(app_name))


    def uninstall_app(self, app_name):
        logger.debug("Check if application exists")
        if app_name in self.__app_data.keys():
            print('{!s} will be removed. Proceed? [y/N]'.format(app_name), end=' ')
            if input() != 'y':
                print('Aborting...')
                sys.exit()
            print("Removing {!s} file".format(self.__app_data[app_name]['desktop']))
            os.remove(self.__app_data[app_name]['desktop'])
            print("Removing firefox profile")
            shutil.rmtree(self.__app_data[app_name]['profile'], ignore_errors=True)
            print("Remove application entry")
            del self.__app_data[app_name]
            print("Saving changes")
            with open(self.__app_json_location, 'w') as json_file:
                json.dump(self.__app_data, json_file)
            print("Successfully uninstalled {!s}".format(app_name))
        else:
            logger.error("%s is not installed.", app_name)

    def list_apps(self):
        print("-"*85)
        print("| {:40s}| {:40s}|".format('Application Name', 'URL'))
        print("-"*85)
        for app in self.__app_data.keys():
            print("| {:40s}| {:40s}|".format(app, self.__app_data[app]['URL']))
        print("-"*85)


    def edit_app(self, app_name, url=None, icon_path=None):
        if app_name in self.__app_data.keys():
            launcher_path = self.__app_data[app_name]['desktop']
            logger.debug("Saving changes in {!s}".format(launcher_path))
            if not Path(launcher_path).exists():
                logger.critical("Desktop file doesn't exists. This should not happen.")
            
            config_obj = RawConfigParser()
            config_obj.optionxform = str
            config_obj.read(launcher_path)
            section_name = 'Desktop Entry'
            
            print("Saving changes in .  desktop file")
            if icon_path is not None:
                logger.debug("Changing the application icon. The new icon path will be {!s}".format(icon_path))
                config_obj[section_name]['Icon'] = str(icon_path)
                logger.debug("Adding new icon in app.json file")
                self.__app_data[app_name]['icon'] = icon_path

            if url is not None:
                logger.debug("Changing the application URL. The new URL will be {!s}".format(url))
                profile = self.__app_data[app_name]['profile']
                config_obj[section_name]['Exec'] = 'firefox --no-remote --profile {0!s} --class {1!s} --ssb {2!s}'.format(profile, app_name, url)
                logger.debug("Adding new URL in app.json file")
                self.__app_data[app_name]['URL'] = url

            print("Saving changes in app.json")
            with open(self.__app_json_location, 'w') as json_file:
                json.dump(self.__app_data, json_file)

            print("Updating complete!")



if __name__ == '__main__':
    console = logging.StreamHandler()
    logger.addHandler(console)
    coloredlogs.install(level='INFO', logger=logger)

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
            print("You haven't provided a valid icon. We will try to find it")
            icon_path = None
        else:
            icon_path = args.icon

    if action in ('edit'):
        if url is None and icon is None:
            logger.error("You must specify a new URL or a new icon. Aborting...")
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
