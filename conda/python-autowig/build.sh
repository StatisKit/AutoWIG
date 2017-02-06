set -ev

python setup.py install --prefix=$PREFIX
mkdir -p $SP_DIR/autowig/site_autowig
mkdir -p $SP_DIR/SCons/site_scons/site_tools
cp $RECIPE_DIR/autowig.py $SP_DIR/SCons/site_scons/site_tools/autowig.py

set +ev