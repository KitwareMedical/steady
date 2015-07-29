#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#
# Library: steady
#
# Copyright 2015 Kitware, Inc., 28 Corporate Dr., Clifton Park, NY 12065, USA.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################

"""steady is a simple workflow package for Python. It is useful when
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

How does steady know when the inputs have changed? Upon successful
completion of a workflow step, the SHA256 hashes for the executable,
each input file, and each output file in the workflow step is computed
and stored in a cache. The next time the workflow step runs with those
input files and output files, the SHA256 of each of the files is
computed and compared to the cached SHA256 for that file. If any of
the hashes are different, the workflow step is
re-executed. Additionally, the hash for the executable is compared to
the cached hash for the executable, and if this has changed, the
workflow step is recomputed. The reason for this is that changes to
the executable may produce changes in the output, hence the executable
should be monitored for changes.

Quickstart guide
------------------

Here is a simple example of a workflow with a single step. It simply
copies one file to another. If the file has already been copied and
the input file has not changed, there is no need to re-execute the
step::

  from steady import workflow as wf

  command = ['/bin/cp', '-v', '-P', wf.infile('/etc/mtab'), wf.outfile('copiedFile')]
  copyStep = wf.CLIWorkflowStep('CopyStep', command)

  workflow = wf.Workflow([copyStep])

Here, we have set up a single ``CLIWorkflowStep`` and added it to a
workflow. It simply copies the mtab file that lists currently mounted
file systems on linux to a destination file.

The input and output files for this workflow step are passed to the
functions ``workflow.infile()`` and ``workflow.outfile()``,
respectively. These functions decorate the arguments to indicate that
they represent input and output files and that the workflow should pay
special attention to them. Aside from this decoration of input and
output files, arguments to command-line executables are in the same
list format passed to ``subprocess.call()``.

Let's see what happens the first time ``Execute`` is called on
the workflow::

  >>> workflow.Execute(verbose=True)
  Workflow step "CopyStep" needs to be executed.
  Executing CLIWorkflowStep "CopyStep"
  Command: "/bin/cp" "/etc/mtab" "copiedFile"
  '/bin/cp' -> 'copiedFile'

The second time it is executed, ``steady`` notes that the input file
contents have not changed, the output file exists, and the output file
has not changed, so it does not re-run the workflow step::

  >>> workflow.Execute(verbose=True)
  Workflow step "CopyStep" is up-to-date.

Now, let's remove the output file and run the workflow again.

  >>> os.remove('copiedFile')
  >>> workflow.Execute(verbose=True)
  Workflow step "CopyStep" needs to be executed.
  Executing CLIWorkflowStep "CopyStep"
  Command: "/bin/cp" "/etc/mtab" "copiedFile"

The ``steady`` workflow notes the output file has been remove and
re-executes the workflow step. Now, let's change the output file
contents::

  >>> with open('copiedFile', 'w') as f:
  ...     f.write('changed content')
  >>> workflow.Execute(verbose=True)
  Workflow step "CopyStep" needs to be executed.
  Executing CLIWorkflowStep "CopyStep"
  Command: "/bin/cp" "/etc/mtab" "copiedFile"

Again, ``steady`` notes the output file has been changed since the
last execution and re-runs the step.

Cache files
-----------

``steady`` stores a set of cache files for each workflow step in a
cache directory. By default, the cache directory is '/tmp', but you
can change it globally with ``Workflow.SetCacheDirectory``::

  Workflow.SetCacheDirectory('/my/cache/directory')

License
-------

``steady`` is licensed under the Apache 2.0 License. See the
COPYRIGHT.rst file in the top level of the source code.

Obtaining the source code
-------------------------

The latest source code is available at
https://github.com/KitwareMedical/steady.

Additional examples
-------------------

Some additional examples are located in the Examples directory.

Acknowledgements
----------------

``steady`` was developed with funding from NIH grant #5R01HL105241-04.

FAQ
---

**Q**: If I change an argument that is not an input or an output, the
workflow step is not rerun. Why not?

**A**: No hashing and caching of command-line arguments is done. It
could be, but it isn't.

"""

import steady.workflow
from steady.workflow import Workflow, WorkflowStep, CLIWorkflowStep

__version__ = '0.5.0'
