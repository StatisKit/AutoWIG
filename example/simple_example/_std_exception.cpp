#include <boost/python.hpp>
#include <//home/pfernique/Desktop/AutoWIG/example/simple_example/binomial.h>
PyObject* error_type_f926cb231a7f5da09f313cd361ff94c7 = 0;

void translate_error_f926cb231a7f5da09f313cd361ff94c7(class ::std::exception const & error)
{ PyErr_SetObject(error_type_f926cb231a7f5da09f313cd361ff94c7, boost::python::object(error).ptr()); }


void _std_exception()
{
        std::string std_a5e4e9231d6351ccb0e06756b389f0af_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".std");
        boost::python::object std_a5e4e9231d6351ccb0e06756b389f0af_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(std_a5e4e9231d6351ccb0e06756b389f0af_name.c_str()))));
        boost::python::scope().attr("std") = std_a5e4e9231d6351ccb0e06756b389f0af_module;
        boost::python::scope std_a5e4e9231d6351ccb0e06756b389f0af_scope = std_a5e4e9231d6351ccb0e06756b389f0af_module;
        boost::python::scope class_f926cb231a7f5da09f313cd361ff94c7 = boost::python::class_< class ::std::exception, class ::std::exception* >("Exception", boost::python::no_init);
        error_type_f926cb231a7f5da09f313cd361ff94c7 = class_f926cb231a7f5da09f313cd361ff94c7.ptr();
        boost::python::register_exception_translator< class ::std::exception >(&translate_error_f926cb231a7f5da09f313cd361ff94c7);
    
}