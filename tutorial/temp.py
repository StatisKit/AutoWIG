includedir = "/usr/local/include"

headers = ["clang/AST/ExternalASTSource.h", "clang/AST/DependentDiagnostic.h", "clang/AST/ParentMap.h",
           "clang/AST/DeclGroup.h", "clang/AST/DeclAccessPair.h", "clang/AST/UnresolvedSet.h",
           "clang/AST/DeclarationName.h", "clang/AST/Stmt.h", "clang/AST/Redeclarable.h", "clang/AST/Type.h",
           "clang/AST/SelectorLocationsKind.h", "clang/AST/ExprObjC.h", "clang/AST/OperationKinds.h",
           "clang/AST/DeclObjC.h", "clang/AST/CXXInheritance.h", "clang/AST/CommentLexer.h",
           "clang/AST/ASTTypeTraits.h", "clang/AST/TemplateBase.h", "clang/AST/DeclFriend.h",
           "clang/AST/OpenMPClause.h", "clang/AST/DeclLookups.h", "clang/AST/StmtVisitor.h",
           "clang/AST/VTableBuilder.h", "clang/AST/ASTUnresolvedSet.h", "clang/AST/GlobalDecl.h",
           "clang/AST/DeclBase.h", "clang/AST/ASTContext.h", "clang/AST/CharUnits.h", "clang/AST/StmtOpenMP.h",
           "clang/AST/TypeLocVisitor.h", "clang/AST/LambdaCapture.h", "clang/AST/CanonicalType.h",
           "clang/AST/PrettyPrinter.h", "clang/AST/CommentCommandTraits.h", "clang/AST/NestedNameSpecifier.h",
           "clang/AST/DeclTemplate.h", "clang/AST/Mangle.h", "clang/AST/StmtIterator.h", "clang/AST/Attr.h",
           "clang/AST/StmtGraphTraits.h", "clang/AST/MangleNumberingContext.h", "clang/AST/StmtCXX.h",
           "clang/AST/CommentSema.h", "clang/AST/RecursiveASTVisitor.h", "clang/AST/ASTConsumer.h",
           "clang/AST/ASTFwd.h", "clang/AST/TypeLoc.h", "clang/AST/CommentDiagnostic.h",
           "clang/AST/VTTBuilder.h", "clang/AST/EvaluatedExprVisitor.h", "clang/AST/CommentParser.h",
           "clang/AST/AttrIterator.h", "clang/AST/DataRecursiveASTVisitor.h", "clang/AST/NSAPI.h",
           "clang/AST/TypeOrdering.h", "clang/AST/TypeVisitor.h", "clang/AST/Decl.h", "clang/AST/ExprCXX.h",
           "clang/AST/CommentVisitor.h", "clang/AST/ASTDiagnostic.h", "clang/AST/AST.h", "clang/AST/ASTLambda.h",
           "clang/AST/StmtObjC.h", "clang/AST/RecordLayout.h", "clang/AST/APValue.h",
           "clang/AST/DeclContextInternals.h", "clang/AST/TemplateName.h", "clang/AST/ASTImporter.h",
           "clang/AST/DeclOpenMP.h", "clang/AST/ASTMutationListener.h", "clang/AST/RawCommentList.h",
           "clang/AST/ASTVector.h", "clang/AST/Comment.h", "clang/AST/DeclCXX.h", "clang/AST/CommentBriefParser.h",
           "clang/AST/Expr.h", "clang/AST/BaseSubobject.h", "clang/AST/DeclVisitor.h", "clang/Frontend/ASTUnit.h",
           "clang/Basic/Specifiers.h"]
headers = [includedir + '/' + header for header in headers]
from vplants.autowig.asg import *
asg = AbstractSemanticGraph()
for header in headers:
    filenode = asg.add_file(header, language='c++')
flags = ['-x', 'c++', '-g', '-std=c++11', '-I'+includedir, '-I/usr/local/lib/clang/3.7.0/include',
         '-D__STDC_LIMIT_MACROS', '-D__STDC_CONSTANT_MACROS']
asg[includedir + '/'].parse(flags=flags, libclang=False)
#flags = ['-x', 'c++', '-g', '-std=c++11', '-I'+includedir]
#asg[includedir + '/'].parse(flags=flags, libclang=True)
