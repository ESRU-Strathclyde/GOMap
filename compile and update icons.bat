@echo off
call "C:\Program Files\QGIS 3.28.1\bin\o4w_env.bat"
Rem "C:\Program Files\QGIS 3.28.1\bin\qt5_env.bat"
Rem "C:\Program Files\QGIS 3.28.1\bin\py3_env.bat"

@echo on
pyrcc5 -o resources.py resources.qrc