#ifndef AUTOWIG__BASIC
#define AUTOWIG__BASIC

#include <boost/python.hpp>
#include <type_traits>
#include <basic/binomial.h>
#include <basic/overload.h>

namespace autowig
{
     template<class T> struct Held {
        typedef T* Type;
        static bool const is_class = false;
    };
}

/*namespace autowig
{}*/
#endif