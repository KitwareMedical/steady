.. Steady documentation master file, created by
   sphinx-quickstart on Tue Jun  2 21:06:55 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Steady's documentation!
==================================

Contents:

.. toctree::
   :maxdepth: 2

.. automodule:: steady
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Introduction
------------

Steady is a simple workflow package for Python. It is useful when you have a
series of processing steps to perform on data sets, and each processing step is
in the form of a command-line executable.

Steady follows a data-flow paradigm where one or more input files is
transformed by a series of algorithms into one or more outputs. The algorithms
are organized into a pipeline of workflow steps. Data communication between
steps is dirt simple - it takes place through the file system. Each step takes
zero or more input files and produces zero or more inputs.

The key feature of this workflow system is that workflow steps are executed
only when needed. This includes, when any of the workflow step's output files do
not exist or when any of the workflow step's inputs have changed since the last
update. How does steady know when the inputs have changed? Upon successful
completion of a workflow step, the SHA256 checksum for each input in the workflow
step is computed and stored in a cache file. The next time the workflow step runs
with those input files, the SHA256 of the file with the given file name is computed
and compared to the cached SHA256. If any of the checksums are different, the
workflow step is re-executed.
