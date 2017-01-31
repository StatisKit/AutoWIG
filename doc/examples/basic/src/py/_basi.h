#ifndef AUTOWIG__BASI
#define AUTOWIG__BASI

#include <boost/python.hpp>
#include <type_traits>
#include <basic/binomial.h>
#include <basic/overload.h>

namespace autowig
{
     template<class T> struct Held {
        typedef T* Type;
    };
}

#endif