#include <boost/python.hpp>
#include <//home/pfernique/Desktop/AutoWIG/example/test/overload/overload.h>

void _non_constness()
{

        void  (::NonConstness::*method_pointer_46ea83fadb995b5aa2668bf54ddc23f3)() const = &::NonConstness::constness;
        void  (::NonConstness::*method_pointer_ecec3f90a0ad5c76ab6d39c6c35ab1cc)() = &::NonConstness::constness;
        boost::python::class_< struct ::NonConstness, struct ::NonConstness* >("NonConstness", boost::python::no_init)
            .def(boost::python::init<  >())
            .def("constness", method_pointer_46ea83fadb995b5aa2668bf54ddc23f3)
            .def("constness", method_pointer_ecec3f90a0ad5c76ab6d39c6c35ab1cc);    
}