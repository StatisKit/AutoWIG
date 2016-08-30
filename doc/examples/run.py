import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from path import path

nbdir = path('.').asbpath()

ep = ExecutePreprocessor()
for notebook in nbdir.files('*.ipynb'):
    try:
        out = ep.preprocess(notebook, {'metadata': {'path': nbdir}})
    except CellExecutionError:
        msg = 'Error executing the notebook "%s".\n\n' % notebook_filename
        msg += 'See notebook "%s" for the traceback.' % notebook_filename_out
        print(msg)
        raise
    finally:
        with open(notebook, mode='wt') as filehandler:
            nbformat.write(notebook, filehandler)
