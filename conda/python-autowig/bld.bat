echo ON

python setup.py install
if errorlevel 1 exit 1
if not exist %SP_DIR%\AutoWIG\site_autowig mkdir %SP_DIR%\SCons\site_autowig
if errorlevel 1 exit 1
if not exist %SP_DIR%\SCons\site_scons\site_tools mkdir %SP_DIR%\SCons\site_scons\site_tools
if errorlevel 1 exit 1
copy %RECIPE_DIR%\autowig.py %SP_DIR%\SCons\site_scons\site_tools\autowig.py
if errorlevel 1 exit 1

echo OFF