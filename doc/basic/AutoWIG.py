from autowig import autowig


asg = autowig.AbstractSemanticGraph()
autowig.parser.plugin = 'pyclanglite'
autowig.parser(asg, ['binomial.h'], ['-x', 'c++', '-std=c++11', '-I.'])

autowig.controller.plugin = 'default'
autowig.controller(asg)

autowig.generator.plugin = 'boost_python_internal'
wrappers = autowig.generator(asg, module='module.cpp',
                        decorator=None,
                        prefix='wrapper_')

for wrapper in wrappers:
    wrapper.write()