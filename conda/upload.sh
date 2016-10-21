set +xe

DEFAULT_ANACONDA_BUILD_RECIPES="python-clang python-autowig"
DEFAULT_ANACONDA_CHANNELS="statiskit conda-forge"
DEFAULT_ANACONDA_CHANNEL="statiskit"

if [[ -z $ANACONDA_CHANNELS ]]; then
    ANACONDA_CHANNELS=$DEFAULT_ANACONDA_CHANNELS
else
    echo "Channels used: "$ANACONDA_CHANNELS
fi

if [[ -z $ANACONDA_CHANNEL ]]; then
    ANACONDA_CHANNEL=$DEFAULT_ANACONDA_CHANNEL
else
    echo "Channel used: "$ANACONDA_CHANNEL
fi

ANACONDA_CHANNEL_FLAGS=""
for ANACONDA_CHANNEL_FLAG in $ANACONDA_CHANNELS; do
    ANACONDA_CHANNEL_FLAGS=$ANACONDA_CHANNEL_FLAGS" -c "$ANACONDA_CHANNEL_FLAG
done

if [[ -z $ANACONDA_BUILD_RECIPES ]]; then
    ANACONDA_BUILD_RECIPES=$DEFAULT_ANACONDA_BUILD_RECIPES
else
    echo "Recipes to build: "$ANACONDA_BUILD_RECIPES
fi

if [[ -z $ANACONDA_USERNAME ]]; then
  read -p "Username: " ANACONDA_USERNAME
else
  echo "Username: "$ANACONDA_USERNAME
fi

if [[ -z $ANACONDA_PASSWORD ]]; then
  read -s -p $ANACONDA_USERNAME"'s password: " ANACONDA_PASSWORD
else
  echo $ANACONDA_USERNAME"'s password: [secure]"
fi

set -x

conda install -n root anaconda-client
if [ $? -ne 0 ]; then
  exit 1
fi

set +x

yes | anaconda login --username "$ANACONDA_USERNAME" --password "$ANACONDA_PASSWORD"
if [ $? -ne 0 ]; then
  exit 1
fi

set -x

if [[ -z $TOOLCHAIN ]]; then
    git clone https://gist.github.com/c491cb08d570beeba2c417826a50a9c3.git toolchain
    if [ $? -ne 0 ]; then
        anaconda logout;
        exit 1
    fi
    cd toolchain
    source config.sh
    if [ $? -ne 0 ]; then
        cd ..
        anaconda logout
        rm -rf toolchain
        exit 1
    fi
    cd ..
    rm -rf toolchain
fi

for ANACONDA_BUILD_RECIPE in $ANACONDA_BUILD_RECIPES; do
  ANACONDA_UPLOAD_RECIPE=`conda build $ANACONDA_BUILD_RECIPE $ANACONDA_CHANNEL_FLAGS $ANACONDA_BUILD_FLAGS --output`
  anaconda upload ${ANACONDA_UPLOAD_RECIPE%%} --user $ANACONDA_CHANNEL $ANACONDA_UPLOAD_FLAGS
done

anaconda logout

set +x