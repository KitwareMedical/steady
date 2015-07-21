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

Steady follows a data-flow paradigm where one or more input files is
transformed by a series of algorithms into one or more outputs. The
algorithms are organized into a pipeline of workflow steps. Each step
takes zero or more input files and produces zero or more outputs.
Data communication between steps is dirt simple - it takes place
through the file system.

The key feature of this workflow system is that workflow steps are
executed *only when needed*. This includes the following situations:

* when any of the workflow step's output files do not exist;

* when the content of any of the workflow step's output files has been
  modified since last execution;

* when the content of any of the workflow step's inputs have changed
  since the last update;

* when the external executable has changed.

How does steady know when the inputs have changed? Upon successful
completion of a workflow step, the SHA256 hashes for the executable,
each input file, and each output file in the workflow step is computed
and stored in separate cache files. The next time the workflow step
runs with those input files and output files, the SHA256 of each of
the files is computed and compared to the cached SHA256 for that
file. If any of the hashes are different, the workflow step is
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

  from steady.workflow import *

  inputFile = '/etc/mtab'
  outputFile = 'copiedFile'
  args = ['-v', 'P', inputFile, outputFile]
  copyStep = CommandLineExecutablePipelineStep('CopyStep',
                                               executable='/bin/cp',
                                               inputs=[inputFile],
                                               outputs=[outputFile],
                                               args=args)

  pipeline = Pipeline([copyStep])

Here, we have set up a single ``CommandLineExecutablePipelineStep``
and added it to a pipeline. It simply copies the mtab file that lists
currently mounted file systems on linux to a destination file.

Let's see what happens the first time ``Execute`` is called on
the pipeline::

  >>> pipeline.Execute(verbose=True)
  Workflow step "CopyStep" needs to be executed.
  Executing CommandLineExecutablePipelineStep "CopyStep"
  Command: "/bin/cp" "/etc/mtab" "copiedFile"

The second time it is executed, ``steady`` notes that the input file
contents have not changed and the output file exists, so it does not
re-run the pipeline step::

  >>> pipeline.Execute(verbose=True)
  Workflow step "CopyStep" is up-to-date.

Notice that the input and output files seem to be listed twice, once
in the ``inputs``/``outputs`` parameter and once in the ``args``
parameter. This redundancy is needed because not all executables take
input and output arguments in the same order, some require inputs and
outputs to be noted with a flag (e.g., ``--input``) so ``steady``
doesn't make any assumptions about how to arrange input and output
files in the arguments list passed to an external executable. However,
``steady`` still needs to know which files are inputs and outputs, so
each step needs an explicit list of inputs and outputs.

Now, let's remove the output file and run the workflow again.

  >>> os.remove(outputFile)
  >>> pipeline.Execute(verbose=True)
  Workflow step "CopyStep" needs to be executed.
  Executing CommandLineExecutablePipelineStep "CopyStep"
  Command: "/bin/cp" "/etc/mtab" "copiedFile"

``steady`` notes the output file has been remove and re-executes the
pipeline step. Now, let's change the output file contents::

  >>> with open(outputFile, 'w') as f:
  ...     f.write('changed content')
  >>> pipeline.Execute(verbose=True)
  Workflow step "CopyStep" needs to be executed.
  Executing CommandLineExecutablePipelineStep "CopyStep"
  Command: "/bin/cp" "/etc/mtab" "copiedFile"

Again, ``steady`` notes the output file has been changed since the
last execution and runs the step again.

As a side note, it is possible to set properties of
CommandLineExecutablePipelineSteps directly, e.g.::

  >>> copyStep.Executable = '/bin/cp'
  >>> copyStep.Inputs = [inputFile]
  >>> copyStep.Outputs = [outputFile]
  >>> copyStep.Arguments = ['-v', 'P', inputFile, outputFile]

Cache files
-----------

``steady`` stores a set of cache files for each pipeline step in a
cache directory. By default, the cache directory is '/tmp', but you
can change it globally with ``Pipeline.SetCacheDirectory``::

  Pipeline.SetCacheDirectory('/my/cache/directory')

Additional examples
-------------------

Some additional examples are located in the Examples directory.

FAQ
---

**Q**: Why do I need to list the inputs, outputs, and arguments
saparately when the arguments are the inputs and outputs?

**A**: Your external process may take arguments besides input and
output files, and it may require the input argument(s) and output
argument(s) to be listed in a specific order.

**Q**: If I change an argument that is not an input or an output, the
pipeline step is not rerun. Why not?

**A**: No hashing and caching of command-line arguments is done. It
could be, but it isn't.

"""

import steady.workflow
from steady.workflow import Pipeline, PipelineStep, CommandLineExecutablePipelineStep

__version__ = '0.5.0'
