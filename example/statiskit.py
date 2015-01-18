from clang import cindex, enumerations

cindex.Config.set_library_path('/usr/lib/llvm-3.5/lib')

index = cindex.Index.create()

translation_unit = index.parse(sys.argv[1], ['-x', 'c++', '-std=c++11', '-D__CODE_GENERATOR__'])
