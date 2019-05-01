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
from pathlib import Path


manifest_dir = 'MCSUAP_manifest'
manifest_versions_filename = 'minecraft_latest_version_info.json'
manifest_package_filename = 'minecraft_package.json'

def get_manifest_json(req_url, req_filename, force):
	#we will try to read from an already available copy of the manifest data unless forced to pull from mojang
	#this is to limit the number of api calls to mojang :)
	try:
		if force:
			manifest_file = open(Path(manifest_dir) / Path(req_filename), "w")
		else:
			manifest_file = open(Path(manifest_dir) / Path(req_filename), "x")
		manifest_string = urllib.request.urlopen(req_url).read()
		manifest_string = str(manifest_string, 'utf-8')
		manifest_file.write(manifest_string)
	except FileExistsError:
		manifest_file = open(Path(manifest_dir) / Path(req_filename), "r")
		manifest_string = manifest_file.read()
	finally:
		manifest_file.close()
	return json.loads(manifest_string)

#parse arguments to the system
parser = argparse.ArgumentParser(description='Minecraft server updater and archiver in python')
parser.add_argument('-p','--pull', action='store_true', dest='PULL', help='force read from mojang for the manifest files')
parser.add_argument('-v','--version', default='0',dest='VERSION', help='specify a unique version of minecraft to change to')
parser.add_argument('-t','--test', action='store_true', dest='TEST_SHA', help='checks manifest sha against current server files sha')
parser.add_argument('-j','--jar', default='server.jar', dest='SERVER_FILENAME', help='specify a filename for the servers jar file, defaults to server.jar')
parser.add_argument('-f','--force', action='store_true', dest='FORCE', help='replace the server file, even if its is the same version')
parser.add_argument('-d','--target-directory', default='0', dest='TARGET_DIRECTORY', help='choose a directory to look for files that isnt in the current working directory')
parser.add_argument('-r','--release', action='store_true', dest='RELEASE', help='use the latest snapshot version instead of the latest stable release')
parser.add_argument('-i','--install', action='store_true', dest='INSTALL', help='unpack certain files for the MCSUAP_manifest folder so the program can use them in normal use')
#parser.add_argumant('--archive-dated', default='0', dest='ARCHIVE_DIRECTORY', help='backup files listed in MCSUAP_manifest to a compressed file with a name corresponding to the date created')

args = parser.parse_args()
#replace with proper working directory as needed
if args.TARGET_DIRECTORY == '0':
	target_directory = Path.cwd()
else:
	target_directory = Path(args.TARGET_DIRECTORY)

#ensure manifest directory exists
try:
	os.mkdir(manifest_dir)
except FileExistsError: #do nothing, we just need this directory to exist
	pass
#create processing directory for temporary files
with tempfile.TemporaryDirectory() as temp_dir:

	#part 1 archiver
	#first we look into the archive folder to determine which files to backup
	
	#next we build the backup file
	
	#name and place it

	#end archiver

	#part 2 updater
	
	versions_manifest_json = get_manifest_json('https://launchermeta.mojang.com/mc/game/version_manifest.json', manifest_versions_filename, args.PULL)

	#now we have the version manifest file, we want *our* versions manifest file
	if args.VERSION == '0':
		if args.RELEASE:
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
	package_manifest_file = get_manifest_json(manifest_url, manifest_package_filename, args.PULL)

	update_flag = args.FORCE
	res_url = package_manifest_file['downloads']['server']['url']
	sha_local = hashlib.sha1()
	try:
		local_jar_file = open(args.SERVER_FILENAME, 'rb')
		sha_local.update(local_jar_file.read())
		if sha_local.hexdigest() == package_manifest_file['downloads']['server']['sha1']:
			print('versions are same')
		else:
			update_flag = True	
		local_jar_file.close()
	except FileNotFoundError:
		update_flag = True
	
	#download a new jar file if sha does not match or force flag is set
	if update_flag and not args.TEST_SHA:
		jar_web_request = urllib.request.urlopen(package_manifest_file['downloads']['server']['url']) 
		server_file = os.path.join(temp_dir, args.SERVER_FILENAME)
		new_jar_file = open(server_file, 'wb')
		shutil.copyfileobj(jar_web_request, new_jar_file)
		new_jar_file.close()
		sha_web = hashlib.sha1()
		new_jar_file = open(server_file, 'rb')
		sha_web.update(new_jar_file.read())
		new_jar_file.close()
		if sha_web.hexdigest() == package_manifest_file['downloads']['server']['sha1']:
			print('sha1 passes')
		else:
			print('sha1 fails, exiting')
			quit()
			#cleanup and quit
			
		#move passing file into place
		shutil.copyfile(server_file, target_directory / Path(args.SERVER_FILENAME))
		
#end updater