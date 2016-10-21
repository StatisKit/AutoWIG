Setlocal EnableDelayedExpansion
echo OFF

set GITHUB_USERNAME=StatisKit
set GITHUB_REPOSITORY=AutoWIG
set DEFAULT_ANACONDA_BUILD_RECIPES=python-clang python-autowig
set DEFAULT_ANACONDA_CHANNELS=statiskit conda-forge

if "%ANACONDA_CHANNELS%" == "" (
    set ANACONDA_CHANNELS=%DEFAULT_ANACONDA_CHANNELS%
) else (
    echo "Channels used: "%ANACONDA_CHANNELS%
)

set ANACONDA_CHANNEL_FLAGS=
for %%i in (%ANACONDA_CHANNELS%) do (
    set "ANACONDA_CHANNEL_FLAGS=!ANACONDA_CHANNEL_FLAGS! -c %%i"
)

if "%ANACONDA_BUILD_RECIPES%" == "" (
    set ANACONDA_BUILD_RECIPES=%DEFAULT_ANACONDA_BUILD_RECIPES%
) else (
    echo Recipes to build: %ANACONDA_BUILD_RECIPES%
)

echo ON

if not exist ..\..\%GITHUB_REPOSITORY% (
    if exist %GITHUB_REPOSITORY% (
        rmdir %GITHUB_REPOSITORY% /s /q
    )
    git clone https://github.com/%GITHUB_USERNAME%/%GITHUB_REPOSITORY%.git
    if errorlevel 1 (
        exit /b 1
    )
    cd %GITHUB_REPOSITORY%/conda
)

git clone https://gist.github.com/c491cb08d570beeba2c417826a50a9c3.git toolchain
if errorlevel 1 (
    if exist %GITHUB_REPOSITORY% (
        rmdir %GITHUB_REPOSITORY% /s /q
    )
    exit /b 1
)
cd toolchain
call config.bat
if errorlevel 1 (
    cd ..
    if exist %GITHUB_REPOSITORY% (
        rmdir %GITHUB_REPOSITORY% /s /q
    )
    rmdir toolchain /s /q
    exit /b 1
)
cd ..
rmdir toolchain /s /q

for %%i in (%ANACONDA_BUILD_RECIPES%) do (
    conda build %%i %ANACONDA_CHANNEL_FLAGS% %ANACONDA_BUILD_FLAGS%
    if errorlevel 1 (
        if exist %GITHUB_REPOSITORY% (
            rmdir %GITHUB_REPOSITORY% /s /q
        )
        exit /b 1
    )
)

if exist %GITHUB_REPOSITORY% (
    rmdir %GITHUB_REPOSITORY% /s /q
)

ECHO OFF
