"""
fMRI: 1st level analysis with SPM

search 'Q:' for unanswered questions

inputs:
    subject_id (subject_list)
    ...

Q: how to get input from preproc results (for connecting pipeline)?
save out e.g. realignment params, and import?

"""

## Set up analysis components
# exper paradigm info for SpecifyModel (to make design mat)


def subjectinfo(subject_id):
    from nipype.interfaces.base import Bunch
    from copy import deepcopy
    print("Subject ID: %s\n" % str(subject_id))
    output = []
    names = ['Task-Odd', 'Task-Even'] # Q: what should this be? sub mem?
    for r in range(4):
        onsets = [list(range(15, 240, 60)), list(range(45, 240, 60))] # Q: inport these?
        output.insert(r,
                      Bunch(conditions=names,
                            onsets=deepcopy(onsets),
                            durations=[[15] for s in names])) # Q: durations vary?
    return output

""" no changes made from this point on"""
## Set up contrast structure

cont1 = ('Task>Baseline', 'T', ['Task-Odd', 'Task-Even'], [0.5, 0.5])
cont2 = ('Task-Odd>Task-Even', 'T', ['Task-Odd', 'Task-Even'], [1, -1])
contrasts = [cont1, cont2]

## Generate SPM-specific design info

modelspec = pe.Node(interface=model.SpecifySPMModel(), name="modelspec")
modelspec.inputs.concatenate_runs = False
modelspec.inputs.input_units = 'secs'
modelspec.inputs.output_units = 'secs'
modelspec.inputs.time_repetition = 3.
modelspec.inputs.high_pass_filter_cutoff = 120

## Generate 1st level SPM.mat file

level1design = pe.Node(interface=spm.Level1Design(), name="level1design")
level1design.inputs.timing_units = modelspec.inputs.output_units
level1design.inputs.interscan_interval = modelspec.inputs.time_repetition
level1design.inputs.bases = {'hrf': {'derivs': [0, 0]}}

## Estimate parameters of model

level1estimate = pe.Node(interface=spm.EstimateModel(), name="level1estimate")
level1estimate.inputs.estimation_method = {'Classical': 1}

## Estimate first level contrasts

contrastestimate = pe.Node(interface=spm.EstimateContrast(), name="contrastestimate")
contrastestimate.inputs.contrasts = contrasts
contrastestimate.overwrite = True
contrastestimate.config = {'execution': {'remove_unnecessary_outputs': False}}



## execute pipeline

if __name__ == '__main__':
    l1pipeline.run('MultiProc')
