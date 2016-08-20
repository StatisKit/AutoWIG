.. _install-source:

Installation from source code
=============================

In order to install **AutoWIG** from source code we recommand to use:

* The source code available on *GitHub* (see `Git <https://git-scm.com/>`_ and `GitHub <https://github.com/>`_ websites for more information).
* The conda recipes present on *GitHub* repositories (see `conda <http://conda.pydata.org/docs/>`_ website for more information).
 
.. note::

    When installing **AutoWIG** from source code, it is highly recommanded to first install **PyClangLite** from source code.
    This is done by typing the following commands.

    .. code-block:: console

        $ git clone https://github.com/StatisKit/PyClangLite.git
        $ conda build PyClangLite/conda/libclang
        $ conda build PyClangLite/conda/libclanglite
        $ conda build PyClangLite/conda/python-clanglite
        $ conda install python-clanglite


This is done by typing the following commands

.. code-block:: console

    $ git clone https://github.com/StatisKit/AutoWIG.git
    $ conda build AutoWIG/conda/python-clang
    $ conda build AutoWIG/conda/python-autowig
    $ conda install python-autowig


.. warning::

    This installation has only been tested on **Ubuntu**.
    Here is the :code:`Dockerfile` for generating a **Ubuntu 14.04** `Docker <https://www.docker.com/>`_ image
    that enables an user to install and run **AutoWIG**.

    .. code-block:: docker


        FROM ubuntu:14.04

        # Update the OS
        RUN apt-get update

        # Install useful tools
        RUN apt-get install -y build-essential git wget

        # Add user for future work
        RUN useradd -ms /bin/bash conda-user

        # select created user
        USER conda-user

        # Install miniconda
        RUN wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O \
          $HOME/miniconda.sh
        RUN bash $HOME/miniconda.sh -b -p $HOME/miniconda
        RUN echo 'export PATH=$PATH:$HOME/miniconda/bin' >> $HOME/.bashrc 
        RUN $HOME/miniconda/bin/conda config --set always_yes yes --set changeps1 no
        RUN $HOME/miniconda/bin/conda update -q conda
        RUN $HOME/miniconda/bin/conda info -a

        # Install conda-build
        RUN $HOME/miniconda/bin/conda install conda-build
