#include <boost/python.hpp>
#include <llvm/Support/PrettyStackTrace.h>


void export_class_llvm__pretty_stack_trace_entry()
{
    std::string llvm_d1608489_da06_5e6e_adeb_67121a123bdd_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".llvm");
    boost::python::object llvm_d1608489_da06_5e6e_adeb_67121a123bdd_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(llvm_d1608489_da06_5e6e_adeb_67121a123bdd_name.c_str()))));
    boost::python::scope().attr("llvm") = llvm_d1608489_da06_5e6e_adeb_67121a123bdd_module;
    boost::python::scope llvm_d1608489_da06_5e6e_adeb_67121a123bdd_scope = llvm_d1608489_da06_5e6e_adeb_67121a123bdd_module;
    boost::python::class_< ::llvm::PrettyStackTraceEntry, ::llvm::PrettyStackTraceEntry*, boost::noncopyable >("PrettyStackTraceEntry", boost::python::no_init);
}