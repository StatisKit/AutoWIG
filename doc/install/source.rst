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

.. Copyright [2017-2018] UMR MISTEA INRA, UMR LEPSE INRA,                ..
..                       UMR AGAP CIRAD, EPI Virtual Plants Inria        ..
.. Copyright [2015-2016] UMR AGAP CIRAD, EPI Virtual Plants Inria        ..
..                                                                       ..
.. This file is part of the AutoWIG project. More information can be     ..
.. found at                                                              ..
..                                                                       ..
..     http://autowig.rtfd.io                                            ..
..                                                                       ..
.. The Apache Software Foundation (ASF) licenses this file to you under  ..
.. the Apache License, Version 2.0 (the "License"); you may not use this ..
.. file except in compliance with the License. You should have received  ..
.. a copy of the Apache License, Version 2.0 along with this file; see   ..
.. the file LICENSE. If not, you may obtain a copy of the License at     ..
..                                                                       ..
..     http://www.apache.org/licenses/LICENSE-2.0                        ..
..                                                                       ..
.. Unless required by applicable law or agreed to in writing, software   ..
.. distributed under the License is distributed on an "AS IS" BASIS,     ..
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or       ..
.. mplied. See the License for the specific language governing           ..
.. permissions and limitations under the License.                        ..

        cd AutoWIG
        git pull origin master
        cd ..
        cd ..
        cd ..
        cd ..

