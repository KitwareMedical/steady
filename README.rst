``steady`` is a simple workflow package for Python. It is useful when
you have a series of processing steps to perform on data sets, and
each processing step is in the form of a command-line executable.

Steady's design is based on the assumption that your workflow involves
of one or more input files being transformed by a series of algorithms
into one or more intermediate and final outputs. The algorithms are
organized into a workflow of individual steps. Each step takes zero or
more input files and produces zero or more output files. Data
communication between steps is dirt simple - it takes place through
the file system. No explicit linkages between workflow steps are
specified - all dependencies are implicit and can be resolved by
ordering the steps appropriately.

The key feature of this system is that workflow steps are executed
*only when needed*. This includes the following situations:

* when any of the workflow step's output files do not exist;

* when the content of any of the workflow step's output files has been
  modified since last execution;

* when the content of any of the workflow step's inputs have changed
  since the last update;

* when the external executable has changed.
