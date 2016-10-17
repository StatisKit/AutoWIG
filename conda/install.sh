set +xe

DEFAULT_INSTALL_TARGETS="python-clang python-autowig"

ANACONDA_INSTALL_FLAGS="-c conda-forge "$ANACONDA_INSTALL_FLAGS
if [[ -z $ANACONDA_CHANNEL ]]; then
    ANACONDA_CHANNEL="statiskit"
else
    echo "Using anaconda channel: "$ANACONDA_CHANNEL;
    ANACONDA_INSTALL_FLAGS="-c statiskit "$ANACONDA_INSTALL_FLAGS;
fi

if [[ -z $INSTALL_TARGETS ]]; then
    INSTALL_TARGETS=$DEFAULT_INSTALL_TARGETS;
else
    echo "Targets to install: "$INSTALL_TARGETS;
fi

set -x

for INSTALL_TARGET in $INSTALL_TARGETS; do
  conda install $INSTALL_TARGET --use-local -c $ANACONDA_CHANNEL $ANACONDA_INSTALL_FLAGS
  if [ $? -ne 0 ]; then
    exit 1;
  fi
done

set +x
