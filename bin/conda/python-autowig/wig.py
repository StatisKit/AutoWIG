from SCons.Script import AddOption, GetOption
import autowig
import os
import pickle
from distutils.sysconfig import get_python_lib
from SCons.Builder import Builder
from SCons.Action import Action
from importlib import import_module

def generate(env):
    """Add Builders and construction variables to the Environment."""

    if not 'autowig' in env['TOOLS'][:-1]:

        env.Tool('textfile')

        AddOption('--site-autowig',
                      dest    = 'site-autowig',
                      type    = 'string',
                      nargs   = 1,
                      action  = 'store',
                      metavar = 'DIR',
                      help    = '',
                      default = os.path.join(get_python_lib(), 'autowig', 'site'))
        env['SITE_AUTOWIG'] = GetOption('site-autowig')

        def boost_python_builder(target, source, env):
            SITE_AUTOWIG = env['SITE_AUTOWIG']
            if 'AUTOWIG_ASG' in env:
                env['AUTOWIG_ASG'][env['AUTOWIG_generator_module'].abspath].remove()
            env['AUTOWIG_ASG'] = autowig.AbstractSemanticGraph()
            asg = env['AUTOWIG_ASG']
            for dependency in env['AUTOWIG_DEPENDS']:
                with open(os.path.join(SITE_AUTOWIG, 'ASG', dependency + '.pkl'), 'rb') as filehandler:
                    asg.merge(pickle.load(filehandler))
            AUTOWIG_PARSER = env['AUTOWIG_PARSER']
            if not AUTOWIG_PARSER in autowig.parser:
                parser = import_module('autowig.site.parser.' +  AUTOWIG_PARSER)
                autowig.parser[AUTOWIG_PARSER] = parser.parser
            autowig.parser.plugin = AUTOWIG_PARSER
            autowig.parser(asg, [header.abspath for header in source],
                           flags = ['-x', 'c++'] + env.subst('$CCFLAGS $CXXFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS').split(),
                           **{kwarg[len('AUTOWIG_parser_'):] : env[kwarg] for kwarg in env.Dictionary() if isinstance(kwarg, basestring) and kwarg.startswith('AUTOWIG_parser_')})
            AUTOWIG_CONTROLLER = env['AUTOWIG_CONTROLLER']
            if not AUTOWIG_CONTROLLER in autowig.controller:
                controller = import_module('autowig.site.controller.' +  AUTOWIG_CONTROLLER)
                autowig.controller[AUTOWIG_CONTROLLER] = controller.controller
            autowig.controller.plugin = AUTOWIG_CONTROLLER
            asg = autowig.controller(asg, 
                                     **{kwarg[len('AUTOWIG_controller_'):] : env[kwarg] for kwarg in env.Dictionary() if isinstance(kwarg, basestring) and kwarg.startswith('AUTOWIG_controller_')})
            AUTOWIG_GENERATOR = env['AUTOWIG_GENERATOR']
            if not AUTOWIG_GENERATOR in autowig.generator:
                generator = import_module('autowig.site.generator.' +  AUTOWIG_GENERATOR)
                autowig.generator[AUTOWIG_GENERATOR] = generator.generator
            autowig.generator.plugin = AUTOWIG_GENERATOR
            wrappers = autowig.generator(asg,
                                         **{kwarg[len('AUTOWIG_generator_'):] : env[kwarg] for kwarg in env.Dictionary() if isinstance(kwarg, basestring) and kwarg.startswith('AUTOWIG_generator_')})
            wrappers.header.helder = env['AUTOWIG_HELDER']
            wrappers.write()
            with open(target[-1].abspath, 'wb') as filehandler:
                pickle.dump(asg, filehandler)
            return None

        def BoostPythonWIG(env, target, sources, module, decorator=None, parser='clanglite', controller='default', generator='boost_python_internal', depends=[], helder='std::shared_ptr', **kwargs):
            #
            SITE_AUTOWIG = env['SITE_AUTOWIG']
            autowig_env = env.Clone()
            autowig_env['BUILDERS']['_BoostPythonWIG'] = Builder(action = Action(boost_python_builder, 'autowig: Generating Boost.Python interface ...'))
            autowig_env['AUTOWIG_DEPENDS'] = depends
            autowig_env['AUTOWIG_HELDER'] = helder
            for kwarg in kwargs:
                autowig_env['AUTOWIG_' + kwarg] = kwargs[kwarg]
            autowig_env['AUTOWIG_generator_module'] = env.File(module).srcnode()
            if decorator:
                autowig_env['AUTOWIG_generator_decorator'] = env.File(decorator).srcnode()
            targets = []
            if parser.endswith('.py'):
                targets.append(env.InstallAs(os.path.join(SITE_AUTOWIG, 'parser', target + '.py'), parser))
                parser = target
            autowig_env['AUTOWIG_PARSER'] = parser
            if controller.endswith('.py'):
                targets.append(env.InstallAs(os.path.join(SITE_AUTOWIG, 'controller', target + '.py'), controller))
                controller = target
            autowig_env['AUTOWIG_CONTROLLER'] = controller
            if generator.endswith('.py'):
                targets.append(env.InstallAs(os.path.join(SITE_AUTOWIG, 'generator', target + '.py'), generator))
                generator = target
            autowig_env['AUTOWIG_GENERATOR'] = generator

            targets.append(autowig_env.File(os.path.join(SITE_AUTOWIG, 'ASG', target + '.pkl')))
            for target in targets[:-1]:
                autowig_env.Depends(targets[-1], target)

            if os.path.exists(targets[-1].abspath):
                with open(targets[-1].abspath, 'rb') as filehandler:
                    autowig_env['AUTOWIG_ASG'] = pickle.load(filehandler)

            autowig_env._BoostPythonWIG(targets[-1], sources)

            return targets

        env.AddMethod(BoostPythonWIG)

def exists(env):
    return 1