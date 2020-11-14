from pathlib import Path
from configparser import RawConfigParser
from mozprofile import profile
import os
import sys
import logging
import argparse
import json


class SSBManager():
    __launchers_path = None
    __profiles_loc = None

    APP_JSON_PATH = './data/app.json'
    LAUNCHERS_PATH = '.local/share/applications'
    PROFILES_PATH = '.firefox-ssb'

    __app_data = None

    def __init__(self):
        logging.debug("Check the existence of apps.json file")

        if Path(self.APP_JSON_PATH).exists():
            logging.debug("app.json file already exists")
            with open(self.APP_JSON_PATH) as json_file:
                self.__app_data = json.load(json_file)
        else:
            logging.debug("app.json file doesn't exists. We will create it...")
            self.__app_data = dict()

        self.__launchers_path = Path("{0!s}/{1!s}".format(str(Path.home()), self.LAUNCHERS_PATH))
        logging.debug("Path of desktop files: %s",self.__launchers_path)
        logging.info("Profiles will be saved in %s", self.PROFILES_PATH)
        self.__profiles_loc = Path(Path.home()) / self.PROFILES_PATH
        if self.__profiles_loc.exists():
            logging.info(".firefox-ssb directory already exists")
        else:
            logging.info(".firefox-ssb directory is missing. Creating new one...")
            try:
                os.mkdir(str(self.__profiles_loc))
            except:
                logging.error("An error occurred during directory creation.")
        
    
    def install_app(self, app_name, url, icon_path=None):
        logging.debug("Check if the application is already installed")
        if app_name in self.__app_data.keys():
            logging.error("%s is already installed. Aborting.", app_name)
            sys.exit()
        
        launcher_file_name = "{!s}.desktop".format(app_name)
        if Path(launcher_file_name).exists():
            logging.error("The desktop entry already exists. Maybe the web application is already installed. Arresting...")
            sys.exit()

        logging.info("Creating new Firefox profile")
        profile_path = self.__profiles_loc / app_name
        new_profile = profile.FirefoxProfile(profile=profile_path, restore=False)

        logging.info("New profile created in: %s",new_profile.profile)
        logging.debug("Setting default profile preferences")
        logging.debug("Enabling ssb")

        new_profile.set_persistent_preferences({'browser.ssb.enabled':True})
        logging.debug("Disabling resume_from_crash")
        new_profile.set_persistent_preferences({'browser.sessionstore.resume_from_crash':False})
        logging.debug("Disabling disk caching")
        new_profile.set_persistent_preferences({'browser.cache.disk.enable':False})

        logging.debug("Saving profile path")
        self.__app_data[app_name] = dict()
        self.__app_data[app_name]['profile'] = str(profile_path)
       
        config_obj = RawConfigParser()
        config_obj.optionxform = str

        logging.info("Creating %s file in %s", launcher_file_name, self.__launchers_path)
        launcher_path = str(self.__launchers_path / launcher_file_name)
        config_obj.read(launcher_path)
        logging.info("Creating Desktop Entry")
        section_name = 'Desktop Entry'
        
        config_obj.add_section(section_name)
        config_obj[section_name]['Comment'] = ''
        config_obj[section_name]['Exec'] = 'firefox --no-remote --profile {0!s} --class {1!s} --ssb {2!s}'.format(new_profile.profile, app_name, url)

        config_obj[section_name]['Icon'] = icon_path
        config_obj[section_name]['Name'] = app_name
        config_obj[section_name]['NoDisplay'] = 'false'
        config_obj[section_name]['Path[$e]'] = ''
        config_obj[section_name]['StartupNotify'] = 'true'
        config_obj[section_name]['Terminal'] = '0'
        config_obj[section_name]['TerminalOptions'] = ''
        config_obj[section_name]['Type'] = 'Application'
        config_obj[section_name]['StartupWMClass'] = app_name
        logging.info("Saving .desktop file")
        

        with open(launcher_path, 'w') as configfile:    # save
            config_obj.write(configfile,space_around_delimiters=False)
        self.__app_data[app_name]['desktop'] = str(launcher_path)

        logging.debug("Saving additional information")
        logging.debug("Saving URL")
        self.__app_data[app_name]['URL'] = url
        logging.debug("Saving icon path")
        self.__app_data[app_name]['icon'] = icon_path

        logging.info("Saving application data")
        
        with open(self.APP_JSON_PATH, 'w') as json_file:
            json.dump(self.__app_data, json_file)

        logging.info("%s application has been installed correctly!", app_name)

    def uninstall_app(self, app_name):
        pass

    def list_apps(self):
        print("-"*85)
        print("| {:40s}| {:40s}|".format('Application Name', 'URL'))
        print("-"*85)
        for app in self.__app_data.keys():
            print("| {:40s}| {:40s}|".format(app, self.__app_data[app]['URL']))
        print("-"*85)


if __name__ == '__main__':
    #argv = sys.argv[1:]
    
    app_name = None
    url = None
    icon_path = None

    parser=argparse.ArgumentParser(description='''Firefox-SSB''', epilog=""".""")
    parser.add_argument('action', choices=['install','uninstall','list'], help='')
    #parser.add_argument('uninstall', action="store_true", help='uninstall a web application')
    #parser.add_argument('list', action="store_true", help='get the list of the installed applications')
    parser.add_argument('-n','--name', type=str, nargs=1, help='name to assign to the web application')
    parser.add_argument('-u','--url', type=str, nargs=1, help='URL pointing to the web application to install')
    parser.add_argument('-i','--icon', type=str, nargs='?', default='./icons/webapp.ico',help='path of the icon to associate with the web application')
    parser.add_argument('-d','--debug',  action="store_true", help='Enable debug mode')
    args = parser.parse_args()
    
    action = args.action
    if action in ('install','uninstall'):
        if args.name is None:
            logging.error("You must specify a name for the application")
            parser.print_help()
            sys.exit()
        app_name = args.name.pop()

    if action in ('uninstall'):
        if args.url is None:
            logging.error("You must specify a valid URL to the web application")
            parser.print_help()
            sys.exit()
        url = args.url.pop()
    
    if action in ('install'):
        icon_path = args.icon

    debug_level = logging.INFO
    if args.debug:
        debug_level = logging.DEBUG
    logging.basicConfig(level=debug_level, format='[%(levelname)-s] - %(message)s')

    manager = SSBManager()
    if args.action == 'install':
        manager.install_app(app_name, url, icon_path)
    
    if args.action == 'list':
        manager.list_apps()

