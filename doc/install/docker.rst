.. _test-docker:

Test it with **Docker**
=======================

.. note::

   **Docker** :cite:`Mer14` is an open-source project that automates the deployment of Linux applications inside software containers.
   
   
We provide **Docker** images to enable to run **AutoWIG** on various platforms (in particular Windows and MacOS).
For the installation of **Docker**, please refers to its `documentation <https://www.docker.com/products/overview>`_.
Then, you can use the :code:`statiskit/autowig` **Docker** image to run **AutoWIG**:

.. code-block:: console

  $ docker run -i -t -p 8888:8888 statiskit/autowig
  
A list of all available images can be found `here <https://hub.docker.com/r/statiskit/autowig/tags/>`_.
The image tagged :code:`latest` is unstable, it could be preferable to use the one attached with the AutoWIG paper submitted in Journal of Computational Science (tagged :code:`v1.0.0-alpha`) as follows:

.. code-block:: console

    $ docker run -i -t -p 8888:8888 statiskit/autowig:v1.0.0-alpha
  
For convenience, examples are presented in  **Jupyter** notebooks.
You can therefore proceed -- in the container's terminal -- as follows to run examples:

1. Launch the Jupyter notebook with the following command

   .. code-block:: console
   
       $ jupyter notebook --ip='*' --port=8888 --no-browser
    
2. Copy the URL given in the container's terminal and paste it in your browser.
   This URL should looks like :code:`http://localhost:8888/?token=/[0-9a-fA-F]+/`.

3. Click on the notebooks you want to run (denoted by :code:`*.ipynb`) and then

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

.. warning::

  For some systems as Ubuntu, **Docker** requires root permissions (see this `page <https://docs.docker.com/engine/installation/linux/linux-postinstall/>`_ for more information).
