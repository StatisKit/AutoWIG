set +xe

GITHUB_USERNAME="StatisKit"
GITHUB_REPOSITORY="AutoWIG"
DEFAULT_ANACONDA_BUILD_RECIPES="python-clang python-autowig"
DEFAULT_ANACONDA_CHANNELS="statiskit conda-forge"

if [[ -z $ANACONDA_CHANNELS ]]; then
    ANACONDA_CHANNELS=$DEFAULT_ANACONDA_CHANNELS
else
    echo "Channels used: "$ANACONDA_CHANNELS
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

set -x

if [[ ! -d ../../$GITHUB_REPOSITORY ]]; then
    if [[ -d "$GITHUB_REPOSITORY" ]]; then
        rm -rf $GITHUB_REPOSITORY
    fi
    git clone https://github.com/$GITHUB_USERNAME/$GITHUB_REPOSITORY.git
    if [ $? -ne 0 ]; then
        exit 1
    fi
    cd PkgTk/conda
fi

if [[ -z $TOOLCHAIN ]]; then
    git clone https://gist.github.com/c491cb08d570beeba2c417826a50a9c3.git toolchain
    if [ $? -ne 0 ]; then
        if [[ -d "$GITHUB_REPOSITORY" ]]; then
            rm -rf $GITHUB_REPOSITORY
        fi
        exit 1
    fi
    cd toolchain
    source config.sh
    if [ $? -ne 0 ]; then
        cd ..
        if [[ -d "$GITHUB_REPOSITORY" ]]; then
            rm -rf $GITHUB_REPOSITORY
        fi
        rm -rf toolchain
        exit 1
        fi
    cd ..
    rm -rf toolchain
fi

for ANACONDA_BUILD_RECIPE in $ANACONDA_BUILD_RECIPES; do
  conda build $ANACONDA_BUILD_RECIPE $ANACONDA_CHANNEL_FLAGS $ANACONDA_BUILD_FLAGS
  if [ $? -ne 0 ]; then
    if [[ -d "$GITHUB_REPOSITORY" ]]; then
        rm -rf $GITHUB_REPOSITORY
    fi
    exit 1
  fi
done

if [[ -d "$GITHUB_REPOSITORY" ]]; then
    rm -rf $GITHUB_REPOSITORY
fi

set +x