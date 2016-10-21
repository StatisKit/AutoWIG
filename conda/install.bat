Setlocal EnableDelayedExpansion
echo OFF

set DEFAULT_ANACONDA_INSTALL_RECIPES=python-clang python-autowig
set DEFAULT_ANACONDA_CHANNELS=statiskit conda-forge
set DEFAULT_ANACONDA_INSTALL_FLAGS=--use-local

if "%ANACONDA_CHANNELS%" == "" (
    set ANACONDA_CHANNELS=%DEFAULT_ANACONDA_CHANNELS%
) else (
    echo Channels used: %ANACONDA_CHANNELS%
)

set ANACONDA_CHANNEL_FLAGS=
for %%i in (%ANACONDA_CHANNELS%) do (
    set "ANACONDA_CHANNEL_FLAGS=!ANACONDA_CHANNEL_FLAGS! -c %%i"
)

if "%ANACONDA_INSTALL_RECIPES%" == "" (
    set ANACONDA_INSTALL_RECIPES=%DEFAULT_ANACONDA_INSTALL_RECIPES%
) else (
    echo Recipes to build: %ANACONDA_INSTALL_RECIPES%
)

if "%ANACONDA_INSTALL_FLAGS%" == "" (
    set ANACONDA_INSTALL_FLAGS=%DEFAULT_ANACONDA_INSTALL_FLAGS%
)

echo ON

for %%i in (%ANACONDA_INSTALL_RECIPES%) do (
    conda install %%i %ANACONDA_CHANNEL_FLAGS% %ANACONDA_INSTALL_FLAGS%
    if errorlevel 1 (
        exit /b 1
    )
)

ECHO OFF
