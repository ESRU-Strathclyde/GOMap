import datetime, glob, os, re, sys

currentDateTime = datetime.datetime.now()
date = currentDateTime.date()
year = date.strftime("%Y")
username = os.path.expanduser('~').split('\\')[2]

# Get command-line arguments defined from "Run shapefile conversion script" batch file
old_qgis_version = sys.argv[1]
new_qgis_version = sys.argv[2]
old_gomap_version = sys.argv[3]
new_gomap_version = sys.argv[4]

gomap_plugin_dir = os.getcwd()
gomap_dev_dir = 'C:/Users/' + username + '/OneDrive - University of Strathclyde/Desktop/GOMap dev/'
gomap_test_dir = gomap_dev_dir + '/GOMap - Test'


def version_control(file, file_path, old_qgis, new_qgis, old_gomap, new_gomap):
	if file == 'metadata':
		with open(file_path, "r+") as f:
			contents = f.read()
			f.seek(0)
			new_contents = re.sub('qgisMinimumVersion=' + str(old_qgis),'qgisMinimumVersion=' + str(new_qgis), str(contents))
			new_contents = re.sub('version=' + str(old_gomap),'version=' + str(new_gomap), str(new_contents))
			f.write(new_contents)
			f.truncate()

	if file == 'about':
		with open(file_path, "r+") as f:
			contents = f.read()
			f.seek(0)
			new_contents = re.sub('QGIS v' + str(old_qgis),'QGIS v' + str(new_qgis), str(contents))
			new_contents = re.sub('GOMap v' + str(old_gomap),'GOMap v' + str(new_gomap), str(new_contents))
			f.write(new_contents)
			f.truncate()

	if file in ['compile_icons', \
				'python_conversion_scripts', \
				'bat_conversion_scripts']:
		with open(file_path, "r+") as f:
			contents = f.read()
			f.seek(0)
			new_contents = re.sub('QGIS ' + str(old_qgis),'QGIS ' + str(new_qgis), str(contents))
			f.write(new_contents)
			f.truncate()

	if file == 'readme':
		with open(file_path, "r+") as f:
			contents = f.read()
			f.seek(0)
			var_string = re.search(r'-(\d{4})', contents)[0]
			# Update year to current
			new_contents = re.sub(var_string, '-' + str(year), contents)
			new_contents = re.sub('QGIS v' + str(old_qgis),'QGIS v' + str(new_qgis), str(new_contents))
			new_contents = re.sub('GOMap v' + str(old_gomap),'GOMap v' + str(new_gomap), str(new_contents))
			f.write(new_contents)
			f.truncate()

	if file == 'version_file':
		with open(file_path, "r+") as f:
			contents = f.read()
			f.seek(0)
			new_contents = re.sub('__VERSION__ = ' + str(old_gomap),'__VERSION__ = ' + str(new_gomap), str(contents))
			f.write(new_contents)
			f.truncate()

	if file == 'python_file':
		with open(file_path, "r+") as f:
			contents = f.read()
			f.seek(0)
			new_contents = re.sub(r'(\d{4} by ESRU)', str(year) + ' by ESRU', str(contents))
			f.write(new_contents)
			f.truncate()

# Version metadata
metadata_file = gomap_plugin_dir + '/metadata.txt'
version_control('metadata', metadata_file, old_qgis_version, new_qgis_version, old_gomap_version, new_gomap_version)

# Version about
about_file = gomap_plugin_dir + '/dockwidgets/ui/about.ui'
version_control('about', about_file, old_qgis_version, new_qgis_version, old_gomap_version, new_gomap_version)

# Version compile and update icons
compile_icons_file = gomap_plugin_dir + '/compile and update icons.bat'
version_control('compile_icons', compile_icons_file, old_qgis_version, new_qgis_version, None, None)

# Version readme file
readme_file = gomap_dev_dir + '/Readme.txt'
version_control('readme', readme_file, old_qgis_version, new_qgis_version, old_gomap_version, new_gomap_version)

# Version VERSION file
version_file = gomap_plugin_dir + '/VERSION.py'
version_control('version_file', version_file, None, None, old_gomap_version, new_gomap_version)

# Version GOMap file
gomap_file = gomap_plugin_dir + '/GOMap.py'
version_control('python_file', gomap_file, None, None, None, None)

# Version python files stored in /tools directory
for python_files in glob.glob(gomap_plugin_dir + "/tools/*.py"):
	version_control('python_file', python_files, None, None, None, None)	

# Version project amd shapefile conversion script files
for py_files in glob.glob(gomap_test_dir + "/Processing scripts/*.py"):
	version_control('python_conversion_scripts', py_files, old_qgis_version, new_qgis_version, None, None)	

# Version project and shapefile conversion batch files
for bat_files in glob.glob(gomap_test_dir + "/Processing scripts/*.bat"):
	version_control('bat_conversion_scripts', bat_files, old_qgis_version, new_qgis_version, None, None)	

print()
print('Versions updated')
