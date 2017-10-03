echo ON

if "%PY3K%" == "1" (
  2to3 -n -w %SRC_DIR%\src\py\autowig
  2to3 -n -w %SRC_DIR%\test
)

%PYTHON% setup.py install --prefix=%PREFIX%
if errorlevel 1 exit 1

echo OFF