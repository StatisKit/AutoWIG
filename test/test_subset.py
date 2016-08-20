import os
import unittest
from path import path
from git import Repo
import subprocess
import sys

from autowig import autowig

class TemplateRender(object):

  def __get__(self, obj, objtype, **kwargs):
    code = obj.code
    code = code.replace('\n    __M_caller = context.caller_stack._push_frame()', '', 1)
    code = code.replace('\n    __M_caller = context.caller_stack._push_frame()', '', 1)
    code = code.replace("        return ''\n    finally:\n        context.caller_stack._pop_frame()\n", "        return __M_string\n    except:\n        return ''", 1)
    code = code.replace("context,**pageargs", "**context", 1)
    code = code.replace("\n        __M_locals = __M_dict_builtin(pageargs=pageargs)", "", 1)
    code = code.replace("__M_writer = context.writer()", "__M_string = u''")
    code = code.replace("__M_writer(", "__M_string = operator.add(__M_string, ")
    code = "import operator\n" + code
    exec code in globals()
    def __call__(**context):
      return globals()["render_body"](**context)
    return __call__

from autowig.boost_python_generator import Template

Template.render = TemplateRender()

class TestSubset(unittest.TestCase):
  """Test the wrapping of a library subset"""

  @classmethod
  def setUpClass(cls):
    autowig.parser.plugin = 'libclang'
    srcdir = path('PyClangLite')
    repo = Repo.clone_from('https://github.com/StatisKit/PyClangLite.git', srcdir.relpath('.'))
    cls.srcdir = srcdir/'src'/'py'
    subprocess.check_output(['scons', 'cpp', '--prefix=' + sys.prefix, '-C', cls.srcdir.parent.parent.abspath()])

  def test_libclang_parser(self):
    """Test `libclang` parser"""

    for wrapper in self.srcdir.walkfiles('*.cpp'):
      wrapper.unlink()
            
    prefix = path(sys.prefix)

    headers = [prefix/'include'/'clanglite'/'tool.h']

    asg = autowig.AbstractSemanticGraph()
    asg = autowig.parser(asg, headers,
                         flags = ['-x', 'c++', '-std=c++11',
                                  '-D__STDC_LIMIT_MACROS', '-D__STDC_CONSTANT_MACROS',
                                  '-I' + str((prefix/'include').abspath())],
                         bootstrap = False,
                         silent = True)

    def clanglite_controller(asg):
            
      for node in asg['::boost::python'].classes(nested = True):
        node.is_copyable = True
                
      for node in asg.classes():
        node.boost_python_export = False
      for node in asg.enumerations():
        node.boost_python_export = False
      for node in asg.enumerators():
        if node.parent.boost_python_export:
          node.boost_python_export = False
                    
      for node in asg.functions(free = True):
        node.boost_python_export = False
      for node in asg.variables(free = True):
        node.boost_python_export = False
                
      from autowig.default_controller import refactoring
      asg = refactoring(asg)
      for fct in asg['::clanglite'].functions():
        if not fct.localname == 'build_ast_from_code_with_args':
          fct.parent = fct.parameters[0].qualified_type.desugared_type.unqualified_type
            
      subset = []
      classes = [asg['class ::clang::Type'], asg['class ::clang::Decl']]
      subset += classes
      subset += classes[0].subclasses(recursive=True)
      subset += classes[1].subclasses(recursive=True)
      subset.append(asg['class ::llvm::StringRef'])
      subset.append(asg['class ::clang::ASTUnit'])
      subset.append(asg['class ::clang::ASTContext'])
      subset.append(asg['class ::clang::FileID'])
      subset.append(asg['class ::clang::SourceLocation'])
      subset.append(asg['class ::clang::CXXBaseSpecifier'])
      subset.append(asg['class ::clang::DeclContext'])
      subset.append(asg['enum ::clang::AccessSpecifier'])
      subset.append(asg['enum ::clang::LinkageSpecDecl::LanguageIDs'])
      subset.append(asg['enum ::clang::BuiltinType::Kind'])
      subset.append(asg['enum ::clang::TemplateArgument::ArgKind'])
      subset.append(asg['enum ::clang::Decl::Kind'])
      subset.extend(asg['::boost::python'].classes(nested = True))
      subset.extend(asg['::boost::python'].enumerations(nested = True))
      subset.extend(asg.nodes('::clanglite::build_ast_from_code_with_args'))

      for node in subset:
        node.boost_python_export = True

      if autowig.parser.plugin == 'libclang':
        for node in (asg.functions(pattern='.*(llvm|clang).*_(begin|end)')
                     + asg.functions(pattern='.*(llvm|clang).*getNameAsString')
                     + asg.nodes('::clang::NamedDecl::getQualifiedNameAsString')
                     + asg.nodes('::clang::ObjCProtocolDecl::collectInheritedProtocolProperties')
                     + asg.nodes('::clang::ASTUnit::LoadFromASTFile')
                     + asg.nodes('::clang::ASTUnit::getCachedCompletionTypes')
                     + asg.nodes('::clang::ASTUnit::getBufferForFile')
                     + asg.nodes('::clang::CXXRecordDecl::getCaptureFields')
                     + asg.nodes('::clang::ASTContext::SectionInfos')
                     + asg.nodes('::clang::ASTContext::getAllocator')
                     + asg.nodes('::clang::ASTContext::getObjCEncodingForFunctionDecl')
                     + asg.nodes('::clang::ASTContext::getObjCEncodingForPropertyDecl')
                     + asg.nodes('::clang::ASTContext::getObjCEncodingForMethodDecl')
                     + asg.nodes('::clang::ASTContext::getAllocator')):
          node.boost_python_export = False
                    
        import sys
        from path import path
        for header in (path(sys.prefix)/'include'/'clang').walkfiles('*.h'):
          asg[header.abspath()].is_external_dependency = False
            
        return asg

      autowig.controller['clanglite'] = clanglite_controller
      autowig.controller.plugin = 'clanglite'
      asg = autowig.controller(asg)

      autowig.generator.plugin = 'boost_python_internal'
      wrappers = autowig.generator(asg,
                                   module = self.srcdir/'_clanglite.cpp',
                                   decorator = self.srcdir/'clanglite'/'_clanglite.py',
                                   closure = False)

      for wrapper in wrappers:
        wrapper.write()
            
# def test_pyclanglite_parser(self):
#     """Test `pyclanglite` parser"""
#     plugin = autowig.parser.plugin
#     autowig.parser.plugin = 'pyclanglite'
#     self.test_libclang_parser()
#     autowig.parser.plugin = plugin
