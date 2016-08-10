#include <type_traits>
#include <boost/python.hpp>
#include <binomial.h>

namespace autowig { template<class T> using HeldType = std::shared_ptr< T >; }

namespace autowig
{
    PyObject* error_a071a76e12df54f186f3f488645acdd7 = nullptr;

    void translate_a071a76e12df54f186f3f488645acdd7(class ::ProbabilityError const & error)
    { PyErr_SetString(error_a071a76e12df54f186f3f488645acdd7, error.what()); };
}



void wrapper_a071a76e12df54f186f3f488645acdd7()
{

    std::string name_a071a76e12df54f186f3f488645acdd7 = boost::python::extract< std::string >(boost::python::scope().attr("__name__"));
    name_a071a76e12df54f186f3f488645acdd7 = name_a071a76e12df54f186f3f488645acdd7 + "." + "ProbabilityError";
    autowig::error_a071a76e12df54f186f3f488645acdd7 = PyErr_NewException(strdup(name_a071a76e12df54f186f3f488645acdd7.c_str()), PyExc_RuntimeError, NULL);
    boost::python::scope().attr("ProbabilityError") = boost::python::object(boost::python::handle<>(boost::python::borrowed(autowig::error_a071a76e12df54f186f3f488645acdd7)));
    boost::python::register_exception_translator< class ::ProbabilityError >(&autowig::translate_a071a76e12df54f186f3f488645acdd7);

}