##################################################################################
#                                                                                #
# AutoWIG: Automatic Wrapper and Interface Generator                             #
#                                                                                #
# Homepage: http://autowig.readthedocs.io                                        #
#                                                                                #
# Copyright (c) 2016 Pierre Fernique                                             #
#                                                                                #
# This software is distributed under the CeCILL-C license. You should have       #
# received a copy of the legalcode along with this work. If not, see             #
# <http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html>.                 #
#                                                                                #
# File authors: Pierre Fernique <pfernique@gmail.com> (7)                        #
#                                                                                #
##################################################################################

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

def mngithub_notebook(configpath='doc/conf.py', as_version=4):
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
