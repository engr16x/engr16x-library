# engr16x

[![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)](http://forthebadge.com)

## Introduction

This repository contains the source code for engr16x python package, which houses resources for students of Purdue University enrolled in ENGR16100 / ENGR16200 to use in their completion of projects, assignments, and other activities.

## Installing the library

To install the library, first make sure you have pip installed on your machine by enetering `pip -V` into the command line/terminal.  If a pip version number is not output, install pip by following the instructions found [here](https://pip.pypa.io/en/stable/installing/#do-i-need-to-install-pip).

Download and install the engr16x library simply by entering the command below into your command prompt/terminal window.

`pip install git+https://github.com/engr16x/engr16x-library`

## Library Contents

The engr16x library is orgainized into submodules for ease of use. To import only specific submodules, simply include `import engr16x.name-of-submodule` at the top of any python script. More information on modules can be found [here](https://docs.python.org/3/tutorial/modules.html#packages).

| Name | Description |
| --- | --- |
| `piTalk` | Allows a Computer to establish a socket connection with a Raspberry Pi and establishes a communication protocol using TCP to send/recieve data from the pi.  For more information see the README.md in this folder |
| `piTalk.pi` | Submodule of piTalk that contains all the functions to be used by the Raspberry Pi. |
| `piTalk.computer` | Submondule of piTalk that contains all the functions to be used by the Computer. |
|   |   |
| `install` | Provides scripts to install python, spyder, and other sofware used in the ENGR16X curriculum. |
| `install.spyder` | Installs python and spyder without installing Anaconda. |
|   |   |
| `projects` | Includes helper files and functions to be used with sensors and motors utilized in projects and in-class activities. |

## Repo Structure

Name | Description
--- | ---
`src/engr16x` | Contains all of the source code for the library
`dist` | Contains distribution files used by pip install when installing or upgrading the library
`build/lib` | Source code structure generated during package building.
`engr16x.egg-info` | Metadata relating to installation requirements. Replaced by .whl files in dist, but remains for backwards-compatibility

**Note:** The convention for files and directories in this repository are [snake_case](https://en.wikipedia.org/wiki/Snake_case)!
