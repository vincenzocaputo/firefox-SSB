![immagine](https://github.com/vincenzocaputo/firefox-SSB/assets/32276363/1eab1973-07ba-4d3d-bd7b-6c65a1f1d801)![immagine](https://github.com/vincenzocaputo/firefox-SSB/assets/32276363/78fdbd75-80be-4fbe-9f99-cd5ba60b7266)

This Python tool aims to provide a workaround for the lack of PWAs (Progressive Web Apps) management in Firefox browser. There are already other alternatives to bypass this limitation (such as: https://github.com/filips123/PWAsForFirefox). However, the idea of this project is to avoid relying on add-ons and extensions. 

**Caveat:** At the moment, Firefox **does not support** PWAs like Chromium-based browser. This tool is not intended to provide full support for PWAs but wants to offer the ability to create standalone launchers to open websites as Site-Specific Browser.

## How it works
The tool creates a Firefox profile for each web app. Separate profiles are needed to open web apps in separate windows as standalone applications. The tool create a .desktop file for each web app as launcher.
Initially, this tool used the Site-Specific Browser (SSB) feature, but Firefox removed it. Now the tool edits some CSS settings in order to avoid unnecessary functionality usually provided by the web browser ( menus, address bar, toolbars, add-ons etc.). 


## Key Features
- No Firefox add-on needed
- Creation of stand-alone launchers for web applications
- Automatic download of web-page favicon (which will be used as launcher icon)
- Deep separation of user data between web applications (your default user profiles aren't affected)
- Simple management of SSB applications (install/edit/uninstall)

# Installing

## Requirements
- Python $>=$ 3.11.4 *required*


## Installation
1. Create a virtual environment (*recommended*)
```
$ python3.8 -m venv .venv
```
2. Activate the virtual envorinment
```
$ source activate virt/bin/activate
```
3. Clone this repository using git:
```
$ git clone https://github.com/VincenzoCaputo/firefox-SSB
```
4. Install dependencies
```
$ pip install -i requirements.txt
```

## User Guide
You can use Firefox-SSB through CLI. You can see help information using this command:
```
$ python firefox-ssb.py --help
```
This tool currently provides four possibile operations:
- install: install a SSB application. You must provide the name of the application, the URL of the associated web page and, optionally, the icon for the web app
- uninstall: remove a web application. Profile folder, icon and launcher will be removed. (**WARNING**: all the user data used by that application will be removed)
- list: get the list of installed applications
- edit: edit the icon of an installed SSB application.

### Install a new web app
```
$ python firefox-ssb.py --name GitHub --url https://github.com/ 
```
Notice that the tool tries to download automatically the favicon of the web page which will be used as application icon. However, the quality of the image may be low. Therefore I suggest you to specify a custom image. 

![immagine](https://github.com/vincenzocaputo/firefox-SSB/assets/32276363/55aa832f-a69b-41e7-9b91-72bcac3cb33e)


# Testing
This tool was tested on Fedora Linux 38 (GNOME 44.3) with Firefox 115.0.2


