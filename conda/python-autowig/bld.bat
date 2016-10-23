echo ON

if "%PY3K%" == "1" (
  2to3 --output-dir=src\py3 -W -n src\py
  rmdir src\py /s /q
  move src\py3 src\py
  2to3 --output-dir=test3 -W -n test
  rmdir test /s /q
  move test3 test
)

python setup.py install