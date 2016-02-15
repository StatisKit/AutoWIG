#include <boost/python.hpp>
#include <//home/pfernique/Desktop/AutoWIG/example/test/overload/overload.h>

void _constness()
{

        void  (::Constness::*method_pointer_2e6eb4405c48508e862c8470054f38ec)() = &::Constness::constness;
        void  (::Constness::*method_pointer_741097f7611b572e896a6c571cd3a473)() const = &::Constness::constness;
        boost::python::class_< struct ::Constness, struct ::Constness* >("Constness", boost::python::no_init)
            .def(boost::python::init<  >())
            .def("constness", method_pointer_2e6eb4405c48508e862c8470054f38ec)
            .def("constness", method_pointer_741097f7611b572e896a6c571cd3a473);    
}