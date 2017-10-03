set -ev

if [[ "$PY3K" = 1 ]]; then
  2to3 -n -w $SRC_DIR/src/py/autowig
  2to3 -n -w $SRC_DIR/test
fi

$PYTHON setup.py install --prefix=$PREFIX

set +ev
