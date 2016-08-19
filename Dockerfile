FROM statiskit/ubuntu:trusty

# Clone the repository
RUN git clone https://github.com/StatisKit/AutoWIG.git $HOME/AutoWIG
RUN git -C $HOME/AutoWIG pull

# Build recipes
RUN $HOME/miniconda/bin/conda build $HOME/AutoWIG/conda/python-clang -c statiskit
RUN $HOME/miniconda/bin/conda build $HOME/AutoWIG/conda/python-autowig -c statiskit -c conda-forge

# Create a file for anaconda upload
RUN touch $HOME/upload.sh
RUN echo $HOME/miniconda/bin/anaconda upload \`conda build $HOME/AutoWIG/conda/python-clang --output\` --user statiskit --force >> $HOME/upload.sh
RUN echo $HOME/miniconda/bin/anaconda upload \`conda build $HOME/AutoWIG/conda/python-autowig --output\` --user statiskit --force >> $HOME/upload.sh

# Install packages
RUN $HOME/miniconda/bin/conda install python-clang -c statiskit --use-local
RUN $HOME/miniconda/bin/conda install python-autowig -c statiskit -c conda-forge --use-local