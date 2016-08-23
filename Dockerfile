FROM statiskit/pyclanglite:trusty

# Build or install
ARG BINDER="true"

# Build or install
ARG BUILD="false"

# Test if build or not
ARG BUILD="true"

# Install libraries and packages from AutoWIG
# Clone the repository
RUN [ $BUILD = "true" ] && git clone https://github.com/StatisKit/AutoWIG.git $HOME/AutoWIG || [ $BUILD = "false" ]
RUN [ $BUILD = "true" ] && git -C $HOME/AutoWIG pull || [ $BUILD = "false" ]

## Create a file for anaconda upload
RUN touch $HOME/upload.sh
RUN echo "set -e" >> $HOME/upload.sh
RUN [ $BUILD = "true" ] && echo "$HOME/anaconda2/bin/conda install anaconda-client" >> $HOME/upload.sh || [ $BUILD = "false" ]

## Build python-clang recipe
RUN [ $BUILD = "true" ] && $HOME/anaconda2/bin/conda build $HOME/AutoWIG/conda/python-clang -c statiskit -c conda-forge --no-test || [ $BUILD = "false" ]
RUN [ $BUILD = "true" ] && echo "$HOME/anaconda2/bin/anaconda upload \`conda build $HOME/AutoWIG/conda/python-clang --output\` --user statiskit --force" >> $HOME/upload.sh || [ $BUILD = "false" ]
RUN $HOME/anaconda2/bin/conda install python-clang -c statiskit --use-local

## Build python-autowig recipe
RUN [ $BUILD = "true" ] && $HOME/anaconda2/bin/conda build $HOME/AutoWIG/conda/python-autowig -c statiskit -c conda-forge --no-test || [ $BUILD = "false" ]
RUN [ $BUILD = "true" ] && echo "$HOME/anaconda2/bin/anaconda upload \`conda build $HOME/AutoWIG/conda/python-autowig --output\` --user statiskit --force" >> $HOME/upload.sh || [ $BUILD = "false" ]
RUN $HOME/anaconda2/bin/conda install python-autowig -c statiskit -c conda-forge --use-local

## Finalize file for anaconda upload
# RUN [ $BUILD = "false" ] && echo "rm -rf $HOME/AutoWIG" >> $HOME/upload.sh || [ $BUILD = "true" ]
RUN [ $BUILD = "true" ] && echo "$HOME/anaconda2/bin/conda remove anaconda-client" >> $HOME/upload.sh || [ $BUILD = "false" ]
RUN [ $BUILD = "true" ] echo "$HOME/anaconda2/bin/conda env remove -n _build" >> $HOME/upload.sh || [ $BUILD = "false" ]
RUN [ $BUILD = "true" ] && echo "conda env remove -n _test" >> $HOME/upload.sh || [ $BUILD = "false" ]
RUN echo "$HOME/anaconda2/bin/conda clean --all" >> $HOME/upload.sh
RUN echo "rm -rf $HOME/anaconda2/pkgs" >> $HOME/upload.sh
RUN echo "rm $HOME/upload.sh" >> $HOME/upload.sh
RUN [ $BUILD = "false" ] && /bin/bash $HOME/upload.sh || [ $BUILD = "true" ]

RUN [ $BINDER = "true" ] && $HOME/anaconda2/bin/conda install python-clanglite python-scons gitpython -c statiskit -c conda-forge|| [ $BINDER = "false" ]
