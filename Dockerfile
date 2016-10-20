FROM statiskit/ubuntu:14.04

RUN git clone https://github.com/StatisKit/PyClangLite.git $HOME/PyClangLite
RUN cd $HOME/PyClangLite/conda && /bin/bash install.sh
RUN rm -rf $HOME/PyClangLite

RUN git clone https://github.com/StatisKit/AutoWIG.git $HOME/AutoWIG
RUN cd $HOME/AutoWIG/conda && /bin/bash install.sh
RUN rm -rf $HOME/AutoWIG

RUN conda install python-gitpython python-scons --use-local -c statiskit -c conda-forge