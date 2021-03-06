#####################################################################
# A python script for updating and archiving vanilla minecraft servers
# Written by Ryan Thorne
# date 5.1.19
# ver 0.2
#
#
# Python is distributed and owned by Python Software Foundation
# Minecraft is distributed and owned by Mojang
#
# this code is distributed under the MIT license 
# have fun modifying it!
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#####################################################################

import urllib.request
import json
import argparse
import shutil
import os
import tempfile
import hashlib
import datetime
from pathlib import Path

version_info = 'mcsuap version 0.2'


#path information
#the directory which represents where actions are to be taken in
working_d = Path.cwd()
#where the executable is invoked from
my_directory = Path.cwd()
archive_output_filename = Path(datetime.datetime.now().strftime('backupon%m.%d.%yat%H.%M'))
server_filename = Path('Server.jar')
manifest_dir = my_directory / Path('MCSUAP_manifest')
manifest_archiver_files = Path('backup_filenames')
manifest_versions_filename = Path('minecraft_version_info.json')
manifest_package_filename = Path('minecraft_package.json')


def get_manifest_json(req_url, req_filename, force):
	#we will try to read from an already available copy of the manifest data unless forced to pull from mojang
	#this is to limit the number of api calls to mojang :)
	try:
		if force:
			manifest_file = open(manifest_dir / req_filename, "w")
		else:
			manifest_file = open(Path(manifest_dir) / req_filename, "x")
		manifest_string = urllib.request.urlopen(req_url).read()
		manifest_string = str(manifest_string, 'utf-8')
		manifest_file.write(manifest_string)
	except FileExistsError:
		manifest_file = open(Path(manifest_dir) / req_filename, "r")
		manifest_string = manifest_file.read()
	finally:
		manifest_file.close()
	return json.loads(manifest_string)
#returns false if sha values are not the same


	

#archive directory with given name
def archive_fileset(filename_list, backup_location_path, name):
    try:
        with zipfile.ZipFile(backup_location_path, mode='x') as arc_dir:
            for i_file_path in filename_list:
                arc_dir.write(i_file_path)
            archive = shutil.make_archive(arc_dir , 'zip', file_location_path)
            shutil.move(archive, name)
    except Exception: #this is unhandleable for this script, if we cant archive, we should absolutely not be trying to update, crash the program
        quit()
	
#parse arguments to the system
parser = argparse.ArgumentParser(description='Minecraft server updater and archiver in python')
parser.add_argument('-i','--install', action='store_true', dest='INSTALL', help='unpack certain files for the MCSUAP_manifest folder so the program can use them')
parser.add_argument('-v','--version', default='0',dest='VERSION', help='specify a unique version of minecraft to change to')
parser.add_argument('-s', '--snapshot', action='store_true', dest='SNAPSHOT', help='use the latest snapshot version instead of the latest stable release')
parser.add_argument('-j','--jar', default='0', dest='SERVER_FILENAME', help='specify a filename for the servers jar file, defaults to server.jar')
parser.add_argument('-t','--test', action='store_true', dest='TEST_SHA', help='checks manifest sha against current server files sha, do not replace any file')
parser.add_argument('-p','--pull', action='store_true', dest='PULL', help='force read from mojang for the manifest files')
parser.add_argument('-f','--force', action='store_true', dest='FORCE', help='replace the server file, even if its is the same version')
parser.add_argument('-d','--target-directory', default='0', dest='TARGET_DIRECTORY', help='choose a directory to look for files that isnt in the current working directory')
parser.add_argument('--archive-dated', action='store_true', dest='ARCHIVE_DIRECTORY', help='backup files listed in MCSUAP_manifest to a compressed file with a name corresponding to the date created')
parser.add_argument('--archive-target', default='0', dest='ARCHIVE_TARGET', help='choose a directory other than the current directory to be where the compressed file is placed')
parser.add_argument('-u', '--no-update', action='store_true', dest='NO_UPDATE', help='do not run updater at all, use this only with archiving')
parser.add_argument('-V', '--info', action='store_true', dest='DISP_VERSION', help='display version information, quit')

args = parser.parse_args()

if args.DISP_VERSION:
	print(version_info)
	quit()

#replace with proper working directory as needed
if not args.TARGET_DIRECTORY == '0':
	working_d = Path(args.TARGET_DIRECTORY)
	
if not args.SERVER_FILENAME == '0':
	server_filename = Path(args.SERVER_FILENAME)

if not args.ARCHIVE_TARGET == '0':
	archive_output_filename = Path(args.ARCHIVE_TARGET)
	
#perform installation if requested
if args.INSTALL:
	try:
		os.mkdir(manifest_dir)
	except FileExistsError: #do nothing, we just need this directory to exist
		pass
	get_manifest_json('https://launchermeta.mojang.com/mc/game/version_manifest.json', manifest_versions_filename, True)
	quit()


#ensure manifest directory exists
if not os.path.isdir(manifest_dir):
	print('could not find necessesary manifest folder, try invoking -i first, exiting')
	quit()

#create processing directory for temporary files
with tempfile.TemporaryDirectory() as temp_dir:


	#begin archiver
	if args.ARCHIVE_DIRECTORY:
        print ('starting archiver')
        try:
            f_archive_filenames = open(Path(manifest_dir) / manifest_archiver_files, "r")
            archive_filelist = f_archive_filenames.readlines()
            f_archive_filenames.close()
        except:
            quit()
            
        archive_fileset_list = []
        try:
            for i_file in archive_filelist:
                archive_fileset_list.append(Path(i_file.strip()).relativeize(archive_output_filename))
        except ValueError:
            print ('err: coul not make file from: ' + i_file)
            quit()
		archive_fileset(archive_filelist, archive_output_filename, event_time)
        
	#end archiver

	
	#part 2 updater
	if args.NO_UPDATE:
		quit()
	
	print ('starting updater')
	versions_manifest_json = get_manifest_json('https://launchermeta.mojang.com/mc/game/version_manifest.json', manifest_versions_filename, args.PULL)

	#now we have the version manifest file, we want *our* versions manifest file
	if args.VERSION == '0':
		if args.SNAPSHOT:
			args.VERSION = versions_manifest_json['latest']['snapshot']
		else:
			args.VERSION = versions_manifest_json['latest']['release']

	found_manifest = False
	for i_ver in versions_manifest_json['versions']:
		if i_ver['id'] == args.VERSION:
			found_manifest = True
			manifest_url = i_ver['url']
	if not found_manifest:
		print('unable to find target version, check the manifest file to ensure you are looing for a valid version')
		quit()
	
	package_manifest_file_server = get_manifest_json(manifest_url, manifest_package_filename, args.PULL)
	if not package_manifest_file_server['id'] == args.VERSION:
		package_manifest_file_server = get_manifest_json(manifest_url, manifest_package_filename, True)
	package_manifest_file_server = package_manifest_file_server['downloads']['server']
	#check to see if current file is same as what we want to put there
	update_flag = args.FORCE
	sha_local = hashlib.sha1()
	try:
		local_jar_file = open(server_filename, 'rb')
		sha_local.update(local_jar_file.read())
		if sha_local.hexdigest() == package_manifest_file_server['sha1']:
			print('versions are same')
		else:
			print('version mismatch')
			update_flag = True	
		local_jar_file.close()
	except FileNotFoundError:
		print ('no server application detected, downloading new one')
		update_flag = True
	
	#download a new jar file if sha does not match or force flag is set
	if update_flag and not args.TEST_SHA:
		jar_web_request = urllib.request.urlopen(package_manifest_file_server['url']) 
		server_file = os.path.join(temp_dir, server_filename)
		new_jar_file = open(server_file, 'wb')
		shutil.copyfileobj(jar_web_request, new_jar_file)
		new_jar_file.close()
		sha_web = hashlib.sha1()
		new_jar_file = open(server_file, 'rb')
		sha_web.update(new_jar_file.read())
		new_jar_file.close()
		if sha_web.hexdigest() == package_manifest_file_server['sha1']:
			print('sha1 from internet passes')
		else:
			print('sha1 from internet fails, exiting')
			quit()
		#move temporary file into permenant location
		shutil.copyfile(server_file, working_d / server_filename)
		
#end updater