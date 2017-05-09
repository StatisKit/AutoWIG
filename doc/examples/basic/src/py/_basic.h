#ifndef AUTOWIG__BASIC
#define AUTOWIG__BASIC

#include <boost/python.hpp>
#include <type_traits>
#include </home/pfernique/.miniconda/envs/statiskit-dev/include/basic/overload.h>
#include </home/pfernique/.miniconda/envs/statiskit-dev/include/basic/binomial.h>

namespace autowig
{
     template<class T> struct Held {
        typedef T* Type;
        static bool const is_class = false;
    };
}

#endif