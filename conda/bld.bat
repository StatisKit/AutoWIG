echo OFF

set REPOSITORY=AutoWIG
set DEFAULT_BUILD_TARGETS=python-clang python-autowig

set ANACONDA_BUILD_FLAGS=-c conda-forge %ANACONDA_BUILD_FLAGS%
if "%ANACONDA_CHANNEL%" == "" (
    set ANACONDA_CHANNEL=statiskit
) else (
    echo "Using anaconda channel: "%ANACONDA_CHANNEL%
    set ANACONDA_BUILD_FLAGS=-c statiskit %ANACONDA_BUILD_FLAGS%
)

if "%BUILD_TARGETS%" == "" (
    set BUILD_TARGETS=%DEFAULT_BUILD_TARGETS%
) else (
    echo "Targets to build: "%BUILD_TARGETS%
)

echo ON

if not exist bld.bat (
    if exist %REPOSITORY% (
        rmdir %REPOSITORY% /s /q
    )
    git clone https://github.com/%ANACONDA_CHANNEL%/%REPOSITORY%.git
    if %errorlevel% neq 0 (
        exit /b %errorlevel%
    )
    cd %REPOSITORY%/conda
)

git clone https://gist.github.com/c491cb08d570beeba2c417826a50a9c3.git toolchain
if %errorlevel% neq 0 (
    if exist %REPOSITORY% (
        rmdir %REPOSITORY% /s /q
    )
    exit /b %errorlevel%
)
cd toolchain
call config.bat
if %errorlevel% neq 0 (
    cd ..
    if exist %REPOSITORY% (
        rmdir %REPOSITORY% /s /q
    )
    rmdir toolchain /s /q
    exit /b %errorlevel%
)
cd ..
rmdir toolchain /s /q

for %%x in (%BUILD_TARGETS%) do (
    conda build %%x -c %ANACONDA_CHANNEL% %ANACONDA_BUILD_FLAGS%
    if %errorlevel% neq 0 (
        if exist %REPOSITORY% (
            rmdir %REPOSITORY% /s /q
        )
        exit /b %errorlevel%
    )
)

if exist %REPOSITORY% (
    rmdir %REPOSITORY% /s /q
)
