.. _installation:

Installation
============

To install bacalhau you first need to download or clone it from the
`GitHub repository`_\. To clone bacalhau, open a Terminal, go to a
directory of your choice and run: ::

  git clone https://github.com/kcl-ddh/bacalhau.git

To update a previous version, go to the directory where bacalhau is
cloned, and run: ::

  git pull

To install bacalhau into your system, first install the requirements: ::

  pip install -r requirements.txt

After all the requiremnts are installed, install the `NLTK data`_\. Once
all the requirements have been installed run the bacalhau setup
script: ::

  python setup.py install

To verify that bacalhau is installed, type bacalhau on a Terminal and
you should see a message on how to use it. If you don't want to install
bacalhau system wide, it can also be installed on a virtual
environment.

.. _GitHub repository: https://github.com/kcl-ddh/bacalhau/
.. _NLTK data: http://nltk.org/data.html


