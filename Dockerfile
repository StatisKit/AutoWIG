FROM statiskit/ubuntu:trusty

# Build or install
ARG BUILD="false"

# Clone the repository
RUN git clone https://github.com/StatisKit/AutoWIG.git $HOME/AutoWIG

# Build libraries and packages from AutoWIG
RUN [ $BUILD = "true" ] && cd $HOME/AutoWIG && /bin/bash conda/build.sh || [ $BUILD = "false" ] 

# Install libraries and packages from AutoWIG
RUN [ $BUILD = "false" ] && cd $HOME/AutoWIG && /bin/bash conda/install.sh || [ $BUILD = "true" ]

# Create a file for anaconda post-link
RUN [ -f $HOME/post-link.sh ] && head -n -1 post-link.sh || touch $HOME/post-link.sh && echo "set -e" >> $HOME/post-link.sh
RUN [ $BUILD = "true" ] && echo "conda install anaconda-client" >> $HOME/post-link.sh || [ $BUILD = "false" ]
RUN ([ $BUILD = "true" ] && for recipe in AutoWIG/conda/*/; do echo "anaconda upload \`conda build" $recipe "--output\` --user statiskit --force" >> $HOME/post-link.sh; done;) || [ $BUILD = "false" ]
RUN [ $BUILD = "false" ] && echo "rm -rf AutoWIG" >> $HOME/post-link.sh || [ $BUILD = "true" ]
RUN [ $BUILD = "true" ] && echo "conda remove anaconda-client" >> $HOME/post-link.sh || [ $BUILD = "false" ]
RUN [ $BUILD = "true" ] && echo "conda env remove -n _build" >> $HOME/post-link.sh
RUN [ $BUILD = "true" ] && echo "conda env remove -n _test" >> $HOME/post-link.sh || [ $BUILD = "true" ]
RUN echo "conda clean --all" >> $HOME/post-link.sh
RUN echo "rm $HOME/post-link.sh" >> $HOME/post-link.sh
RUN [ $BUILD = "false" ] && cd $HOME && /bin/bash post-link.sh || [ $BUILD = "true" ]
