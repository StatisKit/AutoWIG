.. _install-source:

Installation from source code
=============================

For installing **AutoWIG** from source code, please refers to the **StatisKit** `documentation <https://statiskit.rtfd.io>`_ concerning the configuration of the development environment.

.. warning::

    **AutoWIG** and **ClangLite** repositories are considered as submodule of the **StatisKit** repository.
    To update these repositories and benefit from the last development, you must first go to these submodules and pull the code from the actual repositories.
    This step, described below, has to be as soon as the **StatisKit** repository is cloned.

    .. code-block:: bash

        cd StatisKit
        cd share
        cd git
        cd ClangLite
        git pull origin master
        cd ..
        cd AutoWIG
        git pull origin master
        cd ..
        cd ..
        cd ..

