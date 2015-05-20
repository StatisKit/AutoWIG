#include "AST.h"

#ifndef CLANG_BOOTSTRAP

namespace autowig
{
    unsigned int get_nb_decls(const clang::DeclContext& context)
    { 
        unsigned int nb = 0;
        for(auto it = context.decls_begin(), end = context.decls_end(); it != end; ++it)
        { ++nb; }
        return nb; 
    }
    
    clang::Decl* get_decl(const clang::DeclContext& context, const unsigned int& decl)
    {
        auto it_decl = context.decls_begin();
        for(unsigned int i = 0; i < decl; ++i)
        { ++it_decl; }
        return *it_decl;
    }
}

#endif
