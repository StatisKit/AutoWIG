FROM ubuntu:14.04

# Update the OS
RUN apt-get update

# Upgrade the OS
RUN apt-get -y upgrade

# Install useful tools
RUN apt-get install -y vim build-essential git wget curl
# firefox
RUN apt-get autoremove

# Add user for future work
RUN useradd -m main --shell /bin/bash && echo "main:main" | chpasswd && adduser main sudo

# select created user
USER main
WORKDIR /home/main

# Install miniconda2
RUN wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh \
         -O $HOME/miniconda.sh
RUN bash $HOME/miniconda.sh -b -p $HOME/miniconda
RUN rm $HOME/miniconda.sh
ENV PATH /home/main/miniconda/bin:$PATH
RUN conda config --set always_yes yes --set changeps1 no
RUN conda update -q conda
RUN conda info -a

ENV TOOLCHAIN "gnu48"

RUN conda config --set always_yes yes --set changeps1 no
RUN conda update -q conda
RUN conda info -a
RUN conda install conda-build

RUN git config --global alias.co checkout
RUN git config --global alias.br branch
RUN git config --global alias.ci commit
RUN git config --global alias.st status
RUN git config --global alias.unstage 'reset HEAD --'
RUN git config --global alias.last 'log -1 HEAD'

RUN touch autowig.yml
RUN echo "name: autowig" >> autowig.yml
RUN echo "channels:" >> autowig.yml
RUN echo "    - statiskit" >> autowig.yml
RUN echo "    - conda-forge" >> autowig.yml
RUN echo "    - defaults" >> autowig.yml
RUN echo "dependencies:" >> autowig.yml
RUN echo "    - python-autowig" >> autowig.yml
RUN echo "    - python-clanglite" >> autowig.yml
RUN echo "    - python-scons" >> autowig.yml
RUN echo "    - ipython" >> autowig.yml
RUN echo "    - jupyter" >> autowig.yml
RUN echo "    - matplotlib" >> autowig.yml
RUN echo "    - pygments" >> autowig.yml

RUN conda env create -f autowig.yml
RUN rm autowig.yml
RUN /bin/bash -c "source activate autowig && pip install environment_kernels"

RUN git clone https://gist.github.com/b4d9222c60ecb67d011425c800980723.git examples
WORKDIR /home/main/examples
RUN sed -i'' -e "s|jupyter notebook index.ipynb|jupyter notebook index.ipynb --ip='*' --port=8888 --no-browser|g" run.sh
