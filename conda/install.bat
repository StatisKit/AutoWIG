echo OFF

set DEFAULT_INSTALL_TARGETS=python-clang python-autowig

set ANACONDA_INSTALL_FLAGS=-c conda-forge %ANACONDA_INSTALL_FLAGS%
if "%ANACONDA_CHANNEL%" == "" (
  set ANACONDA_CHANNEL=statiskit
) else (
  echo Using anaconda channel: %ANACONDA_CHANNEL%
set ANACONDA_INSTALL_FLAGS=-c statiskit %ANACONDA_INSTALL_FLAGS%
)

if "%INSTALL_TARGETS%" == "" (
  set INSTALL_TARGETS=%DEFAULT_INSTALL_TARGETS%
) else (  
  echo "Targets to install: "%INSTALL_TARGETS%
)

echo ON

for %%x in (%INSTALL_TARGETS%) do (
  conda install %%x --use-local -c %ANACONDA_CHANNEL% %ANACONDA_INSTALL_FLAGS%
  if %errorlevel% neq 0 (
    exit /b %errorlevel%
  )
)
