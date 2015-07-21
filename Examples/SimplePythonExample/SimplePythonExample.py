import sys

# Add Python path two levels up
sys.path.append('../../')

from steady import workflow as wf

#############################################################################
def main():
    wf.Pipeline.SetCacheDirectory('/home/cory/tmp')

    # Set up a pipeline
    p = wf.Pipeline()

    # Set up some workflow steps
    cmd = ['/usr/bin/python', wf.infile('script1.py'), wf.infile('script1-input.txt'), wf.outfile('script1-output.txt')]
    c1 = wf.CommandLineExecutablePipelineStep('FirstStep', cmd)
    p.AddStep(c1)

    cmd = ['/usr/bin/python', wf.infile('script2.py'), wf.infile('script1-output.txt')]
    c2 = wf.CommandLineExecutablePipelineStep('SecondStep', cmd)
    p.AddStep(c2)

    # Optional argument to force execution of all pipeline steps
    if ('--force-execute' in sys.argv):
        p.ClearCache()

    # Optional argument for verbose execution
    verbose = '--verbose' in sys.argv

    # Execute the pipeline
    p.Execute(verbose=verbose)


#############################################################################
if __name__ == '__main__':
    main()
