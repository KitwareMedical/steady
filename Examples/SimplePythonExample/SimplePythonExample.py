import sys

# Add Python path two levels up
sys.path.append('../..')

from Workflow import *

#############################################################################
def main():
    Pipeline.SetCacheDirectory('/home/cory/tmp')

    # Set up a pipeline
    p = Pipeline()

    # Set up some workflow steps
    c1 = CommandLineExecutablePipelineStep('FirstStep')
    c1.ExecutableName = '/usr/bin/python'
    c1.Arguments = ['script1.py', 'script1-input.txt', 'script1-output.txt']
    c1.FileArgumentIndices = [0, 1] # Indices of file arguments (including python script)
    c1.OutputFiles = ['script1-output.txt']
    p.AddStep(c1)

    c2 = CommandLineExecutablePipelineStep('SecondStep')
    c2.ExecutableName = '/usr/bin/python'
    c2.Arguments = ['script2.py', 'script1-output.txt']
    c2.FileArgumentIndices = [0, 1] # Indices of file arguments (including python script)
    p.AddStep(c2)

    # Optional argument to force execution of all pipeline steps
    try:
        sys.argv.index('--force-execute')
        p.ClearCache()
    except:
        pass

    # Execute the pipeline
    p.Execute()


#############################################################################
if __name__ == '__main__':
    main()
