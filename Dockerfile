FROM statiskit/pyclanglite:trusty

# Install libraries and packages from AutoWIG
# Clone the repository
RUN git clone https://github.com/pfernique/AutoWIG.git $HOME/AutoWIG
RUN git -C $HOME/AutoWIG pull
RUN git -C $HOME/AutoWIG checkout mako_coverage

## Create a file for anaconda upload
RUN touch $HOME/upload.sh
RUN echo "set -e" >> $HOME/upload.sh
RUN echo "conda install anaconda-client" >> $HOME/upload.sh

## Build python-clang recipe
# RUN $HOME/miniconda/bin/conda build $HOME/AutoWIG/conda/python-clang -c statiskit -c conda-forge --no-test
# RUN echo "$HOME/miniconda/bin/anaconda upload \`conda build $HOME/AutoWIG/conda/python-clang --output\` --user statiskit --force" >> $HOME/upload.sh

## Build python-autowig recipe
# RUN $HOME/miniconda/bin/conda build $HOME/AutoWIG/conda/python-autowig -c statiskit -c conda-forge --no-test
# RUN echo "$HOME/miniconda/bin/anaconda upload \`conda build $HOME/AutoWIG/conda/python-autowig --output\` --user statiskit --force" >> $HOME/upload.sh

## Finalize file for anaconda upload
RUN echo "rm -rf $HOME/AutoWIG" >> $HOME/upload.sh
RUN echo "conda remove anaconda-client" >> $HOME/upload.sh
RUN echo "conda clean --all" >> $HOME/upload.sh
RUN echo "rm $HOME/upload.sh" >> $HOME/upload.sh

# Install packages
RUN $HOME/miniconda/bin/conda install python-autowig -c statiskit -c conda-forge --use-local