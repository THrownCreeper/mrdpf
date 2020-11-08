.. mRDPf documentation master file, created by
   sphinx-quickstart on Sun Nov  8 10:04:54 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mRDPf's documentation!
=================================

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents:

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Command Line Interface
========================
.. argparse::
   :module: mrdpf_cli
   :func: get_parser
   :prog: mrdpf_cli

Command Line Interface - Documentation
=======================================
.. automodule:: mrdpf_cli
   :members:

Parsers
=====================
.. automodule:: mrdpf.parsers
   :members:
   :show-inheritance:

Core
=====================
.. automodule:: mrdpf.core
   :members:

Parser Definitions
=====================
.. automodule:: mrdpf.parser_definitions
   :members:

Helpers
=====================
.. automodule:: mrdpf.helpers
   :members:

I/O - General
=====================
.. automodule:: mrdpf.io.general
   :members:

I/O - PLIST
=====================
.. automodule:: mrdpf.io.plist
   :members: