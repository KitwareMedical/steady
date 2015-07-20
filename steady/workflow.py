import glob
import hashlib
import os
import subprocess
import sys

###############################################################################
#
# Library: steady
#
# Copyright 2010 Kitware, Inc., 28 Corporate Dr., Clifton Park, NY 12065, USA.
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

#############################################################################
class PipelineStep(object):
    """Base class for pipeline steps.

    :param name: Name of the PipelineStep. It should be unique.

    """
    def __init__(self, name):
        self.Name = name

    def NeedsUpdate(self):
        """
        Indicates whether the pipeline step needs to be updated.
        """
        return False

#############################################################################
class CommandLineExecutablePipelineStep(PipelineStep):
    """Pipeline steps for a command-line executable.

    """
    def __init__(self, name):
        super(CommandLineExecutablePipelineStep, self).__init__(name)
        self.Executable = ''
        self.Arguments = []
        self.InputFiles = []
        self.OutputFiles = []

    def Execute(self, verbose=False):
        """Run the pipeline step.

        :param verbose: If True, produce verbose output while running,
        including the command that is run when this step is
        executed. Otherwise, minimize output.

        """
        sys.stdout.write('Executing CommandLineExecutablePipelineStep "%s"\n' % self.Name)
        args = [self.Executable] + self.Arguments

        if (verbose):
            sys.stdout.write('Command: ')
            sys.stdout.write(' '.join(['"%s"' % arg for arg in args]))
            sys.stdout.write('\n')

        try:
            returnCode = subprocess.call(args)
            if (returnCode != 0):
              print 'Process returned error code', returnCode
              return False

        except:
            print 'Failed to run command-line executable', args
            return False

        try:
            self._WriteSHA256Files()
        except:
            print 'Failed to write SHA 256 files for input'
            return False

        return True

    def NeedsUpdate(self):
        """Returns True if any of the SHA256 hashes of the current InputFiles
        differ from the previously cached SHA256 hashes for those
        inputs, if the SHA256 of the Executable has changed, or if any
        of the OutputFiles are missing or have changed.

        """
        filesToCheck = [self.Executable]
        filesToCheck.extend(self.InputFiles)
        filesToCheck.extend(self.OutputFiles)

        for inputFileName in filesToCheck:
            sha256FileName = self._GetSHA256FileName(inputFileName)

            # Need update if SHA256 file for an input file doesn't exist
            if (not os.path.isfile(sha256FileName)):
                return True

            # Need update if SHA256 file for an input file is different from
            # a freshly computed SHA256 of the file
            try:
                f = open(sha256FileName, 'r')
                oldSHA256Contents = f.readlines()
                oldSHA256 = ''
                if (len(oldSHA256Contents) > 0):
                    oldSHA256 = oldSHA256Contents[0].strip()
                newSHA256 = self._ComputeSHA256(inputFileName)
                if (oldSHA256 != newSHA256):
                    return True
            except:
                print "Error when comparing SHA256 files. Assuming execution of pipeline step is needed."
                return True

        for outputFile in self.OutputFiles:
            # Need an update if any of the outputs are missing
            if (not os.path.exists(outputFile)):
                return True

        # Everything checks out, no execution needed
        return False

    def ClearCache(self):
        """Deletes all the cached SHA256 files for this PipelineStep.

        This essentially forces a re-run of the PipelineStep.

        """
        filesToCheck = [self.Executable]
        filesToCheck.extend(self.InputFiles)
        filesToCheck.extend(self.OutputFiles)

        for inputFileName in filesToCheck:
            sha256FileName = self._GetSHA256FileName(inputFileName)
            sys.stdout.write('Removing %s.\n' % sha256FileName)
            os.remove(sha256FileName)

    def _GetSHA256FileName(self, fileName):
        """Get the file name for the cached SHA256 entry.

        """
        fileName = os.path.join(Pipeline._CacheDirectory,
                                self.Name + '-' + fileName.replace('/', '_') + '.sha256')

        # Create the path if needed
        directory = os.path.dirname(fileName)
        if (not os.path.exists(directory)):
            os.makedirs(directory)

        return fileName

    def _ComputeSHA256(self, path):
        """Compute the SHA256 for a given path.

        :param path: This parameter may be a directory or file. If it
        is a directory, the SHA256 is of all the content in the files
        in the directory hierarchy starting at this path. If it is a
        file, it is the SHA256 of the contents of the file.

        """

        m = hashlib.sha256()
        if os.path.isfile(path):
            f = open(path, 'r').read()
            m.update(f)
        elif os.path.isdir(path):
            # Compute SHA256 over all files in the directory
            for root, dirs, files in os.walk(path):
                files = sorted(files)
                for fileName in files:
                    filePath = os.path.join(root, fileName)
                    f = open(filePath, 'r').read()
                    m.update(f)

        return m.hexdigest()

    def _WriteSHA256Files(self):
        """Writes out SHA256 cache files for the Executable, InputFiles, and OutputFiles.

        """
        filesToCheck = [self.Executable]
        filesToCheck.extend(self.InputFiles)
        filesToCheck.extend(self.OutputFiles)

        for inputFileName in filesToCheck:
            # Save SHA256 file
            sha256FileName = self._GetSHA256FileName(inputFileName)

            try:
                sha256Value = self._ComputeSHA256(inputFileName)
            except:
                sys.stdout.write('Could not compute SHA256 for file "%s"\n' % inputFileName)

            try:
                shaFile = open(sha256FileName, 'w')
                shaFile.write(sha256Value)
                shaFile.write('\n')
            except:
                sys.stdout.write('Could not write SHA256 file "%s".\n' % sha256FileName)

#############################################################################
class Pipeline:
    """Pipeline that defines a set of steps that should be taken to
    execute a workflow.

    """
    def __init__(self):
        self._Steps = []

    def AddStep(self, step):
        """Add a workflow step to the pipeline.

        """
        self._Steps.append(step)

    def Execute(self, dryRun=False, verbose=False):
        """Execute each PipelineStep in the order it was added to the Pipeline
        if needed.

        :parameter dryRun: If set to True, does not actually execute the PipelineStep.
        :parameter verbose: If set to True, tells the PipelineStep to execute verbosely.

        """
        for s in self._Steps:
            if (s.NeedsUpdate()):
                sys.stdout.write('Workflow step "%s" needs to be executed.\n' % s.Name)
                success = True
                if (not dryRun):
                    success = s.Execute(verbose)
                if (not success):
                  break
            else:
                sys.stdout.write('Workflow step "%s" is up-to-date.\n' % s.Name)

    def ClearCache(self):
        """Clear the cache for all steps in the Pipeline.

        Note that this will force re-execution of all steps in the
        Pipeline.

        """
        sys.stdout.write('Clearing cache\n')

        # Remove all SHA256 files from cache directory
        for step in self._Steps:
            step.ClearCache()

    """Location where temporary files are stored."""
    _CacheDirectory = '/tmp'

    @staticmethod
    def SetCacheDirectory(directory):
        """Set the directory where the cached SHA256 files are stored.

        """
        sys.stdout.write('Setting cache directory to "%s"\n' % directory)
        Pipeline._CacheDirectory = directory

        # Warn if directory doesn't exit
        if (not os.path.isdir(directory)):
            sys.stdout.write('Cache directory "%s" does not exist.\n' % directory)
