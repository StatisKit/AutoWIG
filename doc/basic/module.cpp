#include <boost/python.hpp>

void wrapper_4046a8421fe9587c9dfbc97778162c7d();
void wrapper_f926cb231a7f5da09f313cd361ff94c7();
void wrapper_92d464d1243554009adc48a065a5be3e();

boost::python::docstring_options docstring_options(1, 0, 0);

BOOST_PYTHON_MODULE(_module)
{
    wrapper_4046a8421fe9587c9dfbc97778162c7d();
    wrapper_f926cb231a7f5da09f313cd361ff94c7();
    wrapper_92d464d1243554009adc48a065a5be3e();
}