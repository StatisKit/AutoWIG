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
..  File authors: Pierre Fernique <pfernique@gmail.com> (12)                        ..
..                                                                                  ..
.. ................................................................................ ..

.. _using-docker:

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
The image tagged :code:`latest` is unstable, it could be preferable to use the one attached with the AutoWIG paper submitted in Journal of Computational Science.

For convenience, examples are presented in  **Jupyter** notebooks.
You can therefore proceed as follows to run examples:

1. Launch the Jupyter notebook with the following command

   .. code-block:: console
   
    $ jupyter notebook --ip='*' --port=8888 --no-browser
    
2. Copy the URL given in your terminal and paste it in your browser.

3. Click on the notebooks you want to run (denoted by *.ipynb) and then
click on Run All item of the Cell top menu bar.       
