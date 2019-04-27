# mcsuap
a MineCraft Server Updater and Archiver in Python

Using this program

reccommended requirements:
  Python 3.6.3 or better
  Python is included in your PATH variable  
  
Copy the file into your minecraft server folder (where the .jar file is located)
run the execute command
  python mcsuap.py

this will update your server.jar to the latest version if it is not already there

there are additional options that you can specify:
  -h, --help                                show this help message and exit
  
  -p, --pull                                force read from mojang for the manifest files
  
  -v VERSION, --version VERSION             specify a unique version of minecraft to change to
  
  -t, --test                                checks manifest sha1 against current server files sha1
  
  -j SERVER_FILENAME, 
      --jar SERVER_FILENAME                 specify a filename for the servers jar file, defaults
                                            to server.jar
                                            
  -f, --force                               replace the server file, even if its is the same
                                            version
                                            
  -d TARGET_DIRECTORY,
      --target-directory TARGET_DIRECTORY   choose a directory to look for files that isnt in the
                                            current working directory
                                            
Finally, this is distributed under the MIT license.