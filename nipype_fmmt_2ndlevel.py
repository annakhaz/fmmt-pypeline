"""
fMRI: 2nd level analysis with SPM

search 'Q:' for unanswered questions

inputs:
    subject_id (subject_list)

"""


## grab the contrast images across a group of first level subjects

# collect all the con images for each contrast.
contrast_ids = list(range(1, len(contrasts) + 1))
l2source = pe.Node(nio.DataGrabber(infields=['fwhm', 'con']), name="l2source")

l2source.inputs.template = os.path.abspath('spm_tutorial/l1output/*/con*/*/_fwhm_%d/con_%04d.nii') # .img in spm8

# iterate over all contrast images
l2source.iterables = [('fwhm', fwhmlist),
                      ('con', contrast_ids)]
l2source.inputs.sort_filelist = True

## set up a 1-sample t-test node #Q: all we need is 2-sample t-test comparing groups across cons? no, first 1-sample t-tests? yes. to see if diffs w/in groups for e.g. hit v miss. plus intrxns.
onesamplettestdes = pe.Node(interface=spm.OneSampleTTestDesign(), name="onesampttestdes")
l2estimate = pe.Node(interface=spm.EstimateModel(), name="level2estimate")
l2estimate.inputs.estimation_method = {'Classical': 1}
l2conestimate = pe.Node(interface=spm.EstimateContrast(), name="level2conestimate")
cont1 = ('Group', 'T', ['mean'], [1])
l2conestimate.inputs.contrasts = [cont1]
l2conestimate.inputs.group_contrast = True

## set up pipeline

l2pipeline = pe.Workflow(name="level2")
l2pipeline.base_dir = os.path.abspath('spm_tutorial/l2output')
l2pipeline.connect([(l2source, onesamplettestdes, [('outfiles', 'in_files')]),
                    (onesamplettestdes, l2estimate, [('spm_mat_file', 'spm_mat_file')]),
                    (l2estimate, l2conestimate, [('spm_mat_file', 'spm_mat_file'),
                                                 ('beta_images', 'beta_images'),
                                                 ('residual_image', 'residual_image')]),
                    ])

## execute pipeline

if __name__ == '__main__':
    l2pipeline.run('MultiProc')
