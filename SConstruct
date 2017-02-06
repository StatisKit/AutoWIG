# -*-python-*-

import os
from SCons.Errors import EnvironmentError

env = Environment()

try:
  SConscript('SConscript', exports="env")
except EnvironmentError:
  pass
except Exception:
    raise
try:
  SConscript(os.path.join('conda', 'SConscript'), exports="env")
  # except EnvironmentError:
  #   pass
except Exception:
    raise

Default("install")