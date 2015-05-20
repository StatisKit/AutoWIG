#scons parameters file
#use this file to pass custom parameter to SConstruct script

#build_prefix="build_scons"

import sys
if('win' in sys.platform):
    #compiler='msvc'
    compiler= 'mingw' # by default on windows
