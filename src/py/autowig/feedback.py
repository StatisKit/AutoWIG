from autowig.plugin_manager import feedback
from autowig.scons import scons as old_scons

def scons(directory, *args, **kwargs):
    if not isinstance(directory, path):
        directory = path(directory)
    directory = directory.abspath()

    if kwargs.pop('pipe', True):
        s = subprocess.Popen(['scons']+[arg for arg in args] , cwd=directory,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = s.communicate()
        return ShellSession(out, err, **kwargs)
    else:
        s = subprocess.Popen(['scons']+[arg for arg in args], cwd=directory, stderr=subprocess.PIPE)
        out, err = s.communicate()
        return ShellSession(out, err, **kwargs)
