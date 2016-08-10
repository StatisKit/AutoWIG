#include <type_traits>
#include <boost/python.hpp>
#include <binomial.h>

namespace autowig { template<class T> using HeldType = std::shared_ptr< T >; }

namespace autowig
{
    PyObject* error_f926cb231a7f5da09f313cd361ff94c7 = nullptr;

    void translate_f926cb231a7f5da09f313cd361ff94c7(class ::std::exception const & error)
    { PyErr_SetString(error_f926cb231a7f5da09f313cd361ff94c7, error.what()); };
}



void wrapper_f926cb231a7f5da09f313cd361ff94c7()
{

    std::string name_a5e4e9231d6351ccb0e06756b389f0af = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".std");
    boost::python::object module_a5e4e9231d6351ccb0e06756b389f0af(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(name_a5e4e9231d6351ccb0e06756b389f0af.c_str()))));
    boost::python::scope().attr("std") = module_a5e4e9231d6351ccb0e06756b389f0af;
    boost::python::scope scope_a5e4e9231d6351ccb0e06756b389f0af = module_a5e4e9231d6351ccb0e06756b389f0af;
    std::string name_f926cb231a7f5da09f313cd361ff94c7 = boost::python::extract< std::string >(boost::python::scope().attr("__name__"));
    name_f926cb231a7f5da09f313cd361ff94c7 = name_f926cb231a7f5da09f313cd361ff94c7 + "." + "Exception";
    autowig::error_f926cb231a7f5da09f313cd361ff94c7 = PyErr_NewException(strdup(name_f926cb231a7f5da09f313cd361ff94c7.c_str()), PyExc_RuntimeError, NULL);
    boost::python::scope().attr("Exception") = boost::python::object(boost::python::handle<>(boost::python::borrowed(autowig::error_f926cb231a7f5da09f313cd361ff94c7)));
    boost::python::register_exception_translator< class ::std::exception >(&autowig::translate_f926cb231a7f5da09f313cd361ff94c7);

}