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
        $ conda build PyClangLite/conda/libclang -c statiskit
        $ conda build PyClangLite/conda/libclanglite -c statiskit
        $ conda build PyClangLite/conda/python-clanglite -c statiskit
        $ conda install python-clanglite --use-local -c statiskit

This is done by typing the following commands

.. code-block:: console

    $ git clone https://github.com/StatisKit/AutoWIG.git
    $ conda build AutoWIG/conda/python-clang -c statiskit -c conda-forge
    $ conda build AutoWIG/conda/python-autowig -c statiskit -c conda-forge
    $ conda install python-autowig --use-local -c statiskit -c conda-forge

.. warning::

    This installation has only been tested on **Ubuntu**.
    
 .. note::
 
    If you want to install *Python* packages in develop mode, we recommand to remove corresponding targets using **Conda** and re-install the packages using **Pip**.
    This is done by typing the following commands in a shell:
    
    * For **python-clanglite**.
      
      .. code-block:: console
      
         $ conda remove python-clanglite
         $ pip install -e PyClangLite
         
    * For **python-autowig**.
    
      .. code-block:: console
      
         $ conda remove python-autowig
         $ pip install -e AutoWIG
