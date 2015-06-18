#include <boost/python.hpp>
#include <llvm/ADT/FoldingSet.h>

void export_class_llvm_folding_set_impl_node()
{
    std::string llvm_d1608489_da06_5e6e_adeb_67121a123bdd_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".llvm");
    boost::python::object llvm_d1608489_da06_5e6e_adeb_67121a123bdd_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(llvm_d1608489_da06_5e6e_adeb_67121a123bdd_name.c_str()))));
    boost::python::scope().attr("llvm") = llvm_d1608489_da06_5e6e_adeb_67121a123bdd_module;
    boost::python::scope llvm_d1608489_da06_5e6e_adeb_67121a123bdd_scope = llvm_d1608489_da06_5e6e_adeb_67121a123bdd_module;
    std::string FoldingSetImpl_f91cf25f_8a4e_5dc3_8329_ea2796128ba6_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + "._folding_set_impl");
    boost::python::object FoldingSetImpl_f91cf25f_8a4e_5dc3_8329_ea2796128ba6_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(FoldingSetImpl_f91cf25f_8a4e_5dc3_8329_ea2796128ba6_name.c_str()))));
    boost::python::scope().attr("_folding_set_impl") = FoldingSetImpl_f91cf25f_8a4e_5dc3_8329_ea2796128ba6_module;
    boost::python::scope FoldingSetImpl_f91cf25f_8a4e_5dc3_8329_ea2796128ba6_scope = FoldingSetImpl_f91cf25f_8a4e_5dc3_8329_ea2796128ba6_module;
    boost::python::class_< ::llvm::FoldingSetImpl::Node, ::llvm::FoldingSetImpl::Node *, boost::noncopyable >("Node", boost::python::no_init);
}