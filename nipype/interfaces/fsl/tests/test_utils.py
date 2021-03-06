# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

import os
from tempfile import mkdtemp
from shutil import rmtree

import numpy as np

import nibabel as nb
from nipype.testing import (assert_equal, assert_not_equal,
                            assert_raises, parametric, skipif)
import nipype.interfaces.fsl.utils as fsl
from nipype.interfaces.fsl import no_fsl


def create_files_in_directory():
    outdir = mkdtemp()
    cwd = os.getcwd()
    os.chdir(outdir)
    filelist = ['a.nii','b.nii']
    for f in filelist:
        hdr = nb.Nifti1Header()
        shape = (3,3,3,4)
        hdr.set_data_shape(shape)
        img = np.random.random(shape)
        nb.save(nb.Nifti1Image(img,np.eye(4),hdr),
                 os.path.join(outdir,f))
    return filelist, outdir, cwd
    
def clean_directory(outdir, old_wd):
    if os.path.exists(outdir):
        rmtree(outdir)
    os.chdir(old_wd)

@skipif(no_fsl)
def test_extractroi():
    input_map = dict(args = dict(argstr='%s',),
                     environ = dict(),
                     in_file = dict(mandatory=True,argstr='%s',),
                     output_type = dict(),
                     roi_file = dict(argstr='%s',),
                     t_min = dict(argstr='%d',),
                     t_size = dict(argstr='%d',),
                     x_min = dict(argstr='%d',),
                     x_size = dict(argstr='%d',),
                     y_min = dict(argstr='%d',),
                     y_size = dict(argstr='%d',),
                     z_min = dict(argstr='%d',),
                     z_size = dict(argstr='%d',),
                     )
    instance = fsl.ExtractROI()
    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(instance.inputs.traits()[key], metakey), value

@skipif(no_fsl)
def test_imagemaths():
    input_map = dict(args = dict(argstr='%s',),
                     environ = dict(),
                     in_file = dict(argstr='%s',mandatory=True,),
                     in_file2 = dict(argstr='%s',),
                     op_string = dict(argstr='%s',),
                     out_data_type = dict(argstr='-odt %s',),
                     out_file = dict(argstr='%s',),
                     output_type = dict(),
                     suffix = dict(),
                     )
    instance = fsl.ImageMaths()
    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(instance.inputs.traits()[key], metakey), value

@skipif(no_fsl)
def test_merge():
    input_map = dict(args = dict(argstr='%s',),
                     dimension = dict(argstr='-%s',mandatory=True,),
                     environ = dict(),
                     in_files = dict(mandatory=True,argstr='%s',),
                     merged_file = dict(argstr='%s',),
                     output_type = dict(),
                     )
    instance = fsl.Merge()
    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(instance.inputs.traits()[key], metakey), value

@skipif(no_fsl)
def test_filterregressor():
    input_map = dict(Out_vnscales = dict(),
                     args = dict(argstr='%s',),
                     design_file = dict(mandatory=True,),
                     environ = dict(),
                     filter_out = dict(mandatory=True,),
                     in_file = dict(mandatory=True,),
                     mask = dict(),
                     out_file = dict(),
                     output_type = dict(),
                     var_norm = dict(),
                     )
    instance = fsl.FilterRegressor()
    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(instance.inputs.traits()[key], metakey), value

@skipif(no_fsl)
def test_smooth():
    input_map = dict(args = dict(argstr='%s',),
                     environ = dict(),
                     fwhm = dict(argstr='-kernel gauss %f -fmean',mandatory=True,),
                     in_file = dict(argstr='%s',mandatory=True,),
                     output_type = dict(),
                     smoothed_file = dict(argstr='%s',),
                     )
    instance = fsl.Smooth()
    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(instance.inputs.traits()[key], metakey), value

@skipif(no_fsl)
def test_split():
    input_map = dict(args = dict(argstr='%s',),
                     dimension = dict(argstr='-%s',),
                     environ = dict(),
                     in_file = dict(argstr='%s',),
                     out_base_name = dict(argstr='%s',),
                     output_type = dict(),
                     )
    instance = fsl.Split()
    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(instance.inputs.traits()[key], metakey), value
def no_fsl():
    """Checks if FSL is NOT installed
    used with skipif to skip tests that will
    fail if FSL is not installed"""
    
    if fsl.Info().version() == None:
        return True
    else:
        return False

@skipif(no_fsl)
def test_fslroi():
    filelist, outdir, cwd = create_files_in_directory()
    
    roi = fsl.ExtractROI()

    # make sure command gets called
    yield assert_equal, roi.cmd, 'fslroi'

    # test raising error with mandatory args absent
    yield assert_raises, ValueError, roi.run

    # .inputs based parameters setting
    roi.inputs.in_file = filelist[0]
    roi.inputs.roi_file = 'foo_roi.nii'
    roi.inputs.t_min = 10
    roi.inputs.t_size = 20
    yield assert_equal, roi.cmdline, 'fslroi %s foo_roi.nii 10 20'%filelist[0]

    # .run based parameter setting
    roi2 = fsl.ExtractROI(in_file=filelist[0],
                      roi_file='foo2_roi.nii',
                      t_min=20, t_size=40,
                      x_min=3, x_size=30,
                      y_min=40, y_size=10,
                      z_min=5, z_size=20)
    yield assert_equal, roi2.cmdline, \
          'fslroi %s foo2_roi.nii 3 30 40 10 5 20 20 40'%filelist[0]

    clean_directory(outdir, cwd)
    # test arguments for opt_map
    # Fslroi class doesn't have a filled opt_map{}


# test fslmath
@skipif(no_fsl)
def test_fslmaths():
    filelist, outdir, cwd = create_files_in_directory()
    math = fsl.ImageMaths()

    # make sure command gets called
    yield assert_equal, math.cmd, 'fslmaths'

    # test raising error with mandatory args absent
    yield assert_raises, ValueError, math.run

    # .inputs based parameters setting
    math.inputs.in_file = filelist[0]
    math.inputs.op_string = '-add 2.5 -mul input_volume2'
    math.inputs.out_file = 'foo_math.nii'
    yield assert_equal, math.cmdline, \
        'fslmaths %s -add 2.5 -mul input_volume2 foo_math.nii'%filelist[0]

    # .run based parameter setting
    math2 = fsl.ImageMaths(in_file=filelist[0], op_string='-add 2.5',
                           out_file='foo2_math.nii')
    yield assert_equal, math2.cmdline, 'fslmaths %s -add 2.5 foo2_math.nii'%filelist[0]

    # test arguments for opt_map
    # Fslmath class doesn't have opt_map{}
    clean_directory(outdir, cwd)

