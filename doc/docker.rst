.. _use-docker:

Use Docker
==========

Docker is an open-source project that automates the deployment of Linux applications inside software containers.
We provide **Docker** images to enable to run **AutoWIG** on various platforms (in particular Windows and MacOS).
For the installation of **Docker**, please refers to its `documentation <https://www.docker.com/products/overview>`_.
Then, you can use the :code:`statiskit/ubuntu:autowig` **Docker** image to run **AutoWIG**.

.. code-block:: console

  docker run -it statiskit/ubuntu:autowig
  
Note that, for convenience **IPython** and **Jupyter** packages are installed.
You can therefore use:

* The **IPython** console.

  .. code-block:: console
  
    ipython

* The **Jupyter** notebook within the **Firefox** web-browser.

  .. code-block:: console
  
    jupyter notebook
