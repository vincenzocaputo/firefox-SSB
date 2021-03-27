# firefox-SSB
A simple tool to manage web applications by using the SSB feature of Mozilla Firefox browser.

## Background

*What is SSB?*
SSB (Site-Specific Browser) is a feature that allows to access to a specific web-page avoiding unnecessary functionality usually provided by the web browser ( menus, address bar, toolbars, add-ons etc.).
Some web browsers, like Google Chrome, has this feature by default. In addition, Google Chrome gives the possibility to create a shortcut to the web-page, in order to realise a stand-alone SSB application for any site.

In Mozilla Firefox, the SSB feature is currently an experimental feature.  Furthermore, it has some drawbacks that can make user experience annoying and uncomfortable.

*Idea*
This small project aims to give *Linux* users the ability to create stand-alone windows for web application, using Mozilla Firefox.

## Key Features
- Creation of stand-alone launchers for web applications
- Automatic download of web-page favicon (which will be used as launcher icon)
- Deep separation of user data between web applications (the other user profiles aren't affected)
- Simple management of SSB applications (install/edit/uninstall)

# Installing

## Requirements
- Python $>=$ 3.8 *required*
- Some python libraries
  - mozprofile *required*
  - 
- virtualenv *recommended*

## Installation
1. Create a virtual environment (*recommended*)
```
$ python3.8 -m venv virt
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
$ 
```

## User Guide
You can use Firefox-SSB through CLI. You can see help information using this command:
```
$ python firefox-ssb.py --help
```
This tool currently provides four possibile operations:
- install: install a SSB application. You must provide the name of the application, the URL of the associated web page and, optionally, the application icon. 
For example:
```
$ python firefox-ssb.py --name GitHub --url https://github.com/ 
```
Notice that the tool tries to download automatically the favicon of the web page which will be used as application icon. However, the quality of the image may be low. Therefore I suggest you to specify a custom image. 
- uninstall: remove an installed SSB application. (**WARNING**: all the user data used by that application will be removed)
- list: list installed SSB application.
- edit: edit the URL of the icon of an installed SSB application.
For example:
