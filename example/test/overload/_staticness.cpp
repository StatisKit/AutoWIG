#include <boost/python.hpp>
#include <//home/pfernique/Desktop/AutoWIG/example/test/overload/overload.h>

void _staticness()
{

        void  (::Staticness::*method_pointer_dc72b5b10b765f47807c76095c7ea2ee)() = &::Staticness::staticness;
        void  (::Staticness::*method_pointer_c785af599af353ec97ec80225cac0166)(unsigned int  const) = &::Staticness::staticness;
        void  (*method_pointer_272b3c77b65153939934b135d30d57de)(struct ::Staticness  const &, unsigned int  const) = ::Staticness::staticness;
        boost::python::class_< struct ::Staticness, struct ::Staticness* >("Staticness", boost::python::no_init)
            .def(boost::python::init<  >())
            .def("staticness", method_pointer_dc72b5b10b765f47807c76095c7ea2ee)
            .def("staticness", method_pointer_c785af599af353ec97ec80225cac0166)
            .def("staticness", method_pointer_272b3c77b65153939934b135d30d57de)
            .staticmethod("staticness");    
}