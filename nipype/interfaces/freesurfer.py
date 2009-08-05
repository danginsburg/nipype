"""The freesurfer module provides basic functions for interfacing with freesurfer tools.

Currently these tools are supported:

     * Dicom2Nifti: using mri_convert
     * Resample: using mri_convert
     
Examples
--------
See the docstrings for the individual classes for 'working' examples.

"""

import os
from glob import glob
from nipype.interfaces.base import (Bunch, CommandLine, InterfaceResult, setattr_on_read)
from nipype.utils.filemanip import fname_presuffix

def freesurferversion():
    """Check for freesurfer version on system

    Parameters
    ----------
    None

    Returns
    -------
    version : string
       version number as string 
       or None if freesurfer version not found

    """
    # find which freesurfer is being used....and get version from
    # /path/to/freesurfer/
    fs_home = os.getenv('FREESURFER_HOME')
    if fs_home is None:
        return fs_home
    versionfile = os.path.join(fs_home,'build-stamp.txt')
    if not os.path.exists(versionfile):
        return None
    fid = open(versionfile,'rt')
    version = fid.readline()
    fid.close()
    return version.split('-v')[1].strip('\n')


class Dicom2Nifti(CommandLine):
    """use fs mri_convert to convert dicom files to nifti-1 files

    Options
    -------

    To see optianl arguments
    Dicom2Nifti().inputs_help()


    Examples
    --------
    >>> cvt = freesurfer.Dicom2Nifti()
    >>> cvt.inputs.dicomdir = '/software/data/STUT/RAWDATA/TrioTim-35115-20090428-081900-234000/'
    >>> cvt.inputs.file_mapping = [('nifti','*.nii'),('info','dicom*.txt'),('dti','*dti.bv*')]
    >>> out = cvt.run()
   """

    @property
    def cmd(self):
        """sets base command, not editable"""
        return 'fs_dicom2nifti'


    def inputs_help(self):
        doc = """
        Optional Parameters
        -------------------
        (all default to None and are unset)
        
        dicomdir : /path/to/dicomfiles
            directory from which to convert dicom files
        base_output_dir : /path/to/outputdir
            base output directory in which subject specific
            directories are created to store the nifti files
        subject_dir_template : string
            template for subject directory name
            Default:'S.%04d'
        subject_id : string or int
            subject identifier to insert into template. For the
            example above template subject_identifier should be an
            integer. Default: id from Dicom file name 
        file_mapping : list of tuples
            defines the output fields of interface and the kind of
            file type they store
            Example: [('niftifiles','*.nii'),('dtiinfo','*mghdti.bv*')]
        flags = unsupported flags, use at your own risk

        """
        print doc

    def _populate_inputs(self):
        self.inputs = Bunch(dicomdir=None,
                            base_output_dir=None,
                            subject_dir_template=None,
                            subject_id=None,
                            file_mapping=None,
                            flags=None)

    def _parseinputs(self):
        """validate fsl bet options
        if set to None ignore
        """
        out_inputs = {'dicomfiles':None}
        inputs = {}
        [inputs.update({k:v}) for k, v in self.inputs.iteritems() if v is not None ]
        for opt in inputs:
            if opt is 'dicomdir':
                out_inputs['dicomfiles'] = glob(os.path.abspath(os.path.join(inputs[opt],'*-1.dcm')))
                continue
            if opt is 'base_output_dir':
                continue
            if opt is 'subject_dir_template':
                continue
            if opt is 'subject_id':
                continue
            if opt is 'file_mapping':
                continue
            if opt is 'flags':
                continue
            print 'option %s not supported'%(opt)
        
        return out_inputs

    def _compile_command(self):
        """validates fsl options and generates command line argument"""
        valid_inputs = self._parseinputs()
        subjid = self.inputs.subject_id
        if subjid is None:
            path,fname = os.path.split(valid_inputs['dicomfiles'][0])
            subjid = fname.split('-')[0]
        if self.input.subject_dir_template is not None:
            subjid  = self.inputs.subject_dir_template % subjid
        basedir=self.inputs.base_output_dir
        if basedir is None:
            basedir = os.path.abspath('.')
        outdir = os.path.abspath(os.path.join(basedir,subjid))
        cmd = []
        if not os.path.exists(outdir):
            cmdstr = 'mkdir %s;' % outdir
            cmd.extend([cmdstr])
        cmdstr = 'dcmdir-info-mgh %s > %s;' % (self.inputs.dicomdir,os.path.join(outdir,'dicominfo.txt'))
        cmd.extend([cmdstr])
        for f in valid_inputs['dicomfiles']:
            head,fname = os.path.split(f)
            fname,ext  = os.path.splitext(fname)
            outfile = os.path.join(outdir,''.join((fname,'.nii')))
            if not os.path.exists(outfile):
                single_cmd = 'mri_convert %s %s;' % (f, outfile)
                cmd.extend([single_cmd])
        self.cmdline =  ' '.join(cmd)
        return self.cmdline,outdir

    def run(self):
        """Execute the command.
        
        Returns
        -------
        results : Bunch
            A `Bunch` object with a copy of self in `interface`

         """

        # This is expected to populate `command` for _runner to work
        cmd,outdir = self._compile_command()
        returncode, out, err = self._runner(cwd='.')
        outputs = Bunch()
        if self.inputs.file_mapping is not None:
            for field,template in self.inputs.file_mapping:
                outputs[field] = sorted(glob(os.path.join(outdir,template)))
        return  InterfaceResult(runtime=Bunch(returncode=returncode,
                                              stdout=out,
                                              stderr=err),
                                outputs = outputs,
                                interface=self.copy())
        

class Resample(CommandLine):
    """use fs mri_convert to up or down-sample image files

    Options
    -------

    To see optianl arguments
    Resample().inputs_help()


    Examples
    --------
    >>> resampler = freesurfer.Resample()
    >>> resampler.inputs.infile = 'infile.nii'
    >>> resampler.voxel_size = [2,2,2]
    >>> out = resampler.run()
   """

    @property
    def cmd(self):
        """sets base command, not editable"""
        return 'fs_resample'


    def inputs_help(self):
        doc = """
        Optional Parameters
        -------------------
        (all default to None and are unset)
             
        infile : string or list
            file(s) to resample
        voxel_size: 3-element list
            size of x, y and z voxels in mm of resampled image
        outfile_postfix : string
            string appended to input file name to generate output file
            name. Default: '_fsresample'
        flags = unsupported flags, use at your own risk

        """
        print doc

    def _populate_inputs(self):
        self.inputs = Bunch(infile=None,
                            voxel_size=None,
                            outfile_postfix='_fsresample',
                            flags=None)

    def _parseinputs(self):
        """validate fsl bet options
        if set to None ignore
        """
        out_inputs = {'infile':[]}
        inputs = {}
        [inputs.update({k:v}) for k, v in self.inputs.iteritems() if v is not None ]
        for opt in inputs:
            if opt is 'infile':
                out_inputs['infile'] = inputs[opt]
                if type(inputs[opt]) is not type([]):
                    out_inputs['infile'] = [inputs[opt]]
                continue
            if opt is 'voxel_size':
                continue
            if opt is 'outfile_postfix':
                continue
            if opt is 'flags':
                continue
            print 'option %s not supported'%(opt)
        
        return out_inputs

    def outputs_help(self):
        doc = """
        outfile : string or list
            resampled file(s)
        """
        print doc

    def _compile_command(self):
        """validates fsl options and generates command line argument"""
        valid_inputs = self._parseinputs()
        cmd = []
        vs = self.inputs.voxel_size
        outfile = []
        for i,f in enumerate(valid_inputs['infile']):
            path,fname = os.path.split(f)
            outfile.insert(i,fname_presuffix(fname,suffix=self.inputs.outfile_postfix))
            outfile[i] = os.path.abspath(os.path.join(self.inputs.get('cwd','.'),outfile[i]))
            single_cmd = 'mri_convert -vs %d %d %d %s %s;' % (vs[0],vs[1],vs[2], f, outfile[i])
            cmd.extend([single_cmd])
        self.cmdline =  ' '.join(cmd)
        return self.cmdline,outfile

    def run(self):
        """Execute the command.
        
        Returns
        -------
        results : InterfaceResult
            A `InterfaceResult` object with a copy of self in `interface`

         """

        # This is expected to populate `cmdline` for _runner to work
        cmd,outfile = self._compile_command()
        returncode, out, err = self._runner(self.inputs.get('cwd','.'))
        outputs = Bunch(outfile=[])
        for i,f in enumerate(outfile):
            assert glob(f)==[f], 'outputfile %s was not generated'%f
            outputs.outfile.insert(i,f)
        if len(outfile)==1:
            outputs.outfile = outputs.outfile[0]
        return  InterfaceResult(runtime=Bunch(returncode=returncode,
                                              stdout=out,
                                              stderr=err),
                                outputs = outputs,
                                interface=self.copy())
        