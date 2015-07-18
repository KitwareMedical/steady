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
algorithms are organized into a pipeline of workflow steps. Data
communication between steps is dirt simple - it takes place through
the file system. Each step takes zero or more input files and produces
zero or more inputs.

The key feature of this workflow system is that workflow steps are
executed only when needed. This includes when any of the workflow
step's output files do not exist, or when any of the workflow step's
inputs have changed since the last update. How does steady know when
the inputs have changed? Upon successful completion of a workflow
step, the SHA256 checksum for each input in the workflow step is
computed and stored in a cache file. The next time the workflow step
runs with those input files, the SHA256 of the file with the given
file name is computed and compared to the cached SHA256. If any of the
checksums are different, the workflow step is re-executed.

"""

import steady.Workflow
from steady.Workflow import Pipeline, PipelineStep, CommandLineExecutablePipelineStep

__version__ = '0.5.0'
