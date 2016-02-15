#include <boost/python.hpp>
#include <//home/pfernique/Desktop/AutoWIG/example/test/binomial/binomial.h>
PyObject* error_type_92d464d1243554009adc48a065a5be3e = 0;

void translate_error_92d464d1243554009adc48a065a5be3e(struct ::ProbabilityError const & error)
{ PyErr_SetObject(error_type_92d464d1243554009adc48a065a5be3e, boost::python::object(error).ptr()); }


void _probability_error()
{

        boost::python::scope class_92d464d1243554009adc48a065a5be3e = boost::python::class_< struct ::ProbabilityError, struct ::ProbabilityError*, boost::python::bases< class ::std::exception >, boost::noncopyable >("ProbabilityError", boost::python::no_init)
            .def(boost::python::init<  >());
        boost::python::implicitly_convertible< struct ::ProbabilityError*, class ::std::exception* >();
        error_type_92d464d1243554009adc48a065a5be3e = class_92d464d1243554009adc48a065a5be3e.ptr();
        boost::python::register_exception_translator< struct ::ProbabilityError >(&translate_error_92d464d1243554009adc48a065a5be3e);
    
}