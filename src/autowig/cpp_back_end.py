from .asg import *

def char_ptr_to_string(asg, pattern, prefix, namespace=None):
    interface = asg.add_file(prefix + '.h', proxy=HeaderProxy)
    interface.content = ''
    interface.is_independent = True
    implementation = asg.add_file(prefix + '.cpp')
    implementation.content = ''
    fcts = []
    for fct in asg.functions(pattern):
        result_type = fct.result_type
        parameters = fct.parameters
        if all(parameter.localname for parameter in parameters):
            if result_type.is_pointer and result_type.target == '::char' or any(parameter.type.is_pointer and parameter.type.target == '::char' for parameter in parameters):
                fcts.append(fct)
                body = []
                if isinstance(fct, MethodProxy) and not fct.is_static:
                    body.append(fct.parent.globalname + ' const' * fct.is_const + ' & self_' + fct.parent.hash)
                for parameter in parameters:
                    if parameter.type.is_pointer and parameter.type.target == '::char':
                        body.append('std::string' + ' const & ' + parameter.localname)
                    else:
                        body.append(str(parameter.type) + ' ' + parameter.localname)
                body = ' ' + fct.localname + '_' + fct.hash + '(' + ', '.join(body for body in body) + ')'
                if result_type.is_pointer and result_type.target == '::char':
                    body = 'std::string' + body
                else:
                    body = str(result_type) + body
                interface.content += body + ';\n\n'
                body += '\n{\n'
                for parameter in parameters:
                    if parameter.type.is_pointer and parameter.type.target == '::char':
                        body += '\tconst char * ' + parameter.localname + '_' + fct.hash + ' = ' + parameter.localname + '.c_str();\n'
                if not result_type.target == '::void':
                    body += '\treturn '
                    if result_type.is_pointer and result_type.target == '::char':
                        body += 'std::string('
                else:
                    body += '\t'
                if isinstance(fct, MethodProxy) and not fct.is_static:
                    body += 'self_' + fct.parent.hash + '.' + fct.localname
                else:
                    body += fct.globalname
                body += '(' + ', '.join([parameter.localname + '_' + fct.hash if parameter.type.is_pointer and parameter.type.target == '::char' else parameter.localname for parameter in parameters]) +')'
                if not result_type.target == '::void' and result_type.is_pointer and result_type.target == '::char':
                    body += ')'
                implementation.content += body + ';\n}\n\n'
    if namespace is None:
        interface.content = '\n'.join('#include <' + header.path + '>' if not header.language == 'c' else 'extern "C" { #include <' + header.path + '> }' for header in asg.headers(*fcts)) + '\n\n' + interface.content.strip()
        implementation.content = '#include "' + interface.localname + '"\n\n' + implementation.content.strip()
    else:
        interface.content = '\n'.join('#include <' + header.path + '>' if not header.language == 'c' else 'extern "C" { #include <' + header.path + '> }' for header in asg.headers(*fcts)) + '\n\nnamespace ' + namespace + '\n{\n\t' + '\n\t'.join(interface.content.strip().splitlines()) + '\n}'
        implementation.content = '#include "' + interface.localname + '"\n\nnamespace ' + namespace + '\n{\n\t' + '\n\t'.join(implementation.content.strip().splitlines()) + '\n}'
