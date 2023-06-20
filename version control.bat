@echo off
echo.
set old_qgis_version=1
set new_qgis_version=1
set old_gomap_version=1
set new_gomap_version=1

set /p old_qgis_version="Previous QGIS version (eg. 3.26.2): "
set /p new_qgis_version="Latest QGIS version: "
set /p old_gomap_version="Previous GOMap version (eg. 3.10): "
set /p new_gomap_version="Latest GOMap version: "

cmd /k python "version control.py" %old_qgis_version% %new_qgis_version% %old_gomap_version% %new_gomap_version%

