Setlocal EnableDelayedExpansion
echo OFF

set DEFAULT_ANACONDA_BUILD_RECIPES=python-clang python-autowig
set DEFAULT_ANACONDA_CHANNELS=statiskit conda-forge
set DEFAULT_ANACONDA_CHANNEL=statiskit

if "%ANACONDA_CHANNELS%" == "" (
    set ANACONDA_CHANNELS=%DEFAULT_ANACONDA_CHANNELS%
) else (
    echo Channels used: %ANACONDA_CHANNELS%
)

if "%ANACONDA_CHANNEL%" == "" (
    set ANACONDA_CHANNEL=%DEFAULT_ANACONDA_CHANNEL%
) else (
    echo Channel used: %ANACONDA_CHANNEL%
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

if "%ANACONDA_USERNAME%" == "" (
    set /p ANACONDA_USERNAME="Username: "
) else (
    echo Username: %ANACONDA_USERNAME%
)

if "%ANACONDA_PASSWORD%" == "" (
    set /p ANACONDA_USERNAME=%ANACONDA_USERNAME%%"'s password: "
) else (
    echo %ANACONDA_USERNAME%'s password: [secure]
)

echo ON

conda install -n root anaconda-client
if errorlevel 1 (
    exit /b 1
)

echo OFF

echo y|anaconda login --username %ANACONDA_USERNAME% --password %ANACONDA_PASSWORD%
if errorlevel 1 (
    exit /b 1
)

echo ON

if "%TOOLCHAIN%" == "" (
    git clone https://gist.github.com/c491cb08d570beeba2c417826a50a9c3.git toolchain
    if errorlevel 1 (
        anaconda logout
        exit /b 1
    )

    cd toolchain
    call config.bat
    if errorlevel 1 (
        cd ..
        anaconda logout
        rmdir toolchain /s /q
        exit /b 1
    )
    cd ..
    rmdir toolchain /s /q
)

for %%i in (%ANACONDA_BUILD_RECIPES%) do (
    for /f %%j in ('conda build %%i %ANACONDA_CHANNEL_FLAGS% %ANACONDA_BUILD_FLAGS% --output') do anaconda upload %%j --user %ANACONDA_CHANNEL% %ANACONDA_UPLOAD_FLAGS%
)

anaconda logout

ECHO OFF
