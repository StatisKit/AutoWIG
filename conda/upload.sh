set +xe

UPLOAD_TARGETS="python-clang python-autowig"

if [[ -z $ANACONDA_USERNAME ]]; then
  read -p "Username: " ANACONDA_USERNAME;
else
  echo "Username: "$ANACONDA_USERNAME;
fi

if [[ -z $ANACONDA_PASSWORD ]]; then
  read -s -p %ANACONDA_USERNAME"'s password: " ANACONDA_PASSWORD;
else
  echo $ANACONDA_USERNAME"'s password: [secure]";
fi

ANACONDA_UPLOAD_FLAGS="-c conda-forge "$ANACONDA_UPLOAD_FLAGS
if [[ -z $ANACONDA_CHANNEL ]]; then
    ANACONDA_CHANNEL="statiskit";
else
    echo "Using anaconda label: "$ANACONDA_CHANNEL;
    ANACONDA_UPLOAD_FLAGS="-c statiskit "$ANACONDA_UPLOAD_FLAGS;
fi

set -x

conda install -n root anaconda-client
if [ $? -ne 0 ]; then
  exit 1;
fi

set +x

#yes | anaconda login --username "$ANACONDA_USERNAME" --password "$ANACONDA_PASSWORD"
yes | anaconda login --username "$ANACONDA_USERNAME" --password "$ANACONDA_PASSWORD"
if [ $? -ne 0 ]; then
  exit 1;
fi

set -x

git clone https://gist.github.com/c491cb08d570beeba2c417826a50a9c3.git toolchain
if [ $? -ne 0 ]; then
    anaconda logout;
    exit 1;
fi
cd toolchain
source config.sh
if [ $? -ne 0 ]; then
    cd ..
    anaconda logout;
    rm -rf toolchain;
    exit 1;
fi
cd ..
rm -rf toolchain

for UPLOAD_TARGET in $UPLOAD_TARGETS; do
  UPLOAD_FILE=`conda build $UPLOAD_TARGET -c $ANACONDA_CHANNEL $ANACONDA_UPLOAD_FLAGS --output`
  anaconda upload ${UPLOAD_FILE%%} --user $ANACONDA_CHANNEL
done

anaconda logout

set +x
