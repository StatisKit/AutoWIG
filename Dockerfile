FROM statiskit/pyclanglite:trusty

# Build or install
ARG BINDER="true"

# Build or install
ARG BUILD="false"

RUN [ $BINDER = "true" ] && ln -s $HOME/anaconda2 $HOME/miniconda || [ $BINDER = "false" ]

# Install libraries and packages from AutoWIG
# Clone the repository
RUN [ $BUILD = "true" ] && git clone https://github.com/StatisKit/AutoWIG.git $HOME/AutoWIG || [ $BUILD = "false" ]
RUN [ $BUILD = "true" ] && git -C $HOME/AutoWIG pull || [ $BUILD = "false" ]

## Create a file for anaconda upload
RUN touch $HOME/upload.sh
RUN echo "set -e" >> $HOME/upload.sh
RUN [ $BUILD = "true" ] && echo "$HOME/miniconda/bin/conda install anaconda-client" >> $HOME/upload.sh || [ $BUILD = "false" ]

## Build python-clang recipe
RUN [ $BUILD = "true" ] && $HOME/miniconda/bin/conda build $HOME/AutoWIG/conda/python-clang -c statiskit -c conda-forge || [ $BUILD = "false" ]
RUN [ $BUILD = "true" ] && echo "$HOME/miniconda/bin/anaconda upload \`conda build $HOME/AutoWIG/conda/python-clang --output\` --user statiskit --force" >> $HOME/upload.sh || [ $BUILD = "false" ]
RUN $HOME/miniconda/bin/conda install python-clang -c statiskit --use-local

## Build python-autowig recipe
RUN [ $BUILD = "true" ] && $HOME/miniconda/bin/conda build $HOME/AutoWIG/conda/python-autowig -c statiskit -c conda-forge || [ $BUILD = "false" ]
RUN [ $BUILD = "true" ] && echo "$HOME/miniconda/bin/anaconda upload \`conda build $HOME/AutoWIG/conda/python-autowig --output\` --user statiskit --force" >> $HOME/upload.sh || [ $BUILD = "false" ]
RUN $HOME/miniconda/bin/conda install python-autowig -c statiskit -c conda-forge --use-local
RUN [ $BUILD = "true" ] && $HOME/miniconda/bin/conda remove python-autowig || [ $BUILD = "false" ]
RUN [ $BUILD = "true" ] && $HOME/miniconda/bin/pip install -e AutoWIG || [ $BUILD = "false" ]

## Finalize file for anaconda upload
# RUN [ $BUILD = "false" ] && echo "rm -rf $HOME/AutoWIG" >> $HOME/upload.sh || [ $BUILD = "true" ]
RUN [ $BUILD = "true" ] && echo "$HOME/miniconda/bin/conda remove anaconda-client" >> $HOME/upload.sh || [ $BUILD = "false" ]
RUN [ $BUILD = "true" ] && echo "$HOME/miniconda/bin/conda env remove -n _build" >> $HOME/upload.sh || [ $BUILD = "false" ]
RUN [ $BUILD = "true" ] && echo "$HOME/miniconda/bin/conda env remove -n _test" >> $HOME/upload.sh || [ $BUILD = "false" ]
RUN echo "$HOME/miniconda/bin/conda clean --all" >> $HOME/upload.sh
RUN echo "rm -rf $HOME/miniconda/pkgs" >> $HOME/upload.sh
RUN echo "rm $HOME/upload.sh" >> $HOME/upload.sh
# RUN [ $BUILD = "false" ] && /bin/bash $HOME/upload.sh || [ $BUILD = "true" ]

RUN [ $BINDER = "true" ] && $HOME/miniconda/bin/conda install python-clanglite python-scons gitpython -c statiskit -c conda-forge|| [ $BINDER = "false" ]
RUN [ $BINDER = "true" ] && rm $HOME/miniconda || [ $BINDER = "false" ]
RUN [ $BINDER = "true" ] && ls $HOME || [ $BINDER = "false" ]
RUN [ $BINDER = "true" ] && ls $HOME/notebooks || [ $BINDER = "false" ]
RUN [ $BINDER = "true" ] && mv $HOME/notebooks/doc/examples/index.ipynb $HOME/notebooks/index.ipynb || [ $BINDER = "false" ]
RUN [ $BINDER = "true" ] && sed -i 's/\[\(.*\)\](\(.*\)\.ipynb)/[\1](.\/doc\/examples\/\2.ipynb)/g' index.ipynb || [ $BINDER = "false" ]
