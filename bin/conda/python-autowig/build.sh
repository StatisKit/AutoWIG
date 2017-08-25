set -ev

if [[ "$PY3K" = 1 ]]; then
  2to3 -n -w $SRC_DIR/src/py/autowig
  2to3 -n -w $SRC_DIR/test
fi

python setup.py install --prefix=$PREFIX
mkdir -p $SP_DIR/autowig/site
touch $SP_DIR/autowig/site/__init__.py
mkdir -p $SP_DIR/autowig/site/ASG
mkdir -p $SP_DIR/autowig/site/parser
touch $SP_DIR/autowig/site/parser/__init__.py
mkdir -p $SP_DIR/autowig/site/controller
touch $SP_DIR/autowig/site/controller/__init__.py
mkdir -p $SP_DIR/autowig/site/generator
touch $SP_DIR/autowig/site/generator/__init__.py

mkdir -p $SP_DIR/SCons/site_scons/site_tools
cp $RECIPE_DIR/wig.py $SP_DIR/SCons/site_scons/site_tools/wig.py

set +ev
