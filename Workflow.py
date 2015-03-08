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
        self.FileArgumentIndices = []

    def Execute(self):
        sys.stdout.write('Executing CommandLineExecutablePipelineStep "')
        sys.stdout.write(self.Name)
        sys.stdout.write('"\n')
        args = [self.ExecutableName] + self.Arguments

        try:
            subprocess.call(args)

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
        sys.stdout.write('Checking to see if workflow step "')
        sys.stdout.write(self.Name)
        sys.stdout.write('" needs to be executed\n')

        for index in self.FileArgumentIndices:
            inputFileName = self.Arguments[index]
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
                    sys.stdout.write('-- SHA256 mismatch for input file "')
                    sys.stdout.write(inputFileName)
                    sys.stdout.write('". Execution needed.\n')
                    return True
            except:
                print "Error when comparing SHA256 files."
                print "Assuming execution of pipeline step is needed."
                return True

        # Everything checks out, no execution needed
        return False

    def _GetSHA256FileName(self, fileName):
        return self.Name + '-' + fileName + '.sha256'

    def _ComputeSHA256(self, fileName):
        f = open(fileName, 'r').read()
        m = hashlib.sha256(f)
        return m.hexdigest()

    def _WriteSHA256Files(self):
        for index in self.FileArgumentIndices:
            # Save SHA256 file
            inputFileName = self.Arguments[index]
            sha256FileName = self._GetSHA256FileName(self.Arguments[index])
            shaFile = open(sha256FileName, 'w')
            shaFile.write(self._ComputeSHA256(inputFileName))
            shaFile.write('\n')
            

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
            if (s.NeedsUpdate()):
                s.Execute()

#############################################################################
def main():
    # Set up a pipeline
    p = Pipeline()

    # Set up some workflow steps
    c1 = CommandLineExecutablePipelineStep('FirstStep')
    c1.ExecutableName = '/usr/bin/python'
    c1.Arguments = ['script1.py', 'script1-input.txt', 'script1-output.txt']
    c1.FileArgumentIndices = [0, 1] # Indices of file arguments (including python script)
    p.AddStep(c1)

    c2 = CommandLineExecutablePipelineStep('SecondStep')
    c2.ExecutableName = '/usr/bin/python'
    c2.Arguments = ['script2.py', 'script1-output.txt']
    c2.FileArgumentIndices = [0, 1] # Indices of file arguments (including python script)
    p.AddStep(c2)

    # Execute the pipeline
    p.Execute()


#############################################################################
if __name__ == '__main__':
    main()
