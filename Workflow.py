import glob
import hashlib
import os
import subprocess
import sys

#############################################################################
class PipelineStep(object):

    """Base class for pipeline steps."""
    def __init__(self, name):
        self.Name = name

    def NeedsUpdate(self):
        return False

#############################################################################
class CommandLineExecutablePipelineStep(PipelineStep):
    """Pipeline steps for a command-line executable."""
    def __init__(self, name):
        super(CommandLineExecutablePipelineStep, self).__init__(name)
        self.ExecutableName = ''
        self.Arguments = []
        self.InputFiles = []
        self.OutputFiles = []

    def Execute(self):
        sys.stdout.write('Executing CommandLineExecutablePipelineStep "%s"\n' % self.Name)
        args = [self.ExecutableName] + self.Arguments

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
        for inputFileName in self.InputFiles:
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
                print "Error when comparing SHA256 files."
                print "Assuming execution of pipeline step is needed."
                return True

        for outputFile in self.OutputFiles:
            # Need an update if any of the outputs are missing
            if (not os.path.exists(outputFile)):
                return True

        # Everything checks out, no execution needed
        return False

    def ClearCache(self):
        for inputFileName in self.InputFiles:
            sha256FileName = self._GetSHA256FileName(inputFileName)
            sys.stdout.write('Removing %s.\n' % sha256FileName)
            os.remove(sha256FileName)

    def _GetSHA256FileName(self, fileName):
        fileName = os.path.join(Pipeline._CacheDirectory,
                                self.Name + '-' + fileName.replace('/', '_') + '.sha256')

        # Create the path if needed
        directory = os.path.dirname(fileName)
        if (not os.path.exists(directory)):
            os.makedirs(directory)

        return fileName

    def _ComputeSHA256(self, fileName):
        f = open(fileName, 'r').read()
        m = hashlib.sha256(f)
        return m.hexdigest()

    def _WriteSHA256Files(self):
        for inputFileName in self.InputFiles:
            # Save SHA256 file
            sha256FileName = self._GetSHA256FileName(inputFileName)

            try:
                shaFile = open(sha256FileName, 'w')
                shaFile.write(self._ComputeSHA256(inputFileName))
                shaFile.write('\n')
            except:
                sys.stdout.write('Could not write SHA256 file "%s".\n' % sha256FileName)

#############################################################################
class Pipeline:
    """Pipeline that defines a set of steps that should be taken to execute
       a workflow."""
    def __init__(self):
        self._Steps = []

    def AddStep(self, step):
        self._Steps.append(step)

    def Execute(self):
        for s in self._Steps:
            sys.stdout.write('Pipeline step "%s"\n' % s.Name)
            if (s.NeedsUpdate()):
                sys.stdout.write('Workflow step "%s" needs to be executed.\n' % s.Name)
                s.Execute()
            else:
                sys.stdout.write('Workflow step "%s" is up-to-date.\n' % s.Name)

    def ClearCache(self):
        sys.stdout.write('Clearing cache\n')

        # Remove all SHA256 files from cache directory
        #globExpr = os.path.join(Pipeline._CacheDirectory, '*.sha256')
        #sha256Files = glob.glob(globExpr)
        #for f in sha256Files:
        #    os.remove(f)
        for step in self._Steps:
            step.ClearCache()

    """Location where temporary files are stored."""
    _CacheDirectory = ''

    @staticmethod
    def SetCacheDirectory(directory):
        sys.stdout.write('Setting cache directory to "%s"\n' % directory)
        Pipeline._CacheDirectory = directory

        # Warn if directory doesn't exit
        if (not os.path.isdir(directory)):
            sys.stdout.write('Cache directory "%s" does not exist.\n' % directory)
