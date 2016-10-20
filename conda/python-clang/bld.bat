if "%PY3K%" == "1" (
  2to3 --output-dir=bindings\python\clang3 -W -n bindings\python\clang
  rmdir bindings\python\clang /s /q
  move bindings\python\clang3 bindings\python\clang
)

mkdir %SP_DIR%\clang
xcopy bindings\python\clang %SP_DIR%\clang /sy