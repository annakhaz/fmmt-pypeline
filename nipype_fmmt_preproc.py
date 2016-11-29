"""
fMRI: preprocess with SPM

search 'Q:' for unanswered questions
"""

## import necessary modules

from __future__ import print_function
from builtins import str
from builtins import range

import os

from nipype import config

from nipype.interfaces import spm #, fsl

import nipype.interfaces.io as nio
import nipype.interfaces.utility as util
import nipype.pipeline.engine as pe
import nipype.interfaces.matlab as mlab

## preliminaries
# Q: how to point to matlab/spm dirs?
# SPM: /Applications/MATLAB_R2014b.app/toolbox/spm12

mlab.MatlabCommand.set_default_matlab_cmd("matlab -nodesktop -nosplash")

# specify location of data
data_dir = os.path.abspath('data') # Q: where to?
# specify subject directories
subject_list = ['MMT102', 'MMT103']
# map field names to runs.
info = dict(func=[['subject_id', ['s1', 's2', 's3', 's4', 's5','s6']]],
            struct=[['subject_id', ['t1','t2']]) # Q: how to add T2?

infosource = pe.Node(interface=util.IdentityInterface(fields=['subject_id']),
                     name="infosource")

infosource.iterables = ('subject_id', subject_list)

## preprocessing pipeline nodes

datasource = pe.Node(interface=nio.DataGrabber(infields=['subject_id'],
                                               outfields=['func', 'struct']),
                     name='datasource')
datasource.inputs.base_directory = data_dir
datasource.inputs.template = '%s/%s.nii'
datasource.inputs.template_args = info
datasource.inputs.sort_filelist = True

# Q: skull stripping? artifact detection?

## slice time correction
# ref slice = middle; prefix = a

## realign: estimate and reslice
# reslice only mean image; Q: why?

realign = pe.Node(interface=spm.Realign(), name="realign") # Q:how to align only mean?
realign.inputs.register_to_mean = True

## coregister: estimate
# T2* to T2
# T2* and T2 to T1

coregister = pe.Node(interface=spm.Coregister(), name="coregister")
coregister.inputs.jobtype = 'estimate' # this does func to struc; Q: how to specify which struc

coregister = pe.Node(interface=spm.Coregister(), name="coregister")
coregister.inputs.jobtype = 'estimate'  # coreg output of T2 and T2* to T1

## old segment
# Q: why old?

## old normalize
# prefix = w (norm'd to MNI)

normalize = pe.Node(interface=spm.Normalize(), name="normalize") # Q: is this old norm?
normalize.inputs.template = os.path.abspath('data/T1.nii') # Q: dir of MNI?

## smooth
# 8 fwhm


smooth = pe.Node(interface=spm.Smooth(), name="smooth")
fwhmlist = [8] # Q: is this necessary?
smooth.iterables = ('fwhm', fwhmlist)

## set up pipeline

preproc_pipeline = pe.Workflow(name="preproc")
preproc_pipeline.base_dir = os.path.abspath('spm_tutorial/workingdir') #Q: dir?

preproc_pipeline.connect([(infosource, datasource, [('subject_id', 'subject_id')]),
                    (datasource, realign, [('func', 'in_files')]),
                    # Q: slicetime?
                    (realign, coregister, [('mean_image', 'source'),
                                           ('realigned_files', 'apply_to_files')]),
                    (datasource, coregister, [('struct', 'target')]),
                    (datasource, normalize, [('struct', 'source')]),
                    (coregister, normalize, [('coregistered_files', 'apply_to_files')]),
                    # Q: second coreg?
                    (normalize, smooth, [('normalized_files', 'in_files')]))

## set up storage results
# connect outputs from nodes above to storage locs

datasink = pe.Node(interface=nio.DataSink(), name="datasink")
datasink.inputs.base_directory = os.path.abspath('spm_tutorial/l1output') # Q: dir?

preproc_pipeline.connect([(infosource, datasink, [('subject_id', 'container')]), #Q: will this work after removing getstripdir? need to set working dir path anyways?
                    (realign, datasink, [('mean_image', 'realign.@mean'),
                                         ('realignment_parameters', 'realign.@param')])) # Q: this is all?

## Execute pipeline

if __name__ == '__main__':
    preproc_pipeline.run('MultiProc')

