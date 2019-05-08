#####################################################################
# A python script for updating and archiving vanilla minecraft servers
# Written by Ryan Thorne
# date 5.1.19
# ver 0.1
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



manifest_versions_filename = Path('minecraft_version_info.json')
manifest_package_filename = Path('minecraft_package.json')

#path information
#the directory which represents where actions are to be taken in
working_d = Path.cwd()
#where the executable is invoked from
my_d = Path.cwd()
archive_output_filename = Path.cwd()
server_filename = Path('Server.jar')
manifest_dir = my_d / Path('MCSUAP_manifest')

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
def archive_fileset(file_location_path, backup_location_path, name):
	archive = shutil.make_archive(name, 'zip', file_location_path)
	shutil.move(archive, backup_location_path, copy_function=shutil.copy2())

def setup()
	try:
		os.mkdir(manifest_dir)
	except FileExistsError: #do nothing, we just need this directory to exist
		pass
	versions_manifest_json = get_manifest_json('https://launchermeta.mojang.com/mc/game/version_manifest.json', manifest_versions_filename, True)

	
#parse arguments to the system
parser = argparse.ArgumentParser(description='Minecraft server updater and archiver in python')
parser.add_argument('-p','--pull', action='store_true', dest='PULL', help='force read from mojang for the manifest files')
parser.add_argument('-v','--version', default='0',dest='VERSION', help='specify a unique version of minecraft to change to')
parser.add_argument('-t','--test', action='store_true', dest='TEST_SHA', help='checks manifest sha against current server files sha, do not replace any file')
parser.add_argument('-j','--jar', default='0', dest='SERVER_FILENAME', help='specify a filename for the servers jar file, defaults to server.jar')
parser.add_argument('-f','--force', action='store_true', dest='FORCE', help='replace the server file, even if its is the same version')
#parser.add_argument('-d','--target-directory', default='0', dest='TARGET_DIRECTORY', help='choose a directory to look for files that isnt in the current working directory')
parser.add_argument('-s', '--snapshot', action='store_true', dest='SNAPSHOT', help='use the latest snapshot version instead of the latest stable release')
parser.add_argument('-i','--install', action='store_true', dest='INSTALL', help='unpack certain files for the MCSUAP_manifest folder so the program can use them in normal use')
parser.add_argument('--archive-dated', action='store_true', dest='ARCHIVE_DIRECTORY', help='backup files listed in MCSUAP_manifest to a compressed file with a name corresponding to the date created')
#parster.add_argument('--archive-target', default='0', dest='ARCHIVE_TARGET', help='choose a directory other than the current directory to be where the compressed file is placed')

args = parser.parse_args()
#replace with proper working directory as needed
if not args.TARGET_DIRECTORY == '0':
	working_d = Path(args.TARGET_DIRECTORY)
	
if not args.SERVER_FILENAME == '0':
	server_filename = Path(args.SERVER_FILENAME))

if not args.ARCHIVE_TARGET == '0':
	archive_output_filename = Path(args.ARCHIVE_TARGET)
	
#perform installation if requested
if args.INSTALL:
	setup()
	quit()


#ensure manifest directory exists
if not os.path.isdir(manifest_dir):
	print('could not find necessesary manifest folder, try invoking -i first, exiting')
	quit()

#create processing directory for temporary files
with tempfile.TemporaryDirectory() as temp_dir:

	#begin archiver
	event_time = datetime.datetime.now().strftime('backupon%m.%d.%yat%H.%M')

	if args.ARCHIVE_DIRECTORY:
		archive_fileset(working_d, archive_output_filename, event_time)
	#end archiver

	
	#part 2 updater
	
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
	
	package_manifest_file_server = get_manifest_json(manifest_url, manifest_package_filename, args.PULL)['downloads']['server']
	
	#check to see if current file is same as what we want to put there
	update_flag = args.FORCE
	sha_local = hashlib.sha1()
	try:
		local_jar_file = open(args.SERVER_FILENAME, 'rb')
		sha_local.update(local_jar_file.read())
		if sha_local.hexdigest() == package_manifest_file_server['sha1']:
			print('versions are same')
		else:
			update_flag = True	
		local_jar_file.close()
	except FileNotFoundError:
		update_flag = True
	
	#download a new jar file if sha does not match or force flag is set
	if update_flag and not args.TEST_SHA:
		jar_web_request = urllib.request.urlopen(package_manifest_file_server['url']) 
		server_file = os.path.join(temp_dir, args.SERVER_FILENAME)
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