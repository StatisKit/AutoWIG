#include <boost/python.hpp>
#include <//home/pfernique/Desktop/AutoWIG/example/simple_example/binomial.h>
PyObject* error_type_a071a76e12df54f186f3f488645acdd7 = 0;

void translate_error_a071a76e12df54f186f3f488645acdd7(class ::ProbabilityError const & error)
{ PyErr_SetObject(error_type_a071a76e12df54f186f3f488645acdd7, boost::python::object(error).ptr()); }


void _probability_error()
{

        boost::python::scope class_a071a76e12df54f186f3f488645acdd7 = boost::python::class_< class ::ProbabilityError, class ::ProbabilityError*, boost::python::bases< class ::std::exception >, boost::noncopyable >("ProbabilityError", boost::python::no_init);
        boost::python::implicitly_convertible< class ::ProbabilityError*, class ::std::exception* >();
        error_type_a071a76e12df54f186f3f488645acdd7 = class_a071a76e12df54f186f3f488645acdd7.ptr();
        boost::python::register_exception_translator< class ::ProbabilityError >(&translate_error_a071a76e12df54f186f3f488645acdd7);
    
}