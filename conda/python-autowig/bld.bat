echo ON

python setup.py install --prefix=%PREFIX%
if errorlevel 1 exit 1
if not exist %SP_DIR%\AutoWIG\site mkdir %SP_DIR%\AutoWIG\site
if errorlevel 1 exit 1
if not exist %SP_DIR%\AutoWIG\site\__init__.py type NUL > %SP_DIR%\AutoWIG\site\__init__.py
if errorlevel 1 exit 1
if not exist %SP_DIR%\AutoWIG\site\ASG mkdir %SP_DIR%\AutoWIG\site\ASG
if errorlevel 1 exit 1
if not exist %SP_DIR%\AutoWIG\site\parser mkdir %SP_DIR%\AutoWIG\site\parser
if errorlevel 1 exit 1
if not exist %SP_DIR%\AutoWIG\site\parser\__init__.py type NUL > %SP_DIR%\AutoWIG\site\parser\__init__.py
if errorlevel 1 exit 1
if not exist %SP_DIR%\AutoWIG\site\controller mkdir %SP_DIR%\AutoWIG\site\controller
if errorlevel 1 exit 1
if not exist %SP_DIR%\AutoWIG\site\controller\__init__.py type NUL > %SP_DIR%\AutoWIG\site\controller\__init__.py
if errorlevel 1 exit 1
if not exist %SP_DIR%\AutoWIG\site\generator mkdir %SP_DIR%\AutoWIG\site\generator
if errorlevel 1 exit 1
if not exist %SP_DIR%\AutoWIG\site\generator\__init__.py type NUL > %SP_DIR%\AutoWIG\site\generator\__init__.py
if errorlevel 1 exit 1
if not exist %SP_DIR%\SCons\site_scons\site_tools mkdir %SP_DIR%\SCons\site_scons\site_tools
if errorlevel 1 exit 1
copy %RECIPE_DIR%\wig.py %SP_DIR%\SCons\site_scons\site_tools\wig.py
if errorlevel 1 exit 1

echo OFF