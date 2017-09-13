echo ON

if "%PY3K%" == "1" (
  2to3 -n -w %SRC_DIR%\src\py\autowig
  2to3 -n -w %SRC_DIR%\test
  2to3 -n -w %RECIPE_DIR%\wig.py
)

python setup.py install --prefix=%PREFIX%
if errorlevel 1 exit 1
rem if exist %SP_DIR%\AutoWIG move %SP_DIR%\AutoWIG %SP_DIR%\autowig /s /q
if not exist %SP_DIR%\autowig\site mkdir %SP_DIR%\autowig\site
if errorlevel 1 exit 1
if not exist %SP_DIR%\autowig\site\__init__.py type NUL > %SP_DIR%\autowig\site\__init__.py
if errorlevel 1 exit 1
if not exist %SP_DIR%\autowig\site\ASG mkdir %SP_DIR%\autowig\site\ASG
if errorlevel 1 exit 1
if not exist %SP_DIR%\autowig\site\parser mkdir %SP_DIR%\autowig\site\parser
if errorlevel 1 exit 1
if not exist %SP_DIR%\autowig\site\parser\__init__.py type NUL > %SP_DIR%\autowig\site\parser\__init__.py
if errorlevel 1 exit 1
if not exist %SP_DIR%\autowig\site\controller mkdir %SP_DIR%\autowig\site\controller
if errorlevel 1 exit 1
if not exist %SP_DIR%\autowig\site\controller\__init__.py type NUL > %SP_DIR%\autowig\site\controller\__init__.py
if errorlevel 1 exit 1
if not exist %SP_DIR%\autowig\site\generator mkdir %SP_DIR%\autowig\site\generator
if errorlevel 1 exit 1
if not exist %SP_DIR%\autowig\site\generator\__init__.py type NUL > %SP_DIR%\autowig\site\generator\__init__.py
if errorlevel 1 exit 1
if not exist %SP_DIR%\SCons\site_scons\site_tools mkdir %SP_DIR%\SCons\site_scons\site_tools
if errorlevel 1 exit 1
copy %RECIPE_DIR%\wig.py %SP_DIR%\SCons\site_scons\site_tools\wig.py
if errorlevel 1 exit 1

echo OFF