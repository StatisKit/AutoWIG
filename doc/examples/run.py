import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

def mngnb(configpath='doc/conf.py', as_version=4):
    configpath = path(configpath)
    configdict = dict()
    if configpath.is_file():
        execfile(configpath, configdict)
    nbsphinx_execute = configdict.get('nbsphinx_execute', 'auto')
    nbsphinx_timeout = configdict.get('nbsphinx_execute', 'timeout')
    if not nbsphinx_execute == 'always':
        for notebookpath in configpath.walkfiles('*.ipynb'):
            if not notebookpath.parent.basename() == '.ipynb_checkpoints':
                with open(notebookpath.abspath(), 'r') as notebookfile:
                    notebookdict = nbformat.read(notebookfile, as_version)
                    execute = notebookdict.get('metadata', dict()).get('nbsphinx', dict()).get('execute', nbsphinx_execute)
                    if execute == 'never':
                        ep = ExecutePreprocessor(timeout = nbsphinx_timeout,
                                                 kernel_name = notebookdict.get('metadata', dict()).get('kernelspec', dict()).get('name', 'python2'))
                        ep.preprocess(notebookdict, {'metadata': {'path': notebookpath.parent}})
                    elif execute == 'auto':
                        for cell in notebookdict.get('cells', []):
                            if 'outputs' in cell:
                                cell['outputs'] = list()
                with open(notebookpath.abspath(), 'w') as notebookfile:
                    nbformat.write(notebookdict, notebookfile)
