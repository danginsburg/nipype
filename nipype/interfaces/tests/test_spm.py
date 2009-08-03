import nipype.interfaces.spm as spm
from nose.tools import assert_true, assert_false, assert_raises, assert_equal, assert_not_equal


def test_spm_path():
    spm_path = spm.spm_info.spm_path
    if spm_path is not None:
        yield assert_equal,type(spm_path),type('')
        yield assert_equal,'spm' in spm_path,True

def test_reformat_dict_for_savemat():
    mlab = spm.SpmMatlabCommandLine()
    out = mlab.reformat_dict_for_savemat({'a':{'b':{'c':[]}}})
    yield assert_equal,out,[{'a': [{'b': [{'c': []}]}]}]
    
def test_generate_job():
    mlab = spm.SpmMatlabCommandLine()
    out = mlab.generate_job()
    yield assert_equal,out,''
    contents = {'contents':[1,2,3,4]}
    out = mlab.generate_job(contents=contents)
    yield assert_equal,out,'.contents(1) = 1;\n.contents(2) = 2;\n.contents(3) = 3;\n.contents(4) = 4;\n'
    
def test_make_matlab_command():
    mlab = spm.SpmMatlabCommandLine()
    contents = {'contents':[1,2,3,4]}
    cmdline,script = mlab.make_matlab_command('jobtype','jobname',[contents])
    yield assert_equal,cmdline,'matlab -nodesktop -nosplash -r "pyscript_jobname;exit" '
    yield assert_equal,'jobs{1}.jobtype{1}.jobname{1}.contents(3) = 3;' in script, True

def test_spm_realign():
    realign = spm.Realign(write=False)
    updatedopts = realign._parseinputs()
    yield assert_equal, updatedopts, {'data':[],'eoptions':{},'roptions':{}}
    yield assert_equal, realign.inputs.write, False
