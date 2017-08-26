##################################################################################
#                                                                                #
# AutoWIG: Automatic Wrapper and Interface Generator                             #
#                                                                                #
# Homepage: http://autowig.readthedocs.io                                        #
#                                                                                #
# Copyright (c) 2016 Pierre Fernique                                             #
#                                                                                #
# This software is distributed under the CeCILL license. You should have       #
# received a copy of the legalcode along with this work. If not, see             #
# <http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html>.                 #
#                                                                                #
# File authors: Pierre Fernique <pfernique@gmail.com> (46)                       #
#                                                                                #
##################################################################################


import autowig

import unittest
from nose.plugins.attrib import attr

import os
from path import Path
from git import Repo
import subprocess
import sys

import autowig

@attr(linux=True,
      osx=True,
      win=True,
      level=2)
class TestSubset(unittest.TestCase):
    """Test the wrapping of a library subset"""

    @classmethod
    def setUpClass(cls):
        autowig.parser.plugin = 'libclang'
        srcdir = Path('ClangLite')
        Repo.clone_from('https://github.com/StatisKit/ClangLite.git', srcdir.relpath('.'))
        cls.srcdir = srcdir/'src'/'py'
        subprocess.check_output(['scons', 'cpp', '--prefix=' + sys.prefix],
                                cwd=cls.srcdir.parent.parent)

    def test_libclang_parser(self):
        """Test `libclang` parser"""

        for wrapper in self.srcdir.walkfiles('*.cpp'):
            wrapper.unlink()

        prefix = Path(sys.prefix)

        headers = [prefix/'include'/'clanglite'/'tool.h']

        asg = autowig.AbstractSemanticGraph()
        asg = autowig.parser(asg, headers,
                             flags = ['-x', 'c++', '-std=c++11',
                                      '-D__STDC_LIMIT_MACROS', '-D__STDC_CONSTANT_MACROS',
                                      '-I' + str((prefix/'include').abspath()),
                                      '-I' + str((prefix/'include').abspath()/'python2.7')],
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

            for header in (Path(sys.prefix)/'include'/'clang').walkfiles('*.h'):
                asg[header.abspath()].is_external_dependency = False
            
            return asg

        autowig.controller['clanglite'] = clanglite_controller
        autowig.controller.plugin = 'clanglite'
        asg = autowig.controller(asg)

        autowig.generator.plugin = 'boost_python_internal'
        module = autowig.generator(asg,
                                     module = self.srcdir/'_clanglite.cpp',
                                     decorator = self.srcdir/'clanglite'/'_clanglite.py',
                                     closure = False)

        module.write()
