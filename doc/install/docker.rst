.. _using-docker:

Using Docker
============

.. note::

   **Docker** :cite:`Mer14` is an open-source project that automates the deployment of Linux applications inside software containers.
   
   
We provide **Docker** images to enable to run **AutoWIG** on various platforms (in particular Windows and MacOS).
For the installation of **Docker**, please refers to its `documentation <https://www.docker.com/products/overview>`_.
Then, you can use the :code:`statiskit/autowig` **Docker** image to run **AutoWIG**:

.. code-block:: console

  $ docker run -it statiskit/autowig
  
For convenience **IPython** and **Jupyter** packages are aleary installed.
You can therefore use:

* The **IPython** console.

  .. code-block:: console
  
    $ ipython

* The **Jupyter** notebook within the **Firefox** web-browser.

  .. code-block:: console
  
    $ jupyter notebook
    
  This requires to able to run Linux GUI Apps:
  
  * On Linux, this is done using the following command in place of the previous command:
  
    .. code-block:: console
  
      $ docker run -ti --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix statiskit/autowig
    
  * On Windows refers to this `post <http://manomarks.github.io/2015/12/03/docker-gui-windows.html>`_.
  
  * On MacOs refers to this `post <https://github.com/docker/docker/issues/8710>`_.

.. note::

  This **Docker** image is generated using the following :download:`../../Dockerfile`.
  
  .. literalinclude:: ../../Dockerfile
     :language: docker
     
  This file is also used with Binder in order to ensure reproducability of presented examples (see :ref:`Examples`).
  More information can be found on the `Binder documentation <http://docs.mybinder.org/>`_.
