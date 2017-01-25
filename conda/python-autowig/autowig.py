from SCons.Script import AddOption, GetOption
import autowig

def generate(env):
    """Add Builders and construction variables to the Environment."""

    if not 'autowig' in env['TOOLS'][:-1]:

        AddOption('--autowig-site-dir',
                  dest    = 'autowig-site-dir',
                  type    = 'string',
                  nargs   = 1,
                  action  = 'store',
                  metavar = 'DIR',
                  help    = 'autowig cache directory',
                  default = os.path.join(autowig.__path__[0], 'site_autowig'))
        env['AUTOWIG_SITE_DIR'] = GetOption('autowig-site-dir')

        def AutoWIG(env, target, sources, parser, controller, generator, language, **kwargs):
            #
            sources = [source.sourcenode().abspath for source in sources]
            if any(source.has_changed_since_last_build):
                asg = autowig.AbstractSementicGraph()
                for dependency in kwargs.pop('dependencies', []):
                    with open(os.path.join(env['AUTOWIG_SITE_DIR'], arg), 'r') as filehandler:
                        asg.merge(pickle.load(filehandler))
                if isinstance(parser, basestring):
                    autowig.parser.plugin = parser
                else:
                    autowig.parser['SCons'] = parser
                    autowig.parser.plugin = 'SCons'
                parser_kwargs = {key.strip('parser_') : value for key, value in kwargs if key.startswith('parser_')}
                if language == 'c++':
                    if 'flags' not in parser_kwargs:
                        parser_kwargs['flags'] = env.subst('$_CCCOMCOM $CXXFLAGS')
                else:
                    raise NotImplementedError('The ' + language ' is not supported')
                parser_kwargs['language'] = language
                asg = autowig.parser(asg, sources, **parser_kwargs)
                if isinstance(controller, basestring):
                    autowig.controller.plugin = controller
                else:
                    autowig.controller['SCons'] = controller
                    autowig.controller.plugin = 'SCons'
                controller_kwargs = {key.strip('controller_') : value for key, value in kwargs if key.startswith('controller_')}
                asg = autowig.controller(asg, **controller_kwargs)
                if isinstance(generator, basestring):
                    autowig.generator.plugin = generator
                else:
                    autowig.generator['SCons'] = generator
                    autowig.generator.plugin = 'SCons'
                generator_kwargs = {key.strip('generator_') : value for key, value in kwargs if key.startswith('generator_')}
                wrappers = autowig.generator(asg, **generator_kwargs)
                wrappers.write()
                with open(os.path.join(env['AUTOWIG_SITE_DIR'], target), 'w') as filehandler:
                    pickle.dump(asg, filehandler)

        env.AutoWIG = MethodType(AutoWIG, env)

def exists(env):
    return 1
