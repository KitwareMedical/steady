import sys

# Add Python path two levels up
sys.path.append('../../')

from steady import workflow as wf

#############################################################################
def main():
    wf.Workflow.SetCacheDirectory('/home/cory/tmp')

    # Set up a pipeline
    workflow = wf.Workflow()

    # Set up some workflow steps
    cmd = ['/usr/bin/python', wf.infile('script1.py'), wf.infile('script1-input.txt'), wf.outfile('script1-output.txt')]
    c1 = wf.CLIWorkflowStep('FirstStep', cmd)
    workflow.AddStep(c1)

    cmd = ['/usr/bin/python', wf.infile('script2.py'), wf.infile('script1-output.txt')]
    c2 = wf.CLIWorkflowStep('SecondStep', cmd)
    workflow.AddStep(c2)

    # Optional argument to force execution of all pipeline steps
    if ('--force-execute' in sys.argv):
        workflow.ClearCache()

    # Optional argument for verbose execution
    verbose = '--verbose' in sys.argv

    # Execute the pipeline
    workflow.Execute(verbose=verbose)


#############################################################################
if __name__ == '__main__':
    main()
