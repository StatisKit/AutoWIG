.. ................................................................................ ..
..                                                                                  ..
..  AutoWIG: Automatic Wrapper and Interface Generator                              ..
..                                                                                  ..
..  Homepage: http://autowig.readthedocs.io                                         ..
..                                                                                  ..
..  Copyright (c) 2016 Pierre Fernique                                              ..
..                                                                                  ..
..  This software is distributed under the CeCILL license. You should have        ..
..  received a copy of the legalcode along with this work. If not, see              ..
..  <http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html>.                  ..
..                                                                                  ..
..  File authors: Pierre Fernique <pfernique@gmail.com> (5)                         ..
..                                                                                  ..
.. ................................................................................ ..

Installation from Anaconda Cloud
================================
    
**AutoWIG** is available on the *StatisKit* `channel <https://anaconda.org/StatisKit>`_ of `Anaconda <https://www.continuum.io/downloads>`_ for Linux.
To install the latest version with Anaconda or conda you should use the following command (see `conda documentation <http://conda.pydata.org/docs/>`_ for more information).

.. literalinclude:: ../../conda/install.sh
   :lines: 4-

.. warning::

    This installation can fail for compiler compatibility reasons.
    In such cases refers to :
    
    * the :ref:`install-source` section,
    * the :ref:`using-docker` section.

.. note::

    When installing **AutoWIG** from Anaconda cloud, it is highly recommanded to install **PyClangLite** from Anaconda cloud (refers to its `installation guide <http://pyclanglite.readthedocs.io/en/latest/anaconda.html>`_).
