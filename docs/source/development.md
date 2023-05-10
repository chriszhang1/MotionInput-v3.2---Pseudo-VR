# Guidelines
## Branches

**We have 2 important branches:**
 - `main` - Main branch with a stable version of the code
 - `dev` - Development branch where all of our branches are merged first.

**When you are working on a specific task or a feature:**
 - Create a branch using one of those naming schemes:
   - Team branch: `groupnumber-task-name` (i.e. 14-hand-gestures)
   - Personal branch: `firstname-task-name` (i.e. adi-hand-gestures)
 - Commit your changes to your branch.
 - Make a pull request to the `dev` branch

## Pull Requests

When making a pull request follow the [PR-messages](#pr-messages) structure

Once you've made a pull request, you are not allowed to merge it by yourself.

Ask one of the reviewers to check your PR.

 - If your PR is good, the reviewer will merge it.

 - If not, then you will be asked to make changes. In that case do everything that's required and contact the reviewer again once changes has been made.



### PR messages

Things that you **MUST** include in your pull request message:
 - `#What` - a list of features and fixes that were made
 - `#How` - a concise description of how these changes were implemented

Things that you **SHOULD** include in your pull request message:
- `#Why` - reasons for implementing these changes, (this will make reviewers' lifes easier)
- `#Testing` - description of how testing was conducted.

**Sample PR**

```
# What
 - 5 new hand gestures
 - Fixed an issue with the mouse moving around when the hand is stationary

# How
 - Hand gestures:
Trained a few models using video samples from here: (pretend there is a link here).
Updated the configuration view to include new gestures.
 - Mouse jiggling fix:
Added a small motion radius around each hand joint
which diables mouse movement unless the joint goes outside the radius.
# Why
 - Hand gestures: Dean asked me
 - Mouse jiggling fix:
It prevented featureX to work and it generally just annoyed the hell out of me.
# Testing
Used X framework for unit tests
Compiled the project and attempted evey gesture by myself and forced all fo my friends to do the same
```

## Code quality

**PLEASE** document your code. Reviewers will **NOT** merge your branch until its properly documented.

**PLEASE** Compile and test your code. Reviewers will **NOT** merge your branch until your code is compilable.



# Documentation

What you are seeing now is a sphinx documentation.

It references the actual source code and docstrings in there
and compiles all of it to html.

The docs website is updated **on push to the dev branch**

It might take a while until you see the update so its useful to know how get
the documentation build locally.

## Dependencies

So first of all you will need to install needed packages to compile the docs.
Navigate to `docs` directory and run:

	pip install -r requirements.txt

if you have some path issues with your python it is also worth to try:

	python3 -m pip install -r requirements.txt

## Understanding docs

Now let's understand how our documentation works. Here is what you will find in the `docs` directory.

	.
	├── make.bat
	├── Makefile
	├── requirements.txt
	└── source
		├── conf.py
		├── development.md
		├── getting-started.md
		├── index.rst
		├── _static
		└── _templates

- `make.bat` and `Makefile` are there to compile our documentation to html

- `requirements.txt` is what you just used to install our requirements.

- `source/` directory where the source files for our documentation are located. You will find a bunch
  of `.md` and `.rst` files there. These are pages with the actual text and tutorials that you see just now
  (this webpage is made from `development.md`, and the landing page is `index.rst`)

all `.md` files must be referenced in `index.rst` files. You can do it like so:

	.. toctree::
	   :maxdepth: 1
	   :caption: Development

	   development

This creates a table of content entry at the side bar on the landing page
with a caption **Development** and references the file `development.md`
(no need to add file extension in rst files as it doesn't care)

## Build documentation

So now that you have made changes to the actual documentation,
in order to compile it, navigate to the `docs` directory and run:

	make clean; make html

This will create a build folder where you can find all html files.

# Compilation

This section will describe how to compile motion input codebase.

We use [nuitka](https://nuitka.net/) transpiler in order to produce the resultant
``.exe`` file.

A few things to note about the compilation process

- Nuitka will translate our python code into C and then compile it.
- Compilation process is estimated to take around 30 minutes.
- It takes 3 to 4 Gb of RAM.
- By default it will use 100% of your CPU.

Now that you know all of this, read further to learn 2 ways of getting the
desired executable.
 

## Compilation process

Overview of required steps:

1. Install requirements
2. Run compilation command

### Install requirements

Just run: 

	python -m pip install -r requirements.txt

### Run compilation command

A python script for building the executable is provided. Run this build script with:

    python build.py <python_file_to_compile>

<python_file_to_compile> is currently named motioninput_api.py

It simply runs the following command (a python script is used for platform independence).

The complete command is the following:

	python -m nuitka --lto=no --windows-disable-console --assume-yes-for-downloads --standalone --include-data-dir=data=data --plugin-enable=numpy --output-dir=Release --user-plugin=nuitka_plugins/MediapipePlugin.py --user-plugin=nuitka_plugins/OpenvinoPlugin.py <python_file_to_compile>

This is indeed very long, so let's look at each compilation flag and see what it does.

- `--standalone`: This makes nuitka package libraries along side the executable.

- `--assume-yes-for-downloads`: Just a flag that will prevent some prompts from appearing. Nuitka will only prompt to download a C compiler and some dependency tracking tools so just keep it on to save some time.

- `--plugin-enable=numpy`: Numpy is a bit weird cuz it's already primarily written in C so it needs some special treatment.

- `--include-data-dir=data=data`: Ensures that the motioninput data dir is included in the final build.

- `--outuput-dir=Release`: Output directory.

- `--user-plugin=nuitka_plugins/MediapipePlugin.py`: This activates a Nuitka plugin to solve some issues with compiling mediapipe. It does the following: 1) ensures that the implicit dependency of mediapipe.python is included and 2) ensures that necessary data files for running mediapipe are included.

- `--user-plugin=nuitka_plugins/OpenvinoPlugin.py`: This activates a Nuitka plugin to solve some issues with compiling openvino. It does the following: 1) ensures that the implicit dependency on openvino.inference_engine.constants is included and 2) ensure that shared library files for openvino are included.

- `--user-plugin=nuitka_plugins/SounddevicePlugin.py`: The same but for sounddevice. 

That's it. After running this command you should now see a `Release` folder appear the project root.

If everything went well, it should contain 2 folders: `motioninput.build` and `motioninput.dist`.

- `motioninput.build`: source C code, not needed and can be deleted.
- `motioninput.dist`: This is where the compiled project is.

Add and remove flags as appropriate for debugging purposes.

## Things to keep in mind.

When you are extending the code base, make sure that **ALL** non python files are
in the `data` folder.

If you added a new dependency you **MUST** add it to `requirements.txt`

# Backend-Frontend Communication Protocol

During development you maw want to change/extend some functionality that involves both the backend and frontend. The following section covers how the protcol for communication is defined between the two.

Communication works as follows:
* Frontend sends a request to backend.
* Backend recieves the request and attempts to process it.
* If the backend succeeds, a SUCCEES message is returned with any relevant data.
* If not, an ERROR message is sent with a (hopefully) relevant error message.
* Repeat until a END message is recieved.

Messages sent from the back end will be in string format but will contain a dictionary containing any relevant data.

Every protocol message has a command, and each command (with `START`, `STOP`, `END`, `HIDE`, `SHOW` and `REBOOT` being the only exceptions) can take in exactly one request.

All the currently available commands include:
* START
* STOP
* END 
* REBOOT  
* ADD
* REMOVE
* UPDATE
* GET
* SHOW
* HIDE
* CURRENT_STATE
* CHANGE_MODE
* CALIBRATE_MODULE

When "JSON" is mentioned in the following command descriptions, it represents one of the following json files:
* mode
* config
* gestures
* events

### START

Usage:

`START`

Runs MotionInput. Will return an error if Motioninput is currently running

### STOP

Usage:

`STOP`

Terminates MotionInput. Will error if MotionInput is not running.

### END

Usage:

`END`

Terminates MotionInput and ends the connection. Will error if MotionInput is not running.

### REBOOT

Usage:

`REBOOT`

Terminates MotionInput, then runs it again. Will error if MotionInput is not running.

### ADD

Usage:

`ADD: "JSON"/path/to/place/to/add/object=object_to_add` 

Adds the specified object to the "/" seperated path in the specified JSON file. Errors if:
* Used on the config file
* Used to add an invalid gesture or event.
* Used to add anything except a mode in the mode JSON.

### REMOVE

Usage:

`REMOVE: "JSON"/path/to/object/to/remove`

Removes the object at the specified path from the JSON file. Errors if: 
* Used on the config file
* Used incorrectly in the mode JSON file (only modes can be removed).
Please be careful with what you remove, validation isn't a thing yet.

### UPDATE

Usage:

`UPDATE: "JSON"/path/to/attribute/to/update=val`

Used to update an attribute, cannot update objects, only values. Lists are recognised as values.  

### GET

Usage:

`GET: "JSON"/path/to/object/to/get`

Used to recieve an object from the specified JSON file.

### SHOW

Usage:

`SHOW`

Displays the camera view if it is not already visible.

### HIDE

Usage:

`HIDE`

Displays the camera view if it is currently visible.

### CURRENT_STATE

Usage:

`CURRENT_STATE`

Returns if the MI (the model) is running. "Active"/"Inactive"

### CHANGE_MODE

Usage:

`CHANGE_MODE: mode_name`

Changes the mode of interaction to the one given.

### CALIBRATE_MODULE

Usage:

`CALIBRATE_MODULE: module_name {'param1': val, 'param2', val}`

Calls the calibration function of the modules. Can only be called when the MI is not running. Allows for passing parameters to the modules calibration method (if no parametewrs needed add {}).




## Guidance
* When adding a mode to the event JSON you should use the ADD command with the name of the mode. This will initialise the mode with an empty list of events. To change this list of events use the UPDATE command with the list of all the events you want in the mode.
* Objects should be ADDed in their appropriate form:
	* {"attr_1": "val1", "attr_2": "val2"} for objects
	* [item1, item2, ...] for lists
* REBOOT should be called after a change is made to the JSON in order for that change to take effect.
* Only certain non attribute JSON objects can be UPDATED, this is to preserve the structure of the JSON files.