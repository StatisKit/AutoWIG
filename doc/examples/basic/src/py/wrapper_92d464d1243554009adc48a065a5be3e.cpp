#include "_basic.h"


namespace autowig
{
    PyObject* error_92d464d1243554009adc48a065a5be3e = NULL;

    void translate_92d464d1243554009adc48a065a5be3e(struct ::ProbabilityError const & error) { PyErr_SetString(error_92d464d1243554009adc48a065a5be3e, error.what()); };
}



void wrapper_92d464d1243554009adc48a065a5be3e()
{

    std::string name_92d464d1243554009adc48a065a5be3e = boost::python::extract< std::string >(boost::python::scope().attr("__name__"));
    name_92d464d1243554009adc48a065a5be3e = name_92d464d1243554009adc48a065a5be3e + "." + "ProbabilityError";
    autowig::error_92d464d1243554009adc48a065a5be3e = PyErr_NewException(strdup(name_92d464d1243554009adc48a065a5be3e.c_str()), PyExc_RuntimeError, NULL);
    boost::python::scope().attr("ProbabilityError") = boost::python::object(boost::python::handle<>(boost::python::borrowed(autowig::error_92d464d1243554009adc48a065a5be3e)));
    boost::python::register_exception_translator< struct ::ProbabilityError >(&autowig::translate_92d464d1243554009adc48a065a5be3e);

}