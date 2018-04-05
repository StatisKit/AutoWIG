## Copyright [2017-2018] UMR MISTEA INRA, UMR LEPSE INRA,                ##
##                       UMR AGAP CIRAD, EPI Virtual Plants Inria        ##
## Copyright [2015-2016] UMR AGAP CIRAD, EPI Virtual Plants Inria        ##
##                                                                       ##
## This file is part of the AutoWIG project. More information can be     ##
## found at                                                              ##
##                                                                       ##
##     http://autowig.rtfd.io                                            ##
##                                                                       ##
## The Apache Software Foundation (ASF) licenses this file to you under  ##
## the Apache License, Version 2.0 (the "License"); you may not use this ##
## file except in compliance with the License. You should have received  ##
## a copy of the Apache License, Version 2.0 along with this file; see   ##
## the file LICENSE. If not, you may obtain a copy of the License at     ##
##                                                                       ##
##     http://www.apache.org/licenses/LICENSE-2.0                        ##
##                                                                       ##
## Unless required by applicable law or agreed to in writing, software   ##
## distributed under the License is distributed on an "AS IS" BASIS,     ##
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or       ##
## mplied. See the License for the specific language governing           ##
## permissions and limitations under the License.                        ##

import autowig

import unittest
from nose.plugins.attrib import attr

import os
from path import Path
from git import Repo
import subprocess
import sys
import platform

import autowig

@attr(linux=True,
      osx=True,
      win=True,
      level=2)
class TestSubset(unittest.TestCase):
    """Test the wrapping of a library subset"""

    @classmethod
    def setUpClass(cls):
        if 'libclang' in autowig.parser:
            autowig.parser.plugin = 'libclang'
        cls.srcdir = Path('fp17')
        if not cls.srcdir.exists():
            Repo.clone_from('https://github.com/StatisKit/FP17.git', cls.srcdir.relpath('.'), recursive=True)
        cls.srcdir = cls.srcdir/'share'/'git'/'ClangLite'
        cls.incdir = Path(sys.prefix).abspath()
        if any(platform.win32_ver()):
            cls.incdir = cls.incdir/'Library'
        subprocess.check_output(['scons', 'cpp', '--prefix=' + str(cls.incdir)],
                                cwd=cls.srcdir)
        if any(platform.win32_ver()):
            cls.scons = subprocess.check_output(['where', 'scons.bat']).strip()
        else:
            cls.scons = subprocess.check_output(['which', 'scons']).strip()
        cls.incdir = cls.incdir/'include'/'clanglite'

    def test_libclang_parser(self):
        """Test `libclang` parser"""

        headers = [self.incdir/'tool.h']

        asg = autowig.AbstractSemanticGraph()
        asg = autowig.parser(asg, headers,
                             flags = ['-x', 'c++', '-std=c++11',
                                      '-D__STDC_LIMIT_MACROS', '-D__STDC_CONSTANT_MACROS',
                                      '-I' + str(self.incdir.parent),
                                      '-I' + str(self.incdir.parent.abspath()/'python2.7')],
                             bootstrap = False,
                             silent = True)

        def clanglite_controller(asg):
            for node in asg['::boost::python'].classes(nested = True):
                node.is_copyable = True
                
            for node in asg.classes():
                node.boost_python_export = False
            for node in asg.functions(free=True):
                node.boost_python_export = False
            for node in asg.variables(free = True):
                node.boost_python_export = False
            for node in asg.enumerations():
                node.boost_python_export = False
            for node in asg.enumerators():
                if node.parent.boost_python_export:
                    node.boost_python_export = False
            for node in asg.typedefs():
                node.boost_python_export = False
                    
            from autowig.default_controller import refactoring
            asg = refactoring(asg)

            if autowig.parser.plugin == 'libclang':
                for fct in asg.functions(free=False):
                    asg._nodes[fct._node]['_is_virtual'] = False
                    asg._nodes[fct._node]['_is_pure'] = False
                asg['class ::clang::QualType'].is_abstract = False
                asg['class ::clang::QualType'].is_copyable = True
                asg['class ::llvm::StringRef'].is_abstract = False
                asg['class ::llvm::StringRef'].is_copyable = True
                asg['class ::clang::FileID'].is_abstract = False
                asg['class ::clang::FileID'].is_copyable = True
                asg['class ::clang::SourceLocation'].is_abstract = False
                asg['class ::clang::SourceLocation'].is_copyable = True
                asg['class ::clang::TemplateArgument'].is_abstract = False
                asg['class ::clang::TemplateArgument'].is_copyable = True
                for cls in ['::clang::FriendDecl', '::clang::CapturedDecl', '::clang::OMPThreadPrivateDecl',
                            '::clang::NonTypeTemplateParmDecl', '::clang::TemplateArgumentList', '::clang::ImportDecl',
                            '::clang::TemplateTemplateParmDecl', '::clang::CapturedDecl', '::clang::OMPThreadPrivateDecl',
                            '::clang::NonTypeTemplateParmDecl', '::clang::TemplateArgumentList', '::clang::ImportDecl',
                            '::clang::TemplateTemplateParmDecl']:
                    asg['class ' + cls].is_abstract = False
                
            asg['class ::boost::python::api::object'].boost_python_export = True
            asg['class ::boost::python::list'].boost_python_export = True 
            asg['class ::boost::python::str'].boost_python_export = True 
                
            subset = []
            classes = [asg['class ::clang::QualType'],
                       asg['class ::clang::Type'],
                       asg['class ::clang::Decl']]
            subset += classes
            for cls in classes:
                subset += cls.subclasses(recursive=True)
            for cls in subset:
                if not cls.globalname.strip('class ') in ['::clang::QualType',
                                                          '::llvm::StringRef',
                                                          '::clang::FileID',
                                                          '::clang::SourceLocation',
                                                          '::clang::TemplateArgument',
                                                          '::clang::FriendDecl',
                                                          '::clang::CapturedDecl',
                                                          '::clang::OMPThreadPrivateDecl',
                                                          '::clang::NonTypeTemplateParmDecl',
                                                          '::clang::TemplateArgumentList',
                                                          '::clang::ImportDecl',
                                                          '::clang::TemplateTemplateParmDecl']:
                    cls.is_copyable = False
                else:
                    cls.is_copyable = True
            subset.append(asg['class ::llvm::StringRef'])

            subset.append(asg['class ::clang::Sema'])
            subset.append(asg['class ::clang::ASTUnit'])
            subset.append(asg['class ::clang::ASTContext'])
            subset.append(asg['class ::clang::SourceManager'])
            subset.append(asg['class ::clang::FileID'])

            subset.append(asg['class ::clang::SourceLocation'])

            subset.append(asg['class ::clang::CXXBaseSpecifier'])
            subset.append(asg['class ::clang::DeclContext'])
            subset.append(asg['class ::clang::TemplateArgument'])

            subset.append(asg['class ::clang::TemplateArgumentList'])
            subset.append(asg['enum ::clang::Type::TypeClass'])
            subset.append(asg['enum ::clang::AccessSpecifier'])
            subset.append(asg['enum ::clang::LinkageSpecDecl::LanguageIDs'])
            subset.append(asg['enum ::clang::BuiltinType::Kind'])
            subset.append(asg['enum ::clang::TemplateArgument::ArgKind'])
            subset.append(asg['enum ::clang::Decl::Kind'])
            subset.extend(asg.nodes('::clanglite::build_ast_from_code_with_args'))

            for node in subset:
                node.boost_python_export = True
                
            for fct in asg['::clanglite'].functions():
                if not fct.localname == 'build_ast_from_code_with_args':
                    fct.parent = fct.parameters[0].qualified_type.desugared_type.unqualified_type
                fct.boost_python_export = True
                
            for mtd in asg['class ::clang::ASTContext'].methods(pattern='.*getSourceManager.*'):
                if mtd.return_type.globalname == 'class ::clang::SourceManager &':
                        mtd.boost_python_export = True
                        break
                        
            if autowig.parser.plugin == 'libclang':
                for node in (asg.functions(pattern='.*(llvm|clang).*_(begin|end)')
                             + asg.functions(pattern='::clang::CXXRecordDecl::getCaptureFields')
                             + asg.functions(pattern='.*(llvm|clang).*getNameAsString')
                             + asg.nodes('::clang::NamedDecl::getQualifiedNameAsString')
                             + asg.functions(pattern='.*::clang::ObjCProtocolDecl')
                             + asg.nodes('::clang::ObjCProtocolDecl::collectInheritedProtocolProperties')
                             + asg.nodes('::clang::ASTUnit::LoadFromASTFile')
                             + asg.nodes('::clang::ASTUnit::getCachedCompletionTypes')
                             + asg.nodes('::clang::ASTUnit::getBufferForFile')
                             + asg.nodes('::clang::CXXRecordDecl::getCaptureFields')
                             + asg.nodes('::clang::ASTContext::SectionInfos')
                             + asg.nodes('::clang::ASTContext::getAllocator')
                             + asg.nodes('::clang::ASTContext::getObjCEncoding.*')
                             + asg.nodes('::clang::ASTContext::getAllocator')
                             + asg.nodes('::clang::QualType::getAsString')
                             + asg.nodes('::clang::SourceLocation::printToString')
                             + asg['class ::llvm::StringRef'].methods()):
                    node.boost_python_export = False
                    
            if autowig.parser.plugin == 'clanglite':
                for mtd in asg['class ::clang::Decl'].methods():
                    if mtd.localname == 'hasAttr':
                        mtd.boost_python_export = False
                        
            import sys
            try:
                from path import path as Path
            except:
                from path import Path
               
            import platform
            if any(platform.win32_ver()):
                for header in (Path(sys.prefix)/'Library'/'include'/'clang').walkfiles('*.h'):
                    asg[header.abspath()].is_external_dependency = False
            else:
                for header in (Path(sys.prefix)/'include'/'clang').walkfiles('*.h'):
                    asg[header.abspath()].is_external_dependency = False
            
            return asg

        autowig.controller['clanglite'] = clanglite_controller
        autowig.controller.plugin = 'clanglite'
        asg = autowig.controller(asg)

        asg['enum ::max_align_t'].boost_python_export = False
        asg['::max_align_t::__clang_max_align_nonce1'].boost_python_export = False
        
        autowig.generator.plugin = 'boost_python_internal'
        module = autowig.generator(asg,
                                     module = self.srcdir/'py'/'wrapper'/'_clanglite.cpp',
                                     decorator = self.srcdir/'py'/'clanglite'/'_clanglite.py',
                                     closure = False)

        module.write()

        for filepath in (self.srcdir/'src'/'py'/'wrapper').walkfiles():
            if filepath.exists() and filepath.ext in ['.cpp', '.h']:
                filepath.remove()