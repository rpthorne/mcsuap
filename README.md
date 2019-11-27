# mcsuap
a MineCraft Server Updater and Archiver in Python v 0.3

## Using this program

### reccommended requirements:
* [Python 3.6.3](https://www.python.org/downloads/ "Python downloads") or better
* Python is included in your PATH variable  (if you dont want to do this, you can simply find the python command and type the full location instead of just python below)
* If you intend to *use* the jar file, you should also have the minimum [JRE](https://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html "Java Runtime Environment downloads") version installed

### install
1. Copy the file into your minecraft server folder (where the .jar file is located)
1. run the execute command while in that folder (you should [cd](https://en.wikipedia.org/wiki/Cd_(command)) into that folder before running this command)
~~~~~~~~~~~~~~~~
python mcsuap.py -i
~~~~~~~~~~~~~~~~

this will unpack mcsuap int MCSUAP_manifest if it is not already there

### usage
to get the latest release of minecraft server, you might type
~~~~~~~~~~~~~~~~
python mcsuap.py
~~~~~~~~~~~~~~~~

### additional options
there are additional options that you can specify:

option | description
----------------- | ------------------
-h, --help |  show this help message and exit
-i, --install | unpack certain files for the MCSUAP_manifest folder so the program can use them
-v VERSION, --version VERSION |  specify a unique version of minecraft to change to
-s, --snapshot | use the latest snapshot version instead of the latest stable release
-j SERVER_FILENAME, --jar SERVER_FILENAME | specify a filename for the servers jar file, defaults to server.jar
-t, --test |  checks manifest sha1 against current server files sha1
-p, --pull |  force read from mojang for the manifest files
-f, --force  |  replace the server file, even if its is the same version           
-d TARGET_DIRECTORY, --target-directory TARGET_DIRECTORY |  choose a directory to look for files that isnt in the current working directory
--archive-dated | backup files listed in MCSUAP_manifest to a compressed file with a name corresponding to the date created
--archive-target | choose a directory other than the current directory to be where the compressed file is placed
-u, --no-update | do not run updater at all, use this only with archiving

## License
This is distributed under the MIT license.
