from pathlib import Path
from configparser import ConfigParser, RawConfigParser
from mozprofile import profile
from loguru import logger
from rich.progress import track
import yaml
import os
import sys
import json
import shutil
import requests
import subprocess
import signal
import time


class SSBManager():
    __CONFIG_PATH = './config.yml'
    __config = None

    __app_json_path = None
    __launchers_path = None
    __profiles_path = None
    __icons_path = None

    __app_data = None

    def __init__(self):
        logger.debug("Opening {self.__CONFIG_PATH}")

        with open(self.__CONFIG_PATH, 'r') as fd:
            self.__config = yaml.load(fd.read(), Loader=yaml.FullLoader)

        main_config = self.__config['config']
        
        logger.debug("Loading relevant paths")
        self.__apps_path = Path(main_config['apps_path'])

        self.__launchers_path = Path.home() / main_config['launchers_path']
        logger.debug(f"Desktop files will be saved in {self.__launchers_path}")
        self.__profiles_path = Path.home() / main_config['profiles_path']
        logger.debug(f"Profiles will be saved in {self.__launchers_path}")
        self.__icons_path = Path.home() / main_config['icons_path']
        logger.debug(f"Icons will be saved in {self.__icons_path}")

        logger.debug("Check the existence of apps.json file")
        if Path(self.__apps_path).exists():
            logger.debug("apps.json file already exists")
            with open(self.__apps_path) as json_file:
                self.__app_data = json.load(json_file)
        else:
            logger.debug("app.json file doesn't exist. We will create it...")
            self.__app_data = dict()

        logger.debug("Check if firefox profiles directory already exists")
        if self.__profiles_path.exists():
            logger.debug(".firefox-ssb directory already exists")
        else:
            logger.info(".firefox-ssb directory is missing. Creating new one...")
            try:
                self.__profiles_path.mkdir(parents=True)
            except Exception as ex:
                logger.error("An error occurred during directory creation.")
                logger.exception(ex)
        
    
    def install_app(self, app_name, url, icon_path=None):
        logger.debug("Check if the application is already installed")
        if app_name in self.__app_data.keys():
            logger.error(f"{app_name} is already installed. Aborting.")
            sys.exit()
        
        launcher_file_name = f"{app_name.lower()}.desktop"
        if Path(launcher_file_name).exists():
            logger.error("The desktop entry already exists. Maybe the web application is already installed. Arresting...")
            sys.exit()

        logger.info("Creating new Firefox profile")
        profile_path = self.__profiles_path / app_name.lower()
        new_profile = profile.FirefoxProfile(profile=profile_path, restore=False)

        logger.info(f"New profile created in: {new_profile.profile}")
        logger.debug("Setting default profile preferences")

        for setting, value in self.__config['default_settings'].items():
            logger.debug(f"Setting {setting}, value {value}")
            new_profile.set_preferences({setting: value})

        logger.debug("Saving profile path")
        self.__app_data[app_name] = dict()
        self.__app_data[app_name]['profile'] = str(profile_path)
       
        # Copy the css file
        logger.debug("Create chrom folder in profile")
        chrome_folder = profile_path / "chrome"
        os.mkdir(chrome_folder)
        logger.debug("Copying userChrome.css file to chrome folder in profile")
        shutil.copyfile("res/userChrome.css", chrome_folder / "userChrome.css")

        # Creating application desktop file
        config_obj = RawConfigParser()
        config_obj.optionxform = str

        logger.info(f"Creating {launcher_file_name} file in {self.__launchers_path}")
        launcher_path = self.__launchers_path / launcher_file_name
        config_obj.read(launcher_path)
        logger.info("Creating Desktop Entry")
        section_name = 'Desktop Entry'
        
        config_obj.add_section(section_name)
        config_obj[section_name]['Comment'] = f"{app_name} Firefox app"
        config_obj[section_name]['Exec'] = f"firefox --no-remote --profile {new_profile.profile} --class {app_name} --name {app_name} {url}"

        if icon_path is None:
            icon = None
            logger.debug("Trying to download the favicon")
            r = requests.get(f"{url}/favicon.ico")
            if r.status_code == 200:
                icon = r.content
            else:
                logger.warning(f"Request error: status code {r.status_code} returned")

            if icon is not None:
                icon_file_name = f"{app_name.lower()}.ico"
                logger.debug(f"The name of the icon file will be {icon_file_name}.ico")
                if not os.path.exists(self.__icons_path):
                    self.__icons_path.mkdir()
                icon_path = self.__icons_path / icon_file_name
                logger.debug(f"Saving the icon in {icon_path}")

                with open(icon_path,'wb') as f:
                    f.write(icon)
            else:
                logger.warning("No icon found. Default icon will be used.")
                icon = ''

        config_obj[section_name]['Icon'] = str(icon_path)
        config_obj[section_name]['Name'] = app_name
        config_obj[section_name]['NoDisplay'] = 'false'
        config_obj[section_name]['StartupNotify'] = 'true'
        config_obj[section_name]['Terminal'] = '0'
        config_obj[section_name]['TerminalOptions'] = ''
        config_obj[section_name]['Type'] = 'Application'
        config_obj[section_name]['StartupWMClass'] = app_name
        logger.info("Saving .desktop file")
        

        with open(launcher_path, 'w') as configfile:    # save
            config_obj.write(configfile,space_around_delimiters=False)
        self.__app_data[app_name]['desktop'] = str(launcher_path)

        logger.debug("Saving additional information")
        logger.debug("Saving URL")
        self.__app_data[app_name]['URL'] = url
        logger.debug("Saving icon path")
        self.__app_data[app_name]['icon'] = str(icon_path)

        logger.info("Saving application data")
        
        with open(self.__apps_path, 'w') as json_file:
            json.dump(self.__app_data, json_file)
            
        logger.info("Starting Firefox with the new profile for the first time") #It is necessary to pre-load the default settings and overwrite them at the next start
        process = subprocess.Popen(f"{config_obj[section_name]['Exec']} --headless", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            for i in track(range(5), description="Waiting for Firefox to end"):
                time.sleep(1)

            if process.poll() is None:
                os.kill(process.pid, signal.SIGTERM)
        except KeyboardInterrupt:
            os.kill(process.pid, signal.SIGTERM)
            logger.warning(f"Firefox process killed. It may not have been able to fully load settings")
        except Exception as e:
            logger.exception(e)

        logger.info(f"{app_name} application has been installed correctly!")


    def uninstall_app(self, app_name):
        logger.debug("Check if application exists")
        
        with open(self.__apps_path, 'r') as fd:
            self.__app_data = json.loads(fd.read())
            if app_name in self.__app_data.keys():
                if input(f"{app_name} will be removed. Proceed? [y/N] ") != 'y':
                    logger.info('Aborting...')
                    sys.exit()
                logger.info(f"Removing {self.__app_data[app_name]['desktop']} file")
                if not os.path.exists(self.__app_data[app_name]['desktop']):
                    logger.warning("File not found. Skipping...")
                else:
                    os.remove(self.__app_data[app_name]['desktop'])
                logger.info("Removing firefox profile")
                if not os.path.exists(self.__app_data[app_name]['profile']):
                    logger.warning("Profile not found. Skipping...")
                else:
                    shutil.rmtree(self.__app_data[app_name]['profile'], ignore_errors=True)
                logger.info("Removing application icon")
                if not os.path.exists(self.__app_data[app_name]['icon']): 
                    logger.warning("Icon not found. Skipping...")
                else:
                    os.remove(self.__app_data[app_name]['icon'])
            else:
                logger.error(f"{app_name} is not installed.")
                return
        logger.info("Removing application entry")
        self.__app_data.pop(app_name)
        logger.info("Saving changes")
        with open(self.__apps_path, 'w') as json_file:
            json.dump(self.__app_data, json_file)
            logger.info(f"{app_name} successfully uninstalled!")

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
            logger.debug(f"Saving changes in {launcher_path}")
            if not Path(launcher_path).exists():
                logger.critical("Desktop file doesn't exists. This should not happen.")
            
            config_obj = RawConfigParser()
            config_obj.optionxform = str
            config_obj.read(launcher_path)
            section_name = 'Desktop Entry'
            
            logger.info("Saving changes in .  desktop file")
            if icon_path is not None:
                logger.info(f"Changing the application icon. The new icon path will be {icon_path}")
                config_obj[section_name]['Icon'] = str(icon_path)
                logger.debug("Adding new icon in app.json file")
                self.__app_data[app_name]['icon'] = icon_path

            if url is not None:
                logger.info(f"Changing the application URL. The new URL will be {url}")
                profile = self.__app_data[app_name]['profile']
                config_obj[section_name]['Exec'] = 'firefox --no-remote --profile {profile} --class {app_name} {url}'
                logger.debug("Adding new URL in app.json file")
                self.__app_data[app_name]['URL'] = url

            logger.info("Saving changes in app.json")
            with open(self.__apps_path, 'w') as json_file:
                json.dump(self.__app_data, json_file)

            logger.info("Updating complete!")


